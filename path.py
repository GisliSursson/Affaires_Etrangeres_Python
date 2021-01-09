import os

# A mettre à jour

chemin_actuel = os.path.dirname(os.path.abspath(__file__))
print(chemin_actuel)

templates = os.path.join(chemin_actuel, "gazetteer", "templates")
print(templates)
