"""
Flask API: POST multipart ``file`` (PDF) → match pages using ``keywords_embedded.py``,
save filtered PDF under ``output/``, return a standard JSON envelope.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import Flask, Response, request
from werkzeug.utils import secure_filename

from builder import build_filtered_pdf
from keywords_load import load_embedded_keywords
from scanner import scan_pdf

_PROJECT_ROOT = Path(__file__).resolve().parent
_OUTPUT_DIR = _PROJECT_ROOT / "output"

app = Flask(__name__)

SUCCESS_MESSAGE = "PDF compressed successfully"


def _envelope(
    *,
    success: bool,
    message: str,
    data: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    errors: list[Any] | None = None,
    status: int = 200,
) -> Response:
    body = {
        "success": success,
        "message": message,
        "data": data if data is not None else {},
        "meta": meta if meta is not None else {},
        "errors": errors if errors is not None else [],
    }
    return Response(
        json.dumps(body, ensure_ascii=False, sort_keys=False),
        mimetype="application/json; charset=utf-8",
        status=status,
    )


@app.post("/extract")
def extract():
    if "file" not in request.files:
        return _envelope(
            success=False,
            message="Validation failed.",
            errors=[
                "Missing form field `file`. Postman: Body → form-data → key `file` (type File).",
            ],
            status=400,
        )

    upload = request.files["file"]
    if not upload or upload.filename == "":
        return _envelope(
            success=False,
            message="Validation failed.",
            errors=["No file selected."],
            status=400,
        )

    if not (upload.filename or "").lower().endswith(".pdf"):
        return _envelope(
            success=False,
            message="Validation failed.",
            errors=["Upload a PDF (.pdf)."],
            status=400,
        )

    try:
        keywords = load_embedded_keywords()
    except ValueError as e:
        err = str(e)
        return _envelope(
            success=False,
            message="Server configuration error.",
            errors=[err],
            status=500,
        )

    fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        upload.save(tmp_path)
        if os.path.getsize(tmp_path) == 0:
            return _envelope(
                success=False,
                message="Validation failed.",
                errors=["Empty file upload."],
                status=400,
            )

        try:
            matched, total_pages = scan_pdf(
                pdf_path=tmp_path,
                keywords=keywords,
                case_sensitive=False,
                whole_word=False,
            )
        except RuntimeError as e:
            err = str(e)
            return _envelope(
                success=False,
                message="Could not process PDF.",
                errors=[err],
                status=400,
            )

        if not matched:
            return _envelope(
                success=False,
                message="No matching pages.",
                errors=["No pages matched your keywords."],
                data={"total_pages_in_pdf": total_pages},
                status=422,
            )

        _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = secure_filename(upload.filename or "document.pdf")
        stem = Path(safe_name).stem or "document"
        out_file = _OUTPUT_DIR / f"{stem}_filtered_{uuid4().hex[:10]}.pdf"

        try:
            build_filtered_pdf(
                input_path=tmp_path,
                matched=matched,
                output_path=str(out_file),
            )
        except RuntimeError as e:
            err = str(e)
            return _envelope(
                success=False,
                message="Could not save filtered PDF.",
                errors=[err],
                status=500,
            )

        extracted_pages = sorted(i + 1 for i in matched.keys())
        saved_rel = str(out_file.relative_to(_PROJECT_ROOT)).replace("\\", "/")

        return _envelope(
            success=True,
            message=SUCCESS_MESSAGE,
            data={
                "extracted_pages": extracted_pages,
                "filtered_pdf_path": saved_rel,
                "total_pages_in_pdf": total_pages,
            },
            status=200,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
