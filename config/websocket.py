# config/websocket.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from llmprox.api.consumers import LLMCompletionConsumer

websocket_urlpatterns = [
    re_path(r"ws/api/v1/completion/$", LLMCompletionConsumer.as_asgi()),
]

websocket_application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
