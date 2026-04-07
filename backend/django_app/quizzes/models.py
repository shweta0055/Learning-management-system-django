from django.db import models
from django.conf import settings
from courses.models import Course, Lesson


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_limit = models.IntegerField(default=0, help_text='Time limit in minutes (0 = no limit)')
    passing_score = models.IntegerField(default=70, help_text='Passing percentage')
    max_attempts = models.IntegerField(default=3)
    shuffle_questions = models.BooleanField(default=False)
    show_answers_after = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quizzes'
        verbose_name_plural = 'quizzes'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    points = models.IntegerField(default=1)
    explanation = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'questions'
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} | Q{self.order}: {self.text[:50]}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'answers'
        ordering = ['order']

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text[:50]}"


class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timed_out', 'Timed Out'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.FloatField(default=0.0)
    total_points = models.IntegerField(default=0)
    earned_points = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.IntegerField(default=0, help_text='Time taken in seconds')

    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.email} | {self.quiz.title} | {self.score}%"


class QuizResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    text_response = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    points_earned = models.IntegerField(default=0)

    class Meta:
        db_table = 'quiz_responses'
        unique_together = ['attempt', 'question']


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    total_points = models.IntegerField(default=100)
    passing_score = models.IntegerField(default=60)
    attachment = models.FileField(upload_to='assignment_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignments'
        ordering = ['due_date']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('returned', 'Returned'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField()
    attachment = models.FileField(upload_to='submission_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='graded_submissions'
    )

    class Meta:
        db_table = 'assignment_submissions'
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.email} → {self.assignment.title}"
