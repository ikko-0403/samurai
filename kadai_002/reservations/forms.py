from django import forms
from .models import Reservation


class ReservationForm(forms.ModelForm):
    """予約フォーム"""
    
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
