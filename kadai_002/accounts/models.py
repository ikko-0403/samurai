from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("メールアドレスは必須です。")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)#メアドとその他の情報
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
    def create_owner(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_owner_member', True)
        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    username = None  # 使わない（メールログインにする）
    email = models.EmailField(unique=True)

    # 会員基本情報
    company = models.ForeignKey('restaurants.Company', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=10)
    name_kana = models.CharField(max_length=10)
    zipcode = models.CharField(max_length=8)
    address = models.CharField(max_length=20)
    tel = models.CharField(max_length=11)
# companyIDとユーザー紐付け
    # 有料会員フラグ
    is_paid_member = models.BooleanField(default=False)
    # オーナーメンバーフラグ
    is_owner_member = models.BooleanField(default=False)



    # 監査用
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ログイン時に使うフィールド
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'name_kana', 'zipcode', 'address', 'tel']
    objects = CustomUserManager()

    def __str__(self):
        return self.email