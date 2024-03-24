from django.db.models import F
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from chat.models import StoriesModel
from .models import RoomModel, MessageModel, UserModel, AudioModel, ContactModel
from .serializer import MessageModelSerializer, RoomModelSerializer, ProfileModelSerializer, RoomModelCreateSerializer, \
    AudioModelSerializer, ContactModelSerializer
from chat.serializer import UsersForStoriesSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


# from rest_framework.decorators import api_view
# from rest_framework.response import Response


# Create your views here.

class MessageView(ModelViewSet):
    queryset = MessageModel.objects.all()
    serializer_class = MessageModelSerializer
    permission_classes = [IsAuthenticated]


class RoomView(ModelViewSet):
    queryset = RoomModel.objects.filter(users__id=1)
    serializer_class = RoomModelSerializer
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]


class RoomCreateView(CreateAPIView):
    queryset = RoomModel.objects.all()
    serializer_class = RoomModelCreateSerializer
    permission_classes = [IsAuthenticated]


class UserView(ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = ProfileModelSerializer


class ContactView(ModelViewSet):
    queryset = ContactModel.objects.all()
    serializer_class = ContactModelSerializer
    permission_classes = [IsAuthenticated]


class AudioView(ModelViewSet):
    queryset = AudioModel.objects.all()
    serializer_class = AudioModelSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMe(request):
    me = UserModel.objects.get(id=request.user.id)
    serializer = ProfileModelSerializer(me, context={'request': request})
    return Response({
        'me': serializer.data
    })


@api_view(['GET'])
def rooms_messages(request, pk):
    room = RoomModel.objects.get(id=pk)
    messages = MessageModel.objects.filter(room=room)
    serializer = MessageModelSerializer(messages, many=True, context={'request': request})
    return Response({
        'messages': serializer.data
    })


@api_view(['GET'])
def get_user_by_username(request, username):
    try:
        user = UserModel.objects.get(username=username)
        serializer = ProfileModelSerializer(user, context={'request': request})
        return Response(serializer.data)
    except:
        return Response({
            'error_show_him': ['There is no such user']
        })


@api_view(['GET'])
def get_my_rooms(request):
    rooms = RoomModel.objects.filter(users=request.user.id)
    serializer = RoomModelSerializer(rooms, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_room_by_name(request, room_name):
    rooms = RoomModel.objects.get(room_name=room_name)
    serializer = RoomModelSerializer(rooms, context={'request': request})
    return Response(serializer.data)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_my_contacts(request):
    contacts = ContactModel.objects.filter(me=request.user.id)
    serializer = ContactModelSerializer(contacts, many=True, context={'request': request})
    return Response(serializer.data)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def stories(request):
    users = UserModel.objects.filter(id__in=ContactModel.objects.filter(me=request.user.id).values_list('show_him__id', flat=True))
    print(users)
    serializer = UsersForStoriesSerializer(users, many=True, context={'request': request})
    return Response({'stories': serializer.data})
