from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from .models import Certificate
from enrollments.models import Enrollment


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='user.get_full_name', read_only=True)
    verification_url = serializers.ReadOnlyField()

    class Meta:
        model = Certificate
        fields = ['id', 'certificate_id', 'user', 'course', 'course_title',
                  'student_name', 'issued_at', 'pdf_file', 'completion_percentage',
                  'verification_url']
        read_only_fields = ['id', 'certificate_id', 'issued_at']


class MyCertificatesView(generics.ListAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user).select_related('course')


class GenerateCertificateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        enrollment = get_object_or_404(
            Enrollment,
            user=request.user,
            course_id=course_id,
            status='completed'
        )
        cert, created = Certificate.objects.get_or_create(
            user=request.user,
            course=enrollment.course,
            defaults={'completion_percentage': enrollment.progress}
        )
        if created:
            from .tasks import generate_certificate_pdf
            generate_certificate_pdf.delay(cert.id)
        return Response(CertificateSerializer(cert).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class VerifyCertificateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, certificate_id):
        cert = get_object_or_404(Certificate, certificate_id=certificate_id)
        return Response({
            'valid': True,
            'certificate': CertificateSerializer(cert).data
        })


class DownloadCertificateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, certificate_id):
        cert = get_object_or_404(Certificate, certificate_id=certificate_id, user=request.user)
        if cert.pdf_file:
            return FileResponse(cert.pdf_file.open(), content_type='application/pdf')
        return Response({'detail': 'Certificate PDF not ready yet.'}, status=status.HTTP_404_NOT_FOUND)
