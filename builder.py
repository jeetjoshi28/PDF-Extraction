import fitz
from pathlib import Path


def build_filtered_pdf(input_path: str, matched: dict, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with fitz.open(input_path) as src, fitz.open() as out:
        for i in sorted(matched):
            out.insert_pdf(src, from_page=i, to_page=i)

        out.save(output_path)