# accounts/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',  LoginView.as_view(template_name='accounts/login.html'),name='login'),
    path('logout/',LogoutView.as_view(next_page='accounts:login'),name='logout'),
    path('signup/', views.SignUpView.as_view(),name='signup'),
    path('mypage/', views.MyPageView.as_view(),name='mypage'),
    
    # 会員情報
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('user/profile/edit/', views.UserProfileEditView.as_view(), name='user_profile_edit'),
    
    # お支払い・サブスクリプション
    path('user/payment/', views.PaymentMethodView.as_view(), name='payment_method'),
    path('user/subscription/cancel/', views.SubscriptionCancelView.as_view(), name='subscription_cancel'),
]
