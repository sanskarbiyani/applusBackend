from django.contrib import admin
from .models import FinalCV, Parser, UploadPdf
# Register your models here.

admin.site.register(Parser)
admin.site.register(UploadPdf)
admin.site.register(FinalCV)