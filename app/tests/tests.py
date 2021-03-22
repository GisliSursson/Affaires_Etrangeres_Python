# Ces tests ont pour but de vérifier que les données en entrée sont conformes au schéma des données originales
# fourni par le MEAE en cas de mise à jour.

# Librairie permettant de manipuler des fichiers
import json
# Librairie permettant d'interagir avec n'importe quel OS
import os
from os.path import dirname, abspath


print("Lancement des tests")


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

    Le JSON des données doit avoir l'architecture suivante : {"ab" : [{dict}, {dict}...], "cd": ...}
            :param doc: doc à tester
            :type doc: JSON file
    """
    print("Test de conformité du JSON par rapport au schéma de données")
    with open(doc) as doc:
        doc = json.load(doc)
        doc = dict(doc)
        for key, value in doc.items():
            if not isinstance(key, str) or not len(key) == 2:
                if key != "ilps":
                    print("Erreur ! Il y a un problème sur la clef : " + str(key))
            elif isinstance(value, list):
                for element in value:
                    if not isinstance(element, dict):
                        print("Erreur! Il y a un problème sur la chaîne clef/list/dict : " + str(key) + " / "
                              + str(value) + " / " + str(element))
            elif not isinstance(value, list):
                print("Erreur! Il y a un problème sur le couple clef/valeur : " + str(key) + " / " + str(value))
            else:
                print("Votre JSON est conforme au schéma.")

# Tests sur la validité des données (les tests ne doivent remonter aucune erreur s'il n'y a pas eu de
# mise à jour des données de la part de l'utilisateur).

# On parse tous les fichiers du dossier modeles en ne s'arrêtant que sur les JSON. Le seul JSON
# est normalement la "base de données" principale. Les tests ne sont pas censés faire s'arrêter l'application. Ils
# ne donnent que des messages dans le terminal au lancement de l'application.


# Dossier parent de l'actuel
dossier_parent = dirname(dirname(abspath(__file__)))
# Chemin vers le dossier "modeles" où se trouvent les données
chemin_modeles = os.path.abspath(os.path.join(dossier_parent, "modeles"))

for root, dirs, files in os.walk(chemin_modeles, topdown=True):
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

# Etant donné que les fonctions principales du fichier "routes.py" reposent sur des variables dépendantes de
# requêtes HTTP, nous avons déterminé qu'il n'était pas possible de les tester avec Travis.