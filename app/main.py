"""FastAPI application exposing read-only endpoints for Tilda."""
from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import bpium
from .cache import TTLCache
from .config import settings
from .models import Course

app = FastAPI(title="Bpium → Tilda integration API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_cache = TTLCache[List[Course]](ttl_seconds=settings.cache_ttl_seconds)


def get_courses() -> List[Course]:
    """Return cached courses, refreshing via Bpium if TTL expired."""

    def factory() -> List[Course]:
        return bpium.fetch_courses()

    return _cache.get_or_create(factory)


@app.get("/api/courses", response_model=List[Course])
def list_courses(courses: List[Course] = Depends(get_courses)) -> List[Course]:
    return courses


@app.get("/api/courses/latest", response_model=Course)
def latest_course(
    courses: List[Course] = Depends(get_courses),
    record_id: Optional[str] = Query(default=None, description="Specific record id to select"),
) -> Course:
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found")

    if record_id:
        for course in courses:
            if course.id == record_id:
                return course
        raise HTTPException(status_code=404, detail=f"Course {record_id} not found")

    return courses[0]
