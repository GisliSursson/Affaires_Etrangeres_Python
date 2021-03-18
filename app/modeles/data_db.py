import json
import os
from ..app import chemin_actuel

# Attention : les données sources comportent de nombreuses erreurs. Par exemple, la représentation diplomatique
# pour le Bélize (qui se trouve normalement à Ciudad de Guatemala) a des coordonnées qui pointent vers le Salvador.
# Autre exemple, le code ISO attribué à Saint-Marin est faux. Il a été décidé de ne pas corriger
# ces problèmes dans les données sources à la main, mais plutôt d'essayer (dans la
# mesure du possible) de les compenser. De ce fait, les données sources pourront éventuellement être mises à jour.

# Transformation du fichier en objet Python-JSON
with open(os.path.join(chemin_actuel, "modeles", "data.json"), "r") as json_data:
    data = json.load(json_data)