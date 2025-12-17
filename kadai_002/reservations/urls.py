from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.ReservationListView.as_view(), name='reservation_list'),
    path('create/<int:restaurant_pk>/', views.ReservationCreateView.as_view(), name='reservation_create'),
    path('<int:pk>/edit/', views.ReservationUpdateView.as_view(), name='reservation_edit'),
    path('<int:pk>/cancel/', views.ReservationCancelView.as_view(), name='reservation_cancel'),
]
