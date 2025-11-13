"""Bpium API client helpers."""
from __future__ import annotations

import json
from typing import Dict, List, Optional

import requests
from requests import Response

from .config import settings
from .models import Course

CATALOG_ID = 16
FIELD_MAP = {
    "title_field": "2",
    "hours": "3",
    "start_date": "4",
    "status": "5",
    "current_price": "6",
    "first_raise_date": "7",
    "first_raise_price": "8",
    "second_raise_date": "9",
    "second_raise_price": "10",
    "installment_price": "11",
    "doc": "12",
    "course_type": "13",
    "practice_types": "14",
    "is_course_of_month": "15",
}


class BpiumError(RuntimeError):
    """Raised when Bpium API returns error."""


def _call_catalog_records() -> List[Dict]:
    url = f"https://{settings.bpium_domain}/api/v1/catalogs/{CATALOG_ID}/records"
    params = {"fields": json.dumps(list(FIELD_MAP.values()))}
    resp: Response = requests.get(
        url,
        params=params,
        auth=(settings.bpium_email, settings.bpium_password),
        headers={"Accept": "application/json"},
        timeout=15,
    )
    if resp.status_code >= 400:
        raise BpiumError(f"HTTP {resp.status_code}: {resp.text[:200]}")

    try:
        data = resp.json()
    except ValueError as exc:  # pragma: no cover - defensive
        raise BpiumError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise BpiumError("Unexpected response format")
    return data


def _safe_number(value: Optional[str | int | float]) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _bool_value(value: Optional[bool | str | int]) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes"}
    return None


def _string_value(value: Optional[object]) -> Optional[str]:
    if value in (None, "", []):
        return None
    if isinstance(value, list):
        # поля типа radiobutton / multiselect возвращают массив строк
        return _string_value(value[0] if value else None)
    return str(value)


def fetch_courses() -> List[Course]:
    records = _call_catalog_records()

    courses: List[Course] = []
    for record in records:
        values: Dict[str, object] = record.get("values", {})
        course = Course(
            id=str(record.get("id")),
            title=str(record.get("title", "")),
            hours=_safe_number(values.get(FIELD_MAP["hours"])),
            start_date=_string_value(values.get(FIELD_MAP["start_date"])),
            status=_string_value(values.get(FIELD_MAP["status"])),
            current_price=_safe_number(values.get(FIELD_MAP["current_price"])),
            first_raise_date=_string_value(values.get(FIELD_MAP["first_raise_date"])),
            first_raise_price=_safe_number(values.get(FIELD_MAP["first_raise_price"])),
            second_raise_date=_string_value(values.get(FIELD_MAP["second_raise_date"])),
            second_raise_price=_safe_number(values.get(FIELD_MAP["second_raise_price"])),
            installment_price=_safe_number(values.get(FIELD_MAP["installment_price"])),
            doc=_string_value(values.get(FIELD_MAP["doc"])),
            course_type=_string_value(values.get(FIELD_MAP["course_type"])),
            practice_types=_string_value(values.get(FIELD_MAP["practice_types"])),
            is_course_of_month=_bool_value(values.get(FIELD_MAP["is_course_of_month"])),
        )
        courses.append(course)
    return courses
