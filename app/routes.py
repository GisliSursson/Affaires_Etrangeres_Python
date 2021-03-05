import folium
import re
import ast
import json
import numpy
import pandas as pd
import random

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from app.modeles.utilisateurs import User
from .app import app, login, users
from .modeles.data_dict import codes_dict as data
from .modeles.data_db import data as db
from .search import indexation, schema
from whoosh.qparser import QueryParser

# Variable globales utilisables par toutes les fonctions
pays_existe_plus = ["su", "yu", "zr", "cs"]

@app.route("/a_propos")
def a_propos():
    """ Route permettant l'affichage d'une page à propos
        """
    # Calcul des statistiques sur l'appli à afficher dans la page "à propos"
    nb_inscrits = User.query.count()
    nb_recherches = 0
    for user in User.query.all():
        histo = str(user.user_historique)
        histo = histo.split(";")
        nb_rech_user = len(histo)
        nb_recherches += nb_rech_user
    return render_template("a_propos.html", nb_inscrits=nb_inscrits, nb_recherches=nb_recherches)

@app.route("/")
def accueil():
    """ Route permettant l'affichage d'une page accueil
    """
    return render_template("accueil.html", titre="Apli réseau diplo.")

@app.route("/recherche")
@login_required
def recherche():
    # Route permettant l'affichage de la page recherche selon le mode souhaité
    # Va chercher la valeur choisie par l'utilisateur dans l'HTML. Sera None en cas de valeur nulle.
    type_recherche = request.args.get("type_voulu", None)
    # chemin_json = send_from_directory(os.path.join(chemin_actuel, 'modeles'), 'codes_json.json')
    if type_recherche == 'pays':
        type = type_recherche
        # Placeholder choisi arbitrairement
        placeholder = 'Brésil'
        return render_template("recherche.html", type=type, placeholder=placeholder)
    elif type_recherche == 'ville':
        type = type_recherche
        placeholder = 'Rome'
        return render_template("recherche_ville.html", type=type, placeholder=placeholder)

@app.route("/profil")
@login_required
def profil():
    histo = current_user.user_historique.split(";")
    # print(histo)
    return render_template("profil.html", current_user=current_user, histo=histo)

# Définition de la fonction pour la recherche par ville
@app.route("/resultats_ville")
@login_required
def resultats_ville():
    keyword = request.args.get("query", None)
    myMap = folium.Map()
    # Definition de là où on cherche dans l'indexation
    qp = QueryParser("city", schema=schema)
    # Définition du mot-clef recherché
    q = qp.parse(u'{keyword}'.format(keyword=keyword))
    with indexation.searcher() as s:
        # Exécution de la recherche
        results = s.search(q, terms=True)
        if len(results) == 0:
            flash("Erreur ! Vous avez entré : '{keyword}'. Merci de n'utiliser uniquement les valeurs proposées par l'autocomplétion".format(keyword=keyword), "error")
            return redirect("/")
        # S'il n'y a qu'une seule représentation diplomatique dans la ville
        elif len(results) == 1:
            # Liste qui servira à la déterminsation du niveau de zoom optimal
            ensemble_coord = []
            # print(results)
            result_ville = results.fields(0)
            a_afficher = result_ville.get("content")
            # Traitement de la chaîne renvoyée par whoosh pour la transformer en dict. On utilise pas le package
            # JSON car l'encodage de whoosh ne permet pas la conversion en JSON.
            a_afficher = ast.literal_eval(a_afficher)
            # print(type(a_afficher))
            # print(a_afficher)
            a_afficher = dict(a_afficher)
            # Construction du HTML qui sera affiché dans les bulles de la cartes
            html = "<table>"
            for key, value in a_afficher.items():
                if type(value) != dict:
                    html = html + '<tr><td>' + str(key).strip() + '</td><td>' + str(value).strip() + '</td></tr>'
                if type(value) == dict:
                    # Traitement des socials qui peuvent être des nested dict. Conversion en str et on va chercher les anchors
                    # en regex (les seules choses intéresantes pour l'utilisateur graphique)
                    string = json.dumps(value)
                    # regex non greedy
                    socials = re.findall('<a.+?</a>', string)
                    for index, element in enumerate(list(set(socials))):
                        html = html + '<tr><td>rés. soc. n°{}</td><td>'.format(index + 1) + element + '</td></tr>'
            html = html + "</table>"
            popup = folium.Popup(html, min_width=800, max_width=800)
            folium.Marker(location=[a_afficher["latitude"], a_afficher["longitude"]],
                          tooltip=a_afficher["nom"],
                          popup=popup).add_to(myMap)
            ensemble_coord.append([a_afficher["latitude"], a_afficher["longitude"]])


        # S'il y a plusieurs représentations diplomatiques dans la ville
        elif len(results) > 1:
            # Liste qui servira à la déterminsation du niveau de zoom optimal
            ensemble_coord = []
            # "Results" est un whoosh.searching.Results qui contient plusieurs "hits"
            for result_element in results:
                # Transformation du whoosh.searching.Hit en dict
                result_element_dico = result_element.fields()
                dico = result_element_dico.get("content")
                # Transformation de la value associée à la key "content" (qui est str) en dict
                dico = ast.literal_eval(str(dico))
                dico = dict(dico)
                # Renommage pour plus de clarté
                a_afficher = dico
                html = "<table>"
                for key, value in a_afficher.items():
                    if type(value) != dict:
                        html = html + '<tr><td>' + str(key).strip() + '</td><td>' + str(value).strip() + '</td></tr>'
                    if type(value) == dict:
                        # Traitement des socials qui peuvent être des nested dict. Conversion en str et on va chercher les anchors
                        # en regex (les seules choses intéresantes pour l'utilisateur graphique)
                        string = json.dumps(value)
                        # regex non greedy
                        socials = re.findall('<a.+?</a>', string)
                        for index, element in enumerate(list(set(socials))):
                            html = html + '<tr><td>rés. soc. n°{}</td><td>'.format(index + 1) + element + '</td></tr>'
                html = html + "</table>"
                # Modification des coordonnées à afficher si deux points sur la carte ont strictement les mêmes coordonnées
                if [a_afficher["latitude"], a_afficher["longitude"]] in ensemble_coord:
                    nouv_lat = a_afficher["latitude"] + random.uniform(0.00001, 0.00005)
                    nouv_long = a_afficher["longitude"] + random.uniform(0.00001, 0.00005)
                    popup = folium.Popup(html, min_width=800, max_width=800)
                    folium.Marker(location=[nouv_lat, nouv_long], tooltip=a_afficher["nom"],
                                      popup=popup).add_to(myMap)
                else:
                    popup = folium.Popup(html, min_width=800, max_width=800)
                    folium.Marker(location=[a_afficher["latitude"], a_afficher["longitude"]],
                                      tooltip=a_afficher["nom"],
                                      popup=popup).add_to(myMap)
                ensemble_coord.append([a_afficher["latitude"], a_afficher["longitude"]])
                print(ensemble_coord)
        # Détermination du niveau de zoom optimal (Folium utilise des bornes sud-ouest et nord-est)
        # Numpy et panda sont utilisés pour trouver la liste "minimum/maximum" dans une liste de listes.
        ensemble_coord = numpy.array(ensemble_coord)
        data_frame = pd.DataFrame(ensemble_coord, columns=['Lat', 'Long'])
        sw = data_frame[['Lat', 'Long']].min().values.tolist()
        ne = data_frame[['Lat', 'Long']].max().values.tolist()
        myMap.fit_bounds([sw, ne])

        # Ecriture dans l'historique (pour les villes)
        if current_user.is_authenticated is True:
            utilisateur = User.query.filter_by(user_id=current_user.user_id).first()
            # Création de l'historique s'il n'existe pas
            if utilisateur.user_historique is None:
                utilisateur.user_historique = keyword + ";"
            # Ajout à l'historique sinon
            else:
                utilisateur.user_historique += keyword + ";"
            users.session.commit()
    return render_template("resultats.html", myMap=myMap._repr_html_(), query=keyword, ville=keyword)


