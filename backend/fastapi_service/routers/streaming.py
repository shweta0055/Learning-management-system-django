from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
import boto3
import httpx
from decouple import config

router = APIRouter()
AWS_BUCKET = config("AWS_STORAGE_BUCKET_NAME", default="")
AWS_REGION = config("AWS_S3_REGION_NAME", default="us-east-1")


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=config("AWS_ACCESS_KEY_ID", default=""),
        aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY", default=""),
        region_name=AWS_REGION,
    )


@router.get("/presigned-url/{lesson_id}")
async def get_video_presigned_url(
    lesson_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a presigned S3 URL for authenticated video access"""
    # Check the user is enrolled in the course containing this lesson
    q = await db.execute(text("""
        SELECT l.video_url, l.is_free_preview, c.id as course_id
        FROM lessons l
        JOIN sections s ON l.section_id = s.id
        JOIN courses c ON s.course_id = c.id
        WHERE l.id = :lid
    """), {"lid": lesson_id})
    lesson = q.fetchone()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Free preview is accessible without enrollment
    if not lesson.is_free_preview:
        enroll_q = await db.execute(text("""
            SELECT id FROM enrollments
            WHERE user_id = :uid AND course_id = :cid AND status = 'active'
        """), {"uid": current_user["user_id"], "cid": lesson.course_id})
        if not enroll_q.fetchone():
            raise HTTPException(status_code=403, detail="Not enrolled in this course")

    if not lesson.video_url or not AWS_BUCKET:
        return {"url": lesson.video_url, "presigned": False}

    try:
        s3 = get_s3_client()
        # Extract key from URL or use directly
        key = lesson.video_url.split(f"{AWS_BUCKET}.s3.amazonaws.com/")[-1]
        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": AWS_BUCKET, "Key": key},
            ExpiresIn=3600,  # 1 hour
        )
        return {"url": presigned_url, "presigned": True, "expires_in": 3600}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not generate streaming URL: {str(e)}")


@router.get("/proxy/{lesson_id}")
async def proxy_video_stream(
    lesson_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Proxy video streaming with range support.
    Use this when S3 presigned URLs are not desired (self-hosted).
    """
    q = await db.execute(text("""
        SELECT l.video_url, l.is_free_preview, c.id as course_id
        FROM lessons l
        JOIN sections s ON l.section_id = s.id
        JOIN courses c ON s.course_id = c.id
        WHERE l.id = :lid
    """), {"lid": lesson_id})
    lesson = q.fetchone()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    if not lesson.is_free_preview:
        enroll_q = await db.execute(text("""
            SELECT id FROM enrollments
            WHERE user_id = :uid AND course_id = :cid AND status='active'
        """), {"uid": current_user["user_id"], "cid": lesson.course_id})
        if not enroll_q.fetchone():
            raise HTTPException(status_code=403, detail="Not enrolled")

    range_header = request.headers.get("range", "bytes=0-")

    async def stream_video():
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "GET", lesson.video_url,
                headers={"Range": range_header}, timeout=60
            ) as response:
                async for chunk in response.aiter_bytes(chunk_size=1024 * 64):
                    yield chunk

    return StreamingResponse(
        stream_video(),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache",
        }
    )
