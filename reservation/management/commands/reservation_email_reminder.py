from typing import Any
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.utils import timezone

from reservation.models import Reservation

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        reservations = Reservation.objects.filter(start_date__lte=timezone.now() + timezone.timedelta(hours=2))
        for reservation in reservations:
            team = reservation.team
            users = User.objects.filter(team=team)

            for user in users:
                subject = "Meeting time reminder..."
                message = f"""{user.first_name} {user.last_name}, please note,
                reservation for your team's meeting will be held
                from {reservation.start_date} to {reservation.end_date} in {reservation.room}"""
                recipient = user.email
                send_mail(subject, message, recipient_list=(recipient,), from_email="noreply@unchained.com")
