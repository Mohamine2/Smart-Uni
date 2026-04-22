from residence_connectee.models import ObjetConnecte
from django.utils import timezone
import random

def run():
    for objet in ObjetConnecte.objects.all():
        if objet.type_objet == "Lampe":
            objet.marque = objet.marque or random.choice(["Philips", "Xiaomi", "Ikea"])
            objet.connectivite = objet.connectivite or random.choice(["Wi-Fi", "Zigbee"])
            objet.description = objet.description or "Lampe connectée pour éclairage intelligent."
        elif objet.type_objet == "Thermostat":
            objet.marque = objet.marque or random.choice(["Nest", "Tado", "Netatmo"])
            objet.connectivite = objet.connectivite or "Wi-Fi"
            objet.description = objet.description or "Thermostat intelligent pour la régulation thermique."
        elif objet.type_objet == "Prise":
            objet.marque = objet.marque or random.choice(["TP-Link", "Legrand", "Meross"])
            objet.connectivite = objet.connectivite or random.choice(["Wi-Fi", "Bluetooth"])
            objet.description = objet.description or "Prise connectée pour le contrôle à distance."

        if objet.niveau_batterie is None:
            objet.niveau_batterie = random.randint(30, 100)

        if not objet.derniere_interaction:
            objet.derniere_interaction = timezone.now()

        objet.save()

    print("Tous les objets ont été mis à jour.")