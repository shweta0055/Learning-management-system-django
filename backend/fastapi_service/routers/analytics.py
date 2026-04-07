from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from auth import get_current_user, require_instructor, require_admin
from typing import Optional
import redis.asyncio as aioredis
import json
from decouple import config

router = APIRouter()
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")


async def get_redis():
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield r
    finally:
        await r.close()


@router.get("/dashboard/student")
async def student_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Student analytics dashboard"""
    user_id = current_user["user_id"]

    enrollments_q = await db.execute(text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
               AVG(progress) as avg_progress
        FROM enrollments WHERE user_id = :uid
    """), {"uid": user_id})
    row = enrollments_q.fetchone()

    quiz_q = await db.execute(text("""
        SELECT COUNT(*) as total_attempts,
               SUM(CASE WHEN passed THEN 1 ELSE 0 END) as passed,
               AVG(score) as avg_score
        FROM quiz_attempts WHERE user_id = :uid AND status='completed'
    """), {"uid": user_id})
    quiz_row = quiz_q.fetchone()

    certs_q = await db.execute(text(
        "SELECT COUNT(*) FROM certificates WHERE user_id = :uid"
    ), {"uid": user_id})
    cert_count = certs_q.scalar()

    return {
        "enrollments": {
            "total": row.total or 0,
            "completed": row.completed or 0,
            "in_progress": (row.total or 0) - (row.completed or 0),
            "avg_progress": round(float(row.avg_progress or 0), 2),
        },
        "quizzes": {
            "total_attempts": quiz_row.total_attempts or 0,
            "passed": quiz_row.passed or 0,
            "avg_score": round(float(quiz_row.avg_score or 0), 2),
        },
        "certificates": cert_count or 0,
    }


@router.get("/dashboard/instructor")
async def instructor_dashboard(
    current_user: dict = Depends(require_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Instructor analytics dashboard"""
    user_id = current_user["user_id"]

    courses_q = await db.execute(text("""
        SELECT COUNT(*) as total_courses,
               SUM(total_students) as total_students,
               AVG(rating) as avg_rating,
               SUM(price) as total_revenue_potential
        FROM courses WHERE instructor_id = :uid
    """), {"uid": user_id})
    row = courses_q.fetchone()

    revenue_q = await db.execute(text("""
        SELECT SUM(p.amount) as total_revenue
        FROM payments p
        JOIN courses c ON p.course_id = c.id
        WHERE c.instructor_id = :uid AND p.status='completed'
    """), {"uid": user_id})
    revenue_row = revenue_q.fetchone()

    monthly_q = await db.execute(text("""
        SELECT DATE_TRUNC('month', e.enrolled_at) as month, COUNT(*) as enrollments
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE c.instructor_id = :uid
        GROUP BY month ORDER BY month DESC LIMIT 12
    """), {"uid": user_id})
    monthly = [{"month": str(r.month)[:10], "enrollments": r.enrollments} for r in monthly_q.fetchall()]

    return {
        "courses": {
            "total": row.total_courses or 0,
            "total_students": row.total_students or 0,
            "avg_rating": round(float(row.avg_rating or 0), 2),
        },
        "revenue": {
            "total": float(revenue_row.total_revenue or 0),
        },
        "monthly_enrollments": monthly,
    }


@router.get("/dashboard/admin")
async def admin_dashboard(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin analytics dashboard"""
    users_q = await db.execute(text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN role='student' THEN 1 ELSE 0 END) as students,
               SUM(CASE WHEN role='instructor' THEN 1 ELSE 0 END) as instructors
        FROM users
    """))
    users_row = users_q.fetchone()

    courses_q = await db.execute(text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status='published' THEN 1 ELSE 0 END) as published
        FROM courses
    """))
    courses_row = courses_q.fetchone()

    revenue_q = await db.execute(text(
        "SELECT SUM(amount) FROM payments WHERE status='completed'"
    ))
    total_revenue = revenue_q.scalar() or 0

    enrollments_q = await db.execute(text("SELECT COUNT(*) FROM enrollments"))
    total_enrollments = enrollments_q.scalar() or 0

    return {
        "users": {
            "total": users_row.total,
            "students": users_row.students,
            "instructors": users_row.instructors,
        },
        "courses": {
            "total": courses_row.total,
            "published": courses_row.published,
        },
        "revenue": float(total_revenue),
        "enrollments": total_enrollments,
    }


@router.get("/course/{course_id}")
async def course_analytics(
    course_id: int,
    current_user: dict = Depends(require_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Per-course analytics for instructor"""
    completion_q = await db.execute(text("""
        SELECT AVG(progress) as avg_progress,
               SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
               COUNT(*) as total
        FROM enrollments WHERE course_id = :cid
    """), {"cid": course_id})
    row = completion_q.fetchone()

    lesson_q = await db.execute(text("""
        SELECT l.title, COUNT(lp.id) as views,
               SUM(CASE WHEN lp.is_completed THEN 1 ELSE 0 END) as completions
        FROM lessons l
        LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id
        LEFT JOIN enrollments e ON lp.enrollment_id = e.id
        WHERE e.course_id = :cid
        GROUP BY l.id, l.title ORDER BY views DESC LIMIT 10
    """), {"cid": course_id})
    lessons = [{"title": r.title, "views": r.views, "completions": r.completions} for r in lesson_q.fetchall()]

    return {
        "completion": {
            "avg_progress": round(float(row.avg_progress or 0), 2),
            "completed_students": row.completed or 0,
            "total_students": row.total or 0,
        },
        "lessons": lessons,
    }
