from django.db import models

from apps.accounts.models import User

class Mood(models.Model):

    mood = models.CharField(max_length=20)
    created_on = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def record_mood(user, mood):
        return Mood.objects.create(user=user, mood=mood)
