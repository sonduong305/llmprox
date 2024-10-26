# config/asgi.py
import os
import sys
from pathlib import Path

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

# This allows easy placement of apps within the interior
# llmprox directory.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "llmprox"))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# This application object is used by any ASGI server configured to use this file.
django_application = get_asgi_application()

# Import websocket application here, so apps from django_application are loaded first
from config.websocket import websocket_application

app = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": websocket_application,
    }
)
application = app
