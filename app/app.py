import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# stockage du chemin vers le fichier courant (c'est à dire celui depuis lequel on exécute python)
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

# On configure le sel cryptographique
app.config['SECRET_KEY'] = "mon secret"
# On configure la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
# On initie l'extension
users = SQLAlchemy(app)
# On met en place la gestion d'utilisateur-rice-s
login = LoginManager(app)


# Import de la route vers l'accueil pour le démarrage
from .routes import accueil
