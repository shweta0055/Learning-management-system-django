from django.contrib import admin
from .models import Enrollment, LessonProgress, Wishlist


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'progress', 'enrolled_at', 'amount_paid']
    list_filter = ['status']
    search_fields = ['user__email', 'course__title']
    readonly_fields = ['enrolled_at', 'completed_at', 'last_accessed', 'progress']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'watch_time', 'completed_at']
    list_filter = ['is_completed']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'added_at']
    search_fields = ['user__email', 'course__title']
