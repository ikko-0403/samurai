# accounts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView
from .models import User
from .forms import SignUpForm

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
