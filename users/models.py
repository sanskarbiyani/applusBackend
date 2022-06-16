from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, Group, Permission, PermissionsMixin, BaseUserManager
# from ddmapp.models import List_Database
from dynamic_models.models import ModelSchema
from django.apps import apps
from django.conf import settings

class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, user_name, first_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, first_name, password, **other_fields)


    def create_user(self, email, user_name, first_name, password,about,qualifacation, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name,
                          first_name=first_name ,about=about,qualifacation=qualifacation, **other_fields)
        user.set_password(password)
        user.save()
        return user


class NewUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    user_name = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    about = models.TextField(_(
        'about'), max_length=500, blank=True)
    qualifacation = models.TextField(_('qualification'),max_length=100,blank=True)
        
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name', 'first_name','about','qualifacation']

    def __str__(self):
        return self.user_name
    

class User_group_link(models.Model):
    user = models.ForeignKey(NewUser,
    on_delete=models.CASCADE,
    related_name='user'
    )
    group= models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='group'
    )
    permission = models.CharField(max_length=100)


    
class GropFolderLink(models.Model):
    name =  models.CharField(max_length=20)
    group = models.ForeignKey(Group,
            on_delete=models.Case,
            related_name='users.User_group_link.group+')


    
    