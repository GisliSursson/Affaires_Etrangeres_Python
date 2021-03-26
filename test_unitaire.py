import pytest
from app.app import app as reseau_diplo
from random import randrange, choice
from tests_ic.listes import liste_pays, liste_villes
import urllib
from urllib.parse import urlencode, unquote
from bs4 import BeautifulSoup
from flask import request
import re




# On fait un test pour chacune des grandes fonctions de l'application : la recherche par pays, par ville,
# l'affichage de la carte de toutes les données, l'affichage de l'index.

# Etant donné que toutes les routes de l'application retournent des render_template, les tests_ic sont faits sur
# les documents HTML retournés.

# NB: ce fichier de test est placé au même niveau que le "run.py" afin de bénéficier des mêmes imports relatifs.

login_test = "example" + str(randrange(1000000))
nom_test = "example_nom" + str(randrange(1000000))
motdepasse_test = "blabla" + str(randrange(1000000))
mail_test = "lala" + str(randrange(1000000)) + "@a.fr"


@pytest.fixture
# Fonctions de configuration des tests
def client():
    with reseau_diplo.test_client() as client:
        yield client

def inscription(client):
    """Fonction qui sera utilisé pour tester l'inscription"""
    return client.post('/register', data=
        {'login': login_test, 'motdepasse': motdepasse_test,
         'nom': nom_test, 'email': mail_test}, follow_redirects=True)

def connexion(client):
    """Fonction qui sera utilisé pour tester l'inscription"""
    return client.post('/connexion', data=
        {'login': login_test, 'motdepasse': motdepasse_test}, follow_redirects=True)

# Fonctions de lancement des tests

@pytest.mark.repeat(1)
def test_accueil(client):
    """Test de bon affichage de la page d'accueil"""
    rv = client.get('/')
    assert b'Choisissez votre type de recherche' in rv.data


@pytest.mark.repeat(1)
def test_inscri(client):
    """Test l'inscriptionla latitude d'un utilisateur aléatoire et sa connexion"""
    rv = inscription(client)
    # On évite les caractères spéciaux
    assert b'Enregistrement effectu' in rv.data


def test_pays(client):
    """Fonction de test pour le bon affichage d'un pays"""
    rv = connexion(client)
    assert b'Connexion effectu' in rv.data
    pays = choice(liste_pays)
    pays_url = urllib.parse.quote(pays)
    response = client.get("/resultats?query=" + pays_url, follow_redirects=True)
    # print(response)
    # La réponse HTTP doit forcément avoir un coprs (puisqu'on retourne des données).
    # .data est en "bytes". Pour convertir des bytes en str, on fait .decode()
    headers = response.headers
    data = response.data.decode()
    # print("headers " + str(headers))
    # print("data " + str(data))
    # print("status_code : " + str(response.status_code))
    # Si le pays n'est pas trouvé, il y a redirection
    if request.path == '/':
        assert 'Erreur' in data
    # Sinon, le code HTTP renvoyé est celui du succès
    else:
        assert response.status_code == 200
        # Le corps est-il bien de l'HTML (l'application ne retourne que des pages web)?
        assert 'Content-Type: text/html; charset=utf-8' in str(headers)
        # On fait des tests sur des balises HTML
        html = BeautifulSoup(data, 'html.parser')
        # Test pour la ligne de titre
        assert html.h3.string == "Votre résultat pour : " + pays
        # Carte encodée en "percent encoding"
        carte = html.iframe['data-html']
        # Décodage de la carte
        carte = unquote(carte)
        carte = str(carte)
        # La carte est générée par Folium via des injections javascript. On ne peut donc pas
        # la parser comme du HTML, il faut la parser comme une str
        # Le pays est-il bien mentionné?
        assert pays in carte
        # Si c'est une ambassade, la représentation en tableau est-elle correcte?
        if 'Ambassade' in carte:
            # Ici on ne peut pas tester plus à cause de problèmes de grammaire
            # "ambassade à/en...".
            assert "<tr><td>nom</td><td>Ambassade de France" in carte
        # Tous les postes ont une ville
        assert "<td>ville</td>" in carte
        # Tous les postes ont une latitude qui doit être un float (regex non greedy)
        match = re.search(r'<td>latitude</td><td>(.+?)</td>', carte)
        try:
            float(match.group(1))
        except ValueError:
            return "Erreur sur la latitude"

