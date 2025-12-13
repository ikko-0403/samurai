from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
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
    
    def form_valid(self, form):
        # ユーザーと店舗を設定
        form.instance.user = self.request.user
        restaurant_pk = self.kwargs.get('restaurant_pk')
        form.instance.restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
        return super().form_valid(form)


class ReservationCancelView(LoginRequiredMixin, View):
    """予約キャンセル"""
    
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
        # キャンセル済みでなければキャンセルする
        if reservation.status != 'cancelled':
            reservation.status = 'cancelled'
            reservation.save()
        return redirect('reservations:reservation_list')
