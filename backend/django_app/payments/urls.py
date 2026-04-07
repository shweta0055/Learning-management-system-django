from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.CreateCheckoutSessionView.as_view(), name='checkout'),
    path('webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('coupon/validate/', views.ValidateCouponView.as_view(), name='validate_coupon'),
    path('my/', views.MyPaymentsView.as_view(), name='my_payments'),
]
