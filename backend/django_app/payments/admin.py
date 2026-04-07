from django.contrib import admin
from .models import Payment, Coupon


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount', 'currency', 'status', 'gateway', 'created_at']
    list_filter = ['status', 'gateway', 'currency']
    search_fields = ['user__email', 'course__title', 'gateway_payment_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count', 'max_uses', 'valid_to', 'is_active']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']
