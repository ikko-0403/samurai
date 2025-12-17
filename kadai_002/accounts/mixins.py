from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy


class PaidMemberRequiredMixin(UserPassesTestMixin):
    """有料会員限定機能用のMixin"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_paid_member
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            # 未ログインの場合はログインページへ
            return redirect('accounts:login')
        else:
            # 無料会員の場合は有料プラン登録ページへ
            messages.warning(
                self.request,
                'この機能は有料プラン会員限定です。有料プランに登録してご利用ください。'
            )
            return redirect('accounts:payment_method')
