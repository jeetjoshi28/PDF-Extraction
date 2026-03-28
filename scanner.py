"""
scanner.py — Scans PDF pages for exact phrase patterns (case-insensitive).
Returns a dict of { page_index_0based: [matched_pattern_names] }
"""

import fitz  # PyMuPDF


def scan_pdf(
    pdf_path: str,
    patterns: dict[str, str],
) -> tuple[dict, int]:
    """
    Scan every page of the PDF. A page matches if its text contains the full
    phrase for a pattern (substring match, case-insensitive).

    Args:
        pdf_path: path to the PDF
        patterns: mapping of display name → exact phrase to find

    Returns:
        matched: { page_index (0-based): [list of pattern names that matched] }
        total: total number of pages in the PDF
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Could not open PDF: {e}") from e

    total_pages = len(doc)
    matched: dict[int, list[str]] = {}

    for i in range(total_pages):
        try:
            page_text = doc[i].get_text()
        except Exception:
            page_text = ""

        lower_page = page_text.lower()
        found: list[str] = []
        for name, phrase in patterns.items():
            if phrase.lower() in lower_page:
                found.append(name)

        if found:
            matched[i] = found

    doc.close()
    return matched, total_pages
