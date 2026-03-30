import fitz  

def scan_pdf(
    pdf_path: str,
    patterns: dict[str, str],
) -> tuple[dict, int]:
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    page_matches: dict[int, list[str]] = {}

    for page_number in range(total_pages):
        page_text = doc[page_number].get_text().lower()
        page_matches[page_number] = [
            name
            for name, phrase in patterns.items()
            if phrase.lower() in page_text
        ]

    doc.close()
    matched = {page: names for page, names in page_matches.items() if names}
    return matched, total_pages
