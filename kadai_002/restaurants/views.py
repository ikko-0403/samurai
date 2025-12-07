from django import forms
from django.views.generic import View, ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Avg, Count, Exists, OuterRef, Q
from django.contrib.auth import get_user_model
from .models import Restaurant, Category, Favorite, Company
from .forms import CompanyForm, CategoryForm, OwnerRestaurantForm
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
        return redirect('restaurants:restaurant_list')


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

        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # カテゴリ一覧（重複なし）を取得して渡す
        all_categories = Category.objects.filter(is_active=True).values_list('name', flat=True)
        ctx["category_names"] = sorted(list(set(all_categories)))
        
        ctx["categories"] = Category.objects.all() # ID検索用（念のため残す）
        ctx["current_category_id"] = self.request.GET.get("category")
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

    
class MyFavoriteListView(LoginRequiredMixin, ListView):
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
    restaurant = get_object_or_404(Restaurant, pk=restaurant_pk)
    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        restaurant=restaurant
    )
    if not created:
        # すでにあれば削除 = 解除
        fav.delete()

    # 元のページに戻す（next優先→Referer→なければ詳細ページ）
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
    
# ▼▼▼ 修正2: ここにあった class OwnerRestaurantForm を削除したぞな！ ▼▼▼

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


# views.py

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
        qs = super().get_queryset()
        keyword = self.request.GET.get('keyword')
        if keyword:
            keyword = keyword.strip()
        
        if keyword:
            # ▼▼▼ もし「未設定」と検索されたら、中身が空っぽの人を探す ▼▼▼
            if keyword == "未設定":
                qs = qs.filter(name='')
                
            else:
                # それ以外は普通に検索
                qs = qs.filter(
                    Q(name__icontains=keyword) | Q(email__icontains=keyword)
                )

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


class OwnerMemberCSVView(OwnerMemberListView):
    """
    検索結果をCSVでダウンロードするビュー
    OwnerMemberListView を継承してるから、get_queryset（検索絞り込み）がそのまま使える！
    """
    def get(self, request, *args, **kwargs):
        # 1. レスポンスの設定
        # 【重要】WindowsのExcelで開くなら 'Shift-JIS' (cp932) が必須！
        # utf-8だと文字化けしてクレームになるリスクがあるぞな。
        response = HttpResponse(content_type='text/csv; charset=cp932')
        
        # ファイル名を作成（例: members_20251205.csv）
        timestamp = timezone.now().strftime("%Y%m%d")
        filename = f"members_{timestamp}.csv"
        
        # 日本語ファイル名の文字化けを防ぐためのエンコード処理
        quoted_filename = urllib.parse.quote(filename)
        response['Content-Disposition'] = f'attachment; filename="{quoted_filename}"'

        # 2. CSVライターの作成
        writer = csv.writer(response)

        # 3. ヘッダー行（1行目）を書き込む
        header = ['ID', 'ユーザー名', 'メールアドレス', '登録日時']
        writer.writerow(header)

        # 4. データ行を書き込む
        # get_queryset() を呼ぶことで、画面と同じ「検索後のデータ」が取れる！
        queryset = self.get_queryset()

        for user in queryset:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.date_joined.strftime("%Y/%m/%d %H:%M"),
            ])

        return response