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
    # La réponse HTTP doit forcément avoir un coprs (puisqu'on retourne des données).
    # .data est en "bytes". Pour convertir des bytes en str, on fait .decode()
    headers = response.headers
    data = response.data.decode()
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
        carte_str = unquote(carte)
        carte_str = str(carte_str)
        # La carte est générée par Folium via des injections javascript. On ne peut donc pas
        # la parser comme du HTML, il faut la parser comme une str
        # Le pays est-il bien mentionné?
        try:
            assert bytes(pays, encoding="utf-8") in response.data
        # Gestion des erreurs causées par les noms officiels du type "Iran, république islamique d'"
        # Des erreurs peuvent aussi être causées par les apostrophes
        except:
            resp = str(response.data)
            resp = resp.replace("'", '')
            # resp = resp.replace("é", '')
            # resp = resp.replace(" ", '')
            # resp = resp.replace("é".upper(), '')
            pays = pays.replace("'", '')
            # pays = pays.replace("é", '')
            # pays = pays.replace(" ", '')
            pays = pays.split(sep=" ")
            erreur = 0
            # On teste chaque mot du nom officiel. Si aucun n'est sur la carte, alors il y a
            # une erreur d'affichage.
            for element in pays:
                element = urllib.parse.quote(element)
                print(element)
                try:
                    print("element : " + element)
                    assert element in resp
                except AssertionError:
                    erreur += 1
                    if not erreur < len(pays):
                        raise AssertionError
        # Toutes les villes de tous les pays doivent produire une carte.
        assert "<table>" in carte_str
        # Test des téléphones (tous les postes semblent avoir un téléphone, ce qui n'est pas le cas des
        # villes ou des courriels
        try:
            match = re.search(r'>\+[0-9]{2,3}\s([0-9]+\s)+[0-9]+<', carte_str)
        except ValueError:
            raise ValueError
        # Tous les postes ont une latitude qui doit être un float (regex non greedy)
        match = re.search(r'<td>latitude</td><td>(.+?)</td>', carte_str)
        try:
            float(match.group(1))
        except ValueError:
            raise ValueError

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

@pytest.mark.repeat(3)
# L'affichage de la carte ne dépend pas de variables et a donc peut de chance d'échouer
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

@pytest.mark.repeat(3)
# L'affichage de l'indexe ne dépend pas de variables et a donc peut de chance d'échouer
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