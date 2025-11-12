# accounts/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .models import User
from .forms import SignUpForm


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')  # 登録後はログイン画面へ


class MyPageView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/mypage.html'
