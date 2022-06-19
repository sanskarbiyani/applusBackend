import email
import imp
import json
from os import name
import os
import re
import zipfile
from urllib import response
from turtle import clear
from django.db.models import fields
from django.db.models.base import Model
import mimetypes
from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from django.utils.functional import partition
from django.views.decorators.csrf import csrf_protect
from django.db import connection, models
from uritemplate import partial
from dynamic_models.models import ModelSchema, FieldSchema, Lists
from django.urls import clear_url_caches
from importlib import import_module, reload
from django.contrib import admin
from django.conf import settings
from users.perimissions import IsAdminOrAnonymousUser, IsLoggedInUserOrAdmin
from users.models import NewUser, User_group_link
from users.serializers import CreateList_group_linkSerializer, List_group_linkSerializer, ResetFormEmailRequestSerializer, SetNewFormSerializer
from .models import List_Database, List_group_link, LogEntries
from rest_framework import generics, viewsets
from .serializers import GroupListSerializer, ListSerializer, GeneralSerializer, FieldSchemasSerializer, List_Database_Serializer, ModelSchemasSerializer, UpdateFieldSchemasSerializer, UserSerializer, LogentriesSerializer
from django.urls import reverse
from users.utils import Util
from django.apps import apps
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.management import call_command
from django.db import transaction
from dynamic_models import cache
from .permissions import IsLoggedInUser, IsUserHasPermission
from .admin import unregister, register, reregister
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView

from django.core.mail import send_mail
import asyncio
from notifications.models import TrackTime
from django.db.models import Q
from datetime import datetime, timedelta
# Create your views here.


def addModelEntries(request):
    return redirect('/admin')


def base(request):
    return render(request, 'base.html')


class CreateModel(viewsets.ModelViewSet):

    def post(self, request):

        # with transaction.atomic():

        reg_serializer = ModelSchemasSerializer(
            data={'name': (request.data)['modelname']})

        print(request.data)
        print(reg_serializer.is_valid())

        if reg_serializer.is_valid():

            newmodels = reg_serializer.save()

            model_schema = ModelSchema.objects.get(
                name=(request.data)['modelname'])

            if newmodels:
                print("51")
                modelname_serializer = List_Database_Serializer(data={'modelname': (request.data)['modelname'], 'description': (request.data)['description'], 'color': (
                    request.data)['color'], 'icon': (request.data)['icon'], 'created_by': NewUser.objects.get(email=(request.data)['created_by']).id})
                print("52")
                print(modelname_serializer.is_valid())
                print(modelname_serializer.errors)
                if modelname_serializer.is_valid():
                    newModelname = modelname_serializer.save()
                    print("88-done")
                    if newModelname:
                        if request.data['group'] != 'self':
                            link_serializers = CreateList_group_linkSerializer(data={'list': str(
                                newModelname.id), 'group': str(Group.objects.get(name=(request.data)['group']).id)})
                            print(link_serializers.is_valid())
                            print(link_serializers.errors)
                            if link_serializers.is_valid():

                                new_link_model = link_serializers.save()
                                if new_link_model:
                                    register(model_schema)
                                    reload(import_module(
                                        settings.ROOT_URLCONF))
                                    clear_url_caches()
                        else:
                            register(model_schema)
                            reload(import_module(settings.ROOT_URLCONF))
                            clear_url_caches()
                    print("94- life saver done")
                    ct = ContentType.objects.get_for_model(
                        model_schema.as_model())

                    Permission.objects.create(codename='Can_Edit_List',
                                              name='Can edit this the list',
                                              content_type=ct
                                              )
                    Permission.objects.create(codename='Can_Delete_List',
                                              name='Can delte this the list',
                                              content_type=ct
                                              )
                    Permission.objects.create(codename='Can_View_List',
                                              name='Can view this the list',
                                              content_type=ct
                                              )
                    Permission.objects.create(codename='Can_Add_List',
                                              name='Can add this the list',
                                              content_type=ct
                                              )
                    LogEntries.objects.create(user=request.user, contenttype="{} created new list {} in {} group.".format(request.user, (request.data)[
                                              'modelname'], (request.data)['group']), actionflag="Create", list=List_Database.objects.get(modelname=(request.data)['modelname']))
        else:

            return Response(data="List Already exists", status=status.HTTP_400_BAD_REQUEST)

        return Response("List Sucessfully Created!!!", status=status.HTTP_201_CREATED)


