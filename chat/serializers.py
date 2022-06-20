from concurrent.futures import thread
from dataclasses import field
from pyexpat import model
from attr import fields
from rest_framework import serializers
<<<<<<< HEAD
=======
from yaml import serialize
>>>>>>> 95ae8db0fba198080d12019d09c3fa7483f07697
from .models import Messages, Thread, UploadedFiles
from users.models import NewUser
from pprint import pprint


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewUser
        fields = ('email', )


class UserNameEmailSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(source='userstatus.is_online')
<<<<<<< HEAD

    class Meta:
        model = NewUser
        fields = ('email', 'user_name', 'is_online')


class UserNameSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(source='userstatus.is_online')

=======
    class Meta:
        model = NewUser
        fields = ('email', 'user_name', 'is_online')
        

class UserNameSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(source='userstatus.is_online')
>>>>>>> 95ae8db0fba198080d12019d09c3fa7483f07697
    class Meta:
        model = NewUser
        fields = ('user_name', 'is_online')


class MessageSerializer(serializers.ModelSerializer):
    sender_email = UserEmailSerializer(source='sender')

    class Meta:
        model = Messages
        fields = ('message', 'timestamp', 'sender_email', 'msg_type', 'fileId')


class ThreadSerializer(serializers.ModelSerializer):
    # To get all the messages using user defined message (get_message)
    messages = serializers.SerializerMethodField()
    user1 = UserNameEmailSerializer()
    user2 = UserNameEmailSerializer()
    unread_count = serializers.SerializerMethodField()
    # is_online = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ('messages', 'user1', 'user2', 'unread_count',)
        depth = 1

    def get_messages(self, obj):
        message = Messages.objects.filter(thread=obj)
        serializer = MessageSerializer(message, many=True)
        return serializer.data

    def get_unread_count(self, obj):
        curr_user = self.context['curr_user']
        if curr_user == obj.user1:
<<<<<<< HEAD
            messages_count = Messages.objects.filter(
                thread=obj, is_read=False, sender=obj.user2).count()
        else:
            messages_count = Messages.objects.filter(
                thread=obj, is_read=False, sender=obj.user1).count()
=======
            messages_count = Messages.objects.filter(thread = obj, is_read=False, sender=obj.user2).count()
        else:
            messages_count = Messages.objects.filter(thread = obj, is_read=False, sender=obj.user1).count()
>>>>>>> 95ae8db0fba198080d12019d09c3fa7483f07697
        return messages_count


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFiles
        fields = '__all__'

<<<<<<< HEAD

=======
>>>>>>> 95ae8db0fba198080d12019d09c3fa7483f07697
class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
