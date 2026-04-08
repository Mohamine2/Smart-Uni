import os
import django
from faker import Faker
import random
import string

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from residence_connectee.models import Etudiant 

fake = Faker('fr_FR') # On utilise la version française pour des noms cohérents

def generate_random_password(length=12):
    """Génère un mot de passe robuste mélangeant lettres et chiffres"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def populate(n=20):
    for i in range(n):
        # Génération des données de base
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Création d'un username unique (ex: jdupont_42)
        username = f"{first_name[0].lower()}{last_name.lower()}_{random.randint(10, 99)}"
        email = f"{username}@student.cytech.fr"

        # Numéro de téléphonee
        phone = fake.phone_number()

        student_id = str(random.randint(20000000, 29999999)) # Numéro à 8 chiffres

        age = random.randint(17, 26) # La tranche d'âge classique à CY Tech
        sex = random.choice(['M', 'F', 'A'])

        raw_password = generate_random_password()

        # On utilise get_or_create pour ne pas recréer les mêmes si on relance
        user, created = Etudiant.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone,
                'student_id': student_id,
                'age': age,
                'sex': sex,
                'is_active': True,
            }
        )

        if created:
            # IMPORTANT : On définit un mot de passe par défaut
            # Django va le HASHER automatiquement ici
            user.set_password(raw_password)
            user.save()
            print(f"Étudiant créé : {username} | Tel : {phone}")
        else:
            print(f"L'étudiant {username} existe déjà.")

if __name__ == '__main__':
    print("Début du peuplement...")
    populate(20)
    print("Opération terminée avec succès !")