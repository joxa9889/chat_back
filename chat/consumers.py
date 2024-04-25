import base64
import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import F

from main.models import UserModel, MessageModel, AudioModel, RoomModel, ContactModel
from aiofiles import open as async_open
from datetime import datetime
from rest_framework.authtoken.models import Token


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        room_id = text_data_json["room_id"]
        user_id = text_data_json["user"]
        url = text_data_json["url"]
        reply_to = text_data_json["reply_to"]
        is_image = text_data_json["is_image"]

        if is_image:
            image_data = base64.b64decode(url['url'])

            async with async_open(f'media/messages/{url["name"]}', 'wb') as f:
                await f.write(image_data)

            url_db = f'/messages/{url["name"]}'
            url = f'/media/messages/{url["name"]}'
        else:
            url = is_image
            url_db = is_image

        msg_id = await self.create_message(message, room_id, user_id, url_db, is_image, reply_to)

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message,
                "room_id": room_id,
                "user": user_id,
                "url": url,
                "is_image": is_image,
                "reply_to": reply_to,
                "id": msg_id[0],
                "full_name": msg_id[1]
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "room_id": event["room_id"],
            "user": event["user"],
            "url": event["url"],
            "is_image": event["is_image"],
            "reply_to": event["reply_to"],
            "id": event['id'],
            "full_name": event['full_name']
        }))

    @database_sync_to_async
    def create_message(self, message, room_id, user_id, url, is_image, reply_to):
        user = UserModel.objects.get(id=user_id)
        print(reply_to)
        try:
            reply_msg = MessageModel.objects.get(pk=reply_to)
            var = MessageModel.objects.create(message=message, room_id=room_id, user=user, url=url, is_image=is_image,
                                              reply_to=reply_msg)
        except:
            var = MessageModel.objects.create(message=message, room_id=room_id, user=user, url=url, is_image=is_image)
        print(var)
        print(var.id)

        return [var.id, f'{var.user.first_name} {var.user.last_name}']


class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'status'
        self.group_name = f"status_{self.room_name}"
        self.user = None
        await self.channel_layer.group_add("status", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.set_user_status(date=datetime.now())

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "user.disconnected",
                "username": self.user.username,
                "last_active": self.user.last_active.strftime(
                    "%m/%d/%Y, %H:%M:%S") if self.user.last_active is not None else self.user.username
            }
        )
        print('send processss')
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(self.user)
        if self.user:
            if 'update' in text_data_json.keys():
                await self.update_user(text_data_json['field'], text_data_json['value'])
                print('worked')
            else:
                x = await self.get_my_contacts()
                await self.send(text_data=json.dumps({
                   'contacts': x
                }))
            return

        print('what')
        token = text_data_json["token"]
        await self.set_user_status(token=token)
        faaa = await self.my_contacts()
        await self.send(text_data=json.dumps({"message": faaa}))
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "user.disconnected",
                "username": self.user.username,
                "last_active": self.user.last_active.strftime(
                    "%m/%d/%Y, %H:%M:%S") if self.user.last_active is not None else self.user.last_active
            }
        )

    # Receive message from room group
    async def user_disconnected(self, event):
        print('woooork pleaseeee')
        await self.send(text_data=json.dumps({
            'last_active': event["last_active"],
            'username': event["username"],
            'update': True
        }))

    @database_sync_to_async
    def get_my_contacts(self):
        my_contacts = ContactModel.objects.filter(me=self.user).annotate(
            last_active=F('show_him__last_active'),
            username=F('show_him__username')).values('last_active', 'username')
        return [
            {'last_active': i['last_active'].strftime("%m/%d/%Y, %H:%M:%S") if i['last_active'] is not None else None,
             'username': i['username']} for i in list(my_contacts)]

    @database_sync_to_async
    def my_contacts(self):
        x = RoomModel.objects.filter(users=self.user).values_list('id', flat=True)
        l = list(RoomModel.objects.filter(id__in=x).values_list('users', flat=True))
        v = UserModel.objects.filter(id__in=l).exclude(id=self.user.id).values('username', 'last_active')
        v = [{'last_active': i['last_active'].strftime("%m/%d/%Y, %H:%M:%S") if i['last_active'] is not None else None,
              'username': i['username']} for i in v]
        print(v)
        return list(v)

    @database_sync_to_async
    def set_user_status(self, *, token=None, date: datetime = None):
        if token:
            user = Token.objects.get(key=token).user
            self.user = user

        self.user.last_active = date
        self.user.save()

    @database_sync_to_async
    def update_user(self, field, data_replace):
        print('aaa')
        setattr(self.user, field, data_replace)
        self.user.save()
        print('work')
        print(self.user.first_name)
        return 'successfully updated'
