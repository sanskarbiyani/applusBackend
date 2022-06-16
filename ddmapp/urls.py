from django.urls import path, re_path
from rest_framework import routers
from .views import  AddNewListToGroup, AllLists, Allgroups, DeleteField, DeleteModel, EditModelname, FormTokenCheckAPI, GeneralViewSet, CreateModel, CreateFields, RequestFormEntryEmail, SetNewFormDataAPIView, base, EditField,LogEntriesDisplay
from .views import base, displayUserName
from rest_framework.routers import DefaultRouter
app_name = "ddmapp_api"

router = DefaultRouter()
router.register('allLists', AllLists, basename='alllists')
# router.register('allGroups', Allgroups, basename='allgroup')
router.register(r'models/single/(?P<model_name>[\w\s]+)/(?P<group_name>\w+)', GeneralViewSet, basename='dynamic')
router.register(r'deleteField/(?P<model_name>[\w\s]+)',DeleteField,basename='delete_field')
router.register(r'deletemodel/(?P<model_name>\w+)',DeleteModel,basename='delete_model')
router.register(r'editModelname',EditModelname,basename="editModelName")
router.register(r'links/(?P<list_name>\w+)', AddNewListToGroup, basename='links'),
router.register(r'logentries/(?P<model_name>[\w\s]+)',LogEntriesDisplay, basename="log-entries")
# router.register(r'links',AddNewListToGroup,basename='createListLink')
urlpatterns = [
    path('form-reset/<uidb64>/<token>/<entry_id>/<modelname>/',
         FormTokenCheckAPI.as_view(), name='form-reset-confirm'),
    path('request-form-reset-email/', RequestFormEntryEmail.as_view(),
         name="request-form-reset-email"),
    
     path('form-reset-complete', SetNewFormDataAPIView.as_view({'get':'list'}),
         name='form-reset-complete'),

    # path('baseApp/', base, name='base_app'),
    # path('create', createModels, name='create_models'),
    # path('addModelEntries', addModelEntries, name='add_entries'),
    # path('showObjectLists', showObjectLists, name='show_objects'),
    path('allGroups/', Allgroups.as_view(), name='allgroups'),
    path('allGroups/<str:pk>/', Allgroups.as_view(), name='allgroupsdelete'),
    re_path(r'download/(?P<model_name>\w+)/(?P<id>[0-9]+)/(?P<field_name>\w+)/', GeneralViewSet.as_view({'get':'download'}), name='download'),
    re_path(r'models/get/(?P<model_name>[\w\s]+)/(?P<group_name>\w+)/', GeneralViewSet.as_view({'get':'getinfo'}), name='getdynamic'),
    re_path(r'models/getCellUpdate/(?P<model_name>[\w\s]+)/(?P<group_name>\w+)/(?P<pk>[0-9]+)/', GeneralViewSet.as_view({'put':'upadteSingleCell'}), name='upadteSingleCell'),
    path('registerModel/', CreateModel.as_view({'get':'list'}),name='create_model'),   
    path('addFields/', CreateFields.as_view({'get':'list'}),name='add_fields'),   
    re_path(r'^editField/(?P<name>\w+)/(?P<model_name>\w+)/update', EditField.as_view(), name='editfield'),
    # path('parser/', index.as_view(), name='parser')
    # re_path(r'^editModelname/(?P<name>\w+)/update', EditModelname.as_view({'get':'list'}), name='editModelnames'),
    # re_path(r'deleteModel/(?P<model_name>\w+)',DeleteModel.as_view({'get':'list'}),name='delete_model'),
    # re_path(r'^links/(?P<model_name>\w+)/(?P<field_name>\w+)/', AddNewListToGroup.as_view({'get':'list'}), name='links'),
    path('getusername/<str:user_email>/', displayUserName.as_view(), name='get-username'),
]

urlpatterns += router.urls