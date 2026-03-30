import fitz  

def scan_pdf(
    pdf_path: str,
    patterns: dict[str, str],
) -> tuple[dict, int]:
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
