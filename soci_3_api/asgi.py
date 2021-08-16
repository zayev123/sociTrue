
'''
ASGI config for soci_3_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soci_3_api.settings")
django.setup()
'''
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soci_3_api.settings")
django.setup()
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chatSoci.routing

#######################################

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chatSoci.routing.websocket_urlpatterns
        )
    ),
})
