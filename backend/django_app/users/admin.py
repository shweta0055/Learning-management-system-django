from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, InstructorProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    fieldsets = UserAdmin.fieldsets + (
        ('LMS Info', {'fields': ('role', 'bio', 'avatar', 'phone', 'date_of_birth', 'is_verified')}),
    )


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'total_students', 'total_courses', 'is_approved']
    list_filter = ['is_approved']
    search_fields = ['user__email', 'user__username']
    actions = ['approve_instructors']

    def approve_instructors(self, request, queryset):
        queryset.update(is_approved=True)
    approve_instructors.short_description = "Approve selected instructors"
