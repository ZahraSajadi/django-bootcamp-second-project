from __future__ import annotations

from typing import Any
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.utils import timezone

from reservation.models import Reservation

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        timezone.now()

        reservations = Reservation.objects.filter(start_date__lte=timezone.now() + timezone.timedelta(hours=1))

        for reservation in reservations:
            team = reservation.team
            users = User.objects.filter(team=team)

            for user in users:
                subject = "Meeting time reminder..."
                message = f"{user.first_name} {user.last_name}, please note, reservation for your team's meeting will be held at {reservation.start_date}"
                recipient = user.email
                send_mail(message, subject, recipient)
