from django import forms
from django.views.generic import View, ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Avg, Count, Exists, OuterRef, Q
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Restaurant, Category, Favorite, Company
from .forms import CompanyForm, CategoryForm, OwnerRestaurantForm, OwnerMemberCreateForm
from accounts.mixins import PaidMemberRequiredMixin
import csv
import urllib.parse
from django.http import HttpResponse
from django.utils import timezone


User = get_user_model()

class TopRedirectView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('restaurants:restaurant_list')

        user = request.user
        
        # オーナーなら dashboard へ
        if user.is_owner_member:
            return redirect('restaurants:owner_dashboard')

        # 一般ユーザーは店舗一覧へ
        return redirect('restaurants:prefecture_select')


class PrefectureSelectView(TemplateView):
    """都道府県選択画面"""
    template_name = 'restaurants/prefecture_select.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # データベースから都道府県のリストと店舗数を取得
        from django.db.models import Count
        prefectures = (Restaurant.objects
                      .values('prefecture')
                      .annotate(restaurant_count=Count('id'))
                      .order_by('prefecture'))
        
        ctx['prefectures'] = prefectures
        return ctx


class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'
    ordering = ['-id']  # 新しい順に表示

    def get_queryset(self):
        # 関連も一緒に取ってくる
        qs = (super().get_queryset()
              .select_related('category', 'company'))

        # ?category=1 みたいな値を取得して絞り込み
        category_id = self.request.GET.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)

        # --- カテゴリ名で検索 (?category_keyword=和食) ---
        category_keyword = self.request.GET.get('category_keyword')
        if category_keyword:
            qs = qs.filter(
                category__name__icontains=category_keyword
            )
        
        # --- 名前で検索（修正案で出たやつ） ---
        category_name = self.request.GET.get('category_name')
        if category_name:
            qs = qs.filter(category__name=category_name)

        # --- 都道府県で絞り込み ---
        prefecture = self.request.GET.get('prefecture')
        if prefecture:
            qs = qs.filter(prefecture=prefecture)

        # --- 店舗名で検索 ---
        keyword = self.request.GET.get('keyword')
        if keyword:
            qs = qs.filter(name__icontains=keyword)

        # いつでもお気に入り件数を付ける
        qs = qs.annotate(
            favorite_count=Count('favorites', distinct=True)
        )

        # ログイン済みなら「自分がお気に入り済みか」フラグも付ける
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=self.request.user,
                        restaurant=OuterRef('pk')
                    )
                )
            )

        # --- 並び替え機能 ---
        sort_by = self.request.GET.get('sort', 'default')
        if sort_by == 'price_low':
            # 価格が安い順
            qs = qs.order_by('price_min', 'id')
        elif sort_by == 'price_high':
            # 価格が高い順
            qs = qs.order_by('-price_max', '-id')
        else:
            # デフォルト：新しい順
            qs = qs.order_by('-id')

        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # カテゴリ一覧（重複なし）を取得して渡す
        all_categories = Category.objects.filter(is_active=True).values_list('name', flat=True)
        ctx["category_names"] = sorted(list(set(all_categories)))
        
        ctx["categories"] = Category.objects.all() # ID検索用（念のため残す）
        ctx["current_category_id"] = self.request.GET.get("category")
        ctx["keyword"] = self.request.GET.get("keyword", "")
        ctx["sort"] = self.request.GET.get("sort", "default")
        ctx["prefecture"] = self.request.GET.get("prefecture", "")
        return ctx



class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'restaurants/restaurant_detail.html'
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        r = self.object
        agg = r.reviews.aggregate(avg=Avg('rating'), cnt=Count('id'))
        ctx['avg_rating'] = agg['avg'] or 0
        ctx['review_count'] = agg['cnt'] or 0
        ctx['recent_reviews'] = r.reviews.select_related('user')[:3]
        if self.request.user.is_authenticated:
            ctx['my_review'] = r.reviews.filter(user=self.request.user).first()
            ctx["is_favorited"] = Favorite.objects.filter(user=self.request.user, restaurant=r).exists()
        else:
            ctx["is_favorited"] = False
        return ctx

    
