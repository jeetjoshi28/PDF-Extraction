import json
import os
import tempfile
from pathlib import Path
from typing import Any
import urllib.request
import urllib.error

from flask import Flask, Response, request
from werkzeug.utils import secure_filename

from builder import build_filtered_pdf
from keywords_embedded import (
    COMPARABLE_RENTAL_PATTERN_KEYS,
    COMPARABLE_SALES_PATTERN_KEYS,
    PATTERN_DEFINITIONS,
)
from scanner import scan_pdf

_PROJECT_ROOT = Path(__file__).resolve().parent
_OUTPUT_DIR = _PROJECT_ROOT / "output"

app = Flask(__name__)

SUCCESS_MESSAGE = "PDF compressed successfully"
class ApiRequestError(Exception):
    """Structured API error used to return consistent JSON error responses."""

    def __init__(
        self,
        status_code: int,
        message: str,
        errors: list[Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.errors = errors or []
        self.data = data


def _filtered_pdf_response(*, input_pdf_path: str, output_file_name: str) -> Response:
    """Scan a PDF and return the filtered PDF response envelope."""
    matched, total_pages = _scan_pdf_for_patterns(pdf_path=input_pdf_path)

    flags = _derive_comparable_group_flags(matched)

    output_pdf_path = _OUTPUT_DIR / output_file_name

    print(f"input_pdf_path: {input_pdf_path}")
    print(f"matched: {matched}")
    print(f"output_pdf_path: {output_pdf_path}")

    build_filtered_pdf(
        input_path=input_pdf_path,
        matched=matched,
        output_path=str(output_pdf_path),
    )

    extracted_pages = sorted(page_index + 1 for page_index in matched.keys())
    saved_rel = str(output_pdf_path.relative_to(_PROJECT_ROOT)).replace("\\", "/")

    return Response(
        json.dumps({
            "success": True,
            "message": SUCCESS_MESSAGE,
            "data": {
                "extracted_pages": extracted_pages,
                "filtered_pdf_path": saved_rel,
                "total_pages_in_pdf": total_pages,
                **flags,
            },
        }),
        status=200,
        mimetype="application/json",
    )


def _derive_comparable_group_flags(matched: dict[int, list[str]]) -> dict[str, bool]:
    """True if any matched pages include sales or rental group phrases."""
    found: set[str] = set()
    for names in matched.values():
        found.update(names)
    sales = set(COMPARABLE_SALES_PATTERN_KEYS)
    rental = set(COMPARABLE_RENTAL_PATTERN_KEYS)
    return {
        "comparable_sales": bool(found & sales),
        "comparable_rental": bool(found & rental),
    }

@app.post("/extract")
def extract():
    """Main API endpoint that downloads, scans, and filters a PDF from `s3_url`."""
    tmp_path = tempfile.mktemp(suffix=".pdf")
    try:
        s3_url = _read_required_s3_url()
        _download_pdf_from_url(s3_url=s3_url, destination_path=tmp_path)

        source_file_name = Path(s3_url.split("?")[0]).name
        return _filtered_pdf_response(
            input_pdf_path=tmp_path,
            output_file_name=source_file_name,
        )
    except ApiRequestError as err:
        return Response(
            json.dumps({
                "success": False,
                "message": err.message,
                "data": err.data,
                "errors": err.errors,
                "status": err.status_code,
            })
        )

def _read_required_s3_url() -> str:
    """Read and validate `s3_url` from request JSON body."""
    body = request.get_json(silent=True) or {}
    s3_url = body.get("s3_url")

    if not isinstance(s3_url, str):
        raise ApiRequestError(
            status_code=400,
            message="Validation failed.",
            errors=['Missing JSON field `s3_url`'],
        )

    s3_url = s3_url.strip()
    if not s3_url:
        raise ApiRequestError(
            status_code=400,
            message="Validation failed.",
            errors=['Missing JSON field `s3_url`'],
        )

    return s3_url

def _download_pdf_from_url(*, s3_url: str, destination_path: str) -> None:
    """Download PDF bytes from URL and stream them into a local temp file."""
    try:
        request_obj = urllib.request.Request(
            s3_url,
            headers={"User-Agent": "PDF-Extraction/1.0"},
            method="GET",
        )
        with urllib.request.urlopen(request_obj, timeout=120) as resp:
            # Stream download to avoid loading whole PDF into memory.
            with open(destination_path, "wb") as file_handle:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    file_handle.write(chunk)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise ApiRequestError(
            status_code=400,
            message="Could not download PDF from s3_url.",
            errors=[str(exc)],
        )

def _scan_pdf_for_patterns(*, pdf_path: str) -> tuple[dict[int, list[str]], int]:
    """Scan PDF with configured text patterns and map scanner failures to API errors."""
    try:
        return scan_pdf(pdf_path=pdf_path, patterns=PATTERN_DEFINITIONS)
    except RuntimeError as exc:
        raise ApiRequestError(status_code=400, message="Could not process PDF.", errors=[str(exc)])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
