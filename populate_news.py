import os
import django
from datetime import datetime
from django.utils.timezone import make_aware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from residence_connectee.models import Actualite

def populate_news():
    print("Nettoyage de la base de données...")
    Actualite.objects.all().delete()

    news_data = [
        {
            "titre": "Déploiement des thermostats intelligents",
            "contenu": "Installation prévue dans le Bâtiment A. Ces appareils permettront de réduire la consommation d'énergie de 20%. Vous pourrez les piloter via cette plateforme.",
            "categorie": "RESIDENCE",
            # CHOISISSEZ VOTRE DATE ICI : (Année, Mois, Jour, Heure, Minute)
            "date_publication": make_aware(datetime(2026, 4, 15, 10, 30)) 
        },
        {
            "titre": "Maintenance du Wi-Fi",
            "contenu": "Coupure nocturne pour l'installation de la fibre optique. Le réseau sera indisponible de 02h à 05h du matin mercredi prochain.",
            "categorie": "URGENT",
            "date_publication": make_aware(datetime(2026, 4, 17, 14, 0))
        },
        {
            "titre": "Concours Éco-Résidence",
            "contenu": "Participez au défi de la chambre la plus écologique ! Une trottinette électrique est à gagner pour l'étudiant le plus économe en énergie.",
            "categorie": "LOCAL",
            "date_publication": make_aware(datetime(2026, 4, 10, 9, 15))
        }
        {
            "titre": "Menu hebdomadaire du RU",
            "contenu": "Le menu est maintenant disponible sur le site du crous.",
            "categorie": "CROUS",
            "date_publication": make_aware(datetime(2026, 4, 10, 9, 15))
        }
    ]

    for data in news_data:
        Actualite.objects.create(
            titre=data["titre"],
            contenu=data["contenu"],
            categorie=data["categorie"],
            date_publication=data["date_publication"] # On force la date choisie
        )
        print(f" -> Créé : {data['titre']} (Date: {data['date_publication']})")

if __name__ == '__main__':
    populate_news()