"""
Celery Beat periodic task schedule.
Add this to settings.py or import it there.
"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Update instructor stats every 6 hours
    'update-instructor-stats': {
        'task': 'lms_backend.tasks.update_instructor_stats',
        'schedule': crontab(hour='*/6', minute=0),
    },
    # Clean up expired enrollments every day at midnight
    'cleanup-expired-enrollments': {
        'task': 'lms_backend.tasks.cleanup_expired_enrollments',
        'schedule': crontab(hour=0, minute=0),
    },
    # Send weekly digest every Monday at 9am UTC
    'weekly-digest': {
        'task': 'lms_backend.tasks.send_weekly_digest',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
    },
}
