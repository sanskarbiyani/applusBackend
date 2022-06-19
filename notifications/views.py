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
<<<<<<< HEAD
        trackObject = TrackTime.objects.create(list_name = listModelSchema, field_name=fieldName, notified_name=NotifiedName)
=======
        CandidateName = FieldSchema.objects.get(model_schema=listModelSchema, name=request.data["candidate"])
        trackObject = TrackTime.objects.create(list_name = listModelSchema, time_field_name=fieldName, interviewer_field_name=NotifiedName, candidate_field_name=CandidateName)
>>>>>>> 95ae8db0fba198080d12019d09c3fa7483f07697
        trackObject.save()
        return Response(data="Received.")

