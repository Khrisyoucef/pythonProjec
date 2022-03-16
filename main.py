import xml.etree.cElementTree as ET
import re
import utils
import nltk
from nltk.corpus import stopwords
import heapq
from operator import itemgetter
import unicodedata, string
from collections import OrderedDict
from sklearn.feature_extraction.text import TfidfVectorizer
import math


class ToolsText:

# Exercice 1, TP1
    def htmlspecialchars(self, text):
        return (
            text.replace("&", "&amp;").
                replace('"', "&quot;").
                replace("<", "&lt;").
                replace(">", "&gt;")
        )

    def extract(self, nb_page, file, list_):

        title = ""
        text = ""
        first_id = True
        new_id = 0
        mlns = "{http://www.mediawiki.org/xml/export-0.10/}"

        # Get an iterable.
        context = ET.iterparse(file, events=("start", "end"))
        nb = 0

        fichier = open("/home/ufrinfo/PycharmProjects/pythonProject/venv/dataResult.xml", "w")
        fichier.write("<mediawiki>\n")

        for index, (event, elem) in enumerate(context):
            # Get the root element.
            if index == 0:
                root = elem

            if event == "end":

                if elem.tag == mlns + "title":

                    if elem.text is None:
                        title = ""
                    else:
                        title = self.htmlspecialchars(elem.text)

                    root.clear()

                if elem.tag == mlns + "id" and first_id:
                    first_id = False
                    root.clear()

                if elem.tag == mlns + "text":

                    if elem.text is None:
                        title = ""
                    else:
                        text = self.htmlspecialchars(elem.text)

                    root.clear()

                if elem.tag == mlns + "page" and any(
                        re.search(r'\b%s\b' % word.lower(), title.lower()) or re.search(r'\b%s\b' % word.lower(), text.lower()) for word in list_):

                    nb += 1
                    fichier.write("<page>\n")
                    fichier.write("<title>" + title + "</title>\n")
                    fichier.write("<id>" + str(new_id) + "</id>\n")
                    fichier.write("<text>" + text + "</text>\n")
                    fichier.write("</page>\n")

                    new_id += 1
                    title = ""
                    text = ""
                    first_id = True

                    root.clear()
            if nb == nb_page:
                break

        fichier.write("</mediawiki>")
        print(nb)
        fichier.close()


# Exercice 2, TP1

    def dict_mot_frec(self, file):
        dicti = {}
        mlns = ""

        # Get an iterable.
        context = ET.iterparse(file, events=("start", "end"))
        nb = 0
        for index, (event, elem) in enumerate(context):
            # Get the root element.
            if index == 0:
                root = elem

            if event == "end":

                if elem.tag == mlns + "title":
                    title = self.htmlspecialchars(elem.text)
                    self.word_count(title,dicti)
                    root.clear()

                if elem.tag == mlns + "text":

                    text = self.htmlspecialchars(elem.text)
                    self.word_count(text,dicti)
                    root.clear()

                if elem.tag == mlns + "page":
                    nb += 1
                    root.clear()

        # prendre les 10000 mots les plus fréquants
        corrected_dict = dict(sorted(dicti.items(), key = itemgetter(1), reverse = True)[:10000])
        dicti.clear()
        listemotvide = ['ailleurs','fois','avoir','donc','souvent','soit','encore','etait','pour','sur','plus','que','www','date','sont','se','il','ou','son','name','qu','nom','pas','sous','ses','entre','of','mais','deux','ont','aussi','fait','on','cette','ete','meme','dont','prenom','autres','the','etre','tres','elle','apres','lui','egalement','and','notamment', 'vers',"par","dans","lt","gt","ref","le","la","les","l'","du","de","des","d'","un","une","et","au","aux","en","sa","ces","ce","-il","-elle","afin","ai","ainsi","alors","après","as","auprès","auquel","aurait","autre","avec","car","ceci","celui","chacun,'chaque","comme","est","est-ce","hors","leur","leurs","malgré","me","mes","moi","moins","notre","votre","qui","sans","sera",""]
        dicmotvide = {}

        # Supprimer les accents, les majuscules et les redondances
        dicti = { self.remove_accents(k): v for k, v in corrected_dict.items() }
        corrected_dict.clear()

        # Séparer les mots vides
        for key, value in dicti.items():
            if key in listemotvide:
                if key in dicmotvide:
                    dicmotvide[key] = dicmotvide[key]+value
                else:
                    dicmotvide[key] = value
            else:
                if key in corrected_dict:
                    corrected_dict[key] = corrected_dict[key] +value
                else:
                    corrected_dict[key] = value
        dicti.clear()

        # Trier le dict
        dicti = {val[0] : val[1] for val in sorted(corrected_dict.items(), key = lambda x: (-x[1], x[0]))}
        return dicti

    def remove_accents(self,data):
        nkfd_form = unicodedata.normalize('NFKD', data)
        only_ascii = nkfd_form.encode('ASCII', 'ignore')
        l = [c for c in str(only_ascii) if not c.isdigit() and c in string.ascii_letters]
        return ''.join(l[1:]).lower()


    def word_count(self,str,counts):
        words = re.split(r"[\b\W\b\d]+",str)

        for word in words:
            if (len(word)>1):
                if word in counts:
                    counts[word] += 1
                else:
                    counts[word] = 1

        return counts

