from pathlib import Path

from pypdf import PdfReader


def extract_pages(path: Path) -> list[dict[str, str | int]]:
    reader = PdfReader(path)
    return [
        {"page": number, "text": page.extract_text() or ""}
        for number, page in enumerate(reader.pages, start=1)
    ]
