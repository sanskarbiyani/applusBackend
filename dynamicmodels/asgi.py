"""
ASGI config for dynamicmodels project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import django
django.setup()

import chat.routing  # nopep8
from .channelsmiddleware import JwtAuthMiddlewareStack  # nopep8


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dynamicmodels.settings')


asgi_application = get_asgi_application()
application = ProtocolTypeRouter({
    'http': asgi_application,
    'websocket': AllowedHostsOriginValidator(
        JwtAuthMiddlewareStack(
            URLRouter(
                chat.routing.web_socket_urlpatterns
            )
        )
    ),
})
