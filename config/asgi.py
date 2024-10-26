import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import llmprox.api.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(llmprox.api.routing.websocket_urlpatterns)
        ),
    }
)
