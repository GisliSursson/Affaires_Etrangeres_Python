import folium
import re
import ast
import json
import numpy
import pandas as pd
import random

from flask import render_template, request, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required
from app.modeles.utilisateurs import User
from .app import app, login, users
from .modeles.data_dict import codes_dict as data
from .modeles.data_db import data as db
from .search import indexation, schema
from whoosh.qparser import QueryParser
from werkzeug.security import check_password_hash, generate_password_hash


# "data" : liste des codes à deux lettres
# "db" : la BD JSON principale

# Variable globales utilisables par toutes les fonctions
pays_existe_plus = ["su", "yu", "zr", "cs"]

def choix_couleur(dico):
    """Fonction déterminant la couleur du point sur la carte en fonction du type de représentation
    diplomatique (ambassade, consulat, consulat général

        :param [dico]: dict provenant de la base JSON
        :type [dico]: dict

        :return: couleur voulue (selon la doc Folium)
        :rtype: str

        """
    # Rouge : consulat général, vert : consulat, bleu : ambassade
    # NB : le code prend en compte l'inconsistence des données source dans les clefs de dict.
    # Certains consulats généraux
    # sont indiqués en type 'consulat'. Certains postes n'ont pas de type du tout.
    # On est donc obligé de parser des str
    dico = str(dico).lower()
    # NB : ne permet pas de colorier correctement les consulats généraux qui ont pour type
    # 'consulat' au lieu de 'consulat_general'. Les problème est que les consulats généraux
    # sont parfois indiqué dans les numéros d'urgence de postes d'autres types. On ne peut donc pas
    # se baser sur l'occurence de la substring 'general' pour définir un consulat général.
    if "_general" in dico:
        color = 'red'
    elif "consulat'" in str(dico).lower():
        color = 'green'
    else:
        color = 'blue'
    return color

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
    """Route détermiant le type de recherche choisie par l'utilisateur

    :return: template
    :rtype: flask.render_template

    :return: type
    :rtype: str

    :return: placeholder
    :rtype: str

    """
    # Route permettant l'affichage de la page recherche selon le mode souhaité
    # Va chercher la valeur choisie par l'utilisateur dans l'HTML. Sera None en cas de valeur nulle.
    type_recherche = request.args.get("type_voulu", None)
    if type_recherche == 'pays':
        type_voulu = type_recherche
        # Placeholder choisi arbitrairement
        placeholder = 'Brésil'
        return render_template("recherche.html", type=type_voulu, placeholder=placeholder)
    if type_recherche == 'ville':
        type_voulu = type_recherche
        placeholder = 'Rome'
        return render_template("recherche_ville.html", type=type_voulu, placeholder=placeholder)
    # Affichage de l'index général de navigation
    if type_recherche == 'index':
        # L'index général sera affiché via une liste de dict du type [{'pays': [{ville:ville, type:type}]}, ...]
        liste = []
        liste_codes = data.values()
        for code in liste_codes:
            # Ici, ce n'est pas grave si le code n'existe pas dans la base JSON
            try:
                cible = db[code.lower()]
                # Sera une liste de dict
                liste_ville = []
                for representation in cible:
                    # Certains postes n'ont pas de ville indiqué
                    try:
                        ville = representation["ville"]
                        # Traitement des str inconsistantes dans les données sources
                        for lettre in ville:
                            if lettre.isnumeric():
                                ville = ville.replace(lettre, '')
                        # Traitement pour les noms de ville où il y a des abréviations
                        search_object = re.search(r"([A-Z]\.){2}", ville)
                        if search_object:
                            ville = ville.replace(search_object.group(), '')
                        # Correction unique pour Brasilia (si utilisation regex impacte autres villes)
                        if ' - Df' in ville:
                            ville = ville.replace(' - Df', '')
                        # Détermination du "nom exact" du pays (utilisé pour hard coder les URL)
                        for key, value in data.items():
                            if value.lower() == representation['iso2']:
                                pays = key
                        # Filtrage sur les types pour les postes situés dans un pays mais compétents
                        # pour un autre pays. Dans ce cas, la compétence est généralement indiquée dans le nom
                        if "compéten" in representation['nom'].lower():
                            type_rep = representation['nom']
                            # Modification typographique esthétique
                            type_rep = type_rep.replace('(', '')
                            type_rep = type_rep.replace(')', '')
                        else:
                            type_rep = representation["type"]
                        # Nettoyage de la donnée pour le type
                        if '_' in type_rep:
                            type_rep = type_rep.replace('_', ' ')
                        if "general" in type_rep:
                            type_rep = type_rep.replace('general', 'général')
                        liste_ville.append({'ville': ville.title(), 'type': type_rep})
                        # Classement des villes dans un pays par ordre alphabétique n'est pas possible pour les dict
                    except KeyError:
                        pass
                liste.append({pays: liste_ville})
            except KeyError:
                pass
        return render_template("index.html", liste=liste)
    if type_recherche == 'carte':
        # Carte qui sera complétée au fur et à mesure
        myMap = folium.Map()
        # Liste qui servira à la détermination du niveau de zoom optimal
        ensemble_coord = []
        searcher = indexation.searcher()
        # Création d'un itérable contenant toutes les données indexées (les villes)
        iterable = list(searcher.lexicon("city"))
        for element in iterable:
            element = element.decode("utf-8")
            # Definition de là où on cherche dans l'indexation
            qp = QueryParser("city", schema=schema)
            # Définition du mot-clef recherché à chaque itération
            q = qp.parse(u'{keyword}'.format(keyword=element))
            with indexation.searcher() as s:
                # Exécution de la recherche
                results = s.search(q, terms=True)
                # S'il n'y a qu'une seule représentation diplomatique dans la ville
                if len(results) == 1:
                    result_ville = results.fields(0)
                    a_afficher = result_ville.get("content")
                    # Traitement de la chaîne renvoyée par whoosh pour la transformer en dict.
                    a_afficher = ast.literal_eval(a_afficher)
                    a_afficher = dict(a_afficher)
                    # Construction graduelle du HTML qui sera affiché dans les bulles de la cartes
                    # NB : le code prend en compte l'inconsistence des données sources
                    # (certaines clefs manquent à certains dict
                    html = "<table>"
                    for key, value in a_afficher.items():
                        if type(value) != dict:
                            # Modification du type consulat général pour qu'il soit plus joli à afficher
                            if isinstance(value, str) and "consulat_general" in value:
                                value = value.replace("consulat_general", "consulat général")
                            # Modification des URL pour ouverture dans un nouvel onglet
                            if isinstance(value, str) and "<a" in value:
                                # La balise "span" est plus adaptée à un affichage en ligne
                                value = value.replace("<p>", "<span>")
                                value = value.replace("</p>", "</span>")
                                value = value.replace("<a", "<a target='_blank'")
                            html = html + '<tr><td>' + str(key).strip() + '</td><td>' + str(value).strip() + '</td></tr>'
                        if type(value) == dict:
                            # Traitement des socials qui peuvent être des nested dict. Conversion en str et on va chercher les anchors
                            # en regex (les seules choses intéresantes pour l'utilisateur graphique)
                            string = json.dumps(value)
                            # regex non greedy
                            socials = re.findall('<a.+?</a>', string)
                            for index, element in enumerate(list(set(socials))):
                                # Modification de l'URL présent dans les données sources pour ouverture dans un nouvel onglet
                                element = element.replace("<a", "")
                                ajout = "<a target='_blank''"
                                element = ajout + element
                                html = html + '<tr><td>rés. soc. n°{index} :</td><td>'.format(
                                    index=index + 1) + element + '</td></tr>'
                    html = html + "</table>"
                    # Différenciation de couleurs entre ambassades et consulats (on évite le problème de majuscule)
                    color = choix_couleur(a_afficher)
                    popup = folium.Popup(html, min_width=800, max_width=800)
                    folium.Marker(location=[a_afficher["latitude"], a_afficher["longitude"]],
                                  tooltip=a_afficher["nom"],
                                  popup=popup, icon=folium.Icon(color=color)).add_to(myMap)
                    ensemble_coord.append([a_afficher["latitude"], a_afficher["longitude"]])

                # S'il y a plusieurs représentations diplomatiques dans la ville
                elif len(results) > 1:
                    # Liste qui servira à la déterminsation du niveau de zoom optimal
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
                                # Modification du type consulat général pour qu'il soit plus joli à afficher
                                if isinstance(value, str) and "consulat_general" in value:
                                    value = value.replace("consulat_general", "consulat général")
                                # Modification des URL pour ouverture dans un nouvel onglet
                                if isinstance(value, str) and "<a" in value:
                                    # La balise "span" est plus adaptée à un affichage en ligne
                                    value = value.replace("<p>", "<span>")
                                    value = value.replace("</p>", "</span>")
                                    value = value.replace("<a", "<a target='_blank'")
                                html = html + '<tr><td>' + str(key).strip() + '</td><td>' + str(
                                    value).strip() + '</td></tr>'
                            if type(value) == dict:
                                # Traitement des socials qui peuvent être des nested dict.
                                # Conversion en str et on va chercher les anchors
                                # en regex (les seules choses intéresantes pour l'utilisateur graphique)
                                string = json.dumps(value)
                                # regex non greedy
                                socials = re.findall('<a.+?</a>', string)
                                for index, element in enumerate(list(set(socials))):
                                    # Modification de l'URL présent dans les données sources
                                    # pour ouverture dans un nouvel onglet
                                    element = element.replace("<a", "")
                                    ajout = "<a target='_blank''"
                                    element = ajout + element
                                    html = html + '<tr><td>rés. soc. n°{}</td><td>'.format(
                                        index + 1) + element + '</td></tr>'
                        html = html + "</table>"
                        # Différenciation de couleurs entre ambassades et consulats (on évite le problème de majuscule)
                        color = choix_couleur(a_afficher)
                        # Modification des coordonnées à afficher si deux points sur la carte ont
                        # strictement les mêmes coordonnées
                        if [a_afficher["latitude"], a_afficher["longitude"]] in ensemble_coord:
                            nouv_lat = a_afficher["latitude"] + random.uniform(0.00001, 0.00005)
                            nouv_long = a_afficher["longitude"] + random.uniform(0.00001, 0.00005)
                            popup = folium.Popup(html, min_width=800, max_width=800)
                            folium.Marker(location=[nouv_lat, nouv_long], tooltip=a_afficher["nom"],
                                          popup=popup, icon=folium.Icon(color=color)).add_to(myMap)
                        else:
                            popup = folium.Popup(html, min_width=800, max_width=800)
                            folium.Marker(location=[a_afficher["latitude"], a_afficher["longitude"]],
                                          tooltip=a_afficher["nom"],
                                          popup=popup, icon=folium.Icon(color=color)).add_to(myMap)
                        ensemble_coord.append([a_afficher["latitude"], a_afficher["longitude"]])
        # Détermination du niveau de zoom optimal (Folium utilise des bornes sud-ouest et nord-est)
        # Numpy et pandas sont utilisés pour trouver la "liste minimum/maximum" dans une liste de listes.
        ensemble_coord = numpy.array(ensemble_coord)
        data_frame = pd.DataFrame(ensemble_coord, columns=['Lat', 'Long'])
        sw = data_frame[['Lat', 'Long']].min().values.tolist()
        ne = data_frame[['Lat', 'Long']].max().values.tolist()
        myMap.fit_bounds([sw, ne])
        return render_template("resultats.html", myMap=myMap._repr_html_(), query='visualisation de toutes les données', legende=True)



