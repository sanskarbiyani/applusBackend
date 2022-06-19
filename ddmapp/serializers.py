from importlib import import_module
from django.db import models
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from dynamic_models.models import   ModelSchema,FieldSchema, Lists
from users.models import NewUser
from .models import GroupFolderLink_List, List_Database, List_group_link, LogEntries
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)
    class Meta:
        model = Group
        fields = '__all__'

class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List_group_link
        fields = '__all__'
        depth = 1

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model =  User
        fields =('username','groups')


class ListSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = List_Database
        
class GeneralSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = None

class List_Database_Serializer(serializers.ModelSerializer):
    
    class Meta:
        fields = ('modelname','description','color','icon','created_by')
        model = List_Database

    # def create(self, validated_data):
    #     print("Hello")
    #     print(validated_data)
        
        
    #     instance = List_Database.objects.create(
    #         modelname = validated_data['modelname'],
    #         description = validated_data['description'],
    #         color = validated_data['color'],
    #         icon = validated_data['icon'],
    #         created_by = validated_data['created_by']
    #     )
    #     print(instance)
    #     instance.save()
    #     return instance

class ModelSchemasSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = ModelSchema

    def update(self, instance, validated_data):
        modelname = validated_data.get("name",instance.name)
        print(modelname ,'-------------')
        instance.name = validated_data.get("name",instance.name)
        instance.save()
        obj = List_Database.objects.get(modelname=instance.name)
        print("hello") 
        obj.modelname = modelname
        obj.save()
        return instance

        

class FieldSchemasSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = FieldSchema
    
    
    def create(self, validated_data):
        print("Hello")
        return FieldSchema.objects.create(**validated_data)
    
    # def update(self,instance,validated_data):
    #     instance.name =         validated_data.get("name",instance.name)
    #     instance.model_schema = validated_data.get("model_schema",instance.model_schema)
    #     instance.data_type =    validated_data.get("data_type",instance.data_type)
    #     instance.null =         validated_data.get("null",instance.null)
    #     instance.unique =       validated_data.get("unique",instance.unique)
    #     instance.max_length =   validated_data.get("max_length",instance.max_length)
    #     print("Helllooooo",instance)
    #     instance.save()
    #     return instance
class UpdateFieldSchemasSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = FieldSchema
        ReadOnlyField = 'model_schema'


class LogentriesSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.user_name')
    email = serializers.CharField(source='user.email')
    class Meta:
        fields = ('id','action_time','contenttype','actionflag','user_name','email','list')
        model = LogEntries
        depth = 1

