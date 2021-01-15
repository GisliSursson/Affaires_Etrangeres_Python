from flask import render_template, request
from .app import app
from .modeles.data_dict import codes_dict as data

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
        type = 'par pays'
        placeholder = 'Russie'
    if type_recherche == 'ville':
        type = 'par ville'
        placeholder = 'Rome'
    else:
        type = 'librement'
        placeholder = 'Votre recherche ici'
    return render_template("recherche.html", type=type, placeholder=placeholder, titre="Recherche", data=data, type_recherche=type_recherche)


