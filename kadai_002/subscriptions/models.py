from django.db import models
from django.conf import settings

class Subscription(models.Model):
    """サブスクリプション管理モデル"""
    
    STATUS_CHOICES = [
        ('active', 'アクティブ'),
        ('canceled', 'キャンセル済み'),
        ('past_due', '支払い遅延'),
        ('incomplete', '未完了'),
        ('trialing', 'トライアル中'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='ユーザー'
    )
    
    # Stripe関連情報
    stripe_customer_id = models.CharField(
        max_length=255,
        verbose_name='Stripe顧客ID',
        unique=True
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        verbose_name='StripeサブスクリプションID',
        unique=True,
        null=True,
        blank=True
    )
    
    # サブスクリプション情報
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='incomplete',
        verbose_name='ステータス'
    )
    
    # 料金情報
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=300.00,
        verbose_name='月額料金'
    )
    
    # 日付情報
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='開始日'
    )
    next_billing_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='次回請求日'
    )
    canceled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='キャンセル日'
    )
    
    # 監査用
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        verbose_name = 'サブスクリプション'
        verbose_name_plural = 'サブスクリプション'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_status_display()}"
    
    @property
    def is_active(self):
        """サブスクリプションがアクティブかどうか"""
        return self.status == 'active'
