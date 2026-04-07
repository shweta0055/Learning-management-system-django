from celery import shared_task
import os
from django.conf import settings


@shared_task
def generate_certificate_pdf(certificate_id):
    """Generate PDF certificate using ReportLab"""
    from .models import Certificate
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    import io
    from django.core.files.base import ContentFile

    try:
        cert = Certificate.objects.select_related('user', 'course', 'course__instructor').get(pk=certificate_id)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Background
        p.setFillColorRGB(0.98, 0.97, 0.93)
        p.rect(0, 0, width, height, fill=1)

        # Border
        p.setStrokeColorRGB(0.7, 0.6, 0.2)
        p.setLineWidth(4)
        p.rect(20, 20, width - 40, height - 40, fill=0)
        p.setLineWidth(1.5)
        p.rect(28, 28, width - 56, height - 56, fill=0)

        # Title
        p.setFont("Helvetica-Bold", 36)
        p.setFillColorRGB(0.2, 0.2, 0.5)
        p.drawCentredString(width / 2, height - 100, "Certificate of Completion")

        # Decorative line
        p.setStrokeColorRGB(0.7, 0.6, 0.2)
        p.setLineWidth(1.5)
        p.line(100, height - 115, width - 100, height - 115)

        # This is to certify
        p.setFont("Helvetica", 16)
        p.setFillColorRGB(0.3, 0.3, 0.3)
        p.drawCentredString(width / 2, height - 155, "This is to certify that")

        # Student name
        student_name = cert.user.get_full_name() or cert.user.username
        p.setFont("Helvetica-Bold", 28)
        p.setFillColorRGB(0.1, 0.1, 0.4)
        p.drawCentredString(width / 2, height - 200, student_name)

        # Line under name
        name_width = p.stringWidth(student_name, "Helvetica-Bold", 28)
        p.setStrokeColorRGB(0.3, 0.3, 0.3)
        p.setLineWidth(1)
        p.line(width / 2 - name_width / 2, height - 208, width / 2 + name_width / 2, height - 208)

        # Has completed
        p.setFont("Helvetica", 16)
        p.setFillColorRGB(0.3, 0.3, 0.3)
        p.drawCentredString(width / 2, height - 240, "has successfully completed the course")

        # Course name
        p.setFont("Helvetica-Bold", 22)
        p.setFillColorRGB(0.1, 0.4, 0.1)
        p.drawCentredString(width / 2, height - 280, cert.course.title)

        # Date
        p.setFont("Helvetica", 13)
        p.setFillColorRGB(0.4, 0.4, 0.4)
        date_str = cert.issued_at.strftime("%B %d, %Y")
        p.drawCentredString(width / 2, height - 330, f"Issued on {date_str}")

        # Certificate ID
        p.setFont("Helvetica", 9)
        p.setFillColorRGB(0.6, 0.6, 0.6)
        p.drawCentredString(width / 2, 50, f"Certificate ID: {cert.certificate_id}")

        # Instructor signature area
        instructor_name = cert.course.instructor.get_full_name() or cert.course.instructor.username
        p.setFont("Helvetica-Bold", 12)
        p.setFillColorRGB(0.2, 0.2, 0.2)
        p.drawCentredString(width / 2, 100, instructor_name)
        p.line(width / 2 - 80, 108, width / 2 + 80, 108)
        p.setFont("Helvetica", 10)
        p.drawCentredString(width / 2, 90, "Instructor")

        p.showPage()
        p.save()

        buffer.seek(0)
        filename = f"certificate_{cert.certificate_id}.pdf"
        cert.pdf_file.save(filename, ContentFile(buffer.read()), save=True)

        return f"Certificate {certificate_id} generated successfully"

    except Exception as e:
        return f"Error generating certificate {certificate_id}: {str(e)}"
