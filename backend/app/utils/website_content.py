"""Flatten IJAIKE website JSON pages into RAG-friendly plain text."""

from __future__ import annotations

import json
from typing import Any


def _lines(text: str, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    return [f"{prefix}{line}" for line in text.strip().splitlines() if line.strip()]


def _render_list(items: list[Any], indent: int = 0) -> list[str]:
    prefix = "  " * indent
    lines: list[str] = []
    for item in items:
        if isinstance(item, str):
            lines.append(f"{prefix}- {item}")
        elif isinstance(item, dict):
            label = item.get("name") or item.get("title") or item.get("question") or item.get("role")
            if label:
                lines.append(f"{prefix}- {label}")
            for key, val in item.items():
                if key in ("name", "title", "question", "role") or val in (None, "", []):
                    continue
                if isinstance(val, str):
                    lines.append(f"{prefix}  {key.replace('_', ' ').title()}: {val}")
                elif isinstance(val, list) and all(isinstance(v, str) for v in val):
                    lines.extend(_render_list(val, indent + 2))
        else:
            lines.append(f"{prefix}- {item}")
    return lines


def _render_content_block(block: dict[str, Any], indent: int = 0) -> list[str]:
    lines: list[str] = []
    prefix = "  " * indent
    block_type = block.get("type", "")

    if block_type == "paragraph" and block.get("text"):
        lines.append(f"{prefix}{block['text']}")
    elif block_type == "list" and block.get("items"):
        lines.extend(_render_list(block["items"], indent))
    elif block_type == "subsection":
        if block.get("title"):
            lines.append(f"{prefix}{block['title']}:")
        if block.get("text"):
            lines.append(f"{prefix}{block['text']}")
        if block.get("additional"):
            lines.append(f"{prefix}{block['additional']}")
        for item in block.get("items") or []:
            lines.append(f"{prefix}- {item}")
        if block.get("note"):
            lines.append(f"{prefix}Note: {block['note']}")
        for step in block.get("steps") or []:
            lines.append(f"{prefix}- {step}")
    elif block_type == "article_type":
        name = block.get("name", "Article type")
        lines.append(f"{prefix}{name}:")
        for key, val in block.items():
            if key not in ("type", "name") and val:
                label = key.replace("_", " ").title()
                lines.append(f"{prefix}  {label}: {val}")
    elif block_type == "formula" and block.get("text"):
        lines.append(f"{prefix}Formula: {block['text']}")
    elif block_type == "deadline" and block.get("text"):
        lines.append(f"{prefix}Deadline: {block['text']}")
    elif block_type == "note" and block.get("text"):
        lines.append(f"{prefix}Note: {block['text']}")
    elif block_type == "steps" and block.get("items"):
        lines.extend(_render_list(block["items"], indent))
    elif block.get("text"):
        lines.append(f"{prefix}{block['text']}")

    return lines


def _render_section(section: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    sec_num = section.get("section_number")
    sec_title = section.get("section_title", "Section")
    heading = f"## {sec_num}. {sec_title}" if sec_num else f"## {sec_title}"
    lines.append(heading)

    content = section.get("content")
    if isinstance(content, str):
        lines.extend(_lines(content, 1))
    elif isinstance(content, list):
        if content and isinstance(content[0], dict) and content[0].get("type"):
            for block in content:
                if isinstance(block, dict):
                    lines.extend(_render_content_block(block, 1))
        elif content and isinstance(content[0], str):
            lines.extend(_render_list(content, 1))
        else:
            for block in content:
                if isinstance(block, dict):
                    lines.extend(_render_content_block(block, 1))
                elif isinstance(block, str):
                    lines.append(f"  {block}")

    if section.get("items"):
        lines.extend(_render_list(section["items"], 1))
    if section.get("additional"):
        lines.extend(_lines(section["additional"], 1))
    if section.get("methodology"):
        lines.append(f"  Methodology: {section['methodology']}")
    if section.get("closing"):
        lines.extend(_lines(section["closing"], 1))
    if section.get("links") and isinstance(section["links"], dict):
        for key, url in section["links"].items():
            lines.append(f"  {key.replace('_', ' ').title()}: {url}")

    for faq in section.get("faqs") or []:
        lines.append(f"  Q: {faq.get('question', '')}")
        lines.append(f"  A: {faq.get('answer', '')}")

    for concept in section.get("core_concepts") or []:
        lines.append(f"  {concept.get('name', 'Concept')}: {concept.get('description', '')}")

    for sub in section.get("subsections") or []:
        lines.append(f"  ### {sub.get('name', 'Subsection')}")
        if sub.get("text"):
            lines.extend(_lines(sub["text"], 2))
        if sub.get("items"):
            lines.extend(_render_list(sub["items"], 2))

    for key in ("core_topics_ai", "knowledge_engineering_topics", "applied_ai_topics", "ke_in_practice_topics"):
        if section.get(key):
            lines.append(f"  {key.replace('_', ' ').title()}:")
            lines.extend(_render_list(section[key], 2))

    for key in ("important_notes", "steps", "departments"):
        if section.get(key):
            lines.extend(_render_list(section[key], 1))

    if section.get("submission_portal"):
        lines.append(f"  Submission portal: {section['submission_portal']}")
    if section.get("deadline"):
        lines.append(f"  Deadline: {section['deadline']}")

    return lines


def _render_person(person: dict[str, Any]) -> list[str]:
    lines = [f"## {person.get('name', 'Profile')}"]
    for key in ("role", "position", "bio", "leadership_philosophy", "industry_impact", "global_collaboration", "editorial_role"):
        if person.get(key):
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {person[key]}")
    if person.get("academic_distinction"):
        lines.append(f"Academic distinction: {person['academic_distinction']}")
    if person.get("founding_editor"):
        lines.append(f"Founding editor: {person['founding_editor']}")
    if person.get("education"):
        lines.append("Education:")
        lines.extend(_render_list(person["education"], 1))
    if person.get("research_interests"):
        lines.append("Research interests:")
        lines.extend(_render_list(person["research_interests"], 1))
    if person.get("publications"):
        lines.append(f"Publications: {person['publications']}")
    if person.get("links") and isinstance(person["links"], dict):
        for key, url in person["links"].items():
            lines.append(f"{key.replace('_', ' ').title()}: {url}")
    return lines


def page_to_text(page: dict[str, Any]) -> str:
    parts: list[str] = [f"# {page.get('page_title', 'IJAIKE Page')}"]
    if page.get("url"):
        parts.append(f"Source: {page['url']}")
    if page.get("source"):
        parts.append(f"Document: {page['source']}")
    if page.get("intro"):
        parts.append("")
        parts.extend(_lines(page["intro"]))
    if page.get("note"):
        parts.append("")
        parts.append(f"Note: {page['note']}")
    if isinstance(page.get("content"), str):
        parts.append("")
        parts.extend(_lines(page["content"]))

    if page.get("target_readership"):
        parts.append("")
        parts.append("## Target Readership")
        parts.extend(_render_list(page["target_readership"], 0))
    if page.get("closing"):
        parts.append("")
        parts.extend(_lines(page["closing"]))

    if page.get("person"):
        parts.append("")
        parts.extend(_render_person(page["person"]))

    for section in page.get("sections") or []:
        parts.append("")
        parts.extend(_render_section(section))

    if page.get("special_issues"):
        parts.append("")
        parts.append("## Special Issues and Calls for Papers")
        for issue in page["special_issues"]:
            parts.append(f"- {issue.get('title', 'Special issue')}")
            if issue.get("editors"):
                parts.append(f"  Editors: {', '.join(issue['editors'])}")
            if issue.get("guest_editors"):
                parts.append(f"  Guest editors: {', '.join(issue['guest_editors'])}")
            if issue.get("download"):
                parts.append(f"  PDF: {issue['download']}")

    if page.get("contacts"):
        parts.append("")
        parts.append("## Contacts")
        for contact in page["contacts"]:
            name = contact.get("name") or contact.get("role", "Contact")
            parts.append(f"- {name}")
            for key, val in contact.items():
                if key == "name" or val in (None, "", []):
                    continue
                if isinstance(val, list):
                    parts.append(f"  {key.title()}: {', '.join(val)}")
                else:
                    parts.append(f"  {key.replace('_', ' ').title()}: {val}")

    if page.get("general_contact_emails"):
        parts.append(f"General contact: {', '.join(page['general_contact_emails'])}")
    if page.get("message"):
        parts.extend(_lines(page["message"]))

    if page.get("article_types"):
        parts.append("")
        parts.append("## Article Types")
        for article in page["article_types"]:
            parts.append(f"- {article.get('name', 'Article type')}")
            for key, val in article.items():
                if key != "name" and val:
                    parts.append(f"  {key.replace('_', ' ').title()}: {val}")

    for key in ("style_formatting", "title_page"):
        if page.get(key):
            parts.append("")
            parts.append(f"## {key.replace('_', ' ').title()}")
            parts.extend(_render_list(page[key], 0))

    if page.get("main_body") and isinstance(page["main_body"], dict):
        parts.append("")
        parts.append("## Main Body")
        for key, val in page["main_body"].items():
            label = key.replace("_", " ").title()
            parts.append(f"{label}: {val}")

    for key in ("display_items", "ethical_considerations", "references_citations"):
        if page.get(key) and isinstance(page[key], dict):
            parts.append("")
            parts.append(f"## {key.replace('_', ' ').title()}")
            for sub_key, val in page[key].items():
                parts.append(f"{sub_key.replace('_', ' ').title()}: {val}")

    if page.get("letters"):
        parts.append(f"Letters: {page['letters']}")

    return "\n".join(parts).strip() + "\n"


def page_to_text_json(page: dict[str, Any]) -> str:
    """Serialize page as compact JSON text for archival exports."""
    return json.dumps(page, ensure_ascii=False, indent=2)
