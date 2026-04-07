import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { coursesAPI, paymentsAPI } from '../services/api';
import { toast } from 'react-toastify';

export default function CheckoutPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [couponCode, setCouponCode] = useState('');
  const [couponResult, setCouponResult] = useState(null);
  const [checkingCoupon, setCheckingCoupon] = useState(false);

  const { data: course, isLoading } = useQuery({
    queryKey: ['course-checkout', courseId],
    queryFn: () => coursesAPI.list({ id: courseId }),
    select: (r) => r.data.results?.[0],
  });

  const checkoutMutation = useMutation({
    mutationFn: () => paymentsAPI.checkout(courseId, couponCode || undefined),
    onSuccess: (res) => {
      const { checkout_url, detail } = res.data;
      if (checkout_url) {
        window.location.href = checkout_url;
      } else if (detail) {
        toast.success(detail);
        navigate('/dashboard');
      }
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Checkout failed'),
  });

  const validateCoupon = async () => {
    if (!couponCode.trim()) return;
    setCheckingCoupon(true);
    try {
      const res = await paymentsAPI.validateCoupon(couponCode, courseId);
      setCouponResult(res.data);
      if (!res.data.valid) toast.error(res.data.detail);
      else toast.success(`Coupon applied! Save $${(res.data.original_price - res.data.discounted_price).toFixed(2)}`);
    } catch {
      toast.error('Failed to validate coupon');
    } finally {
      setCheckingCoupon(false);
    }
  };

  if (isLoading) return <div className="text-center py-20">Loading...</div>;

  const price = couponResult?.valid ? couponResult.discounted_price : parseFloat(course?.effective_price || 0);

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Checkout</h1>
      {course && (
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-1">{course.title}</h2>
          <p className="text-sm text-gray-500">by {course.instructor?.first_name} {course.instructor?.last_name}</p>
          <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
            <span className="text-gray-600">Course Price</span>
            <span className="font-semibold">${parseFloat(course.price).toFixed(2)}</span>
          </div>
          {couponResult?.valid && (
            <div className="flex items-center justify-between text-green-600 mt-2">
              <span className="text-sm">Coupon Discount</span>
              <span className="font-semibold">-${(couponResult.original_price - couponResult.discounted_price).toFixed(2)}</span>
            </div>
          )}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-200">
            <span className="font-bold text-gray-900">Total</span>
            <span className="font-bold text-xl text-primary-600">${price.toFixed(2)}</span>
          </div>
        </div>
      )}

      {/* Coupon */}
      <div className="card p-6 mb-6">
        <h3 className="font-semibold text-gray-900 mb-3">Have a coupon?</h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={couponCode}
            onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
            placeholder="Enter coupon code"
            className="input flex-1"
          />
          <button onClick={validateCoupon} disabled={checkingCoupon || !couponCode.trim()} className="btn-secondary px-4 py-2">
            {checkingCoupon ? '...' : 'Apply'}
          </button>
        </div>
      </div>

      <button
        onClick={() => checkoutMutation.mutate()}
        disabled={checkoutMutation.isPending}
        className="btn-primary w-full py-3 text-base"
      >
        {checkoutMutation.isPending ? 'Processing...' : `Pay $${price.toFixed(2)} with Stripe`}
      </button>
      <p className="text-center text-xs text-gray-400 mt-3">🔒 Secure payment powered by Stripe</p>
    </div>
  );
}
