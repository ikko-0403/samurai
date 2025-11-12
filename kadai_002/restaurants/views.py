# restaurants/views.py
from django.views.generic import ListView, DetailView
from .models import Restaurant, Category
from django.db.models import Avg, Count


class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'
    ordering = ['-id']  # 新しい順に表示

        # ここで「カテゴリで絞り込み」
    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.request.GET.get('category')  # ?category=1 みたいな値を取得

        if category_id:
            qs = qs.filter(category_id=category_id)

        return qs

    # テンプレートにカテゴリ一覧も渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category_id'] = self.request.GET.get('category')
        return context



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
        return ctx
