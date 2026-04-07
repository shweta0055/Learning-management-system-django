from django.db import models
from django.conf import settings
from courses.models import Course, Lesson


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.FloatField(default=0.0, help_text='Progress percentage 0-100')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    payment_id = models.CharField(max_length=255, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'enrollments'
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"

    def calculate_progress(self):
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            return 0.0
        completed = self.lesson_progress.filter(is_completed=True).count()
        return round((completed / total_lessons) * 100, 2)


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    watch_time = models.IntegerField(default=0, help_text='Seconds watched')
    completed_at = models.DateTimeField(null=True, blank=True)
    last_position = models.IntegerField(default=0, help_text='Last video position in seconds')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        return f"{self.enrollment.user.email} | {self.lesson.title} | {'✓' if self.is_completed else '○'}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlist'
        unique_together = ['user', 'course']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} ♡ {self.course.title}"
