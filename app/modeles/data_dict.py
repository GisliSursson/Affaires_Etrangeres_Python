import csv
import os
from ..app import chemin_actuel

# Script servant à charger les données du CSV dans un dict Python
# Un seul pays a été traité manuellement : Israel. Pour une raison que nous n'avons pas pu déterminer, le code utilisé
# pour ce pays dans les données du MEAE est "ILPS"
with open(os.path.join(chemin_actuel, "modeles", "codes_pays.csv"), "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    codes_dict = {}
    for row in reader:
        codes_dict[row[0].strip()] = row[1].strip()
