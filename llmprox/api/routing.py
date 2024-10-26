# llm_app/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/api/v1/completion/$", consumers.LLMCompletionConsumer.as_asgi()),
]
