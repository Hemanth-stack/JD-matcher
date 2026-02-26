import pdfplumber
import docx
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text(filepath: str) -> str:
    """Extract plain text from a PDF, DOCX, or TXT file."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {suffix}")

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")

    elif suffix == ".pdf":
        pages = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)

    else:  # .docx
        doc = docx.Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
