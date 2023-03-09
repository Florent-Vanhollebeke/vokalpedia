from django.http import JsonResponse

from vokalheart.utils.class_wikipedia import Navigation_sommaire_wikipedia
from vokalheart.utils.text_to_speech_azure import speech_synthesis_with_auto_language_detection_to_speaker
from vokalheart.utils.image_captioning_azure import image_captioning_azure
from vokalheart.models import *

import os
import wikipediaapi
import wikipedia
import re
import datetime
import time
from random import *
from bs4 import BeautifulSoup
import inflect





# Fonction servant à récupérer le contenu d'uns section particulière
def wiki_article_processing(user="",data_prediction="",theme="",page_py="",html_page=""):
    
    filename = ""
    chemin_fichier = ""
    solution = ""
    solution2 = ""

    try:
        p = inflect.engine()
        # Trouver l'indice du début de la liste de mots après `theme`
        start_index = data_prediction.index(theme) + len(theme) + 1

        # Convertir la liste de mots suivant `theme` en une liste de mots
        words = data_prediction[start_index:].split()

        # Mettre tous les mots au pluriel
        plural_words = [p.plural(word) for word in words]

        data_pred_plural = f"Recherche {theme} {' '.join(plural_words)}"
    
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    try:
        #regexTheme = fr'{theme}\s(.*)(?:s)?'
        regexTheme = fr'{theme}\s(.*)' 
      
        data_prediction_singular = re.search(regexTheme, data_prediction)
        print('au singulier ici', data_prediction_singular)

        if data_prediction_singular:
            section_traitee_singular = data_prediction_singular.group(1)
        section_traitee_singular = f'{section_traitee_singular}'
        section_traitee_singular = section_traitee_singular.capitalize()
        print("section_traitee_singular",section_traitee_singular.capitalize())
 
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
    
    try:
        regexTheme = fr'{theme}\s(.*)' 
        data_prediction_plural = re.search(regexTheme, data_pred_plural)
        print('au plural ici', data_prediction_plural)

        if data_prediction_plural:
            section_traitee_plural = data_prediction_plural.group(1)
        section_traitee_plural = f'{section_traitee_plural}'
        section_traitee_plural = section_traitee_plural.capitalize()
        print("section_traitee_plural",section_traitee_plural.capitalize())
        # côté wikipediapai
        #section_plural_asked = page_py.section_by_title(section_traitee_plural)
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    if page_py.exists():

        soup = BeautifulSoup(html_page,"lxml")
        content_table = soup.findAll("span", {"class": "toctext"})
        content_table_clean = []
        
        for x in content_table:
            content_table_clean.append(x.text)
            
        menu_nav = content_table_clean[1]
        menu_nav = re.sub(r'\s+',' ',menu_nav)

    else:
        print("La page demandée n'existe pas.")


    try:
        section_asked_singular = page_py.section_by_title(section_traitee_singular)

        if (section_asked_singular != False) and (section_asked_singular != None):
            print("la section demandée au singulier.....", section_asked_singular)
            print(type(section_asked_singular))
            text_to_transform = str(section_asked_singular)
            match = re.search(r"^(.*)(?=\(\d+\))", text_to_transform)
            result_text_transform = match.group(1)
            regexEssai = r"(?<=Section:\s).*"
            result_text_transform2 = re.findall(regexEssai, result_text_transform)
            solution = result_text_transform2[0]
            print("LE RESUTLAT , " ,result_text_transform)
            print(type(result_text_transform))
            print(f"LE RESUTLAT 22 , ", {result_text_transform},type(result_text_transform), "  FIN  ")
            print(f"LE RESUTLAT 23 , ", {solution}, "  FIN  ")
            print(type(result_text_transform2))
            print(type(solution), solution)
            search_element = f'{theme}_{solution}'
            print(search_element)
            search = Search(text=search_element)
            print("ici la search", search)
            search.save()
            user_search = UserSearch(search=search, user=user)
            user_search.save()
            print("user_search ici" , user_search)
        else: 
            section_asked_plural = page_py.section_by_title(section_traitee_plural)
            print("la section demandée au plural.....", section_asked_plural)
            text_to_transform_plural = str(section_asked_plural)
            print("le text to transform", text_to_transform_plural)
            match_plural = re.search(r"^(.*)(?=\(\d+\))", text_to_transform_plural)
            result_text_transform_plural = match_plural.group(1)
            regexEssai = r"(?<=Section:\s).*"
            result_text_transform3 = re.findall(regexEssai, result_text_transform_plural)
            solution2 = result_text_transform3[0]
            print("LE RESUTLAT AU PLURIEL , " ,result_text_transform3)
            print(f"LE RESUTLAT 23 AU PLURIEL, ", {solution2}, "  FIN  ")
            print(type(result_text_transform3))
            print(type(solution2),solution2)
            search_element = f'{theme}_{solution2}'
            print(search_element)
            search = Search(text=search_element)
            print("ici la search", search)
            search.save()
            user_search = UserSearch(search=search, user=user)
            user_search.save()
            print("user_search ici" , user_search)
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")


    try:
        search_request = Search.objects.filter(text__icontains=search_element)
        search_request_element = search_request[0]
        print("search_request_element ici" , search_request_element)
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    try:
        result_request = SpeechResult.objects.filter(file_name__icontains=search_request_element)
        print("ici result_request", result_request)
        chemin_fichier = result_request[0].file_path
        print("chemin_fichier ici" , chemin_fichier)   
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
        print(f"Le fichier demandé n'existait pas.")
        try:
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            if solution:
                speech_synthesis_with_auto_language_detection_to_speaker(text_to_transform,theme, timestamp,solution)
                filename = f"{theme}_{solution}_{timestamp}.wav"
                chemin_fichier = os.path.join(settings.MEDIA_ROOT, filename)
            elif solution2 :
                speech_synthesis_with_auto_language_detection_to_speaker(text_to_transform_plural,theme, timestamp,solution2)
                filename = f"{theme}_{solution2}_{timestamp}.wav"
                chemin_fichier = os.path.join(settings.MEDIA_ROOT, filename)
            else:
                print("Il y a une erreur ICI")
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}") 

        try: 
            result = SpeechResult(file_name=filename, file_path=chemin_fichier)
            result.save()
            print("result ici", result)
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")


    response = {"fichier_son" : f"/{chemin_fichier}"}
    return response







