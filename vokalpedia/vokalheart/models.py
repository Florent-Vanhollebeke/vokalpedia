import django
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from .managers import UserManager

from datetime import datetime

class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    
    objects = UserManager()

# liaison 1 à 1 avec SpeechResult
class Search(models.Model):
    text = models.CharField(max_length=254)
    type = models.CharField(max_length=254,default="")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

# liaison n à n avec User et avec Search
class UserSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    search = models.ForeignKey(Search, on_delete=models.CASCADE)

# liaison 1 à 1 avec Search
class SpeechResult(models.Model):
    search = models.OneToOneField(Search,on_delete=models.CASCADE, null=True)
    file_name = models.CharField(max_length=254)
    file_path = models.CharField(max_length=254)

    def __str__(self):
        return self.file_name