from django.contrib import admin
from .models import Category, Course, Section, Lesson, CourseReview, Announcement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'level', 'status', 'price', 'total_students', 'rating']
    list_filter = ['status', 'level', 'category', 'is_free']
    search_fields = ['title', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}
    actions = ['publish_courses', 'archive_courses']
    readonly_fields = ['total_students', 'rating', 'total_ratings', 'created_at', 'updated_at']

    def publish_courses(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='published', published_at=timezone.now())
    publish_courses.short_description = "Publish selected courses"

    def archive_courses(self, request, queryset):
        queryset.update(status='archived')
    archive_courses.short_description = "Archive selected courses"


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'course__title']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'content_type', 'video_duration', 'order', 'is_free_preview']
    list_filter = ['content_type', 'is_free_preview']
    search_fields = ['title']


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__email', 'course__title']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'created_at']
    search_fields = ['title', 'course__title']
