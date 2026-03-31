import fitz

def scan_pdf(pdf_path: str, patterns: dict[str, str]) -> tuple[dict, int]:
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)

        matched = {
            i: [
                name
                for name, phrase in patterns.items()
                if phrase.lower() in doc[i].get_text().lower()
            ]
            for i in range(total_pages)
            if any(phrase.lower() in doc[i].get_text().lower() for phrase in patterns.values())
        }

    return matched, total_pages