# Fonction servant à récupérer trois images aléatoires illustrant la page demandée
def wiki_image_processing(user="",theme="",section_traitee=""):
        
    search_request_element = ""
    search_element = f'{theme}_{section_traitee}'
    print(search_element)
    search = Search(text=search_element)
    print("ici la search", search)
    search.save()
    user_search = UserSearch(search=search, user=user)
    user_search.save()
    print("user_search ici" , user_search)


    try:
        search_request = Search.objects.filter(text__icontains=search_element)
        search_request_element = search_request[0]
        print("search_request_element ici" , search_request_element)
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    try:
        result_request = SpeechResult.objects.filter(file_name__icontains=search_request_element)
        print("ici result_request", result_request)
        chemin_fichier = result_request[0].file_path
        print("chemin_fichier ici" , chemin_fichier)
        
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
        print(f"Le fichier demandé n'existait pas.")
    
        wikipage = wikipedia.page(theme)
        liste_images = []

        for i in wikipage.images:
            liste_images.append(i)
        image_random_1 = choice(liste_images)
        image_random_2 = choice(liste_images)
        image_random_3 = choice(liste_images)
        resultat_images = [image_random_1,image_random_2,image_random_3]
        print(resultat_images)
        liste_captioning = []

        try:
            for i in resultat_images:
                liste_captioning.append(image_captioning_azure(i))
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
        
        try:
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            speech_synthesis_with_auto_language_detection_to_speaker(str(liste_captioning),theme,timestamp,section_traitee)
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")

        filename = f"{theme}_{section_traitee}_{timestamp}.wav"
        chemin_fichier = os.path.join(settings.MEDIA_ROOT, filename)

        try: 
            result = SpeechResult(file_name=filename, file_path=chemin_fichier)
            result.save()
            print("result ici", result)
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")

    response = {"fichier_son" : f"/{chemin_fichier}"}
    return response





