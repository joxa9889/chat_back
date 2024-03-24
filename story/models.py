from django.db import models

# Create your models here.


class Story(models.Model):
    title = models.CharField(max_length=110)
    video = models.FileField(upload_to='stories/', null=True, blank=True)
    img = models.ImageField(upload_to='stories_imgs/', null=True, blank=True)
    is_image = models.BooleanField(default=False)

    def __str__(self):
        return self.title