# API

class Allgroups(generics.GenericAPIView):
    serializer_class = GroupListSerializer

    # Define Custom Queryset
    def get(self, request):
        data = {}
        for grp in Group.objects.all():
            data[grp.name] = List_group_link.objects.filter(group=grp).values(
                'group__name', 'list__modelname', 'list__color', 'list__icon')
        print(data)
        return Response(data, status=status.HTTP_202_ACCEPTED)

    def post(self, request):
        print(request.data)
        obj = Group.objects.create(name=request.data['name'])
        User_group_link.objects.create(
            user=request.user, group=obj, permission='edit')
        return Response(data={"message": "created"}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        try:
            Group.objects.get(name=pk).delete()
        except Exception as e:

            print(e)
            pass

        return Response(data={"message": "created"}, status=status.HTTP_200_OK)
    pass


class AllLists(viewsets.ModelViewSet):

    serializer_class = ListSerializer

    def get_object(self, queryset=None, **kwargs):
        item = self.kwargs.get('pk')
        return get_object_or_404(List_Database, modelname=item)

    # Define Custom Queryset
    def get_queryset(self):

        return List_Database.objects.all()
    pass


class GeneralViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    def get_permissions(self):
        permission_classes = []
        if self.kwargs.get('group_name') == 'abc':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]
    permission_classes = [permissions.IsAuthenticated]
    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action == 'create':
    #         permission_classes = [permissions.IsAuthenticated, IsUserHasPermission]
    #     elif self.action == 'list':
    #         permission_classes = [permissions.IsAuthenticated,IsLoggedInUser]
    #     elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
    #         permission_classes = [permissions.IsAuthenticated,IsUserHasPermission]
    #     elif self.action == 'destroy':
    #         print("Called")
    #         permission_classes = [permissions.IsAuthenticated , IsUserHasPermission]
    #     print(permission_classes)
    #     return [permission() for permission in permission_classes]

    @property
    def model(self):
        print(self.kwargs)
        # app_models = apps.all_models['ddmapp']
        # print(app_models.get('user_groups').objects.all())
        # admin.site.register(app_models.get('user_groups'))
        # for app_config in apps.get_app_configs():
        #     for model in app_config.get_models():
        #         print(model)
        model = apps.get_model(app_label=str('ddmapp'), model_name=str(
            self.kwargs['model_name']).replace(" ", ""))
        return model

    def get_object(self):
        # print(self.request.data['indian?'])
        item = self.kwargs.get('pk')
        obj = get_object_or_404(self.model, id=item)
        # print('obj')

        return obj

    def get_queryset(self):
        model = self.model
        print("hello")
        obj = model.objects.all()
        self.check_object_permissions(self.request, {
                                      'list': self.kwargs['model_name'], 'group': self.kwargs['group_name']})
        return obj

    def get_serializer_class(self):
        GeneralSerializer.Meta.model = self.model
        return GeneralSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        print(serializer_class)
        # The context is where the request is added
        # to the serializer
        print(kwargs)
        kwargs['context'] = self.get_serializer_context()
        print(kwargs['context'])
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        print(serializer.is_valid())
        if serializer.is_valid(raise_exception=True):
            print("Inside.. Kaise???")
            newInstance = serializer.save()
            print(newInstance)
            if newInstance:
                pass
            else:
                return Response(data={'message': "Something Went Wrong"},
                                status=status.HTTP_400_BAD_REQUEST)
 #       # LogEntries.objects.create(user = request.user, contenttype = "{} created new Field {} -  in {} group.".format(request.user,(request.data)['modelname'],(request.data)['group']), actionflag = "Create")
        return Response(data={'message': "Success"},
                        status=status.HTTP_201_CREATED)

    @action(methods=['PUT'], detail=True)
    def upadteSingleCell(self, request, **kwargs):
        try:
            print(self.kwargs.get('pk'))

            instance = self.get_object()
            print(type(instance))
            # print(request.data['dateandtime'])
            # print(request.data)
            reg_serializer1 = self.get_serializer(
                instance, data=request.data, partial=True)
            print("Hellp")
            print(reg_serializer1.is_valid())
            print("Hellp")

            print("Hellp")
            if (not reg_serializer1.is_valid()):
                print(reg_serializer1.errors)
                return Response({"error": str("InValid Please Try Again")}, status=status.HTTP_400_BAD_REQUEST)

            reg_serializer1.save()

            print("64-done")

            # LogEntries.objects.create(user = request.user, contenttype = "{} Update {} list to  {}.".format(request.user,item,(request.data)), actionflag = "Update",list=List_Database.objects.get(modelname=item))

            # reload(import_module(settings.ROOT_URLCONF))
            # reload(import_module('ddmapp'))
            # clear_url_caches()

            return Response(reg_serializer1.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=True)
    def getinfo(self, request, **kwargs):
        model = self.model
        print("hello")
        # data = {'email_body': 'Tem msg', 'to_email': 'himanshuchaudhari890@gmail.com',
        #             'email_subject': 'Checking'}
        # Util.send_email(data)
        print("Hello")
        try:
            self.check_object_permissions(self.request, {
                                          'list': self.kwargs['model_name'], 'group': self.kwargs['group_name']})
            validation = User_group_link.objects.get(
                user=self.request.user.id, group__name=self.kwargs['group_name'])
            print(validation.permission)
            if validation.permission == 'view':
                return Response(data={'edit': False})
            else:
                return Response(data={'edit': True})
        except Exception as e:
            try:
                obj = List_Database.objects.get(
                    created_by=self.request.user.id, modelname=self.kwargs['model_name'])
                print("Daya Fir se Gadbad")
                print(obj)
                if obj:
                    return Response(data={'edit': True})

            except Exception as ex:
                print(ex)
                print("Toh Fir Yaha Pe Gadbad Hai ky")
                return Response(data={'edit': False})
            print(e)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['GET'], detail=True)
    def download(self, request, **kwargs):
        # http://127.0.0.1:8000/media/user_TrialList/bcc2_7e7HC82.pdf
        item = self.kwargs.get('id')
        f = self.kwargs.get('field_name')
        # print(self.model.objects.get(id=item))
        # file =  self.model.objects.filter(id=item).values(f)

        file = self.model.objects.only(f).get(id=item)
        print(getattr(file, f))
        file_handle = getattr(file, f).open()
        # print(file_handle)
        mimetype, _ = mimetypes.guess_type(getattr(file, f).path)
        response = FileResponse(file_handle, content_type=mimetype)
        response['Content-Length'] = getattr(file, f).size
        response['Content-Disposition'] = "attachment; filename={}".format(
            getattr(file, f))
        LogEntries.objects.create(user=request.user, contenttype="{} download {} file from {} list.".format(request.user, getattr(
            file, f), self.kwargs.get('model_name')), actionflag="Create", list=List_Database.objects.get(modelname=self.kwargs.get('model_name')))
        return response

    @action(methods=['GET'], detail=True)
    def download_zip(self, request, **kwargs):
        xxx = self.model.objects.only('docs').all()
        f = self.kwargs.get('field_name')
        mem_file = BytesIO()
        zip_file = zipfile.ZipFile(mem_file, 'w')

        for filename in xxx:
            if str(getattr(filename, 'docs')) != '':
                print("media/{}".format(str(getattr(filename, f))))
                zip_file.write("media/{}".format(str(getattr(filename, f))))

        zip_file.close()

        return HttpResponse(mem_file.getvalue(), content_type='application/zip', headers={'Content-Disposition': 'attachment; filename="My_Files.zip"'})

        # print(zip_file)
        # response['Content-Disposition'] = 'attachment; filename={}'.format('zipfile_name')
        # return response

        # # http://127.0.0.1:8000/media/user_TrialList/bcc2_7e7HC82.pdf
        # item = self.kwargs.get('id')
        # f = self.kwargs.get('field_name')
        # # print(self.model.objects.get(id=item))
        # # file =  self.model.objects.filter(id=item).values(f)
        # file = self.model.objects.only(f).get(id=item)
        # print(getattr(file,f))
        # file_handle = getattr(file,f).open()
        # # print(file_handle)
        # mimetype, _ = mimetypes.guess_type(getattr(file,f).path)
        # response = FileResponse(file_handle, content_type=mimetype)
        # response['Content-Length'] = getattr(file,f).size
        # response['Content-Disposition'] = "attachment; filename={}".format(getattr(file,f))
        # LogEntries.objects.create(user = request.user, contenttype = "{} download {} file from {} list.".format(request.user,getattr(file,f),self.kwargs.get('model_name')), actionflag = "Create",list=List_Database.objects.get(modelname=self.kwargs.get('model_name')) )
        # return response

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.id)

        LogEntries.objects.create(user=request.user, contenttype="{} Delete record id = '{}' from {} list.".format(
            request.user, obj.id, self.kwargs.get('model_name')), actionflag="Delete", list=List_Database.objects.get(modelname=self.kwargs.get('model_name')))
        self.perform_destroy(obj)
        if obj:
            return Response(data={'message': "Delete Successfully"},
                            status=status.HTTP_200_OK)
        self.model.refresh_from_db()

        return Response(status=status.HTTP_400_BAD_REQUEST)


