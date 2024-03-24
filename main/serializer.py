from django.core.exceptions import ValidationError
from django.db.models import Value, F
from django.db.models.functions import Concat
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserModel, ContactModel
from rest_framework import serializers
from .models import MessageModel, RoomModel, AudioModel, ContactModel
from django.templatetags.static import static
from django.db.models import Q


class ProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'first_name', 'last_name', 'username', 'profile_img', 'last_active', 'password']

    def create(self, validated_data):
        print(validated_data)
        user = UserModel(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            profile_img=validated_data['profile_img'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RoomModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomModel
        fields = '__all__'

    def validate(self, data):
        room_name = data.get('room_name')
        if room_name:
            l = room_name.split('_')
            x = list(reversed(l))
            z = '_'.join(x)
            print(z)
            a = RoomModel.objects.filter(Q(room_name=z) | Q(room_name=room_name))
            if len(a) > 0:
                raise ValidationError({
                    'room_exist': ['Room already exists!', f'{a.first().room_name}']
                })

        return data


class RoomModelSerializer(serializers.ModelSerializer):
    users = ProfileModelSerializer(many=True, read_only=True)

    class Meta:
        model = RoomModel
        fields = ['id', 'room_name', 'users']

    def to_representation(self, instance):
        data = super(RoomModelSerializer, self).to_representation(instance)
        try:
            data['last_message'] = MessageModel.objects.filter(room__id=instance.id).last().message
            if data['last_message'] == '':
                data['last_message'] = 'Photo'
        except:
            data['last_message'] = ''

        data['users'] = ContactModel.objects.filter(
            show_him_id__in=instance.users.exclude(id=self.context['request'].user.id).values_list('id', flat=True),
            me_id=self.context['request'].user.id).annotate(
            id_s=F('show_him_id'),
            username=F('show_him__username'),
            profile_img=F('show_him__profile_img')
        ).values('id_s', 'first_name', 'last_name', 'username', 'profile_img')

        if not data['users']:
            data['users'] = instance.users.exclude(id=self.context['request'].user.id).values('id', 'username',
                                                                                              'profile_img',
                                                                                              'first_name', 'last_name')

        return data


class MessageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = ['id', 'message', 'user', 'room', 'url', 'is_image', 'created_at', 'reply_to']

    def to_representation(self, instance):
        data = super(MessageModelSerializer, self).to_representation(instance)
        data.pop('room')
        try:
            contact = ContactModel.objects.get(me_id=self.context['request'].user.id, show_him_id=instance.user.id)
            data['full_name'] = contact.first_name + ' ' + contact.last_name
        except:
            data['full_name'] = instance.user.first_name + ' ' + instance.user.last_name
        return data


class AudioModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioModel
        fields = '__all__'


class ContactModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactModel
        fields = '__all__'

    def to_representation(self, instance):
        data = super(ContactModelSerializer, self).to_representation(instance)
        print(instance.show_him.id)
        print(instance.show_him.profile_img)
        try:
            data['profile_img'] = instance.show_him.profile_img.url
        except:
            data['profile_img'] = None
        return data

    def validate(self, data):
        instance = ContactModel(**data)
        instance.clean()
        return data




