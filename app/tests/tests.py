# Ces tests ont pour but de vérifier que les données en entrée sont conformes au schéma des données originales
# fourni par le MEAE en cas de mise à jour.

# Librairie permettant de manipuler des fichiers
import json
# Librairie permettant d'interagir avec n'importe quel OS
import os
from os.path import dirname, abspath

def test_valide(doc):
    """ fonction testant si le JSON est valide
            :param doc: doc à tester
            :type doc: JSON file
    """
    print("Test de validité du JSON")
    with open(doc) as doc:
        try:
            doc = json.load(doc)
            print("Votre JSON est valide.")
        # Type d'erreur levée en cas de JSON malformé.
        except json.decoder.JSONDecodeError:
            print("Attention ! Votre document n'est pas du JSON valide.")

def test_schema(doc):
    """ Test si le document est conforme au schéma de données de data.gouv. Les clefs principales sont les codes
    ISO à 2 chiffres (sauf pour Israel) et les valeurs sont des dicionnaires. Etant donnée l'irrégularité des données
    et la manière dont est codée l'application, il n'est pas nécessaire de vérifier l'intégrités des dict pour chaque
    pays. De plus, cela pourrait aller à l'encontre du principe pythonien de EAFP (Easier to ask for forgiveness than permission)
    qui consiste à faire des itérations sans vérifications des données a priori et d'éventullement prévoir des erreurs.

            :param doc: doc à tester
            :type doc: JSON file
    """
    print("Test de conformité du JSOn par rapport au schéma de données")
    with open(doc) as doc:
        doc = json.load(doc)
        for key, value in doc.item():
            if not isinstance(key, str) or not len(key) == 2:
                if key != "ilps":
                    print("Erreur ! Il y a un problème sur la clef : " + str(key))
            elif not isinstance(value, dict):
                print("Erreur! Il y a un problème sur le couple clef/valeur : " + str(key) + " / " + str(value))

# Tests sur la validité des données (les tests ne doivent remonter aucune erreur s'il n'y a pas eu de
# mise à jour des données de la part de l'utilisateur).

# On parse tous les fichiers du dossier modeles en ne s'arrêtant que sur les JSON. Le seul JSON
# est normalement la "base de données" principale. Les tests ne sont pas censés faire s'arrêter l'application. Ils
# ne donnent que des messages dans le terminal au lancement de l'application.

for root, dirs, files in os.walk("../modeles", topdown=True):
    for name in files:
        filename = os.path.join(root, name)
        if not filename.endswith(".json"):
            print("{fichier} n'est pas du JSON".format(fichier=filename))
        else:
            doc_a_tester = filename
            print("Fichier en cours de test : {fichier}".format(fichier=doc_a_tester))
            # On appelle les fonctions de test sur le document à tester
            test_valide(doc_a_tester)
            test_schema(doc_a_tester)
