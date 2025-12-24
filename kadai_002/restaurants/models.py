from django.conf import settings
from django.db import models


class Company(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_company",
        null=True,  # 既存データがあるなら最初は許可しておくと楽
        blank=True,
    )
    name = models.CharField(max_length=100)
    representative = models.CharField(max_length=100)
    established_at = models.DateField(null=True, blank=True)
    zipcode = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    business = models.TextField()  # 事業内容
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    company = models.ForeignKey(
        'Company',  # 文字列で指定しておくと定義順を気にせんでええけん無難や
        verbose_name="会社",
        on_delete=models.CASCADE, # 会社が消えたらカテゴリも消える
        null=True,  # 既存データがある場合に備えて一時的にTrue推奨
        blank=True
    )

    name = models.CharField("カテゴリ名", max_length=50)
    is_active = models.BooleanField("有効フラグ", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

class Restaurant(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='restaurants',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='restaurants',
    )
    # 🔽 ここがさっきの2つ目の Restaurant から持ってきた owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="my_restaurants",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='restaurant/', blank=True, null=True)
    description = models.TextField(blank=True)
    price_min = models.IntegerField()
    price_max = models.IntegerField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    prefecture = models.CharField('都道府県', max_length=10, default='愛知県')
    city = models.CharField('市区町村', max_length=50, default='名古屋市')
    zipcode = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    tel = models.CharField(max_length=20)
    holiday = models.CharField(max_length=50, blank=True)  # 定休日
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    """テーブル（座席）モデル"""
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='tables',
        verbose_name='店舗'
    )
    capacity = models.PositiveIntegerField(
        verbose_name='定員数',
        help_text='この席の定員数（2名、4名、8名など）'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        ordering = ['restaurant', 'capacity']
        verbose_name = 'テーブル'
        verbose_name_plural = 'テーブル'
        indexes = [
            models.Index(fields=['restaurant', 'capacity']),
        ]
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.capacity}名席 (ID:{self.id})"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "restaurant"], name="unique_favorite_user_restaurant"
            ),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["restaurant"]),
        ]

    def __str__(self):
        return f"{self.user.email} ❤️ {self.restaurant.name}"