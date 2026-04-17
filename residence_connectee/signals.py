from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from decimal import Decimal

@receiver(user_logged_in)
def attribuer_points_connexion(sender, request, user, **kwargs):
    # 'user' est ici directement votre objet Etudiant
    user.points_connexion += Decimal('0.25')
    user.save()