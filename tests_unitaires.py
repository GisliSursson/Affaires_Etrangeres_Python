import random
import urllib
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup
from app.app import app, users
from app.modeles.utilisateurs import User
from unittest import TestCase
from random import randrange


liste_pays = ["Afghanistan", "Afrique du Sud", "Åland, Îles", "Albanie", "Algérie", "Allemagne", "Andorre",
    "Angola", "Anguilla", "Antarctique", "Antigua et Barbuda", "Antilles néerlandaises", "Arabie Saoudite", "Argentine",
    "Arménie", "Aruba", "Australie", "Autriche", "Azerbaïdjan", "Bahamas", "Bahrein", "Bangladesh", "Barbade", "Bélarus",
    "Belgique", "Bélize", "Bénin", "Bermudes", "Bhoutan", "Bolivie (État plurinational de)",
    "Bonaire, Saint-Eustache et Saba", "Bosnie-Herzégovine", "Botswana", "Bouvet, Ile", "Brésil", "Brunéi Darussalam",
    "Bulgarie", "Burkina Faso", "Burundi", "Cabo Verde", "Caïmans, Iles", "Cambodge", "Cameroun", "Canada", "Chili",
    "Chine", "Christmas, île", "Chypre", "Cocos/Keeling (Îles)", "Colombie", "Comores", "Congo",
    "Congo, République démocratique du", "Cook, Iles", "Corée, République de",
    "Corée, République populaire démocratique de", "Costa Rica", "Côte d'Ivoire", "Croatie", "Cuba",
    "Curaçao", "Danemark", "Djibouti", "Dominicaine, République", "Dominique", "Egypte", "El Salvador",
    "Emirats arabes unis", "Equateur", "Erythrée", "Espagne", "Estonie", "Etats-Unis d'Amérique", "Ethiopie",
    "Falkland/Malouines (Îles)", "Féroé, îles", "Fidji", "Finlande", "France", "Gabon", "Gambie", "Géorgie",
    "Géorgie du sud et les îles Sandwich du sud", "Ghana", "Gibraltar", "Grèce", "Grenade", "Groenland", "Guadeloupe",
    "Guam", "Guatemala", "Guernesey", "Guinée", "Guinée-Bissau", "Guinée équatoriale", "Guyana", "Guyane française",
    "Haïti", "Heard, Ile et MacDonald, îles", "Honduras", "Hong Kong", "Hongrie", "Île de Man",
    "Îles mineures éloignées des Etats-Unis", "Îles vierges britanniques", "Îles vierges des Etats-Unis",
    "Inde", "Indien (Territoire britannique de l'océan)", "Indonésie", "Iran, République islamique d'", "Iraq",
    "Irlande", "Islande", "Israël", "Italie", "Jamaïque", "Japon", "Jersey", "Jordanie", "Kazakhstan", "Kenya",
    "Kirghizistan", "Kiribati", "Koweït", "Lao, République démocratique populaire", "Lesotho", "Lettonie", "Liban",
    "Libéria", "Libye", "Liechtenstein", "Lituanie", "Luxembourg", "Macao", "Macédoine du nord", "Madagascar",
    "Malaisie", "Malawi", "Maldives", "Mali", "Malte", "Mariannes du nord, Iles", "Maroc", "Marshall, Iles", "Martinique",
    "Maurice", "Mauritanie", "Mayotte", "Mexique", "Micronésie, Etats Fédérés de", "Moldova, République de", "Monaco",
    "Mongolie", "Monténégro", "Montserrat", "Mozambique", "Myanmar", "Namibie", "Nauru", "Népal", "Nicaragua", "Niger",
    "Nigéria", "Niue", "Norfolk, Ile", "Norvège", "Nouvelle-Calédonie", "Nouvelle-Zélande", "Oman", "Ouganda",
    "Ouzbékistan", "Pakistan", "Palaos", "Palestine, Etat de", "Panama", "Papouasie-Nouvelle-Guinée", "Paraguay",
    "Pays-Bas", "Pays inconnu", "Pays multiples", "Pérou", "Philippines", "Pitcairn", "Pologne", "Polynésie française",
    "Porto Rico", "Portugal", "Qatar", "République arabe syrienne", "République centrafricaine", "Réunion", "Roumanie",
    "Royaume-Uni de Grande-Bretagne et d'Irlande du Nord", "Russie, Fédération de", "Rwanda", "Sahara occidental",
    "Saint-Barthélemy", "Saint-Kitts-et-Nevis", "Saint-Marin", "Saint-Martin (partie française)",
    "Saint-Martin (partie néerlandaise)", "Saint-Pierre-et-Miquelon", "Saint-Siège", "Saint-Vincent-et-les-Grenadines",
    "Sainte-Hélène, Ascension et Tristan da Cunha", "Sainte-Lucie", "Salomon, Iles", "Samoa", "Samoa américaines",
    "Sao Tomé-et-Principe", "Sénégal", "Serbie", "Seychelles", "Sierra Leone", "Singapour", "Slovaquie", "Slovénie",
    "Somalie", "Soudan", "Soudan du Sud", "Sri Lanka", "Suède", "Suisse", "Suriname", "Svalbard et île Jan Mayen",
    "Swaziland", "Tadjikistan", "Taïwan, Province de Chine", "Tanzanie, République unie de", "Tchad", "Tchécoslovaquie",
    "Tchèque, République", "Terres australes françaises", "Thaïlande", "Timor-Leste", "Togo", "Tokelau", "Tonga",
    "Trinité-et-Tobago", "Tunisie", "Turkménistan", "Turks-et-Caïcos (Îles)", "Turquie", "Tuvalu", "Ukraine", "URSS",
    "Uruguay", "Vanuatu", "Vatican", "Venezuela (République bolivarienne du)", "Viet Nam", "Viet Nam (Sud)",
    "Wallis et Futuna", "Yémen", "Yougoslavie", "Zaïre", "Zambie", "Zimbabwe"]

