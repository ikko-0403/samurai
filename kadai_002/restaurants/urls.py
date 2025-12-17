from django.urls import path
from . import views
from .views import TopRedirectView, OwnerDashboardView, OwnerCompanyInfoView, OwnerCompanyDetailView, OwnerMemberDetailView


app_name = 'restaurants'

urlpatterns = [
    # --- 一般ユーザー向け ---
    path("", views.TopRedirectView.as_view(), name="top"),
    path("restaurants/", views.RestaurantListView.as_view(), name="restaurant_list"),
    path('<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('favorites/', views.MyFavoriteListView.as_view(), name='my_favorite_list'),
    path('favorite/<int:restaurant_pk>/', views.favorite_toggle, name='favorite_toggle'),

    # --- オーナー管理画面：ダッシュボード ---
    path("owner/dashboard/", views.OwnerDashboardView.as_view(), name="owner_dashboard"),

    # --- オーナー管理画面：店舗管理 ---
    path("owner/restaurants/", views.OwnerRestaurantListView.as_view(), name="owner_restaurant_list"),
    path("owner/restaurants/create/", views.OwnerRestaurantCreateView.as_view(), name="owner_restaurant_create"), # 新規作成
    path("owner/restaurants/<int:pk>/", views.OwnerRestaurantDetailView.as_view(), name="owner_restaurant_detail"), # 詳細
    path("owner/restaurants/<int:pk>/update/", views.OwnerRestaurantUpdateView.as_view(), name="owner_restaurant_update"), # 編集
    path("owner/restaurants/<int:pk>/delete/", views.OwnerRestaurantDeleteView.as_view(), name="owner_restaurant_delete"), # 削除

    # --- オーナー管理画面：カテゴリ管理 ---
    path("owner/categories/", views.OwnerCategoryListView.as_view(), name="owner_category_list"),
    path("owner/categories/add/", views.OwnerCategoryCreateView.as_view(), name="owner_category_create"),
    path("owner/categories/<int:pk>/edit/", views.OwnerCategoryUpdateView.as_view(), name="owner_category_edit"),
    path("owner/categories/<int:pk>/delete/", views.OwnerCategoryDeleteView.as_view(), name="owner_category_delete"),

    # --- オーナー管理画面：会社情報 ---
    path("owner/company/", views.OwnerCompanyDetailView.as_view(), name="company_detail"),
    path("owner/company/edit/", views.OwnerCompanyInfoView.as_view(), name="company_edit"),

    # --- オーナー管理画面：会員管理 ---
    path("owner/members/", views.OwnerMemberListView.as_view(), name="owner_member_list"),
    path("owner/members/<int:pk>/", views.OwnerMemberDetailView.as_view(), name="owner_member_detail"),

    path('owner/members/create/', views.OwnerMemberCreateView.as_view(), name='owner_member_create'),

    # ▼▼▼ CSV ▼▼▼
    path('owner/restaurants/export/', views.OwnerRestaurantCSVView.as_view(), name='owner_restaurant_csv'),
    path('owner/categories/export/', views.OwnerCategoryCSVView.as_view(), name='owner_category_csv'),
    path('owner/members/export/', views.OwnerMemberCSVView.as_view(), name='owner_member_csv'),
]