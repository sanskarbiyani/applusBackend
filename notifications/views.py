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
        CandidateName = FieldSchema.objects.get(model_schema=listModelSchema, name=request.data["candidate"])
        trackObject = TrackTime.objects.create(list_name = listModelSchema, time_field_name=fieldName, interviewer_field_name=NotifiedName, candidate_field_name=CandidateName)
        trackObject.save()
        return Response(data="Received.")

