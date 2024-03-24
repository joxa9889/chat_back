from django.db import models
from main.models import UserModel
# Create your models here.


class StoriesModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    video = models.FileField(upload_to='stories/')