class DeleteModel(viewsets.ModelViewSet):
    lookup_field = 'name'

    @property
    def model(self):
        return apps.get_model(app_label=str('dynamic_models'), model_name=str('ModelSchema'))

    def get_object(self):

        item = self.kwargs.get('name')
        obj = get_object_or_404(self.model, name=item)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        GeneralSerializer.Meta.model = self.model
        return GeneralSerializer

    def destroy(self, request, *args, **kwargs):
        item = self.kwargs.get('name')
        obj1 = List_Database.objects.get(modelname=item)
        logs = LogEntries.objects.filter(list=obj1)
        self.perform_destroy(logs)
        self.perform_destroy(obj1)
        objs = self.get_object()
        self.perform_destroy(objs)
        objContent = ContentType.objects.get(
            model=item.lower().replace(" ", ""))
        objPermission = Permission.objects.filter(content_type=objContent.id)
        self.perform_destroy(objContent)
        self.perform_destroy(objPermission)
        LogEntries.objects.create(user=request.user, contenttype="{} Delete  List ( {} ) ".format(
            request.user, item), actionflag="Delete")
        reload(import_module(settings.ROOT_URLCONF))
        clear_url_caches()

        # self.get_object().refresh_from_db()
        # obj1.refresh_from_db()
        # step3 :- Drop Model From SQLite Database
        return Response("List Deleted Successfully", status=status.HTTP_202_ACCEPTED)

    def get_queryset(self):

        return self.model.objects.all()