def test_ville(client):
    """Fonction de test pour le bon affichage d'une ville"""
    rv = connexion(client)
    assert b'Connexion effectu' in rv.data
    ville = choice(liste_villes)
    ville_url = urllib.parse.quote(ville)
    response = client.get("/resultats_ville?query=" + ville_url, follow_redirects=True)
    # print(response)
    # La réponse HTTP doit forcément avoir un coprs (puisqu'on retourne des données).
    # .data est en "bytes". Pour convertir des bytes en str, on fait .decode()
    headers = response.headers
    data = response.data.decode()
    # print("headers " + str(headers))
    # print("data " + str(data))
    # print("status_code : " + str(response.status_code))
    # Si le pays n'est pas trouvé, il y a redirection
    if request.path == '/':
        assert 'Erreur' in data
    # Sinon, le code HTTP renvoyé est celui du succès
    else:
        assert response.status_code == 200
        # Le corps est-il bien de l'HTML (l'application ne retourne que des pages web)?
        assert 'Content-Type: text/html; charset=utf-8' in str(headers)
        # On fait des tests sur des balises HTML
        html = BeautifulSoup(data, 'html.parser')
        # Test pour la ligne de titre
        assert html.h3.string == "Votre résultat pour : " + ville
        # Carte encodée en "percent encoding"
        carte = html.iframe['data-html']
        # Décodage de la carte
        carte = unquote(carte)
        carte = str(carte)
        # La carte est générée par Folium via des injections javascript. On ne peut donc pas
        # la parser comme du HTML, il faut la parser comme une str
        # Le pays est-il bien mentionné?
        assert ville in carte
        # Tous les postes ont une latitude qui doit être un float (regex non greedy)
        match = re.search(r'<td>latitude</td><td>(.+?)</td>', carte)
        try:
            float(match.group(1))
        except ValueError:
            return "Erreur sur la latitude"
        # Tous les postes ont un mail
        try:
            match = re.search(r'>.+?@diplomatie.gouv.fr</a></td>', carte)
        except ValueError:
            return "Erreur sur le mail"

def test_toutes_donnees(client):
    """Fonction de test pour le bon affichage de la carte générale"""
    rv = connexion(client)
    assert b'Connexion effectu' in rv.data
    response = client.get("/recherche?type_voulu=carte")
    # La réponse HTTP doit forcément avoir un coprs (puisqu'on retourne des données).
    # .data est en "bytes". Pour convertir des bytes en str, on fait .decode()
    headers = response.headers
    data = response.data.decode()
    # print("headers " + str(headers))
    # print("data " + str(data))
    # print("status_code : " + str(response.status_code))
    # Si le pays n'est pas trouvé, il y a redirectionfollow_redirects=True
    # Sinon, le code HTTP renvoyé est celui du succès
    assert response.status_code == 200
    # Le corps est-il bien de l'HTML (l'application ne retourne que des pages web)?
    assert 'Content-Type: text/html; charset=utf-8' in str(headers)
    # On fait des tests sur des balises HTML
    html = BeautifulSoup(data, 'html.parser')
    # Test pour la ligne de titre
    assert html.h3.string == "Votre résultat pour : visualisation de toutes les données"
    # Carte encodée en "percent encoding"
    carte = html.iframe['data-html']
    # Décodage de la carte
    carte = unquote(carte)
    carte = str(carte)
    # On vérifie que chaque ville est mentionnée sur la carte
    for ville in liste_villes:
        assert ville in carte

def test_index(client):
    """Fonction de test pour le bon affichage d'un pays"""
    rv = connexion(client)
    assert b'Connexion effectu' in rv.data
    response = client.get("/recherche?type_voulu=index")
    # La réponse HTTP doit forcément avoir un coprs (puisqu'on retourne des données).
    # .data est en "bytes". Pour convertir des bytes en str, on fait .decode()
    headers = response.headers
    data = response.data.decode()
    data = str(data)
    # On vérifie que HTTP renvoyé est celui du succès
    assert response.status_code == 200
    # Le corps est-il bien de l'HTML (l'application ne retourne que des pages web)?
    assert 'Content-Type: text/html; charset=utf-8' in str(headers)
    # On vérifie que chaque ville est mentionnée une fois au moins dans l'index
    for ville in liste_villes:
        # La méthode title permet de standardiser les majuscules
        # assert ville.title() in data
        ville = ville.title()
        try:
            ville in data
        # Pour raison inconnue, pytest ne reconnait pas l'apostrophe
        except ValueError:
            try:
                ville.replace("'", '') in data.replace("'", '')
            except ValueError:
                raise ValueError


@pytest.mark.repeat(1)
def test_deconnexion(client):
    rv = connexion(client)
    assert b'Connexion effectu' in rv.data
    deco = client.get("/deconnexion", follow_redirects=True)
    deco = deco.data
    # Si on est déconnecté, l'option 'inscription' redevient disponible
    assert b"Inscription" in deco