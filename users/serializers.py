from unittest.util import _MAX_LENGTH
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
   
from django.contrib.auth.models import Group, Permission, User
from django.db import models
from django.db.models import fields
from django.urls.conf import include
from rest_framework import permissions, serializers
from ddmapp.models import List_group_link
from users.models import  NewUser, User_group_link
from ddmapp.serializers import GroupSerializer, List_Database_Serializer
from django.apps import apps
from django.db import transaction
from django.contrib.contenttypes.models import ContentType


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Currently unused in preference of the below.
    """
    email = serializers.EmailField(required=True)
    user_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=8, write_only=True)
    groups = GroupSerializer(many=True)
    class Meta:
        model = NewUser
        fields = ('email', 'user_name', 'password','groups')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # as long as the fields are the same, we can just use this
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  ContentType
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    
     
    content_type =ContentTypeSerializer()
    class Meta:
        model = Permission
        fields =('name','content_type')


class GroupPermissionSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    
    class Meta:
        app_models = apps.all_models['auth']
        model = app_models.get('group_permissions')
        fields = ('id','group')

class GroupUserSerializer(serializers.ModelSerializer):
    newuser = CustomUserSerializer()
    group = GroupSerializer()

    class Meta:
        app_models = apps.all_models['users']
        model = app_models.get('newuser_groups')
        fields = '__all__'



class CreateList_group_linkSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = List_group_link
    
        fields = '__all__'    
    
    # def create(self, validated_data):
    #     print(validated_data)
    #     return List_group_link(**validated_data)

class List_group_linkSerializer(serializers.ModelSerializer):
    list = List_Database_Serializer()
    group = GroupSerializer()

    class Meta:
        model = List_group_link
        read_only_fields = ('list','group')        
        fields = '__all__'    
    
    def create(self, validated_data):
        print(validated_data)
        return List_group_link(**validated_data)

class User_group_link_serializer(serializers.ModelSerializer):
    
    class Meta:
        model= User_group_link
        fields = '__all__'


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = NewUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
            
        return super().validate(attrs)


# class LogoutSerializer(serializers.Serializer):
#     refresh = serializers.CharField()

#     default_error_message = {
#         'bad_token': ('Token is expired or invalid')
#     }

#     def validate(self, attrs):
#         self.token = attrs['refresh']
#         return attrs

#     def save(self, **kwargs):

#         try:
#             RefreshToken(self.token).blacklist()

#         except TokenError:
#             self.fail('bad_token')

class ResetFormEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    modelname = serializers.CharField(max_length=500, required=True)
    entry_id = serializers.CharField(max_length=500, required=True)
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email','modelname','entry_id']


class SetNewFormSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    # def validate(self, attrs):
    #     try:
    #         password = attrs.get('password')
    #         token = attrs.get('token')
    #         uidb64 = attrs.get('uidb64')

    #         id = force_str(urlsafe_base64_decode(uidb64))
    #         user = NewUser.objects.get(id=id)
    #         if not PasswordResetTokenGenerator().check_token(user, token):
    #             raise AuthenticationFailed('The reset link is invalid', 401)

    #         user.set_password(password)
    #         user.save()

    #         return (user)
    #     except Exception as e:
    #         raise AuthenticationFailed('The reset link is invalid', 401)
            
    #     return super().validate(attrs)
