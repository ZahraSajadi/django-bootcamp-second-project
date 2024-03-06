from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    reserver_user = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True
    )
    team = models.ForeignKey("users.Team", on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reservation for {self.team.name} on {self.start_date.strftime('%Y-%m-%d')} at {self.start_date.strftime('%H:%M:%S')} by {self.reserver_user}"


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    room = models.ForeignKey("Room", on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user} on {self.created_at} in Room {self.room}"


class Rating(models.Model):
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    room = models.ForeignKey("Room", on_delete=models.CASCADE)

    def __str__(self):
        return f"Rating {self.value} by {self.user} for Room {self.room}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "room"], name="unique_rating")
        ]
