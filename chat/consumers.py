from concurrent.futures import thread
from email import message
from asgiref.sync import async_to_sync
import json
from channels.generic.websocket import WebsocketConsumer
from urllib.parse import parse_qs
from users.models import NewUser as User
from chat.models import Thread, Messages, UserStatus, UploadedFiles
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import datetime


class NewChatConsumer(WebsocketConsumer):
    def send_status_messages(self, status):
        print('Sending messages')
        threads = Thread.objects.filter(
            Q(user1=self.me) | Q(user2=self.me))
        msg = {
            'type': 'status',
            'status': status,
            'sender': self.scope['user'].email
        }
        for thread in threads:
            if thread.user1 == self.me:
                room_name = f'personal_chat_room_{thread.user2.user_name}'
                user_obj = User.objects.get(user_name=thread.user2)
                if hasattr(user_obj, 'userstatus') and not user_obj.userstatus.is_online:
                    continue
            else:
                room_name = f'personal_chat_room_{thread.user1.user_name}'
                user_obj = User.objects.get(user_name=thread.user1)
                if hasattr(user_obj, 'userstatus') and not user_obj.userstatus.is_online:
                    continue
            print('Sending status messages.');
            async_to_sync(self.channel_layer.group_send)(room_name, {
                'type': 'chat_message',
                'message': msg,
            })
        
    def connect(self):
        self.me = self.scope['user']
        if hasattr(self.me, 'userstatus'):
            print('Already Exists.')
            print(self.me.userstatus.is_online)
        else:
            statusObj = UserStatus(user=self.me)
            statusObj.save()
        
        self.me.userstatus.is_online = True
        self.me.userstatus.save()
        self.room_name = f'personal_chat_room_{self.me.user_name}'
        async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
        self.accept()
        # Sending the status messages to all the connected users
        self.send_status_messages(True)

    def disconnect(self, code):
        self.me.userstatus.is_online = False
        self.me.userstatus.save()
        self.send_status_messages(False)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name, self.channel_name)

    def receive(self, text_data=None):
        response = json.loads(text_data)
        receiver_email = response['receiver']
        try:
            receiver = User.objects.get(email=receiver_email)
        except ObjectDoesNotExist:
            self.send(json.dumps({
                'type': 'error',
                'message': 'No such user exists.'
            }))
        else:
            # Retreiving the thread. If it does not exists then creating a new one
            thread_obj = Thread.objects.filter(user1__in=[self.me, receiver], user2__in=[self.me, receiver])
            if not thread_obj:
                thread_obj = Thread.objects.create(user1=self.me, user2=receiver)
                thread_obj.save()
            else:
                thread_obj = thread_obj[0]
                thread_obj.updated_at = datetime.now()
                thread_obj.save()
                
            # Sending responses according to the message type
            if response['type'] == 'message' and response.get('receiver'):
                    # Adding the Message to the thread
                message_obj = Messages.objects.create(thread=thread_obj, sender=self.scope['user'], message=response['message'], msg_type='1')
                message_obj.save()
                print(f"Received a Messag from {message_obj.sender} at {message_obj.timestamp}")
                msg = {
                    'type': 'message',
                    'message': response['message'],
                    'sender': [self.scope['user'].email, self.scope['user'].user_name, self.scope['user'].userstatus.is_online]
                }
            elif response['type'] == 'file':
                file_obj = UploadedFiles.objects.get(id=response['fileId'])
                message_obj = Messages.objects.create(thread=thread_obj, sender=self.scope['user'], message=response['fileName'], msg_type='2', fileId=file_obj)
                message_obj.save()
                print(f"Received File from {message_obj.sender} at {message_obj.timestamp}")
                msg = {
                    'type': 'file',
                    'fileId': response['fileId'],
                    'fileName': response['fileName'],
                    'sender': [self.scope['user'].email, self.scope['user'].user_name]
                }
            
            room_name = f'personal_chat_room_{receiver}'
            print(f"{receiver.user_name} is {receiver.userstatus.is_online}")
            if receiver.userstatus.is_online:
                message_obj.is_read = True
                message_obj.save()
                async_to_sync(self.channel_layer.group_send)(room_name, {
                    'type': 'chat_message',
                    'message': msg,
                })
                

    def chat_message(self, event):
        print(f"[{self.channel_name}] - Sent Message - {event['message']}")
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = "broadcast"
#         # me = self.scope['user']
#         # print(f"Me: {me}")
#         # print(f"[{self.channel_name}] - You are connected")
#         # async_to_sync(self.channel_layer.group_add)(
#         #     self.room_name, self.channel_name)
#         # self.accept()
#         me = self.scope['user']
#         other = self.scope['url_route']['kwargs']['username']
#         other_user = User.objects.get(email=other)
#         if(me.id == other_user.id):
#             self.send(json.dumps({
#                 type: 'error',
#                 message: 'Cannot create a thread with oneself.'
#             }))
#         thread_obj = Thread.objects.filter(user1__in=[me, other_user], user2__in=[me, other_user])
#         if not thread_obj:
#             thread_obj = Thread.objects.create(user1=me, user2=other_user)
#             thread_obj.save()
#         else:
#             thread_obj = thread_obj[0]
        
