from dataclasses import field
from django.db import models
from numpy import blackman
from rest_framework import serializers
# Create your models here.
from django.conf import settings
class Parser(models.Model):
    file = models.FileField(upload_to='CVs_Parser/', default=None)

class UploadPdf(models.Model):
    resumes = models.FileField(upload_to='Resumes/', blank=True, null=True)

class FinalCV(models.Model):
    finalcv = models.FileField(upload_to='Final/', blank=True, null=True)
    resume_email    = models.EmailField(unique=True, max_length=254, default="user@idiada.com")
    resume_phone    = models.CharField(max_length=15, null=True, blank=True)
    resume_name     = models.CharField(max_length=256, null=True, blank=True)
    resume_fname    = models.CharField(max_length=256, null=True, blank=True)
    resume_rank     = models.IntegerField(null=True, blank=True)
    resume_summary    = models.CharField(max_length=5056, null=True, blank=True)

class ParserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parser
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadPdf
        fields = '__all__'

class FinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalCV
        fields = '__all__'

# class List_DatabaseParser(models.Model):
#     modelname = models.CharField(max_length=100)
#     description = models.TextField(max_length=1500, null=True)
#     color = models.CharField(max_length=100, null=True)
#     icon = models.CharField(max_length=150, null=True)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
#     on_delete=models.DO_NOTHING,
#     related_name='createduser'
#     )

# from __future__ import unicode_literals

# class Document(models.Model):
#     description = models.CharField(max_length=255, blank=True)
#     document = models.FileField(upload_to='documents/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)