liste_villes = ["Kaboul", "Pretoria", "Cape Town", "Johannesburg", "Tirana", "Alger", "Annaba", "Oran",
    "Berlin", "Düsseldorf", "Francfort", "Hambourg", "Munich", "Sarrebruck", "Stuttgart", "Andorre-la-Vieille",
    "Luanda", "Castries", "None", "Djeddah", "Riyad", "Buenos Aires", "Erevan", "Canberra", "Sydney", "Vienne",
    "Bakou", "Panama", "Manama", "Dacca", "Bruxelles", "Guatemala", "Cotonou", "New Delhi", "Calcutta",
    "Minsk", "Rangoun", "La Paz", "Sarajevo", "Gaborone", "Recife", "Rio de Janeiro",
    "São Paulo", "Brasilia", "None", "Sofia", "Ouagadougou", " Ouagadougou", "Bujumbura", "Phnom Penh",
    "Yaoundé", "Douala", "Ottawa", "Montréal", "Québec", "Toronto", "Vancouver", "Moncton", "None", "Santiago",
    "None", "Shanghai", "Shenyang", "Hong Kong", "Wuhan", "Beijing", "Chengdu", "Canton", "Nicosie", "Bogotá",
    "Bogota", "Moroni", "Brazzaville", "Pointe-Noire", "None", "Séoul", "San José", "Abidjan", "Zagreb",
    "La Havane", "Copenhague", "Djibouti", "Le Caire", "Mancheya - Alexandrie", "Abou Dabi", "Dubaï", "Quito",
    "Asmara", "Madrid", "Barcelone", "Bilbao", "Tallinn", "Atlanta", "Boston", "Chicago",
    "Houston", "New Orleans", "Los Angeles", "Miami", "New York", "San Francisco", "Washington",
    "Addis Abeba", "Helsinki", "Libreville", "Dakar", "None", "Brufut", "Tbilissi", "Accra", "Athènes",
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
    "Dar es Salaam  ", "N'Djamena", "Bangkok", "Lomé", "Port d'Espagne", "Tunis", "Achgabat", "Ankara",
    "Istanbul", "Kiev", "Montevideo", "Caracas", "Hanoï", "Ho Chi-Minh Ville", "Lusaka", "Harare"]

# On fait un test pour chacune des grandes fonctions de l'application : la recherche par pays, par ville,
# l'affichage de la carte de toutes les données, l'affichage de l'index.

# Etant donné que toutes les routes de l'application retournent des render_template, les tests_ic sont faits sur
# les documents HTML retournés.

login_test = "example" + str(randrange(1000))
nom_test = "example_nom" + str(randrange(1000))
motdepasse_test = "blabla" + str(randrange(1000))
mail_test = "lala" + str(randrange(1000)) + "@a.fr"

class TestAppli(TestCase):

    def setUp(self):
        """Instanciation de l'app test"""
        self.app = app
        self.client = self.app.test_client()

    def inscription(self):
        """Inscription de l'utilisateur test"""
        r = self.client.post('/connexion', data={
            'login': login_test, 'motdepasse': motdepasse_test, 'nom': nom_test, 'email':mail_test})
        assert r.status_code == 200

    def connexion_test(self):
        """Connexion de l'utilisateur test"""
        r = self.client.post('/connexion', data={
            'login': login_test, 'motdepasse': motdepasse_test})
        assert r.status_code == 200

    def test_lieu(self):
        """Fonction de test pour le bon affichage d'un pays"""
        pays = random.choice(liste_pays)
        pays_url = urllib.parse.quote(pays)
        response = self.client.get("/resultats?query=" + pays_url+'"')
        # print(response)
        # La réponse HTTP doit forcément avoir un coprs (puisqu'on retourne des données).
        # .data est en "bytes". Pour convertir des bytes en str, on fait .decode()
        data = response.data.decode()
        # Le code HTTP renvoyé est-il celui du succès?
        self.assertEqual(
            response.headers["status"], 200
        )
        # Le corps est-il bien de l'HTML (on retourne tout via render_template)?
        self.assertEqual(
            response.headers["Content-Type"], "text/html; charset=utf-8"
        )
        html = BeautifulSoup(data, 'html.parser')
        # Test pour la balise 'title'
        self.assertEqual(html.title.name, pays)
        # Test pour la ligne de titre
        self.assertEqual(html.h3.name, "Votre résultat pour : " + pays)
        # Folium génère dynamiquement la carte avec du Javascript. Il faut donc tester une version str de la carte
        carte_bytes = html.find(style="width:100%;")
        carte_str = carte_bytes.get_root().render()
        table = carte_str.find_all('table')
        # Le pays est-il bien mentionné?
        self.assertIn(carte_str, pays)
        if 'Ambassade' in carte_str:
            self.assertIn(table, "<tr><td>nom</td><td>Ambassade de France en " + pays + "</td>")
        # Tous les postes ont une ville
        self.assertIn(table, "<td>ville</td>")

if __name__ == "__main__":
    unittest.main()


