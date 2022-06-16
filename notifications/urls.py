from django.urls import path
from . import views

app_name = 'notifications'
urlpatterns = [
    path('', views.Notification.as_view(), name='notification_main'),
]