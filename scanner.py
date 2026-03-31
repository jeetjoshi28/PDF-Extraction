import fitz

def scan_pdf(pdf_path: str, patterns: dict[str, str], excluded_phrases: tuple[str, ...] = ()) -> tuple[dict, int]:
    normalized_patterns = [(name, phrase.lower()) for name, phrase in patterns.items()]
    normalized_exclusions = [phrase.lower() for phrase in excluded_phrases]

    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
        matched: dict[int, list[str]] = {}
        for i in range(total_pages):
            page_text = doc[i].get_text().lower()
            if any(phrase in page_text for phrase in normalized_exclusions):
                continue
            found = [name for name, phrase in normalized_patterns if phrase in page_text]
            if found:
                matched[i] = found

    return matched, total_pages