class CreateFields(viewsets.ModelViewSet):

    def post(self, request):

        try:
            print(request.data)
            model_schema = ModelSchema.objects.get(
                name=request.data['modelname'])

            # special_dict = {"name":"","data_type":"","model_schema":"","max_length":"","null":"","unique":"","input_type":"","description":"","columns":""}

            # special_dict['name'] = (request.data)['name']
            # special_dict['data_type'] = (request.data)['data_type']
            # special_dict['model_schema'] = model_schema
            # special_dict['max_length'] = (request.data)['max_length']
            # special_dict['null'] = (request.data)['null']
            # special_dict['unique'] = (request.data)['unique']
            # special_dict['input_type'] = (request.data)['input_type'],
            # special_dict['description'] = (request.data)['description'],
            # special_dict['columns'] = (request.data)['columns'],
            # field_serializer = FieldSchemasSerializer(data={'name':(request.data)['name']})

            # if field_serializer.is_valid():
            #     field_serializer.save()

            FieldSchema.objects.create(
                name=(request.data)['name'],
                data_type=(request.data)['data_type'],
                model_schema=model_schema,
                max_length=(request.data)['max_length'],
                null=(request.data)['null'],
                unique=(request.data)['unique'],
                input_type=(request.data)['input_type'],
                description=(request.data)['description'],
                columns=(request.data)['columns'],
            )
            print(request.user)
            reregister(model_schema)

            LogEntries.objects.create(user=request.user, contenttype="{} Created New Field ( {} ) in {} List.".format(request.user, (request.data)[
                                      'name'], request.data['modelname']), actionflag="Create", list=List_Database.objects.get(modelname=request.data['modelname']))

        except Exception as e:
            print(e)
            return Response(data={
                "message": "Fields Cannot Created Check It again.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response("New Field Added", status=status.HTTP_201_CREATED)

        # if reg_serializer.is_valid():
        #     newmodels = reg_serializer.save()
        #     model_schema = ModelSchema.objects.get(name=(request.data)['modelname'])


class DeleteField(viewsets.ModelViewSet):
    lookup_field = 'id'

    @property
    def model(self):
        return apps.get_model(app_label=str('dynamic_models'), model_name=str('FieldSchema'))

    @property
    def model_schema(self):
        print('From the property.')
        print(self.kwargs['model_name'])
        return ModelSchema.objects.get(name=str(self.kwargs['model_name']))

    def get_object(self):
        item = self.kwargs.get('id')
        print(item)
        print("model", self.model)
        print("model Schema", self.model_schema)
        # print("ln",FieldSchema.objects.filter(name='Full Name',model_schema=self.model_schema))

        return FieldSchema.objects.get(name=item, model_schema=self.model_schema)

    def get_queryset(self):
        return self.model.objects.filter(model_schema=self.model_schema)

    def get_serializer_class(self):
        GeneralSerializer.Meta.model = self.model
        return GeneralSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            objs = self.get_object()

            self.perform_destroy(objs)

            print("Hello")
            reload(import_module(settings.ROOT_URLCONF))
            reload(import_module('ddmapp'))
            clear_url_caches()
            reregister(self.model_schema)
            # step3 :- Drop Model From SQLite Database
            LogEntries.objects.create(user=request.user, contenttype="{} Delete  Field ( {} ) in {} List.".format(request.user, self.kwargs.get(
                'id'), self.kwargs['model_name']), actionflag="Create", list=List_Database.objects.get(modelname=self.kwargs['model_name']))
            return Response("Delete Sucessfully", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={
                "message": "Fields Not Deleted.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class EditField(generics.RetrieveUpdateAPIView):

    serializer_class = UpdateFieldSchemasSerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'name'

    @property
    def model(self):
        return apps.get_model(app_label=str('dynamic_models'), model_name=str('FieldSchema'))

    @property
    def model_schema(self):
        return ModelSchema.objects.get(name=str(self.kwargs['model_name']))

    def get_object(self):
        item = self.kwargs.get('name')
        return get_object_or_404(self.model, name=item, model_schema=self.model_schema)

    def get_queryset(self):
        return self.model.objects.filter(model_schema=self.model_schema)


class EditModelname(viewsets.ModelViewSet):
    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    serializer_class = ModelSchemasSerializer

    def get_object(self):
        item = self.kwargs.get('name')
        return ModelSchema.objects.get(name=item)

    def get_queryset(self):
        return ModelSchema.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            item = self.kwargs.get('name')

            instance = List_Database.objects.get(modelname=item)
            print(instance)
            print(request.data)
            reg_serializer1 = List_Database_Serializer(
                instance, data=request.data, partial=True)
            print(reg_serializer1.is_valid())
            print(reg_serializer1.errors)
            reg_serializer1.save()
            print("64-done")
            try:
                if request.data['modelname']:
                    instance = self.get_object()
                    data = {'name': request.data['modelname']}
                    print(instance)
                    unregister(instance)
                    reg_serializer = ModelSchemasSerializer(
                        instance, data=data, partial=True)

                    if reg_serializer.is_valid():
                        reg_serializer.save()
                        model_schema = ModelSchema.objects.get(
                            name=request.data['modelname'])
                        print(model_schema)
                        register(model_schema)

            except Exception as e:
                print(e)
                pass

            LogEntries.objects.create(user=request.user, contenttype="{} Update {} list to  {}.".format(
                request.user, item, (request.data)), actionflag="Update", list=List_Database.objects.get(modelname=item))

            reload(import_module(settings.ROOT_URLCONF))
            reload(import_module('ddmapp'))
            clear_url_caches()

            return Response(reg_serializer1.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_204_NO_CONTENT)


class AddNewListToGroup(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated, IsLoggedInUserOrAdmin]
    serializer_class = List_group_linkSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [
                permissions.IsAuthenticated, IsAdminOrAnonymousUser]
        elif self.action == 'list':
            permission_classes = [
                permissions.IsAuthenticated, IsAdminOrAnonymousUser]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [
                permissions.IsAuthenticated, IsLoggedInUserOrAdmin]
        elif self.action == 'destroy':
            print("Called")
            permission_classes = [
                permissions.IsAuthenticated, IsLoggedInUserOrAdmin]
        print(permission_classes)
        return [permission() for permission in permission_classes]

    def get_object(self):
        list1 = self.kwargs['list_name']
        list2 = self.kwargs.get('pk')

        print(str(list1).replace("_", " "))
        obj = List_group_link.objects.get(list=str(List_Database.objects.get(modelname=str(
            list1).replace("_", " ")).id), group=str(Group.objects.get(name=list2).id))
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        return List_group_link.objects.all()

    def create(self, request, *args, **kwargs):
        newuser = []
        print(request.data)
        try:
            for data in request.data['group']:

                link_serializers = CreateList_group_linkSerializer(data={'list': str(List_Database.objects.get(
                    modelname=request.data['list']).id), 'group': str(Group.objects.get(name=data['name']).id)})
                print(link_serializers.is_valid())
                print(link_serializers.errors)
                if link_serializers.is_valid():
                    link_serializers.save()
                    newuser.append(data['name'])
            LogEntries.objects.create(user=request.user, contenttype="{} Share Lists in {} group.".format(
                request.user, ",".join(newuser)), actionflag="Create", list=List_Database.objects.get(modelname=request.data['list']))
            return Response({"success": "New List Share Sucessfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        print("helo")
        return Response({"success": "New List Share Sucessfully"}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            print(self.action)
            list1 = self.kwargs['list_name']
            list2 = self.kwargs.get('pk')
            objs = self.get_object()
            self.perform_destroy(objs)
            LogEntries.objects.create(user=request.user, contenttype="{} Remove  List ( {} ) from {} group.".format(
                request.user, list1, list2), actionflag="Delete", list=List_Database.objects.get(modelname=list1))
            # step3 :- Drop Model From SQLite Database
            return Response("Delete Sucessfully", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={
                "message": "Link Not Deleteed.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    # def update(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         reg_serializer = ModelSchemasSerializer(instance, data=request.data)
    #         print("64-done")
    #         if reg_serializer.is_valid():
    #             reg_serializer.save()
    #         return Response(reg_serializer.data,status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"error":str(e)},status=status.HTTP_204_NO_CONTENT)


class LogEntriesDisplay(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated, IsLoggedInUserOrAdmin]
    serializer_class = LogentriesSerializer
    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action == 'create':
    #         permission_classes = [permissions.IsAuthenticated, IsAdminOrAnonymousUser]
    #     elif self.action == 'list':
    #         permission_classes = [permissions.IsAuthenticated,IsAdminOrAnonymousUser]
    #     elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
    #         permission_classes = [permissions.IsAuthenticated,IsLoggedInUserOrAdmin]
    #     elif self.action == 'destroy':
    #         print("Called")
    #         permission_classes = [permissions.IsAuthenticated , IsLoggedInUserOrAdmin]
    #     print(permission_classes)
    #     return [permission() for permission in permission_classes]

    def get_object(self):
        item = self.kwargs.get('pk')
        obj = LogEntries.objects.filter(
            list=List_Database.objects.get(modelname=item))
        return obj.order_by('-action_time')

    def get_queryset(self):
        item = self.kwargs.get('model_name')
        return LogEntries.objects.filter(list=List_Database.objects.get(modelname=item)).order_by('-action_time')
    # def create(self, request, *args, **kwargs):
    #     newuser=[]
    #     print(request.data)
    #     try:
    #         for data in request.data['group']:

    #                     link_serializers = CreateList_group_linkSerializer(data={'list':str(List_Database.objects.get(modelname=request.data['list']).id),'group':str(Group.objects.get(name=data['name']).id)})
    #                     print(link_serializers.is_valid())
    #                     print(link_serializers.errors)
    #                     if link_serializers.is_valid():
    #                         link_serializers.save()
    #                         newuser.append(data['name'])
    #         LogEntries.objects.create(user = request.user, contenttype = "{} Share Lists in {} group.".format(request.user,",".join(newuser)), actionflag = "Create")
    #         return Response({"success":"New List Share Sucessfully"},status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
    #     print("helo")
    #     return Response({"success":"New List Share Sucessfully"},status=status.HTTP_201_CREATED)

    # def destroy(self, request, *args, **kwargs):
    #     try:
    #         print(self.action)
    #         list1 = self.kwargs['list_name']
    #         list2 = self.kwargs.get('pk')
    #         objs = self.get_object()
    #         self.perform_destroy(objs)
    #         LogEntries.objects.create(user = request.user, contenttype = "{} Remove  List ( {} ) from {} group.".format(request.user,list1,list2), actionflag = "Create")
    #         #step3 :- Drop Model From SQLite Database
    #         return Response("Delete Sucessfully",status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response(data={
    #                                "message": "Link Not Deleteed.",
    #                                 "error": str(e)
    #                                                 },status=status.HTTP_400_BAD_REQUEST )


class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RequestFormEntryEmail(generics.GenericAPIView):
    serializer_class = ResetFormEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')
        print(request.data)
        if True:
            user = NewUser.objects.get(email='himanshuchaudhari2346@gmail.com')
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            # print(user)
            # print(type(user))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse('ddmapp_api:form-reset-confirm', kwargs={
                                   'uidb64': uidb64, 'token': token, 'entry_id': 1, 'modelname': 'ListOne'})
            print(user, uidb64, token, smart_str(
                urlsafe_base64_decode(uidb64)))
            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to Fill your Information  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {'email_body': email_body, 'to_email': 'himanshuchaudhari890@gmail.com',
                    'email_subject': 'Filled Your Information'}
            send_mail(
                'Reset Password Link.',
                email_body,
                'Kshitija.External@idiada.com',
                [user.email],  # Can we wrong.
            )
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class FormTokenCheckAPI(generics.GenericAPIView):
    # serializer_class = SetNewFormSerializer

    def get(self, request, uidb64, token, entry_id, modelname):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = NewUser.objects.get(id=id)
            print(id, user, PasswordResetTokenGenerator().check_token(user, token))
            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:

                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:

                    return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'_'+entry_id+'&token='+token+'_'+modelname)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewFormDataAPIView(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]
    # permission_classes = [permissions.IsAuthenticated]

    @property
    def model(self):
        model = apps.get_model(app_label=str('ddmapp'),
                               model_name=str(self.kwargs['model_name']))
        return model

    def get_object(self):
        item = self.kwargs.get('pk')
        obj = get_object_or_404(self.model, id=item)
        # print('obj')

        return obj

    def get_queryset(self):
        model = self.model
        print("hello")
        obj = model.objects.all()
        self.check_object_permissions(self.request, {
                                      'list': self.kwargs['model_name'], 'group': self.kwargs['group_name']})
        return obj

    def get_serializer_class(self):
        GeneralSerializer.Meta.model = self.model
        return GeneralSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()

        # The context is where the request is added
        # to the serializer
        kwargs['context'] = self.get_serializer_context()

        return serializer_class(*args, **kwargs)

    def patch(self, request):
        try:
            token = request.data.get('token')
            uidb64 = request.data.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = 'himanshu'+'ListOne'
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            # user.set_password(password)
            # user.save()
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            # return (user)
            return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)

# Kush


class displayUserName(APIView):
    def get(self, request, user_email):
        get_User = NewUser.objects.get(email=user_email)
        return Response({'success': True, 'message': get_User.user_name}, status=status.HTTP_200_OK)