# Définition de la fonction pour la recherche par pays
@app.route("/resultats")
@login_required
def resultats():
    query = request.args.get("query", None)
    try:
        code = (data[query]).lower()
    except:
        flash("Erreur ! Vous avez entré : '{keyword}'. Merci de n'utiliser uniquement les valeurs proposées par l'autocomplétion".format(
                keyword=query), "error")
        return redirect("/")
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
    # Liste qui servira à la détermination du niveau de zoom optimal
    ensemble_coord = []
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
        # Modification des coordonnées dans le cas où il y a une ambassade et un consulat strictement au même endroit
        if [element_liste["latitude"], element_liste["longitude"]] in ensemble_coord:
            nouv_lat = element_liste["latitude"] + random.uniform(0.00001, 0.00005)
            nouv_long = element_liste["longitude"] + random.uniform(0.00001, 0.00005)
            popup = folium.Popup(html, min_width=800, max_width=800)
            folium.Marker(location=[nouv_lat, nouv_long], tooltip=element_liste["nom"],
                      popup=popup).add_to(myMap)
        else:
            popup = folium.Popup(html, min_width=800,max_width=800)
            folium.Marker(location=[element_liste["latitude"], element_liste["longitude"]], tooltip=element_liste["nom"],
                          popup=popup).add_to(myMap)
        ensemble_coord.append([element_liste["latitude"], element_liste["longitude"]])
    # Détermination du niveau de zoom optimal (Folium utilise des bornes sud-ouest et nord-est)
    # Numpy et panda sont utilisés pour trouver la liste "minimum/maximum" dans une liste de listes.
    ensemble_coord = numpy.array(ensemble_coord)
    data_frame = pd.DataFrame(ensemble_coord, columns=['Lat', 'Long'])
    # print(ensemble_coord)
    # print(data_frame)
    sw = data_frame[['Lat', 'Long']].min().values.tolist()
    ne = data_frame[['Lat', 'Long']].max().values.tolist()
    # print(sw)
    # print(ne)
    myMap.fit_bounds([sw, ne])
    # Ecriture dans l'historique (pour les pays)
    if current_user.is_authenticated is True:
        utilisateur = User.query.filter_by(user_id=current_user.user_id).first()
        # Création de l'historique s'il n'existe pas
        if utilisateur.user_historique is None:
            utilisateur.user_historique = query + ";"
        # Ajout à l'historique sinon
        else:
            utilisateur.user_historique += query + ";"
        users.session.commit()
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

# Indication à Flask de la page utilisée pour faire les connexions
login.login_view = 'connexion'


@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")

