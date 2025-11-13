"""Pydantic models describing responses."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Course(BaseModel):
    id: str
    title: str
    hours: Optional[float] = None
    start_date: Optional[str] = None
    status: Optional[str] = None
    current_price: Optional[float] = None
    first_raise_date: Optional[str] = None
    first_raise_price: Optional[float] = None
    second_raise_date: Optional[str] = None
    second_raise_price: Optional[float] = None
    installment_price: Optional[float] = None
    doc: Optional[str] = None
    course_type: Optional[str] = None
    practice_types: Optional[str] = None
    is_course_of_month: Optional[bool] = None
