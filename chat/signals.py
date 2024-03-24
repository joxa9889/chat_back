from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import ContactModel, RoomModel


# @receiver(post_save, sender=ContactModel)
# def user_post_save(sender, instance, created, **kwargs):
#     if created:
#         l = [instance.me, instance.show_him]
#         room = RoomModel.objects.create(room_name=f'{instance.me.username}_{instance.show_him.username}')
#         room.users.add(*l)
