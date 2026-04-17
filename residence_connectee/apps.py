from django.apps import AppConfig


class GestionConfig(AppConfig):
    name = 'residence_connectee'

    # Cette méthode est appelée quand Django a fini de charger l'application.
    def ready(self):
        # On importe le fichier signals ici pour "activer" les écouteurs (@receiver).
        import residence_connectee.signals
