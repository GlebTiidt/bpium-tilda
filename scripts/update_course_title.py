#!/usr/bin/env python3
"""Скрипт обновляет плейсхолдер {{course_title}} в HTML, подставляя название курса из Bpium."""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CATALOG_ID = 16
FIELDS_PARAM = "%5B%221%22%5D"  # URL-encoded ["1"]


def env_or_exit(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(f"Environment variable {name} is required", file=sys.stderr)
        sys.exit(1)
    return value


def load_dotenv(path: Path = Path(".env.local")) -> None:
    """Простая загрузка .env файла (без зависимостей)."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        os.environ.setdefault(key, value)


def fetch_records(domain: str, email: str, password: str) -> List[Dict[str, Any]]:
    url = f"https://{domain}/api/v1/catalogs/{CATALOG_ID}/records?fields={FIELDS_PARAM}"
    req = Request(url)
    token = base64.b64encode(f"{email}:{password}".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")
    req.add_header("Accept", "application/json")

    try:
        with urlopen(req) as response:  # nosec B310
            payload = response.read()
    except HTTPError as err:
        print(f"Bpium API error: {err.code} {err.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as err:
        print(f"Connection error: {err.reason}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as err:
        print(f"Cannot decode response: {err}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("Unexpected API response: expected a list of records", file=sys.stderr)
        sys.exit(1)

    if not data:
        print("Catalog 16 returned no records", file=sys.stderr)
        sys.exit(1)

    return data


def pick_title(records: List[Dict[str, Any]], record_id: str | None) -> str:
    if record_id:
        record = next((r for r in records if r.get("id") == record_id), None)
        if not record:
            print(f"Record {record_id} not found in catalog", file=sys.stderr)
            sys.exit(1)
    else:
        record = records[0]

    title = record.get("title")
    if not title:
        print("Record has empty title", file=sys.stderr)
        sys.exit(1)
    return title


def update_html(path: Path, course_title: str, inplace: bool = True) -> None:
    if not path.exists():
        print(f"HTML file {path} not found", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    placeholder = "{{course_title}}"
    if placeholder not in text:
        print(f"Placeholder {placeholder} not found in {path}", file=sys.stderr)
        sys.exit(1)

    updated = text.replace(placeholder, course_title)

    output_path = path if inplace else path.with_suffix(path.suffix + ".updated")
    output_path.write_text(updated, encoding="utf-8")
    print(f"Updated course title in {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update Tilda HTML with course title from Bpium")
    parser.add_argument("html", type=Path, help="Path to exported Tilda HTML file")
    parser.add_argument("--record-id", help="Specific record id to use (defaults to first record)")
    parser.add_argument("--copy", action="store_true", help="Write changes to <file>.updated instead of in place")
    args = parser.parse_args()

    load_dotenv()
    domain = env_or_exit("BPIUM_DOMAIN")
    email = env_or_exit("BPIUM_EMAIL")
    password = env_or_exit("BPIUM_PASSWORD")

    records = fetch_records(domain, email, password)
    title = pick_title(records, args.record_id)
    update_html(args.html, title, inplace=not args.copy)


if __name__ == "__main__":
    main()
