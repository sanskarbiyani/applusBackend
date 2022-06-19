from django.contrib import admin
from chat.models import Thread, Messages, UserStatus, UploadedFiles

# Register your models here.
admin.site.register(Thread)
admin.site.register(Messages)
admin.site.register(UserStatus)
admin.site.register(UploadedFiles)