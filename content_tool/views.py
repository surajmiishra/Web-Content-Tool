from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import json
import logging
from urllib.parse import urlparse, urlunparse
import warnings
import os

logger = logging.getLogger(__name__)

# Suppress TensorFlow deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="tensorflow")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow INFO and WARNING logs

# Load a text generation model (e.g., GPT-2)
text_generation_model = AutoModelForCausalLM.from_pretrained("gpt2")
text_generation_tokenizer = AutoTokenizer.from_pretrained("gpt2")
text_generation_pipeline = pipeline("text-generation", model=text_generation_model, tokenizer=text_generation_tokenizer)

# In-memory storage for ingested content and conversation history
ingested_content = {}
conversation_history = {}

def index(request):
    """Render the main page."""
    return render(request, 'content_tool/index.html')

def normalize_url(url):
    """Normalize a URL by removing fragments and ensuring consistent formatting."""
    parsed_url = urlparse(url)
    return urlunparse(parsed_url._replace(fragment=""))

@csrf_exempt
def ingest_url(request):
    """Ingest content from a URL and store it in memory."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            if not url:
                return JsonResponse({'error': 'URL is required'}, status=400)
            normalized_url = normalize_url(url)
            logger.info(f"Normalized URL for ingestion: {normalized_url}")  # Log the normalized URL
            response = requests.get(normalized_url)
            if response.status_code != 200:
                return JsonResponse({'error': f'Failed to fetch URL. Status code: {response.status_code}'}, status=400)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(strip=True)
            if not text:
                return JsonResponse({'error': 'No content found at the provided URL'}, status=400)
            # Store the content in the in-memory dictionary
            ingested_content[normalized_url] = text
            conversation_history[normalized_url] = []  # Initialize conversation history for the URL
            logger.info(f"Ingested content for URL: {normalized_url}")  # Log the ingested URL
            return JsonResponse({'status': 'success', 'content': text[:200], 'url': normalized_url})  # Return snippet
        except Exception as e:
            logger.error(f"Error in ingest_url: {e}")  # Log the error
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def ask_question(request):
    """Answer a question based on ingested content."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Received data: {data}")  # Log the incoming data
            question = data.get('question')
            url = data.get('url')  # Single URL to retrieve the context
            if not question:
                logger.warning("Question is missing in the request.")
                return JsonResponse({'error': 'Question is required'}, status=400)
            if not url:
                logger.warning("URL is missing in the request.")
                return JsonResponse({'error': 'URL is required'}, status=400)
            normalized_url = normalize_url(url)
            logger.info(f"Normalized URL for question: {normalized_url}")  # Log the normalized URL
            if normalized_url not in ingested_content:
                logger.warning(f"No context available for URL: {normalized_url}")
                return JsonResponse({
                    'error': f'No context available for the provided URL: {normalized_url}. Please ingest this URL first.'
                }, status=400)
            context = ingested_content[normalized_url]
            # Append conversation history to the context
            history = "\n".join(conversation_history[normalized_url])
            full_context = f"Context:\n{context}\n\nHistory:\n{history}\n\nQuestion: {question}\nAnswer:"
            logger.info(f"Using context for URL: {normalized_url}")  # Log the context usage

            # Truncate the input context if it exceeds the model's maximum input length
            max_input_length = text_generation_tokenizer.model_max_length
            input_ids = text_generation_tokenizer(full_context, return_tensors="pt", truncation=True, max_length=max_input_length).input_ids
            truncated_context = text_generation_tokenizer.decode(input_ids[0], skip_special_tokens=True)

            # Generate a conversational response
            try:
                response = text_generation_pipeline(
                    truncated_context,
                    max_new_tokens=100,  # Generate up to 100 new tokens
                    num_return_sequences=1,
                    pad_token_id=text_generation_tokenizer.eos_token_id
                )
                generated_text = response[0]['generated_text']
                logger.info(f"Generated text: {generated_text}")  # Log the generated text

                # Extract the generated answer
                if "Answer:" in generated_text:
                    answer = generated_text.split("Answer:")[-1].strip()
                else:
                    answer = "I'm sorry, I couldn't generate a proper answer based on the ingested content."
            except Exception as e:
                logger.error(f"Error during text generation: {e}")
                answer = "I'm sorry, there was an issue generating a response. Please try again."

            # Update conversation history
            conversation_history[normalized_url].append(f"Q: {question}\nA: {answer}")
            logger.info(f"Answer generated: {answer}")  # Log the generated answer
            return JsonResponse({'answer': answer})
        except json.JSONDecodeError:
            logger.error("Invalid JSON in the request body.")
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logger.error(f"Error in ask_question: {e}")  # Log the error
            return JsonResponse({'error': str(e)}, status=500)
    logger.warning("Invalid request method.")
    return JsonResponse({'error': 'Invalid request method'}, status=405)