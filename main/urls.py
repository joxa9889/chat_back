from django.urls import path, include, re_path
from .views import MessageView, RoomView, UserView, RoomCreateView, rooms_messages, AudioView, getMe, ContactView, \
    get_user_by_username, get_my_rooms, get_room_by_name, get_my_contacts, stories
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'messages', MessageView)
router.register(r'rooms', RoomView)
router.register(r'users', UserView)
router.register(r'audio', AudioView)
router.register(r'contacts', ContactView)

urlpatterns = [
    path('my_rooms/', get_my_rooms, name='my_rooms'),
    path('rooms/create/', RoomCreateView.as_view(), name='room_create'),
    path('rooms_messages/<int:pk>/', rooms_messages, name='rooms_messages'),
    path('me/', getMe, name='me'),
    path('get_user/<str:username>/', get_user_by_username, name='get_user'),
    path('get_room_by_name/<str:room_name>/', get_room_by_name, name='room_by_name'),
    path('get_my_contacts/', get_my_contacts, name='get_my_contacts'),
    path("stories/", stories, name="stories"),
    path('', include(router.urls)),
]
