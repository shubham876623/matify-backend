from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth import get_user_model
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email




class TrainedModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    training_id = models.CharField(max_length=255, unique=True)
    trigger_word = models.CharField(max_length=100)
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=50, default="starting")
    version_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.trigger_word} ({self.status})"




class Gallery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gallery_images")
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.image_url}"
    




class UserCredits(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_credits")
    credits_remaining = models.IntegerField(default=0)
    credits_used = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - Remaining: {self.credits_remaining}, Used: {self.credits_used}"




class GeneratedImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_genrated_images")
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class ProcessedImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_processed_images")
    image_url = models.URLField()
    source = models.ForeignKey(GeneratedImage, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)