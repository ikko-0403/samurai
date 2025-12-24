from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Reservation
from .forms import ReservationForm
from restaurants.models import Restaurant


class ReservationListView(LoginRequiredMixin, ListView):
    """予約一覧"""
    model = Reservation
    template_name = 'reservations/reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 10
    
    def get_queryset(self):
        # ログイン中のユーザーの予約のみ
        return Reservation.objects.filter(user=self.request.user).select_related('restaurant')


class ReservationCreateView(LoginRequiredMixin, CreateView):
    """予約作成"""
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'
    success_url = reverse_lazy('reservations:reservation_list')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 店舗情報を取得
        restaurant_pk = self.kwargs.get('restaurant_pk')
        ctx['restaurant'] = get_object_or_404(Restaurant, pk=restaurant_pk)
        return ctx
    
    def get_form_kwargs(self):
        """フォームに店舗情報を渡す"""
        kwargs = super().get_form_kwargs()
        restaurant_pk = self.kwargs.get('restaurant_pk')
        restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        kwargs['restaurant'] = restaurant
        return kwargs
    
    def form_valid(self, form):
        # ユーザーと店舗を設定
        form.instance.user = self.request.user
        restaurant_pk = self.kwargs.get('restaurant_pk')
        form.instance.restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        
        # フォームのバリデーションで割り当てられた席を設定
        if hasattr(form, 'assigned_table') and form.assigned_table:
            form.instance.table = form.assigned_table
        
        messages.success(self.request, '予約を作成しました。')
        return super().form_valid(form)



class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    """予約編集"""
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'
    success_url = reverse_lazy('reservations:reservation_list')
    
    def get_queryset(self):
        # 自分の予約のみ、かつキャンセル・完了済みでないもの
        return Reservation.objects.filter(
            user=self.request.user,
            status__in=['pending', 'confirmed']
        )
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['restaurant'] = self.object.restaurant
        ctx['is_edit'] = True  # 編集モードフラグ
        return ctx
    
    def get_form_kwargs(self):
        """フォームに店舗情報を渡す"""
        kwargs = super().get_form_kwargs()
        kwargs['restaurant'] = self.object.restaurant
        return kwargs
    
    def form_valid(self, form):
        # フォームのバリデーションで割り当てられた席を設定
        if hasattr(form, 'assigned_table') and form.assigned_table:
            form.instance.table = form.assigned_table
        
        messages.success(self.request, '予約を更新しました。')
        return super().form_valid(form)



class ReservationCancelView(LoginRequiredMixin, View):
    """予約キャンセル"""
    
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
        # キャンセル済みでなければキャンセルする
        if reservation.status != 'cancelled':
            reservation.status = 'cancelled'
            reservation.save()
            messages.success(request, '予約をキャンセルしました。')
        return redirect('reservations:reservation_list')
