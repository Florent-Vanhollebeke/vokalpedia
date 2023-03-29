from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import widgets


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
    username = forms.CharField(max_length=63, label='Nom d’utilisateur', widget=forms.TextInput(
        attrs={'placeholder': 'Username', 'style': "width: 300px;margin-top:190px;"}))
    password = forms.CharField(max_length=63, label='Mot de passe', widget=forms.PasswordInput(
        attrs={'placeholder': 'Password', 'style': "width: 300px;margin-left: 28px;"}))
