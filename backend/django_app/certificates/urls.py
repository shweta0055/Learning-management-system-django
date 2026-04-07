from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.MyCertificatesView.as_view(), name='my_certificates'),
    path('generate/<int:course_id>/', views.GenerateCertificateView.as_view(), name='generate_certificate'),
    path('verify/<uuid:certificate_id>/', views.VerifyCertificateView.as_view(), name='verify_certificate'),
    path('download/<uuid:certificate_id>/', views.DownloadCertificateView.as_view(), name='download_certificate'),
]