class MyFavoriteListView(PaidMemberRequiredMixin, LoginRequiredMixin, ListView):
    template_name = "restaurants/my_favorite_list.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        return (Restaurant.objects
                .filter(favorites__user=self.request.user)
                .select_related("category", "company")
                .annotate(avg_rating=Avg("reviews__rating"),
                          review_count=Count("reviews"),
                          favorite_count=Count("favorites")))
    

@login_required
def favorite_toggle(request, restaurant_pk):
    # 有料会員チェック
    if not request.user.is_paid_member:
        messages.warning(
            request,
            'お気に入り機能は有料プラン会員限定です。有料プランに登録してご利用ください。'
        )
        # Ajaxリクエストの場合はリダイレクト情報を返す
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'redirect': reverse('accounts:payment_method')
            })
        return redirect('accounts:payment_method')
    
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        restaurant=restaurant
    )
    if not created:
        # すでにあれば削除 = 解除
        fav.delete()
        is_favorited = False
    else:
        is_favorited = True

    # お気に入り件数を取得
    favorite_count = restaurant.favorites.count()

    # Ajaxリクエストの場合はJSONレスポンスを返す
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'favorite_count': favorite_count
        })

    # 通常のリクエストの場合は元のページに戻す
    next_url = (
        request.GET.get('next')
        or request.META.get('HTTP_REFERER')
        or reverse('restaurants:restaurant_detail', args=[restaurant.pk])
    )
    return redirect(next_url)




class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "is_owner_member", False)

    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(self.request.get_full_path())    


class OwnerRestaurantListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurants/owner_restaurant_list.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        # 1. 基本：自分の会社の店舗だけに絞り込み
        qs = super().get_queryset().select_related("company", "category")
        user = self.request.user
        
        # 会社情報がないユーザーは何も見せない
        if not (hasattr(user, "company") and user.company):
             return Restaurant.objects.none()

        # 自社の店舗に絞り込み
        qs = qs.filter(company=user.company)

        # 2. 検索機能：キーワード（店舗名）
        keyword = self.request.GET.get('keyword')
        if keyword:
            qs = qs.filter(name__icontains=keyword)

        # 3. 検索機能：カテゴリ（ID指定）
        category_id = self.request.GET.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)

        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 検索フォームの「プルダウン」用に、自社のカテゴリ一覧を渡す
        if hasattr(user, "company") and user.company:
            ctx['categories'] = Category.objects.filter(company=user.company)
        else:
            ctx['categories'] = Category.objects.none()

        # 検索後にフォームに値を残すために、現在のパラメータも渡す
        ctx['keyword'] = self.request.GET.get('keyword', '')
        ctx['selected_category_id'] = self.request.GET.get('category', '')
        
        return ctx
# オーナーダッシュボードのビュー
class OwnerDashboardView(OwnerRequiredMixin, TemplateView):
    template_name = "restaurants/owner_dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx
    

