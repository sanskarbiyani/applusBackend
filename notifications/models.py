from django.db import models
from dynamic_models.models import ModelSchema, FieldSchema

# Create your models here.

class TrackTime(models.Model):
    list_name = models.ForeignKey(ModelSchema, on_delete=models.CASCADE)
    field_name = models.ForeignKey(FieldSchema, on_delete=models.CASCADE, related_name='dateTime', null=True)
    notified_name = models.ForeignKey(FieldSchema, on_delete=models.CASCADE, related_name='notified', null=True)
    last_email_sent = models.JSONField(null=True)
