from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms


class SignupForm(UserCreationForm):
    # Classe pour l'inscription d'un utilisateur
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date')
        labels = {
            'birth_date': 'Date de naissance',
        }

class LoginForm(forms.Form):
    # Classe pour le formulaire de connexion pour l'utilisateur
    username = forms.CharField(max_length=63, label='Nom d’utilisateur')
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label='Mot de passe')


