from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from typing import Optional

router = APIRouter()


@router.get("/courses")
async def search_courses(
    q: str = Query(..., min_length=2, description="Search query"),
    category_id: Optional[int] = None,
    level: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    is_free: Optional[bool] = None,
    sort_by: str = Query(default="relevance", enum=["relevance", "rating", "price_asc", "price_desc", "newest"]),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Full-text course search with filters"""
    offset = (page - 1) * page_size

    where_clauses = ["c.status = 'published'"]
    params: dict = {"q": f"%{q}%", "limit": page_size, "offset": offset}

    where_clauses.append("(c.title ILIKE :q OR c.description ILIKE :q OR c.short_description ILIKE :q)")

    if category_id:
        where_clauses.append("c.category_id = :cat_id")
        params["cat_id"] = category_id
    if level:
        where_clauses.append("c.level = :level")
        params["level"] = level
    if min_price is not None:
        where_clauses.append("c.price >= :min_price")
        params["min_price"] = min_price
    if max_price is not None:
        where_clauses.append("c.price <= :max_price")
        params["max_price"] = max_price
    if min_rating is not None:
        where_clauses.append("c.rating >= :min_rating")
        params["min_rating"] = min_rating
    if is_free is not None:
        where_clauses.append("c.is_free = :is_free")
        params["is_free"] = is_free

    order_map = {
        "relevance": "c.total_students DESC, c.rating DESC",
        "rating": "c.rating DESC",
        "price_asc": "c.price ASC",
        "price_desc": "c.price DESC",
        "newest": "c.created_at DESC",
    }
    order_clause = order_map.get(sort_by, "c.total_students DESC")
    where_sql = " AND ".join(where_clauses)

    count_q = await db.execute(text(f"""
        SELECT COUNT(*) FROM courses c WHERE {where_sql}
    """), params)
    total = count_q.scalar()

    results_q = await db.execute(text(f"""
        SELECT c.id, c.title, c.slug, c.short_description, c.thumbnail,
               c.price, c.discount_price, c.level, c.rating, c.total_students,
               c.duration_hours, c.total_lessons, c.is_free, c.language,
               u.first_name || ' ' || u.last_name as instructor_name,
               cat.name as category_name
        FROM courses c
        JOIN users u ON c.instructor_id = u.id
        LEFT JOIN categories cat ON c.category_id = cat.id
        WHERE {where_sql}
        ORDER BY {order_clause}
        LIMIT :limit OFFSET :offset
    """), params)

    courses = [
        {
            "id": r.id, "title": r.title, "slug": r.slug,
            "short_description": r.short_description, "thumbnail": r.thumbnail,
            "price": float(r.price), "discount_price": float(r.discount_price) if r.discount_price else None,
            "level": r.level, "rating": float(r.rating), "total_students": r.total_students,
            "duration_hours": float(r.duration_hours), "total_lessons": r.total_lessons,
            "is_free": r.is_free, "language": r.language,
            "instructor_name": r.instructor_name.strip(), "category_name": r.category_name,
        }
        for r in results_q.fetchall()
    ]

    return {
        "results": courses,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "query": q,
    }


@router.get("/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db)
):
    """Autocomplete suggestions for search"""
    results_q = await db.execute(text("""
        SELECT DISTINCT title FROM courses
        WHERE status = 'published' AND title ILIKE :q
        ORDER BY title LIMIT 8
    """), {"q": f"%{q}%"})
    return {"suggestions": [r.title for r in results_q.fetchall()]}
