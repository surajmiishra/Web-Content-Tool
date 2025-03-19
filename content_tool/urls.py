from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ingest/', views.ingest_url, name='ingest_url'),
    path('ask/', views.ask_question, name='ask_question'),
]
