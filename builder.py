import fitz
from pathlib import Path


def build_filtered_pdf(
    input_path: str,
    matched: dict,
    output_path: str,
) -> None:
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    source_doc = fitz.open(input_path)
    output_doc = fitz.open()
    for page_idx in sorted(matched):
        output_doc.insert_pdf(
            source_doc,
            from_page=page_idx,
            to_page=page_idx,
            links=True,
            annots=True,
        )

    output_doc.save(output_path)
    output_doc.close()
    source_doc.close()
