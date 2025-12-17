# accounts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView
from .models import User
from .forms import SignUpForm, UserProfileForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user

        # オーナーならオーナーダッシュボードへ
        if getattr(user, "is_owner_member", False):
            return reverse_lazy("restaurants:owner_dashboard")

        # それ以外（普通の会員）は店舗一覧へ
        return reverse_lazy("restaurants:restaurant_list")




class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')  # 登録後はログイン画面へ


class MyPageView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/mypage.html'


class UserProfileView(LoginRequiredMixin, DetailView):
    """会員情報表示"""
    model = User
    template_name = 'accounts/user_profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        # ログイン中のユーザー自身の情報を表示
        return self.request.user


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """会員情報編集"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/user_profile_edit.html'
    success_url = reverse_lazy('accounts:user_profile')
    
    def get_object(self):
        # ログイン中のユーザー自身の情報を編集
        return self.request.user


class PaymentMethodView(LoginRequiredMixin, TemplateView):
    """お支払い方法管理"""
    template_name = 'accounts/payment_method.html'


class SubscriptionCancelView(LoginRequiredMixin, TemplateView):
    """有料プラン解約"""
    template_name = 'accounts/subscription_cancel.html'

