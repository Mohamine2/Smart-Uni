from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from decimal import Decimal

@receiver(user_logged_in)
def attribute_login_points(sender, request, user, **kwargs):
    # 'user' is directly the Student object here
    user.login_points += Decimal('0.25')
    user.save()