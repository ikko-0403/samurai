from django import forms
# ▼▼▼ 追加：ユーザー作成用に必要なインポート ▼▼▼
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
# ▲▲▲ 追加終わり ▲▲▲

from .models import Company, Category, Restaurant

# Userモデルを取得（カスタムユーザー対応）
User = get_user_model()

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "representative", "established_at", "zipcode", "address", "business"]
        labels = {
            "name": "会社名",
            "representative": "代表者名",
            "established_at": "設立日",
            "zipcode": "郵便番号",
            "address": "住所",
            "business": "事業内容",
        }
        # Bootstrap適用（CompanyFormにも適用しておくと綺麗です）
        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control'}),
            "representative": forms.TextInput(attrs={'class': 'form-control'}),
            "established_at": forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            "zipcode": forms.TextInput(attrs={'class': 'form-control'}),
            "address": forms.TextInput(attrs={'class': 'form-control'}),
            "business": forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_active']
        labels = {
            "name": "カテゴリ名",
            "is_active": "有効",
        }
        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control'}),
            "is_active": forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OwnerRestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            "name", "category", "image", "description",
            "price_min", "price_max",
            "open_time", "close_time", "holiday",
            "zipcode", "address", "tel",
        ]
        # ▼▼▼ ここでデザイン（Bootstrap）を当てる ▼▼▼
        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': '店舗名を入力'}),
            "category": forms.Select(attrs={'class': 'form-select'}), 
            "image": forms.ClearableFileInput(attrs={'class': 'form-control'}),
            "description": forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '店舗の魅力を入力してください'}),
            "price_min": forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            "price_max": forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            "open_time": forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            "close_time": forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            "holiday": forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: 月曜日'}),
            "zipcode": forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123-4567'}),
            "address": forms.TextInput(attrs={'class': 'form-control'}),
            "tel": forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # ビューから user を受け取る処理
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ログインユーザーの会社に紐付くカテゴリだけに絞り込み
        if user and hasattr(user, 'company') and user.company:
            self.fields['category'].queryset = Category.objects.filter(company=user.company, is_active=True)
        else:
            self.fields['category'].queryset = Category.objects.none()


# ▼▼▼ 追加：オーナー追加作成用のフォーム ▼▼▼
class OwnerMemberCreateForm(UserCreationForm):
    """
    既存のオーナーが、新しいオーナー（管理者）を作成するためのフォーム
    パスワード入力欄などはUserCreationFormが自動で作ってくれます。
    """
    class Meta:
        model = User
        fields = ('name', 'name_kana', 'email', 'zipcode', 'address', 'tel') 
        labels = {
            "name": "担当者名",
            "name_kana": "担当者名（カナ）",
            "email": "メールアドレス",
            "zipcode": "郵便番号",
            "address": "住所",
            "tel": "電話番号",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # フォームの全フィールドにBootstrapのクラスを一括適用
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'