# オーナーが新しい店舗を作成するビュー
class OwnerRestaurantCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = Restaurant
    form_class = OwnerRestaurantForm
    template_name = "restaurants/owner_restaurant_form.html"
    success_url = reverse_lazy("restaurants:owner_restaurant_list")

    def get_form_kwargs(self):
        """フォームの __init__ に user を渡すためのメソッド"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs

    def form_valid(self, form):
        if hasattr(self.request.user, 'company'):
             form.instance.company = self.request.user.company
        return super().form_valid(form)    

class OwnerCompanyDetailView(LoginRequiredMixin, OwnerRequiredMixin, TemplateView):
    """
    会社情報の閲覧ページ
    """
    template_name = "restaurants/owner_company_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["company"] = getattr(user, "company", None)
        return ctx

    
# オーナーが自分の店舗情報を編集するビュー

class OwnerCompanyInfoView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm 
    template_name = "restaurants/owner_company_form.html"
    success_url = reverse_lazy("restaurants:owner_dashboard")

    def get_object(self, queryset=None):
        user = self.request.user
        company, created = Company.objects.get_or_create(owner=user)
        return company



class OwnerRestaurantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Restaurant
    form_class = OwnerRestaurantForm 
    template_name = "restaurants/owner_restaurant_form.html"
    success_url = reverse_lazy("restaurants:owner_dashboard")
    
    def test_func(self):
        restaurant = self.get_object()
        user = self.request.user
        return (user.is_authenticated 
                and getattr(user, "is_owner_member", False)
                and hasattr(user, "company")
                and restaurant.company == user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs    
    
    def get_success_url(self):
        return reverse_lazy("restaurants:owner_dashboard")



class OwnerRestaurantDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Restaurant
    template_name = "restaurants/owner_restaurant_confirm_delete.html" # 確認画面
    success_url = reverse_lazy("restaurants:owner_restaurant_list")

    # 権限チェック（他人の店を消させないためのガード）
    def test_func(self):
        restaurant = self.get_object()
        user = self.request.user
        return (user.is_authenticated 
                and getattr(user, "is_owner_member", False)
                and hasattr(user, "company")
                and restaurant.company == user.company)


# オーナー用店舗詳細ビュー
class OwnerRestaurantDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Restaurant
    template_name = "restaurants/owner_restaurant_detail.html"
    context_object_name = "restaurant"

    # 権限チェック（自社の店舗のみ閲覧可能）
    def test_func(self):
        restaurant = self.get_object()
        user = self.request.user
        return (user.is_authenticated 
                and getattr(user, "is_owner_member", False)
                and hasattr(user, "company")
                and restaurant.company == user.company)


class OwnerCategoryMixin(UserPassesTestMixin):
    """オーナー自身の会社のカテゴリのみを操作可能にするMixin"""
    
    def test_func(self):
        user = self.request.user
        return (user.is_authenticated 
                and getattr(user, "is_owner_member", False)
                and hasattr(user, "company"))

    def get_queryset(self):
        return Category.objects.filter(company=self.request.user.company)

    def handle_no_permission(self):
        return redirect('restaurants:owner_dashboard')


# カテゴリ一覧
class OwnerCategoryListView(OwnerCategoryMixin, ListView):
    template_name = "restaurants/owner_category_list.html"
    model = Category
    context_object_name = "categories"

# カテゴリ作成
class OwnerCategoryCreateView(OwnerCategoryMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "restaurants/owner_category_form.html"
    success_url = reverse_lazy("restaurants:owner_category_list")

    def form_valid(self, form):
        form.instance.company = self.request.user.company
        return super().form_valid(form)

# カテゴリ編集
class OwnerCategoryUpdateView(OwnerCategoryMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "restaurants/owner_category_form.html"
    success_url = reverse_lazy("restaurants:owner_category_list")


# カテゴリ削除
class OwnerCategoryDeleteView(OwnerCategoryMixin, DeleteView):
    model = Category
    template_name = "restaurants/owner_category_confirm_delete.html"
    success_url = reverse_lazy("restaurants:owner_category_list")
    
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)



# 会員一覧
class OwnerMemberListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = User
    template_name = "restaurants/owner_member_list.html"
    context_object_name = "members"
    paginate_by = 10

    def get_queryset(self):
        # 1. 一般ユーザーのみ取得（オーナー・管理者・スタッフは除外）
        # 会社名を表示するなら select_related は必須（高速化のため）
        qs = User.objects.filter(
            is_owner_member=False,
            is_staff=False,
            is_superuser=False
        ).select_related('company')

        # 2. 検索機能
        keyword = self.request.GET.get('keyword')
        if keyword:
            keyword = keyword.strip()
            if keyword == "未設定":
                qs = qs.filter(name='')
            else:
                qs = qs.filter(
                    Q(name__icontains=keyword) | Q(email__icontains=keyword)
                )

        # 新しい順に表示
        return qs.order_by("-date_joined")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['keyword'] = self.request.GET.get('keyword', '')
        return ctx

class OwnerMemberDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = User
    template_name = "restaurants/owner_member_detail.html"
    context_object_name = "member"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx


# 1. 店舗一覧CSV出力
class OwnerRestaurantCSVView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # レスポンスの設定
        response = HttpResponse(content_type='text/csv')
        response.charset = 'utf-8'
        filename_ascii = "restaurant_list.csv"
        filename_utf8 = "店舗一覧.csv"
        response['Content-Disposition'] = 'attachment; filename="{}"; filename*=UTF-8\'\'{}'.format(
            filename_ascii, urllib.parse.quote(filename_utf8)
        )

        # UTF-8 BOMを追加（Excelで正しく開くため）
        response.write('\ufeff')
        
        writer = csv.writer(response)
        # ヘッダー行
        writer.writerow(['ID', '店舗名', 'カテゴリ', '住所', '電話番号'])

        # 1. まずは自分の会社の店舗に絞り込み
        if hasattr(request.user, 'company') and request.user.company:
            restaurants = Restaurant.objects.filter(company=request.user.company).select_related('category')
        else:
            return response  # 会社がない場合は空で返す

        # 2. 検索条件があればさらに絞り込む
        keyword = request.GET.get('keyword')
        if keyword:
            # 店舗名にキーワードが含まれるか
            restaurants = restaurants.filter(name__icontains=keyword)

        category_id = request.GET.get('category')
        if category_id:
            # カテゴリが選択されていれば一致するものを
            restaurants = restaurants.filter(category_id=category_id)

        # 3. データ書き込み
        for r in restaurants:
            writer.writerow([
                r.id, 
                r.name, 
                r.category.name if r.category else '', 
                r.address, 
                r.tel
            ])

        return response

# 2. カテゴリ一覧CSV出力
class OwnerCategoryCSVView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response.charset = 'utf-8'
        filename_ascii = "category_list.csv"
        filename_utf8 = "カテゴリ一覧.csv"
        response['Content-Disposition'] = 'attachment; filename="{}"; filename*=UTF-8\'\'{}'.format(filename_ascii, urllib.parse.quote(filename_utf8))

        # UTF-8 BOMを追加（Excelで正しく開くため）
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'カテゴリ名', '有効フラグ'])

        # 自分の会社のカテゴリ
        if hasattr(request.user, 'company'):
            categories = Category.objects.filter(company=request.user.company)
        else:
            categories = Category.objects.none()

        for c in categories:
            status = "有効" if c.is_active else "無効"
            writer.writerow([c.id, c.name, status])

        return response

# 3. 会員一覧CSV出力
class OwnerMemberCSVView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response.charset = 'utf-8'
        filename_ascii = "member_list.csv"
        filename_utf8 = "会員一覧.csv"
        response['Content-Disposition'] = 'attachment; filename="{}"; filename*=UTF-8\'\'{}'.format(filename_ascii, urllib.parse.quote(filename_utf8))
        
        # UTF-8 BOMを追加（Excelで正しく開くため）
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow(['ID', '名前', 'メールアドレス', '登録日'])
        members = User.objects.filter(
            is_owner_member=False,
            is_staff=False,
            is_superuser=False
        ).order_by('-date_joined')
        query = request.GET.get('keyword') 

        if query:
            # 半角スペースで区切られた場合のAND検索対応など、
            # 一覧画面の実装レベルに合わせる必要があるが、まずは基本形
            members = members.filter(
                Q(name__icontains=query) | Q(email__icontains=query)
            )

        # データ書き込み（メモリ節約のため iterator を使うのがベター）
        for m in members.iterator():
            joined_at = m.date_joined.strftime('%Y-%m-%d') if m.date_joined else ''
            writer.writerow([m.id, m.name, m.email, joined_at])

        return response
    
# オーナーメンバー増やす
class OwnerMemberCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = User
    form_class = OwnerMemberCreateForm
    template_name = 'restaurants/owner_member_create.html'
    success_url = reverse_lazy('restaurants:owner_member_list') # 作成後は一覧に戻る

    def form_valid(self, form):
        # フォームの入力値を取得（まだDBには保存しない）
        new_user = form.save(commit=False)
        
        # 1. 管理者権限を付与
        new_user.is_owner_member = True
        
        # 2. 会社IDの引継ぎ
        # ログイン中のオーナーと同じ会社に所属させる
        if hasattr(self.request.user, 'company'):
            new_user.company = self.request.user.company
            
        new_user.save()
        return super().form_valid(form)