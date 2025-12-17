from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from .forms import ReviewForm
from .models import Review
from restaurants.models import Restaurant
from django.db.models import Avg, Count
from accounts.mixins import PaidMemberRequiredMixin



class ReviewCreateView(PaidMemberRequiredMixin, LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        # 同一ユーザー×同一店舗は1件まで → 既にあれば編集へリダイレクト
        restaurant = get_object_or_404(Restaurant, pk=kwargs['restaurant_id'])
        existing = Review.objects.filter(user=request.user, restaurant=restaurant).first()
        if existing:
            return redirect('reviews:review_edit', pk=existing.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs['restaurant_id'])
        form.instance.user = self.request.user
        form.instance.restaurant = restaurant
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('restaurants:restaurant_detail', args=[self.object.restaurant_id])


class ReviewUpdateView(PaidMemberRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def get_queryset(self):
        # 自分のレビューのみ編集可能
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('restaurants:restaurant_detail', args=[self.object.restaurant_id])


class ReviewDeleteView(PaidMemberRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'reviews/review_confirm_delete.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('restaurants:restaurant_detail', args=[self.object.restaurant_id])
