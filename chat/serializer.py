from .models import StoriesModel
from main.models import UserModel
from chat.models import StoriesModel
from rest_framework import serializers


class UsersForStoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username']

    def to_representation(self, instance):
        data = super(UsersForStoriesSerializer, self).to_representation(instance)
        data['storieses'] = StoriesModel.objects.filter(user__username=instance.username).values()
        return data