@app.route("/profil")
@login_required
def profil():
    """ Route servant à l'utilisateur pour visualiser son profil

    :return: template
    :rtype: flask.render_template

    :return: current_user
    :rtype: flask_login.current_user

    :return: histo
    :rtype: list

    :return: pas_histo
    :rtype: bool
    """
    histo_user = current_user.user_historique
    if histo_user is None:
        histo = "Vous n'avez pas d'historique de recherche"
        pas_histo = True
    else:
        histo = current_user.user_historique.split(";")
        pas_histo = False
    return render_template("profil.html", current_user=current_user, histo=histo, pas_histo=pas_histo)

# On définie deux grands types de recherche : par ville et par pays. La recherche par pays fonctionne par jeu
# de clefs/valeurs dans le JSON. La recherche par ville fonctionne grâce à l'indexation plein texte de Whoosh.

# Définition de la fonction pour la recherche par ville
@app.route("/resultats_ville")
@login_required
def resultats_ville():
    """Fonction pour la recherche par ville

    :return: template
    :rtype: flask.render_template

    :return: myMap
    :rtype: folium.Map._repr_html_()

    :return: query
    :rtype: str
    """
    keyword = request.args.get("query", None)
    # Carte qui sera complétée au fur et à mesure
    myMap = folium.Map()
    # Definition de là où on cherche dans l'indexation
    qp = QueryParser("city", schema=schema)
    # Définition du mot-clef recherché
    q = qp.parse(u'{keyword}'.format(keyword=keyword))
    with indexation.searcher() as s:
        # Exécution de la recherche
        results = s.search(q, terms=True)
        if len(results) == 0:
            flash("Erreur ! Vous avez entré : '{keyword}'. Merci de n'utiliser uniquement les valeurs "
                  "proposées par l'autocomplétion".format(keyword=keyword), "error")
            return redirect("/")
        # S'il n'y a qu'une seule représentation diplomatique dans la ville
        elif len(results) == 1:
            # Liste qui servira à la détermination du niveau de zoom optimal
            ensemble_coord = []
            # print(results)
            result_ville = results.fields(0)
            a_afficher = result_ville.get("content")
            # Traitement de la chaîne renvoyée par whoosh pour la transformer en dict.
            a_afficher = ast.literal_eval(a_afficher)
            # print(type(a_afficher))
            # print(a_afficher)
            a_afficher = dict(a_afficher)
            # Construction graduelle du HTML qui sera affiché dans les bulles de la cartes
            html = "<table>"
            for key, value in a_afficher.items():
                if type(value) != dict:
                    # Modification du type consulat général pour qu'il soit plus joli à afficher
                    if isinstance(value, str) and "consulat_general" in value:
                        value = value.replace("consulat_general", "consulat général")
                    # Modification des URL pour ouverture dans un nouvel onglet
                    if isinstance(value, str) and "<a" in value:
                        # La balise "span" est plus adaptée à un affichage en ligne
                        value = value.replace("<p>", "<span>")
                        value = value.replace("</p>", "</span>")
                        value = value.replace("<a", "<a target='_blank'")
                    html = html + '<tr><td>' + str(key).strip() + '</td><td>' + str(value).strip() + '</td></tr>'
                if type(value) == dict:
                    # Traitement des socials qui peuvent être des nested dict. Conversion en str et on va chercher les anchors
                    # en regex (les seules choses intéresantes pour l'utilisateur graphique)
                    string = json.dumps(value)
                    # regex non greedy
                    socials = re.findall('<a.+?</a>', string)
                    for index, element in enumerate(list(set(socials))):
                        # Modification de l'URL présent dans les données sources pour ouverture dans un nouvel onglet
                        element = element.replace("<a", "")
                        ajout = "<a target='_blank''"
                        element = ajout + element
                        html = html + '<tr><td>rés. soc. n°{index} :</td><td>'.format(index= index + 1) + element +'</td></tr>'
            html = html + "</table>"
            # Détermination du code couleur
            color = choix_couleur(a_afficher)
            popup = folium.Popup(html, min_width=800, max_width=800)
            folium.Marker(location=[a_afficher["latitude"], a_afficher["longitude"]],
                          tooltip=a_afficher["nom"],
                          popup=popup, icon=folium.Icon(color=color)).add_to(myMap)
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
                        # Modification du type consulat général pour qu'il soit plus joli à afficher
                        if isinstance(value, str) and "consulat_general" in value:
                            value = value.replace("consulat_general", "consulat général")
                        # Modification des URL pour ouverture dans un nouvel onglet
                        if isinstance(value, str) and "<a" in value:
                            # La balise "span" est plus adaptée à un affichage en ligne
                            value = value.replace("<p>", "<span>")
                            value = value.replace("</p>", "</span>")
                            value = value.replace("<a", "<a target='_blank'")
                        html = html + '<tr><td>' + str(key).strip() + '</td><td>' + str(value).strip() + '</td></tr>'
                    if type(value) == dict:
                        # Traitement des socials qui peuvent être des nested dict.
                        # Conversion en str et on va chercher les anchors
                        # en regex (les seules choses intéresantes pour l'utilisateur graphique)
                        string = json.dumps(value)
                        # regex non greedy
                        socials = re.findall('<a.+?</a>', string)
                        for index, element in enumerate(list(set(socials))):
                            # Modification de l'URL présent dans les données sources
                            # pour ouverture dans un nouvel onglet
                            element = element.replace("<a", "")
                            ajout = "<a target='_blank''"
                            element = ajout + element
                            html = html + '<tr><td>rés. soc. n°{}</td><td>'.format(index + 1) + element + '</td></tr>'
                html = html + "</table>"
                # Détermination du code couleur
                color = choix_couleur(a_afficher)
                # Modification des coordonnées à afficher si deux points sur la carte ont
                # strictement les mêmes coordonnées
                if [a_afficher["latitude"], a_afficher["longitude"]] in ensemble_coord:
                    nouv_lat = a_afficher["latitude"] + random.uniform(0.00001, 0.00005)
                    nouv_long = a_afficher["longitude"] + random.uniform(0.00001, 0.00005)
                    popup = folium.Popup(html, min_width=800, max_width=800)
                    folium.Marker(location=[nouv_lat, nouv_long], tooltip=a_afficher["nom"],
                                      popup=popup, icon=folium.Icon(color=color)).add_to(myMap)
                else:
                    popup = folium.Popup(html, min_width=800, max_width=800)
                    folium.Marker(location=[a_afficher["latitude"], a_afficher["longitude"]],
                                      tooltip=a_afficher["nom"],
                                      popup=popup, icon=folium.Icon(color=color)).add_to(myMap)
                ensemble_coord.append([a_afficher["latitude"], a_afficher["longitude"]])
                # print(ensemble_coord)
        # Détermination du niveau de zoom optimal (Folium utilise des bornes sud-ouest et nord-est)
        # Numpy et pandas sont utilisés pour trouver la "liste minimum/maximum" dans une liste de listes.
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
    return render_template("resultats.html", myMap=myMap._repr_html_(), query=keyword)


