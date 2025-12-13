from django.db import models
from django.conf import settings
from restaurants.models import Restaurant


class Reservation(models.Model):
    """予約モデル"""
    
    STATUS_CHOICES = [
        ('pending', '予約確認中'),
        ('confirmed', '予約確定'),
        ('cancelled', 'キャンセル'),
        ('completed', '利用済み'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='予約者'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='店舗'
    )
    
    # 予約日時
    reservation_date = models.DateField(verbose_name='予約日')
    reservation_time = models.TimeField(verbose_name='予約時刻')
    
    # 人数
    party_size = models.PositiveIntegerField(verbose_name='人数')
    
    # ステータス
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='ステータス'
    )
    
    # 備考
    notes = models.TextField(blank=True, verbose_name='備考')
    
    # 監査用
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        ordering = ['-reservation_date', '-reservation_time']
        verbose_name = '予約'
        verbose_name_plural = '予約'
    
    def __str__(self):
        return f"{self.user.name} - {self.restaurant.name} ({self.reservation_date} {self.reservation_time})"
