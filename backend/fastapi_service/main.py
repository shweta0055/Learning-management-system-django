from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from decouple import config

from routers import analytics, recommendations, streaming, search
from middleware import RequestLoggingMiddleware, register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI LMS Service starting up...")
    yield
    print("FastAPI LMS Service shutting down...")


app = FastAPI(
    title="LMS FastAPI Service",
    description="Async microservice for streaming, analytics, recommendations & search",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config("CORS_ALLOWED_ORIGINS", default="http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(streaming.router, prefix="/api/streaming", tags=["Video Streaming"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FastAPI LMS"}
