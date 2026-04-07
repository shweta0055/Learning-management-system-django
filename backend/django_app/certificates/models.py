import uuid
from django.db import models
from django.conf import settings
from courses.models import Course


class Certificate(models.Model):
    certificate_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    completion_percentage = models.FloatField(default=100.0)

    class Meta:
        db_table = 'certificates'
        unique_together = ['user', 'course']
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate: {self.user.email} | {self.course.title}"

    @property
    def verification_url(self):
        return f"/api/certificates/verify/{self.certificate_id}/"
