import wikipedia
import re

wikipedia.set_lang("fr")


def wikipedia_search(search):

    ask = wikipedia.search(search)
    first_resultat = ask[0]
    page = wikipedia.page(first_resultat)
    text = page.content

    text = text.replace("...", ".")
    text = re.sub(r'\[[0-9]*\]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower()
    text = text.split(".")

    return text


'''
from bs4 import BeautifulSoup
html_page = wikipedia.page("San Antonio Spurs").html()
soup = BeautifulSoup(html_page,"lxml")
content_table = soup.findAll("span", {"class": "toctext"})
content_table_clean = []
for x in content_table:
    content_table_clean.append(x.text)
menu_nav = content_table_clean[0]
menu_nav = re.sub(r'\s+',' ',menu_nav)



import bs4 as bs
import urllib
source = urllib.request.urlopen(url).read()
soup = bs.BeautifulSoup(source,'lxml')
content_table = soup.findAll("ul", {"class": "sidebar-toc-contents"})
content_table_clean = []
for x in content_table:
    content_table_clean.append(x.text)
menu_nav = content_table_clean[0]
menu_nav = re.sub(r'\s+',' ',menu_nav)

ou 

content_h2 = soup.findAll("span", {"class": "mw-headline"})
'''


'''
import requests
req = requests.get('https://fr.wikipedia.org/wiki/Avion')
soup = BeautifulSoup(req.text, "lxml")
soup.title.string
for sub_heading in soup.find_all('h2'):
    print(sub_heading.text)
for sub_heading in soup.find_all('h3'):
    print(sub_heading.text)
for sub_heading in soup.find_all('h4'):
    print(sub_heading.text)
for sub_heading in soup.find_all('h5'):
    print(sub_heading.text)  
'''


'''
import requests
from bs4 import BeautifulSoup, SoupStrainer
 
req = requests.get('https://en.wikipedia.org/wiki/United_States')
 
thumb_images = SoupStrainer(class_="thumbimage")
 
soup = BeautifulSoup(req.text, "lxml", parse_only=thumb_images)
 
for image in soup.find_all("img"):
    print(image['src'])
'''


'''
import wikipedia
import requests
from bs4 import BeautifulSoup

wikipedia.set_lang("fr")

covid = wikipedia.page("Coronavirus")
print(covid.content)
print(covid.images)

url = ""
req = requests.get(url)
soup = BeautifulSoup(req.text, "lxml")
soup.title.string
for sub_heading in soup.find_all('h4'):
    print(sub_heading.text)

'''


'''
import requests
import pandas as pd
from bs4 import BeautifulSoup
from itertools import accumulate, groupby


urls = [
    "https://en.wikipedia.org/wiki/England",
    "https://en.wikipedia.org/wiki/Portugal",
]

out = []
for url in urls:
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    tags = soup.select_one(".mw-parser-output").find_all(recursive=False)
    a = accumulate(t.name == "h2" for t in tags)

    d = {"Theme": url.split("/")[-1]}
    for _, g in groupby(zip(a, tags), lambda k: k[0]):
        g = list(t for _, t in g if t.name in {"h2", "p"})
        if g[0].name != "h2" or len(g) == 1:
            continue

        title = g[0].get_text(strip=True).replace("[edit]", "")
        text = "\n".join(
            [t.get_text(strip=True, separator=" ") for t in g[1:]]
        ).strip()

        if not text:
            continue

        d[title] = text

    out.append(d)
'''
