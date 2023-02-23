from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.contrib.auth.models import User

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed


from . import forms
from vokalheart.models import PreviousSearch, TextToSpeechPrediction, ImageCaptioningPrediction

from vokalheart.utils.class_wikipedia import Navigation_sommaire_wikipedia
from vokalheart.utils.text_to_speech_azure import speech_synthesis_with_auto_language_detection_to_speaker

import os
import json
import re
import wikipediaapi
import wikipedia



wiki_wiki = wikipediaapi.Wikipedia('fr')
wikipedia.set_lang("fr")


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

        username = request.POST.get('username')
        data = json.loads(request.body)
        prediction = data['prediction']
        accessoire = data['predAccessoire']

        html_page = wikipedia.page(prediction).html()
        page_py = wiki_wiki.page(prediction)

        # si l'utilisateur demande à obtenir la lecture de la page complète
        if re.search(r"lecture", accessoire):
            resultat = json.dumps(page_py.text)

            #return render(request, 'vokalheart/home.html', context=resultat)
            return JsonResponse(resultat)


        # si l'utilisateur demande à obtenir le sommaire complet, on lui retourne le sommaire complet
        elif re.search(r"sommaire", accessoire):
            section_traitee = "sommaire"
            val_retour = Navigation_sommaire_wikipedia(page_py.sections,section_traitee)
            val_retour.nav_wiki()
            sommaire = val_retour.sommaire
            sommaire = sommaire.replace("""[\'""","""[\"""").replace("""\', \'""","""\", \"""").replace("""\']""","""\"]""").replace("""\', \"""","""\", \"""").replace("""\", \'""","""\", \"""")

            user = User.objects.get(username=username)
            previous_search = PreviousSearch.objects.filter(user_owner=user,previous_search_text__icontains=prediction).values("previous_search_text")

            for i,v in enumerate(previous_search):
                if previous_search[i]['previous_search_text'] == prediction:
                    previous_search_id = previous_search.previous_id
                    print(previous_search_id)
                    pred_to_send = TextToSpeechPrediction.objects.get(previous_id=previous_search_id)
                    print(pred_to_send)
                    # il faut faire le return du fichier dans la BDD 

            try:
                speech_synthesis_with_auto_language_detection_to_speaker(str(sommaire),prediction)
            except Exception as err:
                print(f"Unexpected {err}, {type(err)}")

            chemin_fichier = os.path.join(settings.MEDIA_ROOT, f"{prediction}_{timestamp}.wav")
            # Ouverture du fichier WAV
            with open(chemin_fichier, 'rb') as fichier_wav:
                # Lecture du contenu du fichier WAV
                contenu_wav = fichier_wav.read()

            filename="{prediction}_{timestamp}.wav"
            file = filename.startswith(prediction)

            # Création d'une réponse HTTP contenant le contenu du fichier WAV
            response = HttpResponse(content=contenu_wav, content_type='audio/wav')
            response['Content-Disposition'] = f'attachment; filename="{file}"'

            # Rendre le template HTML en y incluant la réponse HTTP
            context = {'fichier_wav': response}
            return render(request, 'vokalheart/home.html', context)

            # return render(request,'vokalheart/home.html', context=sommaire)

        # si l'utilisateur demande à obtenir seulement les grandes sections, on ne lui retourne que les grandes sections
        elif re.search(r"section", accessoire):
            section_traitee = "section"
            val_retour = Navigation_sommaire_wikipedia(page_py.sections,section_traitee)
            val_retour.nav_wiki()
            sommaire = val_retour.sommaire
            sommaire = sommaire.replace("""[\'""","""[\"""").replace("""\', \'""","""\", \"""").replace("""\']""","""\"]""").replace("""\', \"""","""\", \"""").replace("""\", \'""","""\", \"""")

            try:
                speech_synthesis_with_auto_language_detection_to_speaker(str(sommaire),prediction)
            except Exception as err:
                print(f"Unexpected {err}, {type(err)}")

            return render(request, 'vokalheart/home.html', context=sommaire)
        
        elif re.search(r"aide", prediction):
            help_text = """Voici quelques conseils pour utiliser Vokalpédia. L'application fonctionne sur un enchainement de clics qui se comprenne comme un cycle. 
            D'abord, cliquez une première fois sur le boutton, cela permet de demander le thème recherché. 
            Par exemple, recherche bayonne permettra d'aller sur la page wikipédia de bayonne. 
            Le second clic sur le boutton permet de préciser la demande sur le contenu désiré dans la page avec trois méthodes: lecture, sommaire et section. 
            Si vous dites lecture, cela permet de lire l'intégralité de la page depuis le début.
            Si vous dites sommaire, vous obtiendrez l'intégralité du sommaire avec toutes ses sous-sections incluses. 
            En revanche, si vous dites section, alors vous n'obtiendrez que les grandes sections du sommaire. 
            Enfin, pour lire le contenu d'une section du sommaire, il conviendra de cliquer en demandant le thème suivi du nom de la section."""

            try:
                speech_synthesis_with_auto_language_detection_to_speaker(help_text,prediction)
            except Exception as err:
                print(f"Unexpected {err}, {type(err)}")

            return render(request, 'vokalheart/home.html', context=help_text)

        # cela permet de récupérer le souhait de l'utilisateur après avoir entendu le sommaire et ne lui renvoyer que l'article de la page qui l'intéresse.
        else:
            val_retour = json.dumps("coucou test")

            return render(request,'vokalheart/home.html', context=val_retour)
        
    else:
        return HttpResponseNotAllowed(['POST'])

    






