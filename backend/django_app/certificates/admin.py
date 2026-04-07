from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'certificate_id', 'issued_at', 'completion_percentage']
    search_fields = ['user__email', 'course__title', 'certificate_id']
    readonly_fields = ['certificate_id', 'issued_at']
    list_filter = ['course']
