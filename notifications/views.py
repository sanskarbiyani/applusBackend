from unicodedata import name
from numpy import rint
from rest_framework.views import APIView
from rest_framework.response import Response
from django.apps import apps
from dynamic_models.models import FieldSchema, ModelSchema
from .models import TrackTime

class Notification(APIView):
    def post(self, request):
        # To get the model/ table
        # listModel = apps.get_model(app_label=str('ddmapp'), model_name=listname)
        listModelSchema = ModelSchema.objects.get(name=request.data["listName"])
        fieldName = FieldSchema.objects.get(model_schema=listModelSchema, name=request.data["fieldName"])
        NotifiedName = FieldSchema.objects.get(model_schema=listModelSchema, name=request.data["notified"])
        trackObject = TrackTime.objects.create(list_name = listModelSchema, field_name=fieldName, notified_name=NotifiedName)
        trackObject.save()
        return Response(data="Received.")

