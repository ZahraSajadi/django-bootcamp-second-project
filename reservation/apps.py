from django.apps import AppConfig
from django.db.models.signals import post_delete


class ReservationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reservation"

    def ready(self):
        from .signals import (
            reservation_post_delete_cancell_email,
        )
        from .models import Reservation

        post_delete.connect(reservation_post_delete_cancell_email, sender=Reservation)
