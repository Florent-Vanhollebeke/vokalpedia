import nltk
import urllib
import bs4 as bs
import pandas as pd
import re
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')

def scapping_wikipedia(url):

    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source,'lxml')

    text = ""
    for paragraph in soup.find_all('p'):
        text += paragraph.text

    text = re.sub(r'\[[0-9]*\]',' ',text)
    text = re.sub(r'\s+',' ',text)
    text = text.lower()
    #text = re.sub(r'\d',' ',text)

    sentences = nltk.sent_tokenize(text)
    # le type de sentences: une liste

    str_a_retirer = " pages pour les contributeurs déconnectés en savoir plus contents move to side bar hide"
    str_a_retirer2 = "pour les articles homonymes,"
    str_a_retirer3 = "taxons concernésmodifier "
    str_a_retirer4 = "pour les articles homophones,"
    str_a_retirer5 = " redirige ici. Pour les articles homophones,"

    for i,v in enumerate(sentences):
        if (str_a_retirer in v) or (str_a_retirer2 in v) or (str_a_retirer4 in v) or (str_a_retirer5 in v):
            # sentences.pop(i)
            sentences[i] = sentences[i].replace(str_a_retirer,"")
            sentences[i] = sentences[i].replace(str_a_retirer2,"")
            sentences[i] = sentences[i].replace(str_a_retirer4,"")
            sentences[i] = sentences[i].replace(str_a_retirer5,"")

    for i,v in enumerate(sentences):
        if str_a_retirer3 in v:
            sentences[i] = sentences[i].replace(str_a_retirer3,"")
            
    return sentences
