"""
scanner.py — Scans PDF pages and matches keywords.
Returns a dict of { page_index_0based: [matched_keywords] }
"""

import re
import fitz  # PyMuPDF


def _text_has_term(
    search_text: str,
    term: str,
    *,
    case_sensitive: bool,
    whole_word: bool,
) -> bool:
    search_term = term if case_sensitive else term.lower()
    if whole_word:
        pattern = r"\b" + re.escape(search_term) + r"\b"
        return bool(re.search(pattern, search_text))
    return search_term in search_text


def scan_pdf(
    pdf_path: str,
    keywords: list[str],
    exclude_keywords: list[str] | None = None,
    case_sensitive: bool = False,
    whole_word: bool = False,
) -> tuple[dict, int]:
    """
    Scan every page of the PDF for keyword matches.

    If ``exclude_keywords`` is non-empty, any page where at least one exclude
    term appears is omitted from the result, even when include keywords match.

    Returns:
        matched  : { page_index (0-based): [list of matched include keywords] }
        total    : total number of pages in the PDF
    """
    exclude_keywords = exclude_keywords or []
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Could not open PDF: {e}") from e

    total_pages = len(doc)
    matched = {}

    for i in range(total_pages):
        try:
            page_text = doc[i].get_text()
        except Exception:
            page_text = ""

        search_text = page_text if case_sensitive else page_text.lower()

        if exclude_keywords:
            skip = False
            for ex in exclude_keywords:
                if _text_has_term(
                    search_text, ex, case_sensitive=case_sensitive, whole_word=whole_word
                ):
                    skip = True
                    break
            if skip:
                continue

        found = []
        for kw in keywords:
            if _text_has_term(
                search_text, kw, case_sensitive=case_sensitive, whole_word=whole_word
            ):
                found.append(kw)

        if found:
            matched[i] = found

    doc.close()
    return matched, total_pages
