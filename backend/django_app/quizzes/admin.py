from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, Assignment, AssignmentSubmission


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'passing_score', 'max_attempts', 'is_active']
    list_filter = ['is_active']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'question_type', 'points', 'order']
    inlines = [AnswerInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'passed', 'status', 'started_at']
    list_filter = ['passed', 'status']
    readonly_fields = ['score', 'passed', 'started_at', 'completed_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date', 'total_points']
    list_filter = ['course']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'status', 'score', 'submitted_at']
    list_filter = ['status']
    readonly_fields = ['submitted_at', 'graded_at']
