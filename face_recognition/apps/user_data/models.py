from django.db import models, IntegrityError
from django.db.models import Count

from apps.accounts.models import User

class Mood(models.Model):

    mood = models.CharField(max_length=20)
    created_on = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def record_mood(user, mood):
        return Mood.objects.create(user=user, mood=mood)

    @staticmethod
    def guess_health(user):
        mood = Mood.objects.filter(user=user)
        max_points = 0
        points = 0
        moods = mood.distinct('mood')
        for x in mood:
            if x.mood.lower() in ['happy']:
                points += 2
                max_points += 2
            elif  x.mood.lower() in ['calm']:
                points += 1
                max_points += 1
            elif x.mood.lower() in ['confused', 'surprised']:
                points += 0
                max_points += 0
            elif x.mood.lower() in ['angry', 'disgusted']:
                points -= 1
                max_points += 1
            elif x.mood.lower() in ['sad']:
                points -= 2 
                max_points += 2
        avg = (points*100/max_points)
        return avg

class UserMeta(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    key = models.CharField(max_length=255)
    value = models.TextField(blank=True)

    class Meta:
        unique_together = (('user', 'key'))

    @staticmethod
    def get_key(user, key):
        try:
            return UserMeta.objects.get(key=key, user=user)
        except UserMeta.DoesNotExist:
            return None
    
    @staticmethod
    def save_key(user, key, value):
        try:
            return UserMeta.objects.create(key=key, user=user, value=value)
        except IntegrityError:
            return None

    @staticmethod
    def get_keys_for_user(user):
        return UserMeta.objects.filter(user=user)