#Exercice 3 IDF:

    def findPage(self, id_, file):

        first = 0
        id_find = False
        title = ""
        text = ""
        id = ""
        first_id = True
        mlns = ""

        for event, elem in ET.iterparse(file, events=("start", "end")):

            if event == 'start':

                if elem.tag == (mlns + 'title'):
                    title = elem.text
                    elem.clear()

                if elem.tag == (mlns + 'id') and first_id:

                    if elem.text is None:
                        elem.text = ""
                    else:
                        id = elem.text
                        id = int(id)

                    if id == id_:
                        id_find = True

                    first_id = False
                    elem.clear()

                if (elem.tag == (mlns + 'text')):

                    if elem.text is None:
                        elem.text = ""
                    else:
                        text = elem.text

                    if first == 0:
                        if id_find:
                            break

                    first_id = True
                    elem.clear()

            if (event == 'end'):
                if (elem.tag == (mlns + 'text')):

                    first = 1

                    if elem.text is None:
                        elem.text = ""
                    else:
                        text = elem.text

                    if first == 1:

                        if id_find:
                            break

                    first_id = True
                elem.clear()

            elem.clear()

        if id != id_:
            return {"title": "", "id": "", "text": ""}

        return {"title": title, "id": id, "text": text}

    def word_verif(self,str):
        words = re.split(r"[\b\W\b\d]+",str)
        return words

    def idfm(self,file,dicti):
        dicidf = {}
        liste=[]
        for i in dicti:
            dicidf[i] = 0
        mlns = ""

        # Get an iterable.
        context = ET.iterparse(file, events=("start", "end"))
        nb = 0
        for index, (event, elem) in enumerate(context):
            # Get the root element.
            if index == 0:
                root = elem

            if event == "end":

                if elem.tag == mlns + "title":
                    title = self.htmlspecialchars(elem.text)
                    liste=self.word_verif(title)
                    root.clear()

                if elem.tag == mlns + "text":

                    text = self.htmlspecialchars(elem.text)
                    liste = list(set(liste +self.word_verif(text)))
                    root.clear()

                if elem.tag == mlns + "page":
                    nb += 1
                    listef = { self.remove_accents(k) for k in liste }
                    for w in dicti:
                        if w in listef:
                            dicidf[w]=dicidf[w]+1
                    root.clear()

        for w in dicidf:
            dicidf[w]= math.log10(nb/dicidf[w])
        return dicidf




a = ToolsText()
file = "/home/ufrinfo/PycharmProjects/pythonProject/venv/dataResult100.xml"
#print(a.extract(200_000, "/home/ufrinfo/PycharmProjects/pythonProject/venv/data", ["France", "Paris"]))

#a.dict_mot_frec(file)
#print(a.idfm(a.dict_mot_frec(file)))
#print(a.findPage(1456, file))
abc= a.dict_mot_frec(file)
a.idfm(file,abc)
# ============ main =================== #

