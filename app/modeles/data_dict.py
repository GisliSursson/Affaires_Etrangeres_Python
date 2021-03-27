import csv
import os
from ..app import chemin_actuel

# Script servant à charger les données du CSV dans un dict Python
pays = []
with open(os.path.join(chemin_actuel, "modeles", "codes_pays.csv"), "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    codes_dict = {}
    for row in reader:
        pays.append(row[0])
        # Traitement spécifique pour Israel dont le code ISO est 'IL' mais qui est codé comme 'ILPS' dans les données
        # du ministère. Un traitement manuel a également été fait pour rajouter le Kosovo.
        if row[1] == "IL":
            codes_dict[row[0].strip()] = "ILPS"
        # Traitement spécifique pour Saint-Marin dont le code ISO est 'SM' mais qui a le code 'SH' dans les
        # données du ministère. 'SH' est normalement le code des territoires britanniques de l'Atlantique sud.
        # Le seul moyen de régler cette incohérence a été de modifier manuellement le CSV des codes ISO et
        # de remplacer la valeur du code ici.
        elif row[1] == "SM":
            codes_dict[row[0].strip()] = "SH"
        else:
            codes_dict[row[0].strip()] = row[1].strip()