from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


from datetime import datetime


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)


class PreviousSearch(models.Model):
    # Modèle des recherches déjà effectuées par l'utilisateur
    previous_search_text = models.CharField(max_length=254)
    user_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    previous_id = models.IntegerField()

    def __str__(self):
        return self.previous_search_text


class TextToSpeechPrediction(models.Model):
    # Modèle de la prédiction audio résultant du text to speech
    audio_track_prediction = models.FileField(
        upload_to=f"{settings.MEDIA_ROOT}/{datetime.now()}")
    audio_name = models.CharField(max_length=30)
    user_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    previous_id = models.ForeignKey(PreviousSearch, on_delete=models.CASCADE)

    def __str__(self):
        return self.audio_name


class ImageCaptioningPrediction(models.Model):
    # Modèle de la prédiction écrite résultant de la description d'images
    text_prediction = models.CharField(max_length=254)
    user_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    previous_id = models.ForeignKey(PreviousSearch, on_delete=models.CASCADE)

    def __str__(self):
        return self.text_prediction
