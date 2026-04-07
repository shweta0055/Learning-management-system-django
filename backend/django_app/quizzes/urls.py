from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/', views.QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('create/', views.QuizCreateView.as_view(), name='quiz_create'),
    path('<int:quiz_id>/submit/', views.SubmitQuizView.as_view(), name='submit_quiz'),
    path('<int:quiz_id>/my-attempts/', views.MyQuizAttemptsView.as_view(), name='my_attempts'),
    path('assignments/course/<int:course_id>/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<int:assignment_id>/submit/', views.SubmitAssignmentView.as_view(), name='submit_assignment'),
    path('assignments/<int:assignment_id>/submissions/', views.AssignmentSubmissionsView.as_view(), name='assignment_submissions'),
    path('submissions/<int:submission_id>/grade/', views.GradeSubmissionView.as_view(), name='grade_submission'),
]
