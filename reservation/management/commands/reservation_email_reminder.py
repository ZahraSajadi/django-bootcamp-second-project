from typing import Any
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        timezone.now()
        # start_date <= timezone.now() + timezone.timedelta(hours=4)
        # query reservation = Reservation.object.filter(start_date__lte=timezone.now() + timezone.timedelta(hours=4)).all()
        # reservation.team
        # users = User.objects.filter(team=reservation.team).all()
        # for user in users
        # str(reservation)
        # reservation.room
        # send_mail(message,subject,recipent=user.email)
        pass
