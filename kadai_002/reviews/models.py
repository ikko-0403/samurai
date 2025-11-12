from django.db import models
from django.conf import settings
from restaurants.models import Restaurant
from django.core.exceptions import ValidationError


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField() 
    title = models.CharField(max_length=100, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'restaurant'], name='unique_user_restaurant_review')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.restaurant.name} - {self.user.email} ({self.rating})'


    

    def clean(self):
        super().clean()
        if not (1 <= self.rating <= 5):
            raise ValidationError({'rating': '評価は1〜5で入力してください。'})