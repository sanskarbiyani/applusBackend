from django.db import models
from dynamic_models.models import ModelSchema, FieldSchema

# Create your models here.


class TrackTime(models.Model):
    list_name = models.ForeignKey(ModelSchema, on_delete=models.CASCADE)
    time_field_name = models.ForeignKey(
        FieldSchema, on_delete=models.CASCADE, related_name='dateTime', null=True)
    interviewer_field_name = models.ForeignKey(
        FieldSchema, on_delete=models.CASCADE, related_name='notified', null=True)
    candidate_field_name = models.ForeignKey(
        FieldSchema, on_delete=models.CASCADE, related_name='candidate_name', null=True)
    last_email_sent = models.JSONField(null=True)
