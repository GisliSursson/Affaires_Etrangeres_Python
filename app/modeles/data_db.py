import json
import os
from ..app import chemin_actuel

with open(os.path.join(chemin_actuel, "modeles", "data.json"), "r") as json_data:
    data = json.load(json_data)