from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from ..app import users, login

# Définition de la table users dans la bd sqlite
class User(UserMixin, users.Model):
    user_id = users.Column(users.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    user_nom = users.Column(users.Text, nullable=False)
    user_login = users.Column(users.String(45), nullable=False, unique=True)
    user_email = users.Column(users.Text, nullable=False)
    user_password = users.Column(users.String(100), nullable=False)
    # Ajout colonne historique
    user_historique = users.Column(users.String(1000))

    @staticmethod
    def identification(login, motdepasse):
        """ Identifie un utilisateur. Si cela fonctionne, renvoie les données de l'utilisateurs.

        :param login: Login de l'utilisateur
        :param motdepasse: Mot de passe envoyé par l'utilisateur
        :returns: Si réussite, données de l'utilisateur. Sinon None
        :rtype: User or None
        """
        utilisateur = User.query.filter(User.user_login == login).first()
        if utilisateur and check_password_hash(utilisateur.user_password, motdepasse):
            return utilisateur
        return None

    @staticmethod
    def creer(login, email, nom, motdepasse):
        """ Crée un compte utilisateur-rice. Retourne un tuple (booléen, User ou liste).
        Si il y a une erreur, la fonction renvoie False suivi d'une liste d'erreur
        Sinon, elle renvoie True suivi de la donnée enregistrée

        :param login: Login de l'utilisateur-rice
        :param email: Email de l'utilisateur-rice
        :param nom: Nom de l'utilisateur-rice
        :param motdepasse: Mot de passe de l'utilisateur-rice (Minimum 6 caractères)

        """
        erreurs = []
        if not login or login == "":
            erreurs.append("Le login fourni est vide")
        if not email or email == "":
            erreurs.append("L'email fourni est vide")
        if not nom or nom == "":
            erreurs.append("Le nom fourni est vide")
        if not motdepasse or len(motdepasse) < 6:
            erreurs.append("Le mot de passe fourni est vide ou trop court")

        # On vérifie que personne n'a utilisé cet email ou ce login
        uniques = User.query.filter(
            users.or_(User.user_email == email, User.user_login == login)
        ).count()
        if uniques > 0:
            erreurs.append("L'email ou le login sont déjà inscrits dans notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs

        # On crée un utilisateur
        utilisateur = User(
            user_nom=nom,
            user_login=login,
            user_email=email,
            user_password=generate_password_hash(motdepasse)
        )

        try:
            # On l'ajoute au transport vers la base de données
            users.session.add(utilisateur)
            # On envoie le paquet
            users.session.commit()

            # On renvoie l'utilisateur
            return True, utilisateur
        except Exception as erreur:
            return False, [str(erreur)]

    def get_id(self):
        """ Retourne l'id de l'objet actuellement utilisé

        :returns: ID de l'utilisateur
        :rtype: int
        """
        return self.user_id

# Création de la table
users.create_all()
users.session.commit()

@login.user_loader
def trouver_utilisateur_via_id(identifiant):
    return User.query.get(int(identifiant))
