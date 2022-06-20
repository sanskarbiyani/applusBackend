from django.contrib.auth.models import Group
from django.db import models
from django.db.models.base import Model

from django.apps import apps
from django.conf import settings
from users.models import NewUser, User_group_link, GropFolderLink
# Create your models here.

class List_Database(models.Model):
    modelname = models.CharField(max_length=100)
    description = models.TextField(max_length=1500, null=True)
    color = models.CharField(max_length=100, null=True)
    icon = models.CharField(max_length=150, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
    on_delete=models.DO_NOTHING,
    related_name='createduser'
    )

    def __str__(self):
        return self.modelname

class List_group_link(models.Model):
    list = models.ForeignKey(List_Database,
    on_delete=models.CASCADE,
    related_name='model_list'
    )

    group = models.ForeignKey(
        
        Group,
        on_delete=models.CASCADE,
        related_name='users.List_group_link.group+'
    )

    
class GroupFolderLink_List(models.Model):
    groupfolderlink = models.ForeignKey(GropFolderLink,on_delete=models.CASCADE,related_name='users.GropFolderLink.group+')
    list            = models.ForeignKey(List_Database,on_delete=models.CASCADE,related_name='lists')


class LogEntries(models.Model):
    action_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
    on_delete=models.DO_NOTHING,
    related_name='userwhochange'
    )
    contenttype = models.TextField(max_length=2000)
    actionflag = models.CharField(max_length=200)
    list = models.ForeignKey(List_Database,
    on_delete=models.DO_NOTHING,
    related_name="logentrilist",
        blank=True,
        null=True)
