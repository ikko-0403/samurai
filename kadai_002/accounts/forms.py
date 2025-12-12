from django.contrib.auth.forms import UserCreationForm
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