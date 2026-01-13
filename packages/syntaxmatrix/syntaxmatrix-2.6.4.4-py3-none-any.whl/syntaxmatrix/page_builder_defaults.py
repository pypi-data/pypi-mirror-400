from __future__ import annotations

import html as _html
import re as _re
from typing import Any, Dict, List


def _title_from_slug(slug: str) -> str:
    s = (slug or "").strip().replace("_", " ").replace("-", " ")
    s = _re.sub(r"\s+", " ", s).strip()
    if not s:
        return "New page"
    return s[:1].upper() + s[1:]


def make_default_layout(page_name: str, website_description: str = "") -> Dict[str, Any]:
    """Create a starter layout JSON for the drag-and-drop page builder."""
    page = (page_name or "page").strip().lower()
    desc = (website_description or "").strip()

    def sec(_id: str, _type: str, title: str, text: str, cols: int, items: List[Dict[str, Any]]):
        return {
            "id": _id,
            "type": _type,
            "title": title,
            "text": text,
            "cols": cols,
            "items": items or [],
        }

    def item(_id: str, _type: str, title: str, text: str, image_url: str = ""):
        return {
            "id": _id,
            "type": _type,
            "title": title,
            "text": text,
            "imageUrl": image_url or "",
        }

    hero_title = _title_from_slug(page)
    hero_text = desc or "Describe your offering here. Replace this text with your own message."

    return {
        "page": page,
        "sections": [
            sec(
                "sec_hero",
                "hero",
                hero_title,
                hero_text,
                1,
                [
                    item("item_hero_1", "card", "Get started", "Add a short call-to-action here.", ""),
                ],
            ),
            sec(
                "sec_features",
                "features",
                "Features",
                "Three quick reasons people choose you.",
                3,
                [
                    item("item_feat_1", "card", "Fast setup", "Be up and running quickly.", ""),
                    item("item_feat_2", "card", "Secure by design", "Built with sensible defaults.", ""),
                    item("item_feat_3", "card", "Support that cares", "We help you succeed.", ""),
                ],
            ),
            sec(
                "sec_gallery",
                "gallery",
                "Gallery",
                "Add images that show your product, team, or work.",
                3,
                [
                    item("item_gal_1", "card", "Image", "Drop an image onto this card.", ""),
                    item("item_gal_2", "card", "Image", "Drop an image onto this card.", ""),
                    item("item_gal_3", "card", "Image", "Drop an image onto this card.", ""),
                ],
            ),
            sec(
                "sec_testimonials",
                "testimonials",
                "Testimonials",
                "A couple of short quotes from customers.",
                2,
                [
                    item("item_test_1", "quote", "Customer name", "“A short customer quote goes here.”", ""),
                    item("item_test_2", "quote", "Customer name", "“Another short quote goes here.”", ""),
                ],
            ),
            sec(
                "sec_faq",
                "faq",
                "FAQ",
                "Answer the most common questions upfront.",
                2,
                [
                    item("item_faq_1", "faq", "What do you offer?", "Explain in one or two sentences.", ""),
                    item("item_faq_2", "faq", "How do I get started?", "Tell them the first step.", ""),
                ],
            ),
            sec(
                "sec_cta",
                "cta",
                "Ready to talk?",
                "Add a clear call-to-action with next steps.",
                2,
                [
                    item("item_cta_1", "card", "Book a demo", "Invite people to contact you.", ""),
                    item("item_cta_2", "card", "Email us", "Add your preferred contact method.", ""),
                ],
            ),
        ],
    }


def _esc(s: str) -> str:
    return _html.escape(s or "", quote=True)


def layout_to_html(st: Dict[str, Any]) -> str:
    """Render layout JSON into HTML snippets used by /page/<page_name>."""
    sections = st.get("sections") if isinstance(st, dict) else None
    if not isinstance(sections, list):
        return ""

    blocks: List[str] = []

    for s in sections:
        if not isinstance(s, dict):
            continue

        title = _esc(s.get("title") or "")
        text = _esc(s.get("text") or "")

        try:
            cols = int(s.get("cols") or 1)
        except Exception:
            cols = 1
        cols = max(1, min(5, cols))

        items_html: List[str] = []
        for it in (s.get("items") or []):
            if not isinstance(it, dict):
                continue

            it_title = _esc(it.get("title") or "")
            it_text = _esc(it.get("text") or "")
            img = (it.get("imageUrl") or "").strip()

            img_html = (
                f'<img src="{_esc(img)}" alt="{it_title}" style="width:100%;height:auto;border-radius:12px;">'
                if img else ""
            )

            items_html.append(
                '<div style="border:1px solid rgba(148,163,184,.25);border-radius:16px;'
                'padding:14px;background:rgba(15,23,42,.35);">'
                f'{img_html}'
                f'<h3 style="margin:10px 0 6px;font-size:1.05rem;">{it_title}</h3>'
                f'<p style="margin:0;color:#cbd5e1;line-height:1.5;">{it_text}</p>'
                '</div>'
            )

        grid = ""
        if items_html:
            joined = "\n".join(items_html)
            grid = (
                f'<div style="display:grid;gap:12px;grid-template-columns:repeat({cols}, minmax(0,1fr));">'
                f'{joined}</div>'
            )

        p = f'<p style="margin:0 0 14px;color:#cbd5e1;line-height:1.55;">{text}</p>' if text else ""

        blocks.append(
            '<section style="max-width:1100px;margin:22px auto;padding:0 14px;">'
            f'<h2 style="margin:0 0 8px;font-size:1.6rem;">{title}</h2>'
            f'{p}'
            f'{grid}'
            '</section>'
        )

    return "\n\n".join(blocks)
