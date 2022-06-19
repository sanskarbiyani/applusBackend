from django.db import router
from django.urls import path
from django.urls.conf import re_path


from users.serializers import CustomUserSerializer
from .views import  AllPermission, Allinfo, CustomUserCreate, Allgroups, GroupPermission, PasswordTokenCheckAPI, PermissionOfUserAccGroup, AddUserToGroup, RequestPasswordResetEmail, SetNewPasswordAPIView, BlacklistTokenUpdateView
from rest_framework.routers import DefaultRouter


app_name = 'users'
router = DefaultRouter()
router.register('alluser', CustomUserCreate, basename='alluser')
router.register('allgroups', Allgroups, basename='allgroup')
router.register('allpermission', AllPermission, basename='allpermission')
router.register('groupPermission', GroupPermission, basename='groupPermission')
router.register('allinfo',Allinfo,basename='allinformation')
router.register(r'Share-user/(?P<user_name>[-\w.]+)', AddUserToGroup, basename='usersPermission'),
urlpatterns = [
     path('password-reset/<uidb64>/<token>/',
         PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
     # path('allgroups/', Allgroups.as_view({'get':'list'}),name='create_group'),       
     re_path(r'alluser/specific/(?P<group_name>\w+)',CustomUserCreate.as_view({'get':'getSpecificUserDetail'}),name='getSpecificUserDetail'),
     re_path(r'Share-user/specific/(?P<group_name>\w+)', AddUserToGroup.as_view({'get':'getUserInfo'}), name='getUserInfo'),
     path('allinformations/',Allinfo.as_view({'get': 'AllInformations'}),name="All Information"),
     re_path(r'listDetails/', Allinfo.as_view({'get':'listDetail'}), name='listDetail'),
     path('permissionOfUserAccGroup/<grp>/<username>',PermissionOfUserAccGroup,name="permissions"),
     path('request-reset-email/', RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    
     path('password-reset-complete', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
     path('logout/blacklist/', BlacklistTokenUpdateView.as_view(),
         name='blacklist')
# re_path(r'^permissionOfUserAccGroup/<int:pk>/', PermissionOfUserAccGroup, name='permssions'),
]

urlpatterns += router.urls