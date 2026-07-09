"""Instant FAQ answers when RAG index is empty or embeddings unavailable."""

from app.schemas.common import CitationSchema

FAQ_ENTRIES: list[dict] = [
    {
        "keywords": ["apc", "charge", "fee", "processing", "cost", "price", "payment"],
        "answer": """**IJAIKE Article Processing Charges (APC)**

• **No fees** for initial submission or peer review — APC applies only after acceptance.
• **Inaugural issues:** $99/page (text and illustration pages); color figures at 2× B&W rate.
• **Formula:** APC = (formatted text pages × rate) + (figures/tables × illustration rate).
• **Package reference rates:**
  - Standard article (20 pages): **$1,000**
  - Short paper (15 pages): **$750**
  - Review article (30 pages): **$1,500**
  - Long paper (40 pages): **$2,000**
  - Special issue paper: **$800**
  - Per-page rate (accepted manuscripts): **$49/page**
• **50% discount** for papers submitted by December 30, 2025.
• **Waivers** for low-income economies, Ph.D. candidates without funding, and exceptional-impact papers — email Editor-in-Chief@ijaike.com.

Use the **APC Estimator** on this site for a personalized estimate, or visit https://ijaike.org/article-processing-charges-apc/""",
        "source": "IJAIKE — Article Processing Charges (APC)",
    },
    {
        "keywords": ["submit", "submission", "manuscript central", "where", "upload"],
        "answer": """**How to submit to IJAIKE**

1. Prepare your manuscript in **Microsoft Word (.doc/.docx)** — PDF is not accepted for initial submission.
2. Submit online at: **https://mc04.manuscriptcentral.com/jaike**
3. Use subject line: **"IJAIKE Submission – [Paper Title]"**
4. Include: title, abstract (250–350 words), keywords (7–9), main text, references, author info.

Acknowledgment email within 3–7 business days. Double-blind peer review typically takes 4–8 weeks.""",
        "source": "IJAIKE — Submission Procedure",
    },
    {
        "keywords": ["format", "formatting", "template", "font", "margin", "word"],
        "answer": """**IJAIKE formatting requirements**

• **Format:** Microsoft Word (.doc/.docx) only for submission (PDF not accepted)
• **Font:** 12-pt Times New Roman (or equivalent), double-spaced
• **Margins:** 1 inch (2.5 cm) on all sides
• **Page Numbering:** Bottom-center
• **Abstract:** 250–350 words; **Keywords:** 7–9 terms
• **References:** IEEE or APA — apply consistently
• **Figures & Tables:** Embed near first citation, resolution ≥300 dpi, sequential numbering with descriptive legends
• **Structure:** Introduction, Related Work, Methodology, Results, Discussion, Conclusion""",
        "source": "IJAIKE — Submission Requirements",
    },
    {
        "keywords": ["review", "peer", "double-blind", "reviewer", "decision"],
        "answer": """**IJAIKE peer review process**

• **Double-blind** review — author and reviewer identities are concealed.
• At least **two independent reviewers** evaluate each manuscript.
• Timeline: typically **4–8 weeks** for peer review; editorial decision within **4–6 weeks**.
• Possible decisions: Accept, Minor Revision, Major Revision, Reject.
• Reviewer reports are shared with authors in anonymized form.""",
        "source": "IJAIKE — Reviewer Anonymity Policy",
    },
    {
        "keywords": ["discount", "waiver", "special issue"],
        "answer": """**APC discounts and waivers**

• **50% APC discount** for early submissions (deadline: December 30, 2025)
• **50% waiver** for Ph.D. candidates without research grants
• **30% discount** for institutional partners
• **Special issue papers:** $800 package rate
• Request waivers at submission via **Editor-in-Chief@ijaike.com** with eligibility explanation.""",
        "source": "IJAIKE — APC Policy",
    },
]


def faq_fallback(query: str) -> tuple[str, list[CitationSchema]] | None:
    q = query.lower()
    best: dict | None = None
    best_score = 0
    for entry in FAQ_ENTRIES:
        score = sum(1 for kw in entry["keywords"] if kw in q)
        if score > best_score:
            best_score = score
            best = entry
    if not best or best_score == 0:
        return None
    citation = CitationSchema(
        document_title=best["source"],
        excerpt=best["answer"][:200] + "...",
        relevance_score=1.0,
    )
    return best["answer"], [citation]
