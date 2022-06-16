from msilib.schema import File
from django.urls import path, re_path
from .views import GetMessages, GetConnectedUsers, GetAllUsers, GetUserName
from .views import GetFileInput, FileDownload, MarkAsRead

app_name = 'chatApp'
urlpatterns = [
    path('messages/<str:user_email>/<str:receiver_email>/',
         GetMessages.as_view(), name='get-user-messages'),
    path('users/<str:curr_user_email>/',
         GetConnectedUsers.as_view(), name='get-connected-users'),
    path('users/', GetAllUsers.as_view(), name='get-all-users'),
    path('getusername/<str:email>/', GetUserName.as_view(), name='get-username'),
    path('upload/', GetFileInput.as_view(), name='get-file-input'),
    path('download/<int:fileId>/', FileDownload.as_view(), name='download-file'),
    path('messages/', MarkAsRead.as_view(), name='mark-as-read'),
]
