"""
Celery tasks for the LMS platform.
Covers: email notifications, periodic analytics updates, cleanup jobs.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# ─── Email Notifications ─────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_enrollment_confirmation(self, user_id: int, course_id: int):
    """Send enrollment confirmation email to a student."""
    try:
        from django.contrib.auth import get_user_model
        from courses.models import Course

        User = get_user_model()
        user = User.objects.get(pk=user_id)
        course = Course.objects.get(pk=course_id)

        send_mail(
            subject=f"🎓 You're enrolled in {course.title}!",
            message=f"""
Hi {user.first_name or user.username},

Welcome to "{course.title}"! You're now enrolled and ready to start learning.

Start learning: http://localhost:3000/learn/{course.slug}

Happy learning,
The LearnHub Team
            """.strip(),
            from_email=settings.EMAIL_HOST_USER or 'noreply@learnhub.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Enrollment email sent to {user.email} for course {course.title}")
    except Exception as exc:
        logger.error(f"Failed to send enrollment email: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_course_completion_email(self, user_id: int, course_id: int):
    """Send course completion email with certificate link."""
    try:
        from django.contrib.auth import get_user_model
        from courses.models import Course
        from certificates.models import Certificate

        User = get_user_model()
        user = User.objects.get(pk=user_id)
        course = Course.objects.get(pk=course_id)

        cert = Certificate.objects.filter(user=user, course=course).first()
        cert_url = f"http://localhost:3000/certificates" if cert else ""

        send_mail(
            subject=f"🏅 Congratulations! You completed {course.title}",
            message=f"""
Hi {user.first_name or user.username},

Congratulations on completing "{course.title}"! 🎉

{"Your certificate is ready: " + cert_url if cert_url else ""}

Keep up the amazing work,
The LearnHub Team
            """.strip(),
            from_email=settings.EMAIL_HOST_USER or 'noreply@learnhub.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Completion email sent to {user.email}")
    except Exception as exc:
        logger.error(f"Failed to send completion email: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def send_quiz_result_email(self, user_id: int, quiz_attempt_id: int):
    """Send quiz result notification."""
    try:
        from django.contrib.auth import get_user_model
        from quizzes.models import QuizAttempt

        User = get_user_model()
        user = User.objects.get(pk=user_id)
        attempt = QuizAttempt.objects.select_related('quiz').get(pk=quiz_attempt_id)

        status_word = "passed" if attempt.passed else "did not pass"
        send_mail(
            subject=f"Quiz Result: {attempt.quiz.title}",
            message=f"""
Hi {user.first_name or user.username},

You {status_word} the quiz "{attempt.quiz.title}" with a score of {attempt.score:.1f}%.

{"Great job! 🎉" if attempt.passed else f"The passing score is {attempt.quiz.passing_score}%. You can try again!"}

LearnHub Team
            """.strip(),
            from_email=settings.EMAIL_HOST_USER or 'noreply@learnhub.com',
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as exc:
        logger.error(f"Failed to send quiz result email: {exc}")


# ─── Periodic Tasks ──────────────────────────────────────────────────────────

@shared_task
def update_instructor_stats():
    """
    Periodic task: refresh instructor profile totals.
    Schedule: every 6 hours via Celery Beat.
    """
    from users.models import InstructorProfile
    from courses.models import Course
    from enrollments.models import Enrollment
    from django.db.models import Avg, Sum, Count

    updated = 0
    for profile in InstructorProfile.objects.select_related('user').all():
        courses = Course.objects.filter(instructor=profile.user)
        total_courses = courses.count()
        total_students = courses.aggregate(s=Sum('total_students'))['s'] or 0
        avg_rating = courses.aggregate(r=Avg('rating'))['r'] or 0.0

        InstructorProfile.objects.filter(pk=profile.pk).update(
            total_courses=total_courses,
            total_students=total_students,
            rating=round(avg_rating, 2),
        )
        updated += 1

    logger.info(f"Updated stats for {updated} instructors")
    return f"Updated {updated} instructor profiles"


@shared_task
def cleanup_expired_enrollments():
    """
    Periodic task: mark expired enrollments.
    Schedule: daily at midnight via Celery Beat.
    """
    from enrollments.models import Enrollment
    now = timezone.now()

    expired = Enrollment.objects.filter(
        status='active',
        expiry_date__isnull=False,
        expiry_date__lt=now,
    )
    count = expired.count()
    expired.update(status='expired')
    logger.info(f"Marked {count} enrollments as expired")
    return f"Expired {count} enrollments"


@shared_task
def send_weekly_digest():
    """
    Weekly digest email to students with their progress summary.
    Schedule: every Monday at 9am.
    """
    from django.contrib.auth import get_user_model
    from enrollments.models import Enrollment

    User = get_user_model()
    students = User.objects.filter(role='student', is_active=True)
    sent = 0

    for student in students:
        in_progress = Enrollment.objects.filter(
            user=student, status='active', progress__gt=0, progress__lt=100
        ).select_related('course')[:3]

        if not in_progress:
            continue

        course_list = "\n".join(
            f"  • {e.course.title} — {e.progress:.0f}% complete"
            for e in in_progress
        )

        send_mail(
            subject="📚 Your weekly learning digest",
            message=f"""
Hi {student.first_name or student.username},

Here's your learning progress this week:

{course_list}

Keep going — you're doing great!

Resume learning: http://localhost:3000/dashboard

LearnHub Team
            """.strip(),
            from_email=settings.EMAIL_HOST_USER or 'noreply@learnhub.com',
            recipient_list=[student.email],
            fail_silently=True,
        )
        sent += 1

    logger.info(f"Sent weekly digest to {sent} students")
    return f"Sent {sent} weekly digests"
