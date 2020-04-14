import csv
import scrapy
from requests import get
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from typing import Sequence, TypeVar
from difflib import ndiff
import time

def ScrappingParMonstre(bestiary,monstre):
    phrase=""

    if bestiary==2:
        phrase="http://legacy.aonprd.com/bestiary2/"
        phrase = phrase + monstre
        response = get(phrase)
        xpathselection1 = Selector(response).xpath("/html/body/div[3]/div[2]/div/p").getall()
        xpathselection2 = Selector(response).xpath("/html/body/div[3]/div[2]/div/p/b/a").getall()
        xpathselection3 = Selector(response).xpath("/html/body/div[3]/div[2]/div/p/b").getall()

    else :
        if bestiary == 1:
            phrase = "http://legacy.aonprd.com/bestiary/"
        if bestiary == 3:
            phrase = "http://legacy.aonprd.com/bestiary3/"
        if bestiary == 4:
            phrase = "http://legacy.aonprd.com/bestiary4/"
        if bestiary == 5:
            phrase = "http://legacy.aonprd.com/bestiary5/"

        phrase = phrase + monstre
        response = get(phrase)
        xpathselection1 = Selector(response).xpath("/html/body/div[3]/div[2]/p/a").getall()
        xpathselection1 = Selector(response).xpath("/html/body/div[3]/div[2]/p").getall()
        xpathselection2 = Selector(response).xpath("/html/body/div[3]/div[2]/p/b/a").getall()
        xpathselection3=""
        if bestiary == 5:
         xpathselection3 = Selector(response).xpath("/html/body/div[3]/div[2]/p/strong").getall()
        else:
         xpathselection3 = Selector(response).xpath("/html/body/div[3]/div[2]/p/b").getall()

    nomDesMonstreDeLaPage = Selector(response).xpath("//*[@class='stat-block-title']/b/text()").getall()
    if len(nomDesMonstreDeLaPage)==0:
     nomDesMonstreDeLaPage = Selector(response).xpath("//*[@class='stat-block-title']/text()").getall()
     #/ html / body / div[3] / div[2] / p[2]
    listeReturn = []
    if len(nomDesMonstreDeLaPage)==1:
     nomMonstres=nomDesMonstreDeLaPage[0]
     rechercherSpell = MonstrePossedeSort(xpathselection2, xpathselection3)
     if (rechercherSpell):
        MonstreNode = selectionDeLaPartieDuMonstre(xpathselection1, nomMonstres)
        listeSpell = ExtraitElementsClef(MonstreNode)
        liste = CleanLine(listeSpell)
        listeReturn.append(liste)
    else:
     if "#" in monstre:
      nomMonstres=trouveLeBonMonstre(nomDesMonstreDeLaPage,monstre)
      for elementMonstres in nomMonstres:
         rechercherSpell = MonstrePossedeSort(xpathselection2, xpathselection3)

         if (rechercherSpell):
             MonstreNode = selectionDeLaPartieDuMonstre(xpathselection1, elementMonstres)
             listeSpell = ExtraitElementsClef(MonstreNode)
             liste = CleanLine(listeSpell)
             listeReturn.append(liste)

    return listeReturn
def ExtraitElementsClef(MonstreNode):
    listeSpell = []
    for element in MonstreNode:
        if "<i>" in element:
           MonstreNode.remove(element)
           elements=element.split("<i>")
           for particule in elements:
               MonstreNode.append(particule)
    for element in MonstreNode:
        if "At Will" in element:
            listeSpell.append(element)
        if "day" in element:
            listeSpell.append(element)
        if "CR" in element:
            listeSpell.append(element)
        if "CL" in element:
            listeSpell.append(element)
        if "DC" in element:
            listeSpell.append(element)
        if "/coreRulebook/spells/" in element:
            listeSpell.append(element)
    return  list(dict.fromkeys(listeSpell))
def MonstrePossedeSort(xpathselection2,xpathselection3):
    SpellTrouve=False
    for element in xpathselection2:
        if "Spell" in element:
            #print("Il existe des spell " + monstre)
            SpellTrouve = True
            break
    for line in xpathselection3:
        if "Spell"in line:
            #print("Il existe des spell prepare pour le monstre " + monstre)
            SpellTrouve = True
            break
    return SpellTrouve
def selectionDeLaPartieDuMonstre(xpathselection1,elementMonstres):
    indexDebut = -1
    indexFin = -1
    for element in xpathselection1:
        if elementMonstres in element and indexDebut == -1: indexDebut = xpathselection1.index(element)
        if 'Statistics' in element and indexFin == -1 and indexDebut != -1:
            if indexFin == -1:
                indexFin = xpathselection1.index(element, indexDebut)
    return xpathselection1[indexDebut:indexFin]
def ScrappingListeMonstre(page):
    response = get(page)
    listMonstre = Selector(response).xpath("/html/body/div[3]/div[2]/div[1]/ul/li/a/@href").getall()
    return listMonstre
