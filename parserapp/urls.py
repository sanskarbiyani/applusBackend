from django.db import router
from django.urls import path
from rest_framework.routers import DefaultRouter
from parserapp import views
app_name = "parserapp"
router = DefaultRouter()

urlpatterns = [
    path('parse-through/', views.index.as_view(), name='parserapp'),
    path('registerModel1/', views.CreateModels.as_view({'get':'list'}),name='create_model'),
    path('getFiles/<str:filename>/', views.FileDownloadListAPIView.as_view(),name='create_model')
]

urlpatterns += router.urls
