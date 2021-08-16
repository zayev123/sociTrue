# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/myChats/<int:profId>', consumers.MyChatsCnsmr.as_asgi()),
]