def WritteCSV(listeMonstre,titreFichier ):
    spamWriter = csv.writer(open(titreFichier+'.csv', 'w'))
    for element in listeMonstre:
        spamWriter.writerow(element)
def TraitementListe(listeMonstre):
    listname=[]
    liste=[listeMonstre,listname]

    for liensMonstre in liste[0]:
        if "#" in liensMonstre:
         debut=int(liensMonstre.index("#"))+1
         fin=int(len(liensMonstre))
         nom=liensMonstre[debut:fin]
         liste[1].append(nom)
        if '#' not in liensMonstre :liste[0].pop(liste[0].index(liensMonstre))

    nametopop=[]
    for monstre in liste[1]:
        for testMonstre in liste[1]:
         if str(monstre) in testMonstre and monstre != testMonstre:
             nametopop.append(monstre)
             break

    for element in nametopop:
        for x in range(0,len(liste[0])-1):
            if "#" not in liste[0][x]:
                liste[0].pop(x)
            if "#" in liste[0][x]:
                debut=liste[0][x].index("#")+1
                if liste[0][x][debut:len(liste[0][x])]==element:
                    liste[0].pop(x)
                    break
            print(x)
def CleanLine(liste):
    newlist=[]
    for line in liste:
        subelement=line.split(',')
        for element in subelement:
         exclusif=True
         if "stat-block-title"in  element and exclusif :
             debutrecherche = element.find("title")
             debut = element.find(">", debutrecherche)
             fin = element.find("<span", debut)
             if "<b>"in element[debut + 1:fin]:
              debut=debut+3
             newlist.append(element[debut + 1:fin])
             exclusif=False
         if "/coreRulebook/spells/" in element:
            debutrecherche=element.find(".html")
            debut=element.find(">",debutrecherche)
            fin=element.find("</a>",debut)
            newlist.append(element[debut+1:fin])
         if "stat-block-cr" in element and exclusif:
            debut = element.find("b>")
            fin = element.find("<span class=", debut)
            newlist.append(element[debut + 2:fin])
            debut = element.find("CR")
            fin = element.find("</span>", debut)
            newlist.append(element[debut :fin])
         if "CL" in element:
             debutrecherche = element.find("CL")
             fin = element.find("<", debutrecherche)
             element = element[debutrecherche:fin]
             element = element.replace(")", "")
             newlist.append(element)
         if "day" in element:
             debutrecherche = element.find("day")
             newlist.append(element[debutrecherche -2:debutrecherche+3])
         if "DC" in element:
             debutrecherche = element.find("DC")
             fin = element.find("<", debutrecherche)
             element=element[debutrecherche :fin]
             element=element.replace(")","")
             newlist.append(element)

    return newlist
def trouveLeBonMonstre(nomDesMonstreDeLaPage,monstre):
    nomMonstre=""
    prefixe = monstre.replace(".html", "")
    if "#" in str(monstre):
     nomMonstre = monstre[monstre.index("#") + 1:len(monstre)]
     nomMonstre = nomMonstre.replace("-", " ")
     nomMonstre = nomMonstre.replace(",", "")
     nomMonstre = nomMonstre.split(" ")
     prefixe = monstre[0:monstre.find(".html")]
     if prefixe in str(nomMonstre):
         nomMonstre.remove(prefixe)
    else: nomMonstre = monstre


    nomsRestant = []
    for nom in nomMonstre:
        if len(nom)>1:
         nomIntermediaire=nom[0].upper()+nom[1:len(nom)-1]
         for element in nomDesMonstreDeLaPage:
          if nomIntermediaire in element:
             nomsRestant.append(element)
    return nomsRestant
def scrappingParBestiaire(value):
    liensBestiaires=["http://legacy.aonprd.com/bestiary/monsterIndex.html",
                     "http://legacy.aonprd.com/bestiary2/additionalMonsterIndex.html",
                     "http://legacy.aonprd.com/bestiary3/monsterIndex.html",
                     "http://legacy.aonprd.com/bestiary4/monsterIndex.html",
                     "http://legacy.aonprd.com/bestiary5/index.html"]
    liste = []
    listeTraitee = []
    listeMonstre = ScrappingListeMonstre(liensBestiaires[value-1])
    for element in listeMonstre:
     time.sleep(.200)
     ListeSortsMonstres = ScrappingParMonstre(value, element)
     if (ListeSortsMonstres != 0):
      liste = liste+ListeSortsMonstres
    for element in liste:
     if len(element) > 1:
      listeTraitee.append(element)
    WritteCSV(listeTraitee, "DandDindex"+str(value))
def main():
    for index in range(5,6):
        scrappingParBestiaire(index)
        print("Scrapping du bestiaire "+str(index)+" fini :) ")


main()
print("Fin du scrapping")