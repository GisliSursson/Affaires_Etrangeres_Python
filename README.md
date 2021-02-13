# "Réseau-diplo." : application de navigation dans les données du réseau diplomatique français

Devoir final réalisé dans le cadre du cours de Python de M. Clérice à l'Ecole nationale des chartes.

## Présentation

## Fonctionnalités

L'application permet de rechercher dans les données par pays et via une recherche libre. 

La recherche libre s'effectue via un moteur de recherche plein texte *pure Python*. La recherche plein texte renvoie des résultats pour les pays ou les villes. La recherche sur les villes n'est pas limitée aux capitales et peut également renvoyer des villes où se trouvent des représentations consulaires. 

Les résultats de recherche sont présentés sous forme de cartes. 

L'application gère également des comptes utilisateurs (inscription, connexion, mise à jour des données utilisateur, historique des recherches). 

## Installation et lancement

### Prérequis

Les packages suivants sont nécessaires. Lancez depuis votre terminal (Mac / Linux) la commande suivante qui vérifiera si les packages existent sur votre système et les installera sinon

```bash
sudo apt-get install python3 libfreetype6-dev python3-pip python3-virtualenv sqlite3
```

Clonez le présent *repository* dans un dossier de votre 

 ```bash
git clone https://github.com/GisliSursson/Affaires_Etrangeres_Python.git
```

Créez un environnement virtuel (dossier) dans lequel seront installées les librairies

```bash

virtualenv [chemin vers le dossier où vous voulez stocker l'environnement] -p python3
```

Activez l'environnement virtuel 

```bash
source [chemin vers le dossier d'environnement]/bin/activate
```

Dans le dossier où vous avez cloné le projet, installez ensuite les librairies nécessaires 

```bash
pip install -r requirements.txt
```

Pour désactiver l'environnement virtuel, tapez

```bash
deactivate 
```

### Lancement

Dans le dossier contenant le projet, lancez 

```bash
python3 run.py 
```

### Droits et licences

L'image de fond, issue du site [Pexel](https://www.pexels.com/fr-fr/), est libre de réutilisation.
La liste des codes pays à deux lettres (ISO 3166-1 alpha-2) est issue de [cette](http://documentation.abes.fr/sudoc/formats/CodesPays.htm) source. 



