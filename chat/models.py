from django.db import models
from users.models import NewUser

# Create your models here.


class UserStatus(models.Model):
    user = models.OneToOneField(NewUser, on_delete=models.CASCADE, primary_key=True)
    is_online = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f'{self.user.user_name} -- {self.is_online}'


class TrackingModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Thread(models.Model):
    user1 = models.ForeignKey('users.NewUser', on_delete=models.CASCADE, related_name='user1', null=True)
    user2 = models.ForeignKey('users.NewUser', on_delete=models.CASCADE, related_name='user2', null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    # unread_count = models.IntegerField(default=0, null=False)

    def __str__(self) -> str:
            return f'Thread Between Users {self.user1} and {self.user2}'
    
    class Meta:
        ordering = ['-updated_at']


class Messages(models.Model):
    MESSAGE_TYPES = (
        ('1', 'message'),
        ('2', 'file'),
    )
    MESSAGE_STATUS = (
        ('1', 'unread'),
        ('2', 'read'),
    )
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(
        NewUser, on_delete=models.CASCADE, related_name='sender')
    msg_type = models.CharField(max_length=2, choices = MESSAGE_TYPES, default='1')
    message = models.CharField(max_length=1200)
    fileId = models.ForeignKey('chat.UploadedFiles', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    is_read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.message} -- {self.is_read}"

class UploadedFiles(models.Model):
    file = models.FileField(upload_to='chat/', blank=True, default='')
    thread = models.ForeignKey('chat.thread', on_delete=models.CASCADE)
    sender = models.ForeignKey('users.NewUser', on_delete=models.CASCADE, default='')
    received = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self) -> str:
        return f'{self.file} -- {self.received}'