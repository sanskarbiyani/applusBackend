from concurrent.futures import thread
from statistics import mode
from urllib import response
from django.dispatch import receiver
from rest_framework.views import APIView
from .models import Messages, Thread, UploadedFiles
from users.models import NewUser as User
from .serializers import MessageSerializer, ThreadSerializer, UserEmailSerializer, UserNameSerializer, UserNameEmailSerializer
from .serializers import UploadedFileSerializer, FileSerializer
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.renderers import BaseRenderer
from django.core.files import File
from django.http import FileResponse, HttpResponse
import mimetypes
# Create your views here.


class GetMessages(APIView):
    """
    API endpoint that gets the Messages of a particular user
    """

    def get(self, request, user_email, receiver_email):
        sender = User.objects.get(email=user_email)
        receiver = User.objects.get(email=receiver_email)
        thread_obj = Thread.objects.filter(
            user1__in=[sender, receiver], user2__in=[sender, receiver])[0]
        message_list = Messages.objects.filter(thread=thread_obj)
        # print(getattr(message_list[0], 'message'))
        serializer = MessageSerializer(message_list, many=True)
        return Response(serializer.data)


class GetConnectedUsers(APIView):
    """
    URL endpoint to get the other_users connected to current_user in the past (Thread for them exists)
    """

    def get(self, request, curr_user_email):
        curr_user_obj = User.objects.get(email=curr_user_email)
        threads = Thread.objects.filter(
            Q(user1=curr_user_obj) | Q(user2=curr_user_obj))
        thread_serializer = ThreadSerializer(
            threads, many=True, context={'threads': threads, 'curr_user': curr_user_obj})
        return Response(thread_serializer.data)


class GetAllUsers(APIView):
    """
    URL endpoint to get all the user's email.
    """
    
    def get(self, request):
        all_users = User.objects.all().values('email', 'user_name')
        print(all_users)
        serializer = UserEmailSerializer(all_users, many=True)
        return Response(serializer.data)


class GetUserName(APIView):
    """
    URL endpoint to get username of the given user
    """
    def get(self, request, email):
        user_name = User.objects.get(email = email)
        serializer = UserNameSerializer(user_name)
        return Response(serializer.data)


class GetFileInput(APIView):
    """
    URL endpoint to get the files uploaded by the users.
    """
    parser_classes = [FormParser, MultiPartParser]
    
    def get(self, request):
        return Response('Found..', status=status.HTTP_200_OK)

    def post(self, request):
        try:
            file = request.data['file']
            receiver = request.data['to']
        except:
            return Response('File Or Receiver not found.', status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                receiver_obj = User.objects.get(email=receiver)
            except ObjectDoesNotExist:
                return Response('Receiver not found.', status=status.HTTP_404_NOT_FOUND)
            else:
                thread_obj = Thread.objects.filter(
                        user1__in=[request.user, receiver_obj], user2__in=[request.user, receiver_obj])[0]
                obj = UploadedFiles.objects.create(file=file, thread = thread_obj, sender = receiver_obj)
                obj.save()
                print(obj.id)
                # print(obj.name)
                return Response({'fileId': obj.id, 'message': 'File Received Successfully'}, status=status.HTTP_201_CREATED)
            

class MarkAsRead(APIView):
    def post(self, request):
        print(request.data)
        receiver_obj = User.objects.get(email=request.data['receiver'])
        thread_obj = Thread.objects.filter(user1__in=[request.user, receiver_obj], user2__in=[request.user, receiver_obj])[0]
        Messages.objects.filter(thread = thread_obj, is_read=False, sender=receiver_obj).update(is_read=True)
        return Response('Received Receiver.')
    

class FileDownload(APIView):
    """
    API endpoint to send the downloadable to the user.
    """
    # renderer_classes = [PassThroughRenderer]
    
    def get(self, request, fileId):
        file_obj = UploadedFiles.objects.get(pk=fileId)
        file_mime_type = mimetypes.guess_type(file_obj.file.name)[0]
        
        file_handler = file_obj.file.open()
        
        # response = FileResponse(file_handler, content_type=file_mime_type)
        # response['Content-Length'] = file_obj.file.size
        # response['Content-Disposition'] = f"attachment; filename={file_obj.file.name}"
        response = HttpResponse(file_handler.read())
        response['Content-Disposition'] = f"attachment; filename={file_obj.file.name}"
        
        return response