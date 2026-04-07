from django.urls import path
from . import views

urlpatterns = [
    path('enroll/', views.EnrollView.as_view(), name='enroll'),
    path('my/', views.MyEnrollmentsView.as_view(), name='my_enrollments'),
    path('<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment_detail'),
    path('<int:enrollment_id>/progress/<int:lesson_id>/', views.LessonProgressUpdateView.as_view(), name='lesson_progress'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('course/<int:course_id>/students/', views.CourseStudentsView.as_view(), name='course_students'),
]
