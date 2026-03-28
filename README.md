# PDF Keyword Filter (API only)

Upload a PDF via **Postman**; the app finds pages that contain any keyword from `keywords_embedded.py`, **saves** the filtered PDF under **`output/`**, and **returns JSON** with status, extracted page numbers, and total pages.

## Setup

```bash
cd "D:\Personal project\pdf_filter"
pip install -r requirements.txt
```

Edit **`keywords_embedded.py`**: `KEYWORDS_JSON` is JSON with:

- **`keywords`** — include pages that contain any of these strings.
- **`exclude_keywords`** — never include a page if it contains any of these (even if it matched `keywords`).
- **`exclude_image_heavy_pages`** (optional, default `true` when using an object) — skip pages that have embedded images and very little extractable text (typical photo / map pages).
- **`image_page_max_text_chars`** (optional, default `80`) — text length threshold used with the rule above.

You can still use a plain JSON array for `KEYWORDS_JSON` for backward compatibility (no excludes, no image skipping).

## Run

```bash
python api.py
```

Server: `http://127.0.0.1:8000`

## Postman

1. **POST** `http://127.0.0.1:8000/extract`
2. **Body** → **form-data**
3. Key **`file`** → type **File** → choose your PDF

Every response uses the same shape, in this **order**: `success`, `message`, `data`, `meta`, `errors` (Flask’s default sorted keys are avoided so Postman matches this layout).

**Success (200):**

```json
{
  "success": true,
  "message": "PDF compressed successfully",
  "data": {
    "extracted_pages": [1, 5, 12],
    "filtered_pdf_path": "output/report_filtered_abc123def45.pdf",
    "total_pages_in_pdf": 30
  },
  "meta": {},
  "errors": []
}
```

- **`data.extracted_pages`** — 1-based page numbers from the **original** PDF in the filtered file.
- **`data.total_pages_in_pdf`** — total pages in the **uploaded** PDF.
- **`data.filtered_pdf_path`** — saved file path (relative to the project).

**Error example:** `success` is `false`, `message` summarizes the case, details are in **`errors`** (list of strings). Optional fields may appear in **`data`** (e.g. **`total_pages_in_pdf`** on **422** when no page matches). HTTP status: **400**, **422**, or **500**.

## Project layout

```
pdf_filter/
├── api.py               ← start here (Flask)
├── scanner.py           ← page text + keyword matching
├── builder.py           ← writes filtered PDF
├── keywords_load.py     ← reads KEYWORDS_JSON
├── keywords_embedded.py ← your keywords (JSON string)
├── requirements.txt
└── output/              ← filtered PDFs saved here
```
