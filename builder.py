import fitz
from pathlib import Path


def build_filtered_pdf(
    input_path: str,
    matched: dict,
    output_path: str,
) -> None:
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        source_doc = fitz.open(input_path)
    except Exception as e:
        raise RuntimeError(f"Cannot open source PDF: {e}") from e

    output_doc = fitz.open()
    for page_idx in sorted(matched.keys()):
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
