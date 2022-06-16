from django.urls import path
from . import consumers

web_socket_urlpatterns = [
    # path('ws/room/<str:username>/', consumers.ChatConsumer.as_asgi()),
    # path('ws/', consumers.EchoConsumer.as_asgi()),
    path('ws/chat/', consumers.NewChatConsumer.as_asgi()),
]