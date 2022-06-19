from django.contrib import admin
from django.db.models.base import Model
from dynamic_models.models import ModelSchema,  FieldSchema, Lists
from .models import List_Database, List_group_link, GroupFolderLink_List, LogEntries
from dynamic_models import cache
from django.urls import clear_url_caches
from importlib import import_module, reload
from dynamicmodels import settings
from django.apps import apps


# @admin.register(CustomGroup)
# class CustomGroups(admin.ModelAdmin):
#     list_display = ('name','creater')

@admin.register(Lists)
class ListsAdmin(admin.ModelAdmin):
    list_display = ('Id', 'name', 'date', 'columns')


@admin.register(LogEntries)
class LogEnteriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'action_time', 'user',
                    'contenttype', 'actionflag', 'list')


admin.site.register(ModelSchema)
admin.site.register(FieldSchema)
# admin.site.register(LogEntries)
# admin.site.register(ModelSchema.objects.get(name='Demo').as_model())
# admin.site.register(ModelSchema.objects.get(name='Experiment').as_model())
# admin.site.register(ModelSchema.objects.get(name='TempList').as_model())


def register(model_schema):
    class ddmappAdmin(admin.ModelAdmin):
        pass
    print(model_schema)
    admin.site.register(model_schema.as_model(), ddmappAdmin)
    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()


def reregister(modelSchema, **kwargs):
    unregister(modelSchema)
    register(modelSchema)
    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()


def unregister(modelSchema, **kwargs):
    for reg_model in list(admin.site._registry.keys()):
        if modelSchema.get_db_table().db_table == reg_model._meta.db_table:
            del admin.site._registry[reg_model]
    try:
        admin.site.unregister(modelSchema.as_model())
    except admin.sites.NotRegistered:
        pass
    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()


# def registerModel(model):
#     admin.site.register(model)

# def unregisterModel(model):
#     admin.site.unregister(model)


models = List_Database.objects.all()
for model in models:
    reg_model = ModelSchema.objects.get(name=model.modelname).as_model()
    admin.site.register(reg_model)

# app_models = apps.all_models['auth']
# print(app_models.get('user_groups').objects.all())
# admin.site.register(app_models.get('user_groups'))
# for app_config in apps.get_app_configs():
#     for model in app_config.get_models():
#         print(model)
admin.site.register(List_group_link)
admin.site.register(List_Database)


@admin.register(GroupFolderLink_List)
class ListsAdmin(admin.ModelAdmin):
    list_display = ('id', 'groupfolderlink', 'list')
