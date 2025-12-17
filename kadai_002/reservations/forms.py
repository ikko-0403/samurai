from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Reservation


class ReservationForm(forms.ModelForm):
    """予約フォーム"""
    
    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.restaurant = restaurant
    
    class Meta:
        model = Reservation
        fields = ['reservation_date', 'reservation_time', 'party_size', 'notes']
        widgets = {
            'reservation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reservation_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'party_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ご要望やアレルギー情報などがあればご記入ください'
            })
        }
        labels = {
            'reservation_date': '予約日',
            'reservation_time': '予約時刻',
            'party_size': '人数',
            'notes': '備考'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')
        
        if not reservation_date or not reservation_time:
            return cleaned_data
        
        # 1. 過去日時チェック
        now = timezone.now()
        today = now.date()
        current_time = now.time()
        
        if reservation_date < today:
            raise ValidationError('過去の日付は予約できません。')
        
        if reservation_date == today and reservation_time <= current_time:
            raise ValidationError('現在時刻より前の時間は予約できません。')
        
        # 2. 営業時間チェック
        if self.restaurant:
            if reservation_time < self.restaurant.open_time:
                raise ValidationError(
                    f'営業時間外です。営業開始時刻は{self.restaurant.open_time.strftime("%H:%M")}です。'
                )
            
            if reservation_time > self.restaurant.close_time:
                raise ValidationError(
                    f'営業時間外です。営業終了時刻は{self.restaurant.close_time.strftime("%H:%M")}です。'
                )
        
        return cleaned_data
