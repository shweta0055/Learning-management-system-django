from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Payment, Coupon
from courses.models import Course
from enrollments.models import Enrollment
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'course', 'course_title', 'amount', 'currency',
                  'status', 'gateway', 'gateway_payment_id', 'receipt_url', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'gateway_payment_id', 'receipt_url', 'created_at']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'is_active']


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        coupon_code = request.data.get('coupon_code')
        course = get_object_or_404(Course, pk=course_id, status='published')

        if Enrollment.objects.filter(user=request.user, course=course).exists():
            return Response({'detail': 'Already enrolled.'}, status=status.HTTP_400_BAD_REQUEST)

        amount = course.effective_price

        # Apply coupon
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid():
                    if coupon.discount_type == 'percentage':
                        amount = amount * (1 - coupon.discount_value / 100)
                    else:
                        amount = max(0, amount - coupon.discount_value)
            except Coupon.DoesNotExist:
                return Response({'detail': 'Invalid coupon code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle free courses
        if amount == 0 or course.is_free:
            payment = Payment.objects.create(
                user=request.user, course=course, amount=0,
                status='completed', gateway='free'
            )
            Enrollment.objects.get_or_create(
                user=request.user, course=course,
                defaults={'amount_paid': 0, 'payment_id': str(payment.id)}
            )
            return Response({'detail': 'Enrolled successfully (free course).', 'payment': PaymentSerializer(payment).data})

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': course.title},
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{request.scheme}://{request.get_host()}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{request.scheme}://{request.get_host()}/payment/cancel",
                metadata={'course_id': course_id, 'user_id': request.user.id}
            )
            payment = Payment.objects.create(
                user=request.user, course=course, amount=amount,
                gateway='stripe', gateway_order_id=session.id, status='pending'
            )
            return Response({'checkout_url': session.url, 'session_id': session.id, 'payment_id': payment.id})
        except stripe.error.StripeError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            course_id = session['metadata'].get('course_id')
            user_id = session['metadata'].get('user_id')
            try:
                payment = Payment.objects.get(gateway_order_id=session['id'])
                payment.status = 'completed'
                payment.gateway_payment_id = session.get('payment_intent', '')
                payment.receipt_url = session.get('receipt_url', '')
                payment.save()
                Enrollment.objects.get_or_create(
                    user_id=user_id, course_id=course_id,
                    defaults={'amount_paid': payment.amount, 'payment_id': str(payment.id)}
                )
            except Payment.DoesNotExist:
                pass
        return Response({'status': 'ok'})


class ValidateCouponView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        course_id = request.data.get('course_id')
        try:
            coupon = Coupon.objects.get(code=code)
            if not coupon.is_valid():
                return Response({'valid': False, 'detail': 'Coupon is expired or exhausted.'})
            course = get_object_or_404(Course, pk=course_id)
            original = float(course.effective_price)
            if coupon.discount_type == 'percentage':
                discounted = original * (1 - float(coupon.discount_value) / 100)
            else:
                discounted = max(0, original - float(coupon.discount_value))
            return Response({
                'valid': True,
                'discount_type': coupon.discount_type,
                'discount_value': str(coupon.discount_value),
                'original_price': original,
                'discounted_price': round(discounted, 2),
            })
        except Coupon.DoesNotExist:
            return Response({'valid': False, 'detail': 'Coupon not found.'})


class MyPaymentsView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('course')
