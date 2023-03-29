import pytest
from utils.class_wikipedia import Navigation_sommaire_wikipedia
from utils.image_captioning_azure import image_captioning_azure
from utils.text_to_speech_azure import speech_synthesis_with_auto_language_detection_to_speaker
import datetime
import os
from pathlib import Path


class MockSection:
    def __init__(self, title, sections=None):
        self.title = title
        self.sections = sections or []
        print(f"Création de MockSection: {title}, sections={sections}")


exemple_sections = [
    MockSection("Histoire", [
        MockSection("Préhistoire"),
        MockSection("Antiquité")
    ]),
    MockSection("Géographie", [
        MockSection("Localisation"),
        MockSection("Communes limitrophes")
    ])
]


def test_print_sections_h2():
    nav = Navigation_sommaire_wikipedia(exemple_sections, "section")
    result = nav.print_sections_h2(nav.sections)
    assert result == [
        "Histoire", "Géographie"], "Les sections h2 ne sont pas correctement récupérées"


def test_nav_wiki_sommaire():
    nav = Navigation_sommaire_wikipedia(exemple_sections, "sommaire")
    nav.nav_wiki()
    expected_output = "['Histoire', 'Préhistoire', 'Antiquité', 'Géographie', 'Localisation', 'Communes limitrophes']"
    print(nav.sommaire)
    assert nav.sommaire == expected_output, f"La méthode nav_wiki ne retourne pas le sommaire complet correctement. Attendu : {expected_output}, Obtenu : {nav.sommaire}"


def test_nav_wiki_section():
    nav = Navigation_sommaire_wikipedia(exemple_sections, "section")
    nav.nav_wiki()
    assert nav.sommaire == "['Histoire', 'Géographie']", "La méthode nav_wiki ne retourne pas les sections h2 correctement"


def test_nav_wiki_erreur():
    nav = Navigation_sommaire_wikipedia(exemple_sections, "erreur")
    with pytest.raises(ValueError, match="Erreur dans le fonctionnement de la classe Navigation_sommaire_wikipedia."):
        nav.nav_wiki()


def test_image_captioning_azure():
    # Test de la fonction image_captioning_azure avec une URL d'image valide
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Mapadefrancia.svg/langfr-1024px-Mapadefrancia.svg.png"
    result = image_captioning_azure(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Mapadefrancia.svg/langfr-1024px-Mapadefrancia.svg.png")
    assert isinstance(result, str) and len(
        result) > 0, "La fonction ne retourne pas une chaîne de caractères non vide"


def test_speech_synthesis_with_auto_language_detection_to_speaker():
    # Chemin vers le répertoire des médias
    media_dir = "media"

    # Créer le répertoire s'il n'existe pas
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    # Vérifier les autorisations d'écriture
    if not os.access(media_dir, os.W_OK):
        raise ValueError(
            f"Le répertoire {media_dir} n'a pas les autorisations d'écriture nécessaires.")
        # Define test input
    text = "Hello World by Simplon!"
    search = "TestAzureTTS"
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    section_traitee = "testAzure"

    # Call function
    speech_synthesis_with_auto_language_detection_to_speaker(
        text, search, timestamp, section_traitee)

    file_path = Path(
        f"media/{search}_{section_traitee}_{timestamp}.wav")

    # Assert that output file exists
    assert file_path.is_file(), "Output file does not exist"


if __name__ == "__main__":
    pytest.main([__file__])
