# import email
# from turtle import update
# from asgiref.sync import async_to_sync
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from users.models import NewUser as User
from chat.models import Thread, Messages, UserStatus, UploadedFiles
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import datetime
from channels.db import database_sync_to_async
from users.models import NewUser
from asgiref.sync import sync_to_async


@database_sync_to_async
def get_thread(**kwargs):
    curr_user = kwargs['currUser']
    if 'otherUser' in kwargs:
        other_user = kwargs['otherUser']
        if 'update' in kwargs:
            field = kwargs['update']
            value = kwargs['value']
            (threads, created) = Thread.objects.update_or_create(
                user1__in=[curr_user, other_user], user2__in=[
                    curr_user, other_user],
                defaults={
                    field: value,
                    'user1': curr_user,
                    'user2': other_user
                })
            print(f"Thread Created: {created}")
        else:
            threads = Thread.objects.filter(
                user1__in=[curr_user, other_user], user2__in=[
                    curr_user, other_user])
    else:
        threads = Thread.objects.filter(
            Q(user1=curr_user) | Q(user2=curr_user))
        threads = list(threads)
    return threads


@database_sync_to_async
def create_new_message(thread, user, message, file=None):
    if (file):
        message_obj = Messages.objects.create(
            thread=thread, sender=user, message=message, msg_type='2', fileId=file)
        print("Received File.")
    else:
        message_obj = Messages.objects.create(
            thread=thread, sender=user, message=message, msg_type='1')
    message_obj.save()
    return message_obj


@database_sync_to_async
def get_user(**kwargs):
    if "user_name" in kwargs:
        userObj = User.objects.get(user_name=kwargs["user_name"])
    elif "email" in kwargs:
        userObj = User.objects.get(email=kwargs["email"])
    return userObj


@database_sync_to_async
def get_file(file):
    return UploadedFiles.objects.get(id=file)


@database_sync_to_async
def user_status_present(user):
    if hasattr(user, 'userstatus'):
        return True
    else:
        return False


@database_sync_to_async
def update_or_create_status(user, value=False):
    (status, created) = UserStatus.objects.update_or_create(
        user=user, defaults={'is_online': value})
    # if created or not status.is_online:
    #     return False
    # else:
    #     return True
    return status


class NewChatConsumer(AsyncWebsocketConsumer):
    async def compare_and_send(self, threads, msg):
        for thread in threads:
            user1 = await sync_to_async(lambda: thread.user1)()
            user2 = await sync_to_async(lambda: thread.user2)()
            if user1 == self.me:
                room_name = f'personal_chat_room_{user2.user_name}'
                # user_obj = await get_user(user_name=user2)
                self.status = await sync_to_async(lambda: user1.userstatus)()
                status = await sync_to_async(lambda: user2.userstatus)()
                if user_status_present and not status.is_online:
                    continue
            else:
                room_name = f'personal_chat_room_{user1.user_name}'
                # user_obj = await get_user(user_name=user1)
                self.status = await sync_to_async(lambda: user2.userstatus)()
                status = await sync_to_async(lambda: user1.userstatus)()
                if user_status_present and not status.is_online:
                    continue
            # print('Sending status messages.')
            await self.channel_layer.group_send(room_name, {
                'type': 'chat_message',
                'message': msg,
            })

    async def send_status_messages(self, status):
        # print('Sending messages')
        threads = await get_thread(currUser=self.me)
        msg = {
            'type': 'status',
            'status': status,
            'sender': self.scope['user'].email
        }
        await self.compare_and_send(threads, msg)

    async def connect(self):
        self.me = self.scope['user']
        await update_or_create_status(self.me, True)
        self.room_name = f'personal_chat_room_{self.me.user_name}'
        await self.channel_layer.group_add(
            self.room_name, self.channel_name)
        await self.accept()
        # Sending the status messages to all the connected users
        await self.send_status_messages(True)

    async def disconnect(self, code):
        await update_or_create_status(self.me, False)
        await self.send_status_messages(False)
        await self.channel_layer.group_discard(
            self.room_name, self.channel_name)

    async def receive(self, text_data=None):
        response = json.loads(text_data)
        receiver_email = response['receiver']
        try:
            receiver = await get_user(email=receiver_email)
        except ObjectDoesNotExist:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'No such user exists.'
            }))
        else:
            status = await update_or_create_status(user=receiver)
            # Retreiving the thread. If it does not exists then creating a new one
            thread_obj = await get_thread(
                currUser=self.me, otherUser=receiver, update='updated_at', value=datetime.now())
            # Sending responses according to the message type
            if response['type'] == 'message' and response.get('receiver'):
                # Adding the Message to the thread
                message_obj = await create_new_message(
                    thread=thread_obj, user=self.scope['user'], message=response['message'])
                # print(f"Received a Message from {message_obj.sender} at {message_obj.timestamp}")
                msg = {
                    'type': 'message',
                    'message': response['message'],
                    'sender': [self.scope['user'].email, self.scope['user'].user_name, self.status.is_online]
                }
            elif response['type'] == 'file':
                file_obj = await get_file(file=response['fileId'])
                message_obj = await create_new_message(
                    thread=thread_obj, user=self.scope['user'], message=response['fileName'], file=file_obj)
                # print( f"Received File from {message_obj.sender} at {message_obj.timestamp}")
                msg = {
                    'type': 'file',
                    'fileId': response['fileId'],
                    'fileName': response['fileName'],
                    'sender': [self.scope['user'].email, self.scope['user'].user_name, self.status.is_online]
                }

            room_name = f'personal_chat_room_{receiver}'
            # print(f"{receiver.user_name} is {status.is_online}")
            if status.is_online:
                message_obj.is_read = True
                message_obj.save()
                await self.channel_layer.group_send(room_name, {
                    'type': 'chat_message',
                    'message': msg,
                })

    async def chat_message(self, event):
        # print(f"[{self.channel_name}] - Sent Message - {event['message']}")
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
