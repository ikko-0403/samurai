from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import stripe

from .models import Subscription

# Stripe APIキーを設定
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionCreateView(LoginRequiredMixin, View):
    """有料会員登録（Stripe Checkoutセッション作成）"""
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        # 既に有料会員の場合はリダイレクト
        if user.is_paid_member:
            messages.warning(request, '既に有料会員に登録されています。')
            return redirect('accounts:payment_method')
        
        try:
            # Stripe顧客を作成または取得
            subscription_obj = Subscription.objects.filter(user=user).first()
            
            if subscription_obj and subscription_obj.stripe_customer_id:
                customer_id = subscription_obj.stripe_customer_id
            else:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=user.name,
                    metadata={'user_id': user.id}
                )
                customer_id = customer.id
                
                # Subscriptionオブジェクトを作成
                if not subscription_obj:
                    subscription_obj = Subscription.objects.create(
                        user=user,
                        stripe_customer_id=customer_id
                    )
                else:
                    subscription_obj.stripe_customer_id = customer_id
                    subscription_obj.save()
            
            # Stripe Checkoutセッションを作成
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.build_absolute_uri(reverse('subscriptions:success')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('subscriptions:cancelled')),
                metadata={'user_id': user.id}
            )
            
            return redirect(checkout_session.url)
            
        except Exception as e:
            messages.error(request, f'決済処理でエラーが発生しました: {str(e)}')
            return redirect('accounts:payment_method')


class SubscriptionSuccessView(LoginRequiredMixin, TemplateView):
    """決済成功後の処理"""
    template_name = 'subscriptions/subscription_success.html'
    
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        
        if session_id:
            try:
                # Checkoutセッションを取得
                session = stripe.checkout.Session.retrieve(session_id)
                
                # サブスクリプション情報を取得
                subscription_id = session.subscription
                subscription = stripe.Subscription.retrieve(subscription_id)
                
                # ユーザーのサブスクリプション情報を更新
                user = request.user
                subscription_obj, created = Subscription.objects.get_or_create(
                    user=user,
                    defaults={'stripe_customer_id': session.customer}
                )
                
                subscription_obj.stripe_subscription_id = subscription_id
                subscription_obj.status = 'active'
                subscription_obj.started_at = timezone.now()
                subscription_obj.next_billing_date = timezone.datetime.fromtimestamp(
                    subscription.current_period_end,
                    tz=timezone.get_current_timezone()
                )
                subscription_obj.save()
                
                # ユーザーの有料会員フラグを更新
                user.is_paid_member = True
                user.save()
                
                messages.success(request, '有料会員登録が完了しました！')
                
            except Exception as e:
                messages.error(request, f'サブスクリプション情報の更新中にエラーが発生しました: {str(e)}')
        
        return super().get(request, *args, **kwargs)


class SubscriptionCancelledView(LoginRequiredMixin, TemplateView):
    """決済キャンセル画面"""
    template_name = 'subscriptions/subscription_cancelled.html'
    
    def get(self, request, *args, **kwargs):
        messages.info(request, '決済がキャンセルされました。')
        return super().get(request, *args, **kwargs)


class SubscriptionCancelView(LoginRequiredMixin, View):
    """有料会員解約処理"""
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        if not user.is_paid_member:
            messages.warning(request, '有料会員ではありません。')
            return redirect('accounts:payment_method')
        
        try:
            # ユーザーのサブスクリプション情報を取得
            subscription_obj = Subscription.objects.get(user=user)
            
            # Stripeでサブスクリプションをキャンセル
            if subscription_obj.stripe_subscription_id:
                stripe.Subscription.delete(subscription_obj.stripe_subscription_id)
            
            # サブスクリプション情報を更新
            subscription_obj.status = 'canceled'
            subscription_obj.canceled_at = timezone.now()
            subscription_obj.save()
            
            # ユーザーの有料会員フラグを更新
            user.is_paid_member = False
            user.save()
            
            messages.success(request, '有料プランを解約しました。')
            
        except Subscription.DoesNotExist:
            messages.error(request, 'サブスクリプション情報が見つかりません。')
        except Exception as e:
            messages.error(request, f'解約処理でエラーが発生しました: {str(e)}')
        
        return redirect('accounts:payment_method')
