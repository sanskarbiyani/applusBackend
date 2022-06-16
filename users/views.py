from asyncio.windows_events import NULL
import email
from django.contrib.auth.models import Group, Permission, PermissionsMixin
from django.http import request
from rest_framework import serializers, status, viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from ddmapp.models import LogEntries
from .serializers import GroupSerializer, PermissionSerializer, ResetFormEmailRequestSerializer, ResetPasswordEmailRequestSerializer, SetNewFormSerializer, SetNewPasswordSerializer, User_group_link_serializer
from .serializers import CustomUserSerializer, GroupPermissionSerializer, GroupUserSerializer
from rest_framework import generics, viewsets
from django.shortcuts import render, redirect , get_object_or_404
from rest_framework.permissions import AllowAny
from django.apps import apps
from .models import NewUser, User_group_link
from django.contrib.admin.models import LogEntry, ADDITION,DELETION,CHANGE
from ddmapp.models import List_Database, List_group_link
from django.contrib.contenttypes.models import ContentType
import json
from rest_framework.decorators import action
from .perimissions import IsAdminOrAnonymousUser
from .utils import Util
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import Util
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
import os
from django.core.mail import send_mail

# class CustomUserCreate(APIView):
#     # permission_classes = [AllowAny]

#     def post(self, request, format='json'):
#         serializer = CustomUserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             if user:
#                 json = serializer.data
#                 return Response(json, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogEntryDisplay(viewsets.ModelViewSet):
    lookup_field = 'id'
    
    @property
    def model(self):
        return LogEntry

    def get_object(self):
        item = self.kwargs.get('id')
        return get_object_or_404(self.model,id=item)

    def get_serializer_class(self):
        return CustomUserSerializer

    def get_queryset(self):
        return self.model.objects.all()
    

class CustomUserCreate(viewsets.ModelViewSet):
    lookup_field = 'id'
    
    @property
    def model(self):
        return NewUser

    def get_object(self):
        item = self.kwargs.get('id')
        return get_object_or_404(self.model,id=item)

    
    def get_serializer_class(self):
        return CustomUserSerializer
    
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)\
   
    def get_queryset(self):
        
        return self.model.objects.all()

    @action(methods=['GET'], detail=True)
    def getSpecificUserDetail(self, request, **kwargs):
        group = self.kwargs['group_name']
        alllist = []
        print(self.kwargs['group_name'],'gelo')
        for user in self.model.objects.all():
            obj  = User_group_link.objects.filter(group__name = group, user= user.id).values('user__user_name','user__email')
            if len(obj) ==0:
                alllist.append({'user_name':user.user_name,'email':user.email,'id':user.id})
            # print(user.id)

        return Response(alllist)


