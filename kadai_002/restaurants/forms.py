from django import forms
from .models import Company, Category, Restaurant

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

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_active']
        labels = {
            "name": "カテゴリ名",
            "is_active": "有効",
        }

# 店舗登録・編集用フォーム（修正版）
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
            "category": forms.Select(attrs={'class': 'form-select'}), # セレクトボックス用
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
            # 会社未登録ならカテゴリは選べない（空にする）
            self.fields['category'].queryset = Category.objects.none()