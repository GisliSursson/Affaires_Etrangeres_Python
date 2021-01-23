import folium
import re
import json

from flask import render_template, request, flash, redirect
from flask_login import login_user, current_user, logout_user
from app.modeles.utilisateurs import User
from .app import app, login
from .modeles.data_dict import codes_dict as data
from .modeles.data_db import data as db


pays_existe_plus = ["su", "yu", "zr", "cs"]


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
        placeholder = 'Brésil'
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
    # Test pour les erreurs prévues par rapport aux codes pays du csv
    # Test pour les pays qui n'existent plus
    if code in pays_existe_plus:
        flash("Erreur : le pays demandé ('{query}') n'existe plus !".format(query=query), "error")
        return redirect("/")
    # Test pour les territoires qui sont dans le csv mais n'ont pas de représentation diplomatique
    try:
        print(db[code])
    except:
        flash("Erreur : le territoire demandé ('{query}') n'a pas de représentation diplomatique française !".format(query=query), "error")
        return redirect("/")
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

@app.route("/register", methods=["GET", "POST"])
def inscription():
    """ Route gérant les inscriptions
    """
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        statut, donnees = User.creer(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            flash("Enregistrement effectué. Vous devez maintenant réaliser votre première connexion", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("inscription.html")
    else:
        return render_template("inscription.html")


@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    """ Route gérant les connexions
    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté-e", "info")
        return redirect("/")
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        utilisateur = User.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")

    return render_template("connexion.html")
login.login_view = 'connexion'


@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")

