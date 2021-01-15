import csv
import os
from ..app import chemin_actuel

# Script servant à charger les données du CSV dans un dict Python
with open(os.path.join(chemin_actuel, "modeles", "codes_pays.csv"), "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    codes_dict = {}
    for row in reader:
        codes_dict[row[0].strip()] = row[1].strip()
