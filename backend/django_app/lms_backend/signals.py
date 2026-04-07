"""
Django signals for automatic stat updates across the platform.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count


@receiver(post_save, sender='enrollments.Enrollment')
def update_course_student_count(sender, instance, created, **kwargs):
    """Update course total_students on enrollment create/delete."""
    if created:
        from courses.models import Course
        Course.objects.filter(pk=instance.course_id).update(
            total_students=sender.objects.filter(course_id=instance.course_id).count()
        )


@receiver(post_delete, sender='enrollments.Enrollment')
def update_course_student_count_on_delete(sender, instance, **kwargs):
    from courses.models import Course
    Course.objects.filter(pk=instance.course_id).update(
        total_students=sender.objects.filter(course_id=instance.course_id).count()
    )


@receiver(post_save, sender='courses.CourseReview')
def update_course_rating(sender, instance, **kwargs):
    """Recalculate course average rating when a review is saved."""
    from courses.models import Course
    course = instance.course
    stats = sender.objects.filter(course=course).aggregate(
        avg=Avg('rating'), count=Count('id')
    )
    Course.objects.filter(pk=course.pk).update(
        rating=round(stats['avg'] or 0, 2),
        total_ratings=stats['count'],
    )


@receiver(post_delete, sender='courses.CourseReview')
def update_course_rating_on_delete(sender, instance, **kwargs):
    from courses.models import Course
    course = instance.course
    stats = sender.objects.filter(course=course).aggregate(
        avg=Avg('rating'), count=Count('id')
    )
    Course.objects.filter(pk=course.pk).update(
        rating=round(stats['avg'] or 0, 2),
        total_ratings=stats['count'],
    )


@receiver(post_save, sender='enrollments.Enrollment')
def auto_generate_certificate_on_completion(sender, instance, **kwargs):
    """Auto-generate certificate when enrollment is completed."""
    if instance.status == 'completed' and instance.course.certificate_available:
        from certificates.models import Certificate
        from certificates.tasks import generate_certificate_pdf
        cert, created = Certificate.objects.get_or_create(
            user=instance.user,
            course=instance.course,
            defaults={'completion_percentage': instance.progress}
        )
        if created:
            generate_certificate_pdf.delay(cert.id)


@receiver(post_save, sender='users.User')
def create_instructor_profile(sender, instance, created, **kwargs):
    """Auto-create InstructorProfile when a user is assigned the instructor role."""
    if created and instance.role == 'instructor':
        from users.models import InstructorProfile
        InstructorProfile.objects.get_or_create(user=instance)
