import folium
import re
import json

from flask import render_template, request
from .app import app
from .modeles.data_dict import codes_dict as data
from .modeles.data_db import data as db
@app.route("/")
def accueil():
    """ Route permettant l'affichage d'une page accueil
    """
    return render_template("accueil.html", titre="Apli réseau diplo.")

@app.route("/recherche")
def recherche():
    # Route permettant l'affichage de la page recherche généraliste
    # Va chercher la valeur choisie par l'utilisateur dans l'HTML. Sera None en vas de valeur nulle.
    type_recherche = request.args.get("type_voulu", None)
    if type_recherche == 'pays':
        type = type_recherche
        placeholder = 'Russie'
    if type_recherche == 'ville':
        type = type_recherche
        placeholder = 'Rome'
    # pas de else pour raison de debug
    if type_recherche == 'libre':
        type = type_recherche
        placeholder = 'Votre recherche ici'
    return render_template("recherche.html", type=type, placeholder=placeholder)

# Définition de plusieurs fonctions pour la page résultats selon le type de recherche choisi
@app.route("/resultats")
def resultats():
    query = request.args.get("query", None)
    code = (data[query]).lower()
    myMap = folium.Map()
    for element_liste in db[code]:
        html = "<table>"
        for key, value in element_liste.items():
            if type(value) != dict:
                html = html + '<tr><td>'+ str(key).strip() + '</td><td>' + str(value).strip() + '</td></tr>'
            if type(value) == dict:
                # Traitement des socials qui peuvent être des nested dict. Conversion en str et on va chercher les anchors
                # en regex (les seules choses intéresantes pour l'utilisateur graphique)
                string = json.dumps(value)
                # regex non greedy
                socials = re.findall('<a.+?</a>', string)
                for index, element in enumerate(list(set(socials))):
                    html = html + '<tr><td>rés. soc. n°{}</td><td>'.format(index+1) + element + '</td></tr>'
        html = html + "</table>"
        popup = folium.Popup(html, min_width=800,max_width=800)
        folium.Marker(location=[element_liste["latitude"], element_liste["longitude"]], tooltip=element_liste["nom"],
                      popup=popup).add_to(myMap)

    #query = request.args.get("query", None)
    #code = (data[query]).lower()
    #dico = db[code]
    #nom = query
    return render_template("resultats.html", myMap=myMap._repr_html_(), query=query)


