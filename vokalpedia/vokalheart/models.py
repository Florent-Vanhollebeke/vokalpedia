import django
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from .managers import UserManager

#from datetime import datetime

# Custom user model


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)

    objects = UserManager()

    # Function that provides the ability to delete a user's searches before deleting the user.
    def delete(self, *args, **kwargs):
        user_searches = UserSearch.objects.filter(user=self)

        for user_search in user_searches:
            search = user_search.search
            user_search.delete()
            search.delete()

        super(User, self).delete(*args, **kwargs)

# Search model for storing search queries


class Search(models.Model):
    text = models.CharField(max_length=254)
    type = models.CharField(max_length=254, default="")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

# Many-to-many relationship model between User and Search


class UserSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    search = models.ForeignKey(Search, on_delete=models.CASCADE)

# SpeechResult model with a one-to-one relationship with Search


class SpeechResult(models.Model):
    search = models.OneToOneField(Search, on_delete=models.CASCADE, null=True)
    file_name = models.CharField(max_length=254)
    file_path = models.CharField(max_length=254)

    def __str__(self):
        return self.file_name
