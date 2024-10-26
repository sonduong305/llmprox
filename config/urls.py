# config/urls.py

from django.contrib import admin
from django.urls import path

from llmprox.api.views import llm_completion  # Import your view

urlpatterns = [
    path("api/v1/chat-completion/", llm_completion, name="chat-completion"),
]
