import os.path

from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir
from .modeles.data_db import data as db

# Il a été déterminé que l'indexation via un moteur de recherche plein texte ne serait utile que pour la recherche
# via nom de ville.

# Définition du schéma du moteur de recherche. Le code du pays sera indexé et le contenu
# sera retourné en fonction du mot indexé (stored). "City" sert à l'indexation des noms de ville.
# "Name" sert au type de représentation. Le contenu de "Content" servira à produire le marqueur de la carte.
# Whoosh ne peut pas indexer des chaînes de caractères en UTF-8.
schema = Schema(city=TEXT, name=TEXT(stored=True), content=TEXT(stored=True))

# L'indexation n'est lancée que si le dossier "index" n'existe pas (la documentation Whoosh conseille de
# stocker l'index dans un dossier comme cela). L'indexation n'est donc lancée qu'une seule fois dans le cycle de vie
# de l'application installée en local. Si on refaisait l'indexation à chaque lancement de l'application, cela
# gaspillerait des ressources.
villes = []
if not os.path.exists("index"):
    # Ce print ne doit s'afficher que lorsque l'index est écrit, c'est-à-dire lors du 1er lancement de l'application,
    # ou lors d'un changement des données décidé par l'utilisateur. Logiquement, il apparaît lors du lancement des
    # tests.
    print("Création du dossier 'index'.")
    os.mkdir("index")
    index = create_in("index", schema)
    # On ouvre l'index vide (qui a maintenant un schéma) pour y ajouter ce qu'on veut indexer.
    index = open_dir("index")
    writer = index.writer()
    # Ajout des documents indexés selon les villes. Le contenu est le nom de la représentation diplomatique concernée.
    for key, value in db.items():
        for element in value:
            writer.add_document(city=u"{nom_ville}".format(nom_ville=element.get("ville")),
                                name=u"{nom_representation}".format(nom_representation=element.get("nom")),
                                content=u"{contenu}".format(contenu=element.copy()))
            villes.append(element.get("ville"))
    # On enregistre les modifications.
    writer.commit()
    indexation = index
# Variable finale pour import relatif
else:
    # Si le dossier index existe, on reprend simplement l'indexation qu'il contient
    indexation = open_dir("index")