# Fonction servant à fournir le contenu de la demande d'aide dans l'application
def wiki_help_processing(user="",theme="",section_traitee=""):
        
    text = """Voici quelques conseils pour utiliser votre application Vokalpédia. 
    Il existe quatre principales méthodes à connaitre: lecture, sommaire, section et enfin image. 
    Toutes commandes s'articulent de la même façon. Il convient de dire: recherche, suivi de l'objet de la demande.
    Par exemple, pour consulter la page wikipédia de Bayonne:
    Si vous dites recherche bayonne lecture, cela permet de lire l'intégralité de la page depuis le début.
    Si vous dites recherche bayonne sommaire, vous obtiendrez l'intégralité du sommaire avec toutes ses sous-sections incluses. 
    En revanche, si vous dites recherche bayonne section, alors vous n'obtiendrez que les grandes sections dudit sommaire. 
    Une fois votre choix fait quant au contenu désiré, dites: recherche bayonne suivi de l'article voulu.
    Par exemple, recherche bayonne hydrographie, vous permettra de consulter la section hydrographie de la page.
    Enfin, recherche bayonne image vous retournera la description auditive de trois images prises aléatoirement sur la page.
    Pour terminer, taper deux fois sur la barre d'espace met en pause la lecture qui se lance de manière automatique. Taper une seule fois relancera ou arrêtera à nouveau la lecture. 
    Bonne utilisation de Vokalpédia."""


    search_request_element = ""
    search_element = f'{theme}_{section_traitee}'
    print(search_element)
    search = Search(text=search_element)
    print("ici la search", search)
    search.save()
    user_search = UserSearch(search=search, user=user)
    user_search.save()
    print("user_search ici" , user_search)

    try:
        search_request = Search.objects.filter(text__icontains=search_element)
        search_request_element = search_request[0]
        print("search_request_element ici" , search_request_element)
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    try:
        result_request = SpeechResult.objects.filter(file_name__icontains=search_request_element)
        print("ici result_request", result_request)
        chemin_fichier = result_request[0].file_path
        print("chemin_fichier ici" , chemin_fichier)
        
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
        print(f"Le fichier demandé n'existait pas.")

        try:
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            speech_synthesis_with_auto_language_detection_to_speaker(str(text),theme,timestamp,section_traitee)
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")

        filename = f"{theme}_{section_traitee}_{timestamp}.wav"
        print("filename ici", filename)
        chemin_fichier = os.path.join(settings.MEDIA_ROOT, filename)
        print("chemin_fichier là bas" , chemin_fichier)

        try: 
            result = SpeechResult(file_name=filename, file_path=chemin_fichier)
            result.save()
            print("result ici", result)
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")

    response = {"fichier_son" : f"/{chemin_fichier}"}
    return response




# Fonction servant à la récupération du menu de navigation: soit le sommaire complet, soit les grandes sections seulement
def wiki_navigation_processing(user="",theme="",section_traitee="",page_py=""):

 
    search_request_element = ""
    search_element = f'{theme}_{section_traitee}'
    print(search_element)
    search = Search(text=search_element)
    print("ici la search", search)
    search.save()
    user_search = UserSearch(search=search, user=user)
    user_search.save()
    print("user_search ici" , user_search)

    try:
        search_request = Search.objects.filter(text__icontains=search_element)
        search_request_element = search_request[0]
        print("search_request_element ici" , search_request_element)
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")

    try:
        result_request = SpeechResult.objects.filter(file_name__icontains=search_request_element)
        print("ici result_request", result_request)
        chemin_fichier = result_request[0].file_path
        print("chemin_fichier ici" , chemin_fichier)
        
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
        print(f"Le fichier demandé n'existait pas.")

        try:
            val_retour = Navigation_sommaire_wikipedia(page_py.sections,section_traitee)
            val_retour.nav_wiki()
            sommaire = val_retour.sommaire
            sommaire = sommaire.replace("""[\'""","""[\"""").replace("""\', \'""","""\", \"""").replace("""\']""","""\"]""").replace("""\', \"""","""\", \"""").replace("""\", \'""","""\", \"""")

            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            speech_synthesis_with_auto_language_detection_to_speaker(str(sommaire),theme,timestamp,section_traitee)
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")

        filename = f"{theme}_{section_traitee}_{timestamp}.wav"
        print("filename ici", filename)
        chemin_fichier = os.path.join(settings.MEDIA_ROOT, filename)
        print("chemin_fichier là bas" , chemin_fichier)

        try: 
            result = SpeechResult(file_name=filename, file_path=chemin_fichier)
            result.save()
            print("result ici", result)
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")

    response = {"fichier_son" : f"/{chemin_fichier}"}
    return response
