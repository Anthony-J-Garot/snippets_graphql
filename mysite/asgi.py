import os
import channels
from django.core.asgi import get_asgi_application
from snippets.routing import websocket_urlpatterns

# ------------------------------------------------------------------------- ASGI ROUTING

# Need to do this before importing anything channels related.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django_asgi_app = get_asgi_application()

# Now I can import channels related packages
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# NOTE: Please note `channels.auth.AuthMiddlewareStack` wrapper, for
# more details about Channels authentication read:
# https://channels.readthedocs.io/en/latest/topics/authentication.html
application = channels.routing.ProtocolTypeRouter({

    # Normally, Django uses HTTP to communicate between the client and server
    "http": django_asgi_app,

    # ws:// and wss://
    # Wrapping in AllowedHostsOriginValidator uses the ALLOWED_HOSTS from settings
    # Auth is for authenticated user handling.
    # URLRouter sends the request along to the particular consumer.
    "websocket": AuthMiddlewareStack(
        URLRouter(
            # Put in the websocket_urlpatterns
            websocket_urlpatterns
        )
    ),
})