class Allgroups(viewsets.ModelViewSet):
    lookup_field = 'name'
    lookup_url_kwarg = 'name'
    serializer_class = GroupSerializer

    def get_object(self, queryset=None, **kwargs):
        item = self.kwargs.get('name')
        print("hello",item)
        return get_object_or_404(Group, name=item)

    
    
    def post(self,request):
        serializer = GroupSerializer(data={'name':request.data['name'],'permissions':[]})

        if serializer.is_valid(raise_exception=True):
            
            newInstance = serializer.save()
            print(newInstance)
            if newInstance:
                if len(request.data['permissions']):
                    for per in request.data['permissions']:
                        print(per)
                        newInstance.permissions.add(Permission.objects.get(codename=per['codename']))
                    print((request.data['permissions']))
                    # newInstance.permissions.set(request.data['permissions'])
                pass
            else:
                return Response(data={'message':"Something Went Wrong"},
                                        status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data={'message':"Success"},
                                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
            try:
                instance = self.get_object()
                reg_serializer = GroupSerializer(instance, data={'name':request.data['name'],'permissions':[]})
                
                if reg_serializer.is_valid():
                    reg_serializer.save()
                    if len(request.data['permissions']):
                        for per in request.data['permissions']:
                            if per not in instance.permissions.all():
                                instance.permissions.add(Permission.objects.get(codename=per['codename']))
                    else:
                        instance.permissions.clear()    
                return Response(reg_serializer.data,status=status.HTTP_302_FOUND)
            except Exception as e:
                return Response({"error":str(e)},status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(data={
                                    "message":'Group Deleted Successfully'
            },                    status=status.HTTP_301_MOVED_PERMANENTLY)
        except Exception as e:
            return Response(data={
                                   "message": "Group Not Deleted.",
                                    "error": str(e)
                                                    },status=status.HTTP_400_BAD_REQUEST )


        
    # Define Custom Queryset
    def get_queryset(self):
        return Group.objects.all()
    pass

class AllPermission(viewsets.ModelViewSet):
    
    serializer_class = PermissionSerializer

    def get_object(self, queryset=None, **kwargs):
        item = self.kwargs.get('pk')
        return get_object_or_404(Permission, id=item)

    # Define Custom Queryset
    def get_queryset(self):
        return Permission.objects.all()
    pass

class GroupPermission(viewsets.ModelViewSet):
    
    serializer_class = GroupPermissionSerializer

    @property
    def model(self):
        app_models = apps.all_models['auth']
        return app_models.get('group_permissions')


    def get_object(self, queryset=None, **kwargs):
        item = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=item)

    # Define Custom Queryset
    def get_queryset(self):
        return (self.model).objects.all()


    
    pass



class Allinfo(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAnonymousUser]
    serializer_class = GroupUserSerializer

    # def get_permissions(self):
    #     if self.action in ['update', 'partial_update', 'destroy', 'list']:
    #         # which is permissions.IsAdminUser 
    #         return request.user and request.user.is_staff
    #     elif self.action in ['create']:
    #         # which is permissions.IsAuthenticated
    #         return request.user and Permissions.Is is_authenticated(request.user)             
    #     else :
    #         # which is permissions.AllowAny
    #         return True
    @property
    def model(self):
        app_models = apps.all_models['users']
        return app_models.get('newuser_groups')


    def get_object(self, queryset=None, **kwargs):
        item = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=item)

    
    # Define Custom Queryset
    def get_queryset(self):
        return (self.model).objects.all()
    pass

    @action(methods=['GET'], detail=True)
    def listDetail(self, request, **kwargs):
        alllist = {}
        temp =[]
        tempforgroup =[]
        for i in List_Database.objects.filter(created_by__email=request.user.email).values('modelname','description','icon','color'):
            temp.append((i['description'],i['icon'],i['color']))
            for j in List_group_link.objects.filter(list__modelname = i['modelname']).values('group__name'):

                tempforgroup.append(j['group__name'])
                
            if len(tempforgroup) == 0:
                temp.append("Private List")
            temp.append(tempforgroup)
            alllist[str(i['modelname'])] = temp
            temp = []
            tempforgroup=[]

        return Response(alllist)
    
    @action(methods=['GET'], detail=True)
    def AllInformations(self,request,**kwargs):
        print("From main",request.user.email)

        alldata ={}
        if request.method == "GET":        
            for index,id in  enumerate (User_group_link.objects.filter(user__email= request.user.email).values('group__id','group__name')):
                temp = {}
                temp['name'] = id['group__name']
                users = []
                lists =[]
                for i in User_group_link.objects.filter(group__name= id['group__name']).values('user__email','permission','user__user_name'):
                    users.append((i['user__email'],i['permission'],i['user__user_name']))
                for i in List_group_link.objects.filter(group__name=id['group__name']).values('list__modelname','list__created_by__email','list__description','list__color','list__icon'):
                    lists.append((i['list__modelname'],i['list__icon'],i['list__color'], i['list__created_by__email'],i['list__description']))
                temp['users'] = users
                temp['list'] = lists
                
                alldata[index] = temp
                
        return Response(alldata)
        # alldata ={}
        # if request.method == "GET":        
        #     for index,id in  enumerate (Group.objects.all().values('id','name')):
        #         temp = {}
        #         temp['name'] = id['name']
        #         users = []
        #         lists =[]
        #         for i in User_group_link.objects.filter(group__name= id['name']).values('user__email','permission','user__user_name'):
        #             users.append((i['user__email'],i['permission'],i['user__user_name']))
        #         for i in List_group_link.objects.filter(group__name=id['name']).values('list__modelname','list__created_by__email','list__description','list__color','list__icon'):
        #             lists.append((i['list__modelname'],i['list__icon'],i['list__color'], i['list__created_by__email'],i['list__description']))
        #         temp['users'] = users
        #         temp['list'] = lists
                
        #         alldata[index] = temp
                
        #     return Response(alldata)








@api_view(['GET'])
def PermissionOfUserAccGroup(request,grp,username):
    permission_classes = [permissions.IsAuthenticated]
    temp ={}
    temp1={}
    temp2={}
    temp3=[]
    app_models = apps.all_models['users']
    model= app_models.get('newuser_user_permissions')
    
    users_per ={}
    remaining ={}
    custom =[i['permission__id'] for i in model.objects.filter(newuser__email=username).values('permission__id')]
    
    

    for index,i in enumerate( List_group_link.objects.filter(group__name=grp).values('list__modelname')):
        
        user =[]
        rem  =[]
        # temp3.append(i['list__modelname'])
        for j in Permission.objects.filter(content_type__model=i['list__modelname'].lower()).values('codename','id'):
            print(j['id'])
            if j['id'] in custom:
                print("true")
                user.append(j['codename'])
            else:
                print("false")
                rem.append(j['codename'])
        if len(user):
            users_per[i['list__modelname']] = user
        remaining[i['list__modelname']] = rem
    # temp1['list']= temp3
    temp2['userPermission'] = users_per
    temp2['remainingPermission'] = remaining
    temp1['permission'] = temp2
    temp['index'] = temp1
        
        
    
    return Response(temp)



