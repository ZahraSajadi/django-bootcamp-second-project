from django.db import models
from django.contrib.auth import get_user_model

class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    description = models.TextField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Reservation(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, null=True)
    date = models.DateField()
    time = models.TimeField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Reservation for {self.user.team.name} on {self.date} at {self.time}'
    

class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)


class Rating(models.Model):
    value = models.IntegerField()
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
