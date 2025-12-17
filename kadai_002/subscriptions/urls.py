from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('create/', views.SubscriptionCreateView.as_view(), name='create'),
    path('success/', views.SubscriptionSuccessView.as_view(), name='success'),
    path('cancelled/', views.SubscriptionCancelledView.as_view(), name='cancelled'),
    path('cancel/', views.SubscriptionCancelView.as_view(), name='cancel'),
]
