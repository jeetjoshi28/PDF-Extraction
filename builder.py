"""
builder.py — Builds the filtered output PDF from matched page indices.
"""

import fitz  # PyMuPDF
from pathlib import Path


def build_filtered_pdf(
    input_path: str,
    matched: dict,
    output_path: str,
) -> None:
    """
    Writes a new PDF that contains only the matched pages, copied as native
    pages from the source file (same content streams, layout, fonts, images —
    not redrawn or rasterized onto blank pages).

    Args:
        input_path  : path to the original PDF
        matched     : { page_index_0based: [keywords] }
        output_path : where to save the filtered PDF
    """
    # Ensure output directory exists
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        source_doc = fitz.open(input_path)
    except Exception as e:
        raise RuntimeError(f"Cannot open source PDF: {e}") from e

    output_doc = fitz.open()  # blank new document

    for page_idx in sorted(matched.keys()):
        # Copy the actual PDF page objects from the source (MuPDF insert_pdf).
        output_doc.insert_pdf(
            source_doc,
            from_page=page_idx,
            to_page=page_idx,
            links=True,
            annots=True,
        )

    try:
        output_doc.save(output_path)
    except Exception as e:
        raise RuntimeError(f"Could not save output PDF: {e}") from e
    finally:
        output_doc.close()
        source_doc.close()
