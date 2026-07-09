"""PDF ingestion helpers — auto-categorize IJAIKE documents."""

from pathlib import Path

from app.models.enums import DocumentCategory

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = _PROJECT_ROOT / "data" / "pdfs"

# Explicit titles for known documents
KNOWN_TITLES: dict[str, str] = {
    "S1MAuthorGuideNov2025_SC.pdf": "IJAIKE Author Guidelines (Nov 2025)",
    "S1MEditorGuideMarch2025_SC.pdf": "IJAIKE Editor Guidelines (March 2025)",
    "Reviewer Guidelines--Reviewing Process.pdf": "IJAIKE Reviewer Guidelines — Reviewing Process",
    "JAIKE Manuscript Page Length Policy.pdf": "IJAIKE Manuscript Page Length Policy",
    "IJAIKE_Formatting_for_Publication.pdf": "IJAIKE Formatting for Publication",
    "Roles-and-Responsibilities-of-Guest-Editors-for-IJAIKE.pdf": "Roles and Responsibilities of Guest Editors for IJAIKE",
    "Call-for-Papers-Inaugural-Issues-of-IJAIKE-Journal-2.pdf": "Call for Papers — Inaugural Issues of IJAIKE Journal",
}


def title_for_pdf(filename: str) -> str:
    if filename in KNOWN_TITLES:
        return KNOWN_TITLES[filename]
    stem = Path(filename).stem
    if stem.lower().startswith("call-for-papers") or stem.lower().startswith("call-for-papers"):
        name = stem.replace("Call-for-Papers-", "").replace("Call-For-Papers-", "")
        name = name.replace("-", " ").replace("_", " ")
        return f"Call for Papers — {name}"
    return stem.replace("-", " ").replace("_", " ")


def category_for_pdf(filename: str) -> DocumentCategory:
    lower = filename.lower()
    if "call-for-papers" in lower:
        return DocumentCategory.CALL_FOR_PAPERS
    if "special-issue" in lower or "inaugural" in lower:
        return DocumentCategory.SPECIAL_ISSUE
    if "formatting" in lower or "author" in lower or "manuscript" in lower or "s1mauth" in lower:
        return DocumentCategory.AUTHOR_GUIDELINES
    if "editor" in lower or "reviewer" in lower or "guest" in lower or "roles" in lower:
        return DocumentCategory.EDITORIAL_POLICIES
    if "apc" in lower:
        return DocumentCategory.APC_POLICY
    return DocumentCategory.OTHER


def discover_pdf_sources() -> list[dict]:
    sources: list[dict] = []
    if not PDF_DIR.exists():
        return sources
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        sources.append({
            "path": pdf,
            "title": title_for_pdf(pdf.name),
            "category": category_for_pdf(pdf.name),
        })
    return sources
