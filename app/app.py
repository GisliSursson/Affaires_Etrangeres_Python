from flask import Flask


import os

# stockage du chemin vers le fichier courant
chemin_actuel = os.path.dirname(os.path.abspath(__file__))
# stockage du chemin vers les templates
templates = os.path.join(chemin_actuel, "templates")
# stockage du chemin vers les statics
statics = os.path.join(chemin_actuel, "static")


# Instanciation de l'application Flask dans la variable app. Appel des variables de chemin
#   définies ci-dessus.
app = Flask(
    "Mon_application",
    template_folder=templates,
    static_folder=statics
)

# Import de la route vers l'accueil pour le démarrage
from .routes import accueil
