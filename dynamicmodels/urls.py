"""dynamicmodels URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import rest_framework
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.generic import TemplateView
from react import views

# catch_all = TemplateView.as_view(template_name="reactFrontEnd/index.html")

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    # path('', include('ddmapp.urls')),
    path('api/',include('ddmapp.urls',namespace='ddmapp_api')),
    path('', include('django.contrib.auth.urls')),
    path('project/docs/', include_docs_urls(title='RecuritmentAPI')),
    path('project/schema', get_schema_view(
        title="RecuritmentAPI",
        description="API for the Recuritment",
        version="1.0.0"
    ), name='openapi-schema'),
    path('api/user/', include('users.urls', namespace='users')),
    path('api-auth/', include('rest_framework.urls'), name='rest_framework'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/parser/', include('parserapp.urls', namespace='parserapp')),
    path('api/chat/', include('chat.urls', namespace='chatApp')),
    path('api/addNotificationTask/', include('notifications.urls', namespace='notifications')),
    path('reactFrontEnd/', views.render_react),
]
