from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed


from . import forms
from vokalheart.models import *

from vokalheart.utils.class_wikipedia import Navigation_sommaire_wikipedia
from vokalheart.utils.text_to_speech_azure import speech_synthesis_with_auto_language_detection_to_speaker
from vokalheart.utils.image_captioning_azure import image_captioning_azure
from vokalheart.utils.wiki_fonctions_processing import wiki_navigation_processing, wiki_help_processing, wiki_image_processing, wiki_article_processing

import os
import json
import re
import datetime
import time
import wikipediaapi
import wikipedia
from bs4 import BeautifulSoup
from random import *



wiki_wiki = wikipediaapi.Wikipedia('fr')
wikipedia.set_lang("fr")

User = get_user_model()





@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


def signup_page(request):
    # View permettant l'inscription d'un utilisateur
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # auto-login user
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'vokalheart/signup.html', context={'form': form})


def login_page(request):
    # View permettant la connexion de l'utilisateur
    form = forms.LoginForm()
    message = ''
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('home')
        message = 'Identifiants invalides.'
    return render(request, 'vokalheart/login.html', context={'form': form, 'message': message})


def logout_user(request):
    # View permettant la déconnexion de l'utilisateur
    logout(request)
    return redirect('login')


@login_required
def home(request):
    return render(request, 'vokalheart/home.html')



# View récupération demande utilisateur pour prédiction

@login_required
def wikispeech(request):

    if request.method == 'POST':

        user = request.user
        data = json.loads(request.body)
        data_prediction = data['prediction']
        theme = data_prediction.split(" ")[1]
        
        try:
            html_page = wikipedia.page(f'{theme}').html()
            page_py = wiki_wiki.page(f'{theme}')
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")

        # si l'utilisateur demande à obtenir la lecture de la page complète
        if re.search(r"lecture", data_prediction):

            resultat = {"lecture": json.dumps(page_py.text)}

            return JsonResponse(resultat)


        # si l'utilisateur demande à obtenir le sommaire complet, on lui retourne le sommaire complet
        elif re.search(r"sommaire", data_prediction):
            
            section_traitee = "sommaire"
            response = wiki_navigation_processing(user=user,theme=theme,section_traitee=section_traitee,page_py=page_py)

            return JsonResponse(response)


        # si l'utilisateur demande à obtenir seulement les grandes sections, on ne lui retourne que les grandes sections
        elif re.search(r"section", data_prediction):
       
            section_traitee = "section"
            response = wiki_navigation_processing(user=user,theme=theme,section_traitee=section_traitee,page_py=page_py)

            return JsonResponse(response)
        

        # retourne l'aide à l'utilisation de l'application 
        elif re.search(r"aide", data_prediction):
            
            section_traitee = "aide"
            response = wiki_help_processing(user=user,theme=theme, section_traitee=section_traitee)
        
            return JsonResponse(response)
        

        # retourne la description de trois images aléatoires 
        elif re.search(r"image", data_prediction):

            section_traitee = "image"
            response = wiki_image_processing(user=user,theme=theme,section_traitee=section_traitee)
        
            return JsonResponse(response)

        # cela permet de récupérer le souhait de l'utilisateur après avoir entendu le sommaire et ne lui renvoyer que l'article de la page qui l'intéresse.
        else:

            response = wiki_article_processing(user=user,data_prediction=data_prediction,theme=theme,page_py=page_py,html_page=html_page)

            return JsonResponse(response)
        
    else:
        return HttpResponseNotAllowed(['POST'])