from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'email',
            'name',
            'name_kana',
            'zipcode',
            'address',
            'tel',
        )

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # 管理画面用やから、一般用よりも項目を多くするで！
        fields = (
            'email',
            'name',
            'name_kana',
            'zipcode',
            'address',
            'tel',
            'company',
            'is_owner_member',
        )

    # ※ここはもしエラーが出たら書くくらいでOK（念のための保険）
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'company' in self.fields:
            self.fields['company'].required = False # 会社は空欄でもOKにする設定


class UserProfileForm(forms.ModelForm):
    """ユーザープロフィール編集フォーム"""
    
    class Meta:
        model = User
        fields = ['name', 'name_kana', 'zipcode', 'address', 'tel']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_kana': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: 123-4567'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'tel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例: 09012345678'}),
        }
        labels = {
            'name': '氏名',
            'name_kana': '氏名（カナ）',
            'zipcode': '郵便番号',
            'address': '住所',
            'tel': '電話番号',
        }