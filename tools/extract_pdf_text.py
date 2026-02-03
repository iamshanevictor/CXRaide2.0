from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader


def main() -> None:
    pdf_path = Path(__file__).resolve().parents[1] / "Automatic_Chest_X_Ray_Pattern_Annotation_and_Classification-2.pdf"
    reader = PdfReader(str(pdf_path))

    print(f"pages: {len(reader.pages)}")

    all_pages: list[str] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = re.sub(r"\s+", " ", text).strip()
        all_pages.append(text)
        print(f"\n--- page {i} ---")
        print(text)

    out_path = Path(__file__).resolve().parents[1] / "tools" / "pdf_text.txt"
    out_path.write_text("\n\n".join(all_pages), encoding="utf-8")
    print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    main()
