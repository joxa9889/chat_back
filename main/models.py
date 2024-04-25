from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, UserManager, Group, Permission
from django.utils.translation import gettext_lazy as _


class UserModel(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_img = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.CharField(max_length=70, null=True, blank=True)
    last_active = models.DateTimeField(null=True, blank=True, default=datetime.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    groups = models.ManyToManyField(
        Group,
        related_name='user_groups',  # Use a unique related_name
        blank=True,
        verbose_name=_('groups'),
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='user_permissions',  # Use a unique related_name
        blank=True,
        verbose_name=_('user permissions'),
        help_text=_('Specific permissions for this user.'),
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class RoomModel(models.Model):
    room_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(UserModel, related_name='rooms')

    def __str__(self):
        return f'{self.id}. {self.room_name}'

    def clean(self):
        l = self.room_name.split('_')
        print(l)
        if list(reversed(l)) == l:
            raise ValidationError({'room_name': ['This room is already exist']})


class MessageModel(models.Model):
    message = models.TextField()
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE)
    url = models.FileField(upload_to='messages/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    is_image = models.BooleanField()

    def __str__(self):
        return f'{self.message} {self.url}'


class AudioModel(models.Model):
    audio = models.FileField(upload_to='audio/')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class ContactModel(models.Model):
    me = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='men')
    show_him = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='korinedigon_odam')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def clean(self):
        if self.me == self.show_him:
            raise ValidationError({
                'error_show_him': 'You cannot add yourself to contacts',
            })
        try:
            ContactModel.objects.get(me=self.me, show_him=self.show_him)
            exists = True
        except:
            exists = False

        if exists:
            raise ValidationError({
                'error_show_him': 'Contact already exists',
            })

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
