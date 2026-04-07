from django.urls import path
from . import views

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('my-courses/', views.InstructorCourseListView.as_view(), name='instructor_courses'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    path('<int:course_id>/sections/', views.SectionListCreateView.as_view(), name='section_list'),
    path('<int:course_id>/sections/<int:pk>/', views.SectionDetailView.as_view(), name='section_detail'),
    path('<int:course_id>/lessons/', views.LessonListCreateView.as_view(), name='lesson_list'),
    path('<int:course_id>/lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('<int:course_id>/reviews/', views.CourseReviewListCreateView.as_view(), name='review_list'),
    path('<int:course_id>/announcements/', views.AnnouncementListCreateView.as_view(), name='announcement_list'),
]
