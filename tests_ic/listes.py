from app.modeles.data_dict import pays as liste_pays


# Listes qui serviront aux tests

# Suppression des espaces inutiles (on sait jamais)
for pays in liste_pays:
    pays = pays.strip()


# On a décidé d'hard coder la liste des villes. En effet, elle générée via Whoosh. Si on voulait
# la générer dynamiquement, il faudrait relancer l'indexation à chaque lancement de l'application.
# Si on ne fait pas ça, la liste "liste_villes" est perpétuellement vide, sauf lors du premier lancement
# de l'application.

liste_villes = ["Kaboul", "Pretoria", "Cape Town", "Johannesburg", "Tirana", "Alger", "Annaba", "Oran",
    "Berlin", "Düsseldorf", "Francfort", "Hambourg", "Munich", "Sarrebruck", "Stuttgart", "Andorre-la-Vieille",
    "Luanda", "Castries", "Djeddah", "Riyad", "Buenos Aires", "Erevan", "Canberra", "Sydney", "Vienne",
    "Bakou", "Panama", "Manama", "Dacca", "Bruxelles", "Guatemala", "Cotonou", "New Delhi", "Calcutta",
    "Minsk", "Rangoun", "La Paz", "Sarajevo", "Gaborone", "Recife", "Rio de Janeiro",
    "São Paulo", "Brasilia", "Sofia", "Ouagadougou", " Ouagadougou", "Bujumbura", "Phnom Penh",
    "Yaoundé", "Douala", "Ottawa", "Montréal", "Québec", "Toronto", "Vancouver", "Moncton", "Santiago",
    "Shanghai", "Shenyang", "Hong Kong", "Wuhan", "Beijing", "Chengdu", "Canton", "Nicosie", "Bogotá",
    "Bogota", "Moroni", "Brazzaville", "Pointe-Noire", "Séoul", "San José", "Abidjan", "Zagreb",
    "La Havane", "Copenhague", "Djibouti", "Le Caire", "Mancheya - Alexandrie", "Abou Dabi", "Dubaï", "Quito",
    "Asmara", "Madrid", "Barcelone", "Bilbao", "Tallinn", "Atlanta", "Boston", "Chicago",
    "Houston", "New Orleans", "Los Angeles", "Miami", "New York", "San Francisco", "Washington",
    "Addis Abeba", "Helsinki", "Libreville", "Dakar", "Brufut", "Tbilissi", "Accra", "Athènes",
    "Thessalonique", " Athènes", "Guatemala ciudad", "Conakry", "Malabo", "Bissao", "Paramaribo",
    "Port-au-Prince", "Tegucigalpa", " Budapest", "Wellington", "Suva", "Port-Vila", "Mumbai",
    "Pondichéry", "Bangalore", "Jakarta", "Bagdad", "Erbil", "Téhéran", "Dublin", "Reykjavik", "Tel-Aviv",
    "Haïfa", "Jérusalem", "Rome", "Naples", "Milan", "Kingston", "Tokyo", "Kyoto", "Amman", "Nour-Soultan",
    "Almaty", "Nairobi", "Bichkek", "Pristina", "Koweït", "Vientiane", "Riga", "Beyrouth", "Monrovia",
    "Tripoli", "Vilnius", "Luxembourg", "Skopje", "Antananarivo", "Kuala Lumpur", "Colombo", "Bamako",
    "La Valette", "Rabat - Chellah", "Agadir", "Casablanca", "Marrakech", "Tanger", "Fès", "Rabat",
    "Port-Louis", "Nouakchott", "Mexico", "Chisinau", "Monaco", "Oulan Bator", "Podgorica", "Maputo",
    "Windhoek", "Katmandou", "Managua", "Niamey", "Abuja", "Lagos", "Oslo", "Mascate", "Kampala",
    "Tachkent", "Islamabad", "Karachi", "Port Moresby", "Asunción", "La Haye", "Amsterdam", "Lima",
    "Makati city", "Manille", "Varsovie", "Cracovie", "Lisbonne", "Doha", "Bangui", "Kinshasa",
    "Saint-Domingue", "Prague", "Bucarest", "Londres", "Edimbourg", "Moscou", "Ekaterinbourg",
    "Saint-Pétersbourg", "Kigali", "San Salvador", "Belgrade", "Mahé", "Singapour", "Bratislava", "Ljubljana",
    "Khartoum", "Djouba", "Stockholm", "Berne", "Zurich", "Genève", "Damas", "Douchanbé", "Taipei",
    "Dar es Salaam ", "N'Djamena", "Bangkok", "Lomé", "Port d'Espagne", "Tunis", "Achgabat", "Ankara",
    "Istanbul", "Kiev", "Montevideo", "Caracas", "Hanoï", "Ho Chi-Minh Ville", "Lusaka", "Harare"]

