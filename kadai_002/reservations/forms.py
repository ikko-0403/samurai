from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Reservation
from restaurants.models import Table


class ReservationForm(forms.ModelForm):
    """予約フォーム"""
    
    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.restaurant = restaurant
        self.assigned_table = None  # 割り当てられた席を保存
    
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
    
    def _find_available_table(self, party_size, reservation_date, reservation_time):
        """
        指定された人数と日時に対して空いているテーブルを検索します。
        2時間制を考慮し、Best Fit（最小の定員で条件を満たす席）を返します。
        """
        if not self.restaurant:
            return None
        
        # 2時間後の終了時刻を計算
        start_datetime = datetime.combine(reservation_date, reservation_time)
        end_datetime = start_datetime + timedelta(hours=2)
        end_time = end_datetime.time()
        
        # 日をまたぐ場合の処理
        if end_datetime.date() > reservation_date:
            # 日をまたぐ場合は23:59:59まで
            from datetime import time as datetime_time
            end_time = datetime_time(23, 59, 59)
        
        # この店舗の全テーブルを取得（人数制約を満たすもののみ）
        available_tables = Table.objects.filter(
            restaurant=self.restaurant,
            capacity__gte=party_size  # 定員が予約人数以上
        ).order_by('capacity')  # Best Fit のため定員の小さい順
        
        # 各テーブルについて空き状況をチェック
        for table in available_tables:
            # このテーブルの予約をチェック（編集中の予約は除外）
            overlapping_reservations = Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
                status__in=['pending', 'confirmed']  # キャンセル・完了済みは除外
            )
            
            # 編集中の予約は除外
            if self.instance and self.instance.pk:
                overlapping_reservations = overlapping_reservations.exclude(pk=self.instance.pk)
            
            # 時間の重複をチェック
            is_available = True
            for existing_reservation in overlapping_reservations:
                existing_start = existing_reservation.reservation_time
                existing_end_datetime = datetime.combine(
                    reservation_date, 
                    existing_start
                ) + timedelta(hours=2)
                existing_end = existing_end_datetime.time()
                
                # 日をまたぐ場合の処理
                if existing_end_datetime.date() > reservation_date:
                    from datetime import time as datetime_time
                    existing_end = datetime_time(23, 59, 59)
                
                # 時間の重複チェック
                # 新規予約: [reservation_time, end_time]
                # 既存予約: [existing_start, existing_end]
                # 重複 = NOT (新規の終了 <= 既存の開始 OR 既存の終了 <= 新規の開始)
                if not (end_time <= existing_start or existing_end <= reservation_time):
                    is_available = False
                    break
            
            if is_available:
                return table  # Best Fit: 最初に見つかった（最小定員の）席を返す
        
        return None  # 空き席なし
    
    def clean(self):
        cleaned_data = super().clean()
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')
        party_size = cleaned_data.get('party_size')
        
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
            
            # 3. 空き席検索（2時間制を考慮）
            if party_size:
                available_table = self._find_available_table(
                    party_size, 
                    reservation_date, 
                    reservation_time
                )
                
                if not available_table:
                    raise ValidationError(
                        f'申し訳ございません。{party_size}名様でご利用いただける空席が見つかりませんでした。'
                        f'別の日時をお選びいただくか、お問い合わせください。'
                    )
                
                # 割り当てられた席を保存（viewで使用）
                self.assigned_table = available_table
        
        return cleaned_data