# Définition de la fonction pour la recherche par pays
@app.route("/resultats")
@login_required
def resultats():
    """Fonction pour la recherche par pays

        :return: template
        :rtype: flask.render_template

        :return: myMap
        :rtype: folium.Map._repr_html_()

        :return: query
        :rtype: str
        """
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
    # (par ex. les territoires d'Outre-Mer)
    try:
        len(db[code])
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
                # Modification du type consulat général pour qu'il soit plus joli à afficher
                if isinstance(value, str) and "consulat_general" in value:
                    value = value.replace("consulat_general", "consulat général")
                # Modification des URL pour ouverture dans un nouvel onglet
                if isinstance(value, str) and "<a" in value:
                    # La balise "span" est plus adaptée à un affichage en ligne
                    value = value.replace("<p>", "<span>")
                    value = value.replace("</p>", "</span>")
                    value = value.replace("<a", "<a target='_blank'")
                html = html + '<tr><td>'+ str(key).strip() + '</td><td>' + str(value).strip() + '</td></tr>'
            if type(value) == dict:
                # Traitement des socials qui peuvent être des nested dict. Conversion
                # en str et on va chercher les anchors
                # en regex (les seules choses intéresantes pour l'utilisateur graphique)
                string = json.dumps(value)
                # regex non greedy
                socials = re.findall('<a.+?</a>', string)
                for index, element in enumerate(list(set(socials))):
                    # Modification de l'URL présent dans les données sources pour ouverture dans un nouvel onglet
                    element = element.replace("<a", "")
                    ajout = "<a target='_blank''"
                    element = ajout + element
                    html = html + '<tr><td>rés. soc. n°{}</td><td>'.format(index+1) + element + '</td></tr>'
        html = html + "</table>"
        # Détermination du code couleur
        color = choix_couleur(element_liste)
        # Modification d'un des deux dict de coordonnées dans le
        # cas où il y a une ambassade et un consulat strictement au même endroit
        if [element_liste["latitude"], element_liste["longitude"]] in ensemble_coord:
            nouv_lat = element_liste["latitude"] + random.uniform(0.00001, 0.00005)
            nouv_long = element_liste["longitude"] + random.uniform(0.00001, 0.00005)
            popup = folium.Popup(html, min_width=800, max_width=800)
            folium.Marker(location=[nouv_lat, nouv_long], tooltip=element_liste["nom"],
                      popup=popup, icon=folium.Icon(color=color)).add_to(myMap)
        else:
            popup = folium.Popup(html, min_width=800,max_width=800)
            folium.Marker(location=[element_liste["latitude"], element_liste["longitude"]], tooltip=element_liste["nom"],
                          popup=popup, icon=folium.Icon(color=color)).add_to(myMap)
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
    """Fonction pour les inscriptions

    :return: template
    :rtype: flask.render_template
    """

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
    """Fonction pour les connexions

    :return: template
    :rtype: flask.render_template
    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté-e", "info")
        return redirect("/")
    # Si on est en POST, cela veut dire que le formulaire a été envoyé depuis la page "connexion" déjà chargée
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
    """Fonction pour les déconnexions

        :return: template
        :rtype: flask.render_template
        """
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")

@app.route("/modification", methods=["POST", "GET"])
@login_required
def modification():
    """Fonction pour les inscriptions

        :return: template
        :rtype: flask.render_template

        :return: user
        :rtype: flask_login.user
        """
    id = current_user.user_id
    user = User.query.get_or_404(id)
    # Si on est en POST, cela veut dire que le formulaire a été envoyé depuis la page déjà chargée
    if request.method == "POST":
        login = request.form.get("login", None)
        email = request.form.get("email", None)
        nom = request.form.get("nom", None)
        nouv_motdepasse = request.form.get("nouv_motdepasse", None)
        anc_motdepasse = request.form.get("anc_motdepasse", None)
        if 'effacer' in request.form:
            effacer = True
        else:
            effacer = False
        if len(login) == 0:
            flash("Erreur : vous avez entré un login vide", "error")
            return render_template("edition.html", user=user)
        if len(email) == 0:
            flash("Erreur : vous avez entré un email vide", "error")
            return render_template("edition.html", user=user)
        if len(nom) == 0:
            flash("Erreur : vous avez entré un nom vide", "error")
            return render_template("edition.html", user=user)
        else:
            user.user_login = login
            user.user_email = email
            user.user_nom = nom
        # S'il y a modification du mot de passe
        if len(nouv_motdepasse) > 0 and check_password_hash(user.user_password, anc_motdepasse):
            user.user_password = generate_password_hash(nouv_motdepasse)
        # Si on a choisi d'effacer l'historique (est-ce que la checkbox retourne une valeur)
        print(effacer)
        if effacer is True:
            user.user_historique = None
        users.session.add(user)
        users.session.commit()
        flash("Vos informations ont bien été modifiées", "success")
        return render_template("accueil.html")
    return render_template("edition.html", user=user)


#@app.after_request
#def after(response):
    #print(response.status)
    #print(response.headers)
    #print(response.get_data().decode('utf-8'))
    #return response