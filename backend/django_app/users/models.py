from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_instructor(self):
        return self.role == 'instructor'

    @property
    def is_student(self):
        return self.role == 'student'


class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    expertise = models.JSONField(default=list)
    rating = models.FloatField(default=0.0)
    total_students = models.IntegerField(default=0)
    total_courses = models.IntegerField(default=0)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'instructor_profiles'

    def __str__(self):
        return f"Profile: {self.user.email}"