#         self.room_name = f'personal_thread__{thread_obj.id}'
#         print(f'{me}  ->   {self.room_name}')
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_name, self.channel_name)
#         self.accept()

#     def disconnect(self, code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_name, self.channel_name)

#     def receive(self, text_data=None):
#         # message = json.loads(text_data)
#         # print(message)
#         # self.accept()
#         # if message['type'] == 'other_user':
#         #     try:
#         #         other_user = User.objects.get(message['email'])
#         #     except User.DoesNotExists:
#         #         self.send(json.dumps({
#         #             type: 'error',
#         #             message: 'Requested User Does Not Exists'
#         #         }))
#         #     else:
#         #         try:
#         #             thread_obj = Thread.objects.get(user1=self.scope['user'], user2=other_user);
#         #         except ObjectDoesNotExist:
#         #             try:
#         #                 thread_obj = Thread.objects.get(user2=self.scope['user'], user1=other_user);
#         #             except:
#         #                 thread_obj = Thread(user1=self.scope['user'], user2=other_user)
#         #                 thread_obj.save()
#         #                 self.send(json.dumps({
#         #                     type: 'success',
#         #                     message: 'Thread Created.'
#         #                 }))
#         #         else:
#         #             self.send(json.dumps({
#         #                 type: 'success',
#         #                 message: 'Thread Already Exists.'
#         #             }))
#         # elif message['type'] == 'chat_message':
#         #     pass
            
#         print(f"[{self.channel_name}] - Received Message - {text_data}")

#         new_message = json.dumps({
#             'message': text_data,
#             'username': self.scope['user'].email
#         })
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_name,
#             {
#                 'type': 'chat_message',
#                 'message': text_data
#             }
#         )

#     def chat_message(self, event):
#         print(f"[{self.channel_name}] - Sent Message - {event['message']}")
#         message = event['message']
#         self.send(text_data=json.dumps({
#             'message': message
#         }))


# class EchoConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = 'broadcast'
#         # print("Request for connection accepted.")
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_name, self.channel_name)
#         print(f"[{self.channel_name}] - You are connected")
#         self.accept()

#     def disconnect(self, code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_name, self.channel_name)
#         print(f"[{self.channel_name}] - You are disconnected")

#     def receive(self, text_data=None):
#         print("Data Received.")
#         print(f"[{self.channel_name}] - Received Message - {text_data}")
#         return_msg = f'[{self.scope["user"]}] :- From Django.'
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_name,
#             {
#                 'type': 'chat_message',
#                 'message': return_msg
#             }
#         )

#     def chat_message(self, event):
#         print(f"[{self.channel_name}] - Sending Message - {event['message']}")
#         message = event['message']
#         self.send(text_data=message)