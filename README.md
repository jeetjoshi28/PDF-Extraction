# PDF phrase filter

Small **Flask** service that accepts a PDF upload, finds pages whose extractable text contains any of your configured **full phrases** (substring match, **case-insensitive**), writes a **new PDF** with only those pages, and returns **JSON** with page numbers and the saved file path.

Matching is driven by **`PATTERN_DEFINITIONS`** in `keywords_embedded.py`—not a loose keyword list: each entry is one exact phrase that must appear somewhere on the page (as returned by the PDF library’s text extractor).

## How it works

1. **Scan** — [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) opens the PDF and reads each page with `get_text()`.
2. **Match** — For each pattern, the phrase is compared to the page text after lowercasing both sides. If the phrase appears as a substring, that page is included and the pattern’s **label** is recorded (e.g. `"Addendum"`).
3. **Build** — Matched pages are **copied** from the source PDF into a new file (`insert_pdf`), preserving layout, fonts, and images where possible.
4. **Output** — Filtered PDFs are written under **`output/`** with a unique suffix in the filename.

## Requirements

- Python **3.10+** (type hints used in the codebase)
- Dependencies in `requirements.txt`:
  - **pymupdf** — PDF read, text extraction, and page assembly
  - **flask** — HTTP API

## Installation

```bash
cd pdf_filter
pip install -r requirements.txt
```

## Configuring phrases

Edit **`keywords_embedded.py`**:

- Define phrase strings as variables (optional, for clarity).
- Map **display names** → **phrases** in **`PATTERN_DEFINITIONS`**.

Example:

```python
addendum = "market conditions addendum to the appraisal report"

PATTERN_DEFINITIONS: dict[str, str] = {
    "Addendum": addendum,
    # "Label shown in logic": "exact phrase to find in page text",
}
```

- **Case** — Phrases can be written in any casing; matching is case-insensitive.
- **Add patterns** — Add a new key and phrase. Empty or all-whitespace phrases are rejected at startup (HTTP 500).
- **Page must match at least one phrase** — If no page contains any configured phrase, the API responds with **422** and no output file.

**Note:** Text comes from the PDF’s encoded content. If a title is only an image, or extraction splits words oddly, a phrase might not match even though it looks correct on screen.

## Run the server

```bash
python api.py
```

Default URL: **http://127.0.0.1:8000**

## API

### `POST /extract`

- **Content type:** `application/json`
- **Body JSON:** must include `s3_url`

#### Try with curl

```bash
curl -s -X POST http://127.0.0.1:8000/extract -H "Content-Type: application/json" -d "{\"s3_url\":\"https://your-bucket.s3.amazonaws.com/path/to/file.pdf\"}"
```

#### Postman
1. Method **POST** → `http://127.0.0.1:8000/extract`
2. **Body** → **raw** → **JSON**
3. Paste: `{"s3_url":"https://your-bucket.s3.amazonaws.com/path/to/file.pdf"}`

### Response shape

Every JSON body uses this structure (key order preserved for readability in clients):

| Field     | Meaning                                      |
| --------- | -------------------------------------------- |
| `success` | `true` or `false`                            |
| `message` | Short human-readable summary                 |
| `data`    | Payload (may be empty on errors)             |
| `meta`    | Reserved for future use; currently `{}`      |
| `errors`  | List of detail strings when something failed |

#### Success (HTTP 200)

```json
{
  "success": true,
  "message": "PDF compressed successfully",
  "data": {
    "extracted_pages": [1, 5, 12],
    "filtered_pdf_path": "output/report_filtered_a1b2c3d4e5.pdf",
    "total_pages_in_pdf": 30
  },
  "meta": {},
  "errors": []
}
```

- **`extracted_pages`** — 1-based page numbers from the **original** PDF that were kept (sorted ascending).
- **`filtered_pdf_path`** — Path to the new PDF, **relative to the project root** (forward slashes).
- **`total_pages_in_pdf`** — Page count of the uploaded PDF.

#### Common errors

| HTTP    | Typical cause                                                                        |
| ------- | ------------------------------------------------------------------------------------ |
| **400** | Missing `s3_url`, download failure, empty downloaded file, corrupt/unreadable PDF |
| **422** | No page contained any configured phrase (`data` may include `total_pages_in_pdf`)    |
| **500** | Invalid pattern config (e.g. empty `PATTERN_DEFINITIONS`), or failure writing output |

## Project layout

```
pdf_filter/
├── api.py                 # Flask app, /extract endpoint
├── scanner.py             # PyMuPDF text scan + phrase matching
├── builder.py             # Build filtered PDF from matched page indices
├── keywords_embedded.py   # PATTERN_DEFINITIONS and phrase strings
├── requirements.txt
├── README.md
└── output/                # Generated filtered PDFs (created on first success)
```
