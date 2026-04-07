from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from auth import get_current_user
from typing import List

router = APIRouter()


@router.get("/courses")
async def recommend_courses(
    limit: int = Query(default=6, le=20),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Content-based & collaborative filtering recommendations.
    Strategy:
    1. Get user's enrolled course categories
    2. Find similar courses in those categories not yet enrolled
    3. Fall back to top-rated courses
    """
    user_id = current_user["user_id"]

    # Get categories user is interested in
    cats_q = await db.execute(text("""
        SELECT DISTINCT c.category_id
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.user_id = :uid AND c.category_id IS NOT NULL
        LIMIT 5
    """), {"uid": user_id})
    category_ids = [r.category_id for r in cats_q.fetchall()]

    # Get already-enrolled course IDs
    enrolled_q = await db.execute(text(
        "SELECT course_id FROM enrollments WHERE user_id = :uid"
    ), {"uid": user_id})
    enrolled_ids = [r.course_id for r in enrolled_q.fetchall()] or [0]

    if category_ids:
        recs_q = await db.execute(text("""
            SELECT c.id, c.title, c.slug, c.thumbnail, c.price, c.discount_price,
                   c.rating, c.total_students, c.level,
                   u.first_name || ' ' || u.last_name as instructor_name,
                   cat.name as category_name
            FROM courses c
            JOIN users u ON c.instructor_id = u.id
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.status = 'published'
              AND c.category_id = ANY(:cat_ids)
              AND c.id != ALL(:enrolled_ids)
            ORDER BY c.rating DESC, c.total_students DESC
            LIMIT :lim
        """), {"cat_ids": category_ids, "enrolled_ids": enrolled_ids, "lim": limit})
    else:
        # Cold start: return top-rated published courses
        recs_q = await db.execute(text("""
            SELECT c.id, c.title, c.slug, c.thumbnail, c.price, c.discount_price,
                   c.rating, c.total_students, c.level,
                   u.first_name || ' ' || u.last_name as instructor_name,
                   cat.name as category_name
            FROM courses c
            JOIN users u ON c.instructor_id = u.id
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.status = 'published'
              AND c.id != ALL(:enrolled_ids)
            ORDER BY c.rating DESC, c.total_students DESC
            LIMIT :lim
        """), {"enrolled_ids": enrolled_ids, "lim": limit})

    courses = []
    for r in recs_q.fetchall():
        courses.append({
            "id": r.id,
            "title": r.title,
            "slug": r.slug,
            "thumbnail": r.thumbnail,
            "price": float(r.price),
            "discount_price": float(r.discount_price) if r.discount_price else None,
            "rating": float(r.rating),
            "total_students": r.total_students,
            "level": r.level,
            "instructor_name": r.instructor_name.strip(),
            "category_name": r.category_name,
        })

    return {"recommendations": courses, "count": len(courses)}


@router.get("/continue-learning")
async def continue_learning(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Return in-progress courses sorted by last accessed"""
    user_id = current_user["user_id"]
    q = await db.execute(text("""
        SELECT c.id, c.title, c.slug, c.thumbnail, e.progress, e.last_accessed,
               u.first_name || ' ' || u.last_name as instructor_name
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        JOIN users u ON c.instructor_id = u.id
        WHERE e.user_id = :uid AND e.status = 'active' AND e.progress > 0
        ORDER BY e.last_accessed DESC
        LIMIT 5
    """), {"uid": user_id})
    return {"courses": [
        {
            "id": r.id, "title": r.title, "slug": r.slug,
            "thumbnail": r.thumbnail, "progress": float(r.progress),
            "last_accessed": str(r.last_accessed),
            "instructor_name": r.instructor_name.strip()
        }
        for r in q.fetchall()
    ]}


@router.get("/trending")
async def trending_courses(
    limit: int = Query(default=8, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Trending courses based on recent enrollment velocity"""
    q = await db.execute(text("""
        SELECT c.id, c.title, c.slug, c.thumbnail, c.price, c.rating,
               c.total_students, c.level,
               u.first_name || ' ' || u.last_name as instructor_name,
               COUNT(e.id) as recent_enrollments
        FROM courses c
        JOIN users u ON c.instructor_id = u.id
        LEFT JOIN enrollments e ON c.id = e.course_id
            AND e.enrolled_at >= NOW() - INTERVAL '7 days'
        WHERE c.status = 'published'
        GROUP BY c.id, u.id
        ORDER BY recent_enrollments DESC, c.rating DESC
        LIMIT :lim
    """), {"lim": limit})
    return {"trending": [
        {
            "id": r.id, "title": r.title, "slug": r.slug,
            "thumbnail": r.thumbnail, "price": float(r.price),
            "rating": float(r.rating), "total_students": r.total_students,
            "level": r.level, "instructor_name": r.instructor_name.strip(),
            "recent_enrollments": r.recent_enrollments
        }
        for r in q.fetchall()
    ]}
