import json
import tempfile
from pathlib import Path
from typing import Any
import urllib.request

from flask import Flask, Response, request
from builder import build_filtered_pdf
from keywords_embedded import (COMPARABLE_RENTAL_PATTERN_KEYS, COMPARABLE_SALES_PATTERN_KEYS, EXCLUDED_PAGE_PHRASES, PATTERN_DEFINITIONS)
from scanner import scan_pdf

_PROJECT_ROOT = Path(__file__).resolve().parent
app = Flask(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"

#  Custom Error
class ApiRequestError(Exception):
    def __init__(self, status_code: int, message: str, errors=None, data=None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.errors = errors or []
        self.data = data


def get_s3_url() -> str:
    body = request.get_json(silent=True) or {}
    s3_url = (body.get("s3_url") or "").strip()
    if not s3_url:
        raise ApiRequestError(400, "Missing `s3_url`")
    return s3_url

def download_pdf(url: str, path: str):
    try:
        with urllib.request.urlopen(url, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    except Exception as e:
        raise ApiRequestError(400, "Download failed", [str(e)])

def scan_pdf_safe(path: str):
    try:
        return scan_pdf(
            pdf_path=path,
            patterns=PATTERN_DEFINITIONS,
            excluded_phrases=EXCLUDED_PAGE_PHRASES,
        )
    except RuntimeError as e:
        raise ApiRequestError(400, "PDF processing failed", [str(e)])

def get_flags(matched: dict[int, list[str]]) -> dict[str, bool]:
    found = {name for names in matched.values() for name in names}
    return {
        "comparable_sales": bool(found & set(COMPARABLE_SALES_PATTERN_KEYS)),
        "comparable_rental": bool(found & set(COMPARABLE_RENTAL_PATTERN_KEYS)),
    }

def process_pdf(input_path: str, output_name: str):
    matched, total_pages = scan_pdf_safe(input_path)
    flags = get_flags(matched)

    output_path = OUTPUT_DIR / output_name

    build_filtered_pdf(
        input_path=input_path,
        matched=matched,
        output_path=str(output_path),
    )

    return {
        "extracted_pages": sorted(p + 1 for p in matched),
        "filtered_pdf_path": str(output_path.relative_to(PROJECT_ROOT)),
        "total_pages_in_pdf": total_pages,
        **flags,
    }

@app.post("/extract")
def extract():
    tmp_path = tempfile.mktemp(suffix=".pdf")

    try:
        url = get_s3_url()
        download_pdf(url, tmp_path)

        file_name = Path(url.split("?")[0]).name
        data = process_pdf(tmp_path, file_name)

        return Response(json.dumps({
            "success": True,
            "message": "PDF processed successfully",
            "data": data
        }), mimetype="application/json")

    except ApiRequestError as e:
        return Response(json.dumps({
            "success": False,
            "message": e.message,
            "errors": e.errors,
            "data": e.data,
            "status": e.status_code
        }), mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)