class AddUserToGroup(viewsets.ModelViewSet):
    
    serializer_class = User_group_link_serializer
    def get_object(self):
        list1 = self.kwargs['user_name']
        list2 = self.kwargs.get('pk')
        
        print(self.request.user.id)
        return User_group_link.objects.get(user=self.request.user.id,group__name=list2)

    def get_queryset(self):
        return User_group_link.objects.all()
    
    def create(self, request, *args, **kwargs):
        newuser= []
        # print(request.data)
        try:
            for user in request.data['email']:
                ss = NewUser.objects.get(user_name=user['user_name'])
                link_serializers = User_group_link_serializer(data={'user':str(ss.id),'group':str(Group.objects.get(name=request.data['group']).id),'permission':request.data['permission']})
                if link_serializers.is_valid():
                    print("data")
                    newuser.append(ss.user_name)
                    link_serializers.save()
                    email_body = 'Hello {}, \n{} shared list with you. \n'.format(", ".join(newuser),request.user)    
                    send_mail(
                        'List Shared with you',
                        email_body,
                        'Kshitija.Supekar.external@idiada.com',
                        [ss.email],
                        fail_silently=False,
                    )
            
            
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
        try:
            LogEntries.objects.create(user = request.user, contenttype = "{} Share List With  ( {} ) in {} group.".format(request.user,",".join(newuser),request.data['group']), actionflag = "Create",list=List_Database.objects.get(modelname=request.data['modelname'])) 
        except Exception as e:
            LogEntries.objects.create(user = request.user, contenttype = "{} Added ( {} ) in {} group.".format(request.user,",".join(newuser),request.data['group']), actionflag = "Create")
        return Response({"success":"New User Share Sucessfully"},status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            list1 = self.kwargs['user_name']
            list2 = self.kwargs.get('pk')
        
            print(self.request.user.id)
            objs = User_group_link.objects.get(user=str(NewUser.objects.get(user_name=list1).id),group__name=list2)
            print(objs)
            self.perform_destroy(objs)
            LogEntries.objects.create(user = request.user, contenttype = "{} remove {} from group ( {} ).".format(request.user,list1,list2), actionflag = "Delete")
            
            print("Hello")
            
            #step3 :- Drop Model From SQLite Database
            return Response("Delete Sucessfully",status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data={
                                   "message": "Link Not Deleteed.",
                                    "error": str(e)
                                                    },status=status.HTTP_400_BAD_REQUEST )

    def update(self, request, *args, **kwargs):
        print("jello")
        try:
            list1 = self.kwargs['user_name']
            list2 = self.kwargs.get('pk')
            print(list1,list2)
            instance = User_group_link.objects.get(user=str(NewUser.objects.get(user_name=list1).id),group__name=list2)
            print(instance)
            reg_serializer = User_group_link_serializer(instance, data={'user':str(NewUser.objects.get(user_name=request.data['user']).id),'group':str(Group.objects.get(name=request.data['group']).id),'permission':request.data['permission']})
            print("64-done")
            reg_serializer.is_valid()
            print(reg_serializer.errors)
            if reg_serializer.is_valid():
                reg_serializer.save()
            try:
                LogEntries.objects.create(user = request.user, contenttype = "{} Update Permssion of   ( {} ) to {} in {} group.".format(request.user,request.data['user'],request.data['permission'],request.data['group']), actionflag = "Update")      
            except Exception as e:
                print(e)    
            return Response(reg_serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_204_NO_CONTENT)

    
    @action(methods=['GET'], detail=True)
    def getUserInfo(self,request,**kwargs):
        # list1 = self.kwargs['user_name']
        list2 = self.kwargs['group_name']
        print("From main",list2)

        obj = User_group_link.objects.filter(group__name=list2).values('user__user_name','user__email','permission')        
        print(obj)
        return Response(data=obj)


class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')
        print(request.data)
        if NewUser.objects.filter(email=email).exists():
            user = NewUser.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            print(user)
            print(type(user))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse('users:password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            print(user,uidb64,token,smart_str(urlsafe_base64_decode(uidb64)))
            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            
                
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = NewUser.objects.get(id=id)
            print(id,user,PasswordResetTokenGenerator().check_token(user, token))
            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')
                    
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)



class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)

class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request):
        print("Helo")
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print("Jeol")
            return Response(status=status.HTTP_400_BAD_REQUEST)

##############################################################################################################

        
        
