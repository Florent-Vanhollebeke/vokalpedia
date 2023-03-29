import json
import http.client
import urllib.request
import urllib.parse
import urllib.error
import base64
from translate import Translator


def image_captioning_azure(url):
    # Fonction réalisant un appel API au modèle de description d'images de Microsoft Azure

    headers = {'Content-Type': 'application/json',
               'Ocp-Apim-Subscription-Key': 'f5aae19eb1024e39a4ed30ed514779d9'}

    body = json.dumps({"url": url})

    params = urllib.parse.urlencode({
        'maxCandidates': '1',
        'language': 'en',
        'model-version': 'latest',
    })

    params += '&VisualFeatures=description'

    try:
        conn = http.client.HTTPSConnection(
            'francecentral.api.cognitive.microsoft.com')
        conn.request("POST", "/vision/v3.2/analyze?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    data = json.loads(data)

    res = data['description']['captions'][0]['text']

    translator = Translator(to_lang="fr")
    translation = translator.translate(res)

    return translation
