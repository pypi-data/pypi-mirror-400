from __future__ import annotations

import hashlib
import io
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import requests
from PIL import Image
from bs4 import BeautifulSoup

PIXABAY_API_URL = "https://pixabay.com/api/"


# ─────────────────────────────────────────────────────────
# Icons (inline SVG)
# ─────────────────────────────────────────────────────────
_ICON_SVGS: Dict[str, str] = {
    "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
             '<path d="M12 2l1.2 6.2L20 12l-6.8 3.8L12 22l-1.2-6.2L4 12l6.8-3.8L12 2z"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
              '<path d="M12 2l7 4v6c0 5-3.5 9-7 10-3.5-1-7-5-7-10V6l7-4z"/></svg>',
    "stack": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
             '<path d="M12 2l9 5-9 5-9-5 9-5z"/><path d="M3 12l9 5 9-5"/><path d="M3 17l9 5 9-5"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
             '<path d="M3 3v18h18"/><path d="M7 14v4"/><path d="M12 10v8"/><path d="M17 6v12"/></svg>',
    "rocket": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
              '<path d="M5 13l4 6 6-4c6-4 5-12 5-12S13 2 9 8l-4 5z"/><path d="M9 8l7 7"/>'
              '<path d="M5 13l-2 2"/><path d="M11 19l-2 2"/></svg>',
    "plug": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
            '<path d="M9 2v6"/><path d="M15 2v6"/><path d="M7 8h10"/>'
            '<path d="M12 8v7a4 4 0 0 1-4 4H7"/><path d="M12 8v7a4 4 0 0 0 4 4h1"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
             '<path d="M5 12h12"/><path d="M13 6l6 6-6 6"/></svg>',
}


def _slug_title(slug: str) -> str:
    s = (slug or "").strip().replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return (s[:1].upper() + s[1:]) if s else "New page"


def _short_site_desc(desc: str, limit: int = 220) -> str:
    d = (desc or "").strip()
    if not d:
        return ""
    d = re.sub(r"\s+", " ", d).strip()
    if len(d) <= limit:
        return d
    cut = d[:limit]
    # cut at end of sentence if possible
    m = re.search(r"[.!?]\s", cut)
    if m:
        return cut[:m.end()].strip()
    return cut.rstrip() + "…"


def _page_kind(slug: str) -> str:
    s = (slug or "").lower()
    if any(k in s for k in ["service", "services", "solutions", "what-we-do"]):
        return "services"
    if "about" in s or "company" in s:
        return "about"
    if "pricing" in s or "plans" in s:
        return "pricing"
    if "contact" in s or "get-in-touch" in s:
        return "contact"
    if "docs" in s or "documentation" in s:
        return "docs"
    return "generic"


def build_layout_for_page(page_slug: str, website_description: str) -> Dict[str, Any]:
    """
    Returns builder layout JSON with non-placeholder copy that fits the page title.
    Includes optional `imgQuery` fields which we can use to fetch Pixabay images.
    """
    slug = (page_slug or "page").strip().lower()
    title = _slug_title(slug)
    kind = _page_kind(slug)
    site_blurb = _short_site_desc(website_description)

    def sec(_id: str, _type: str, title_: str, text: str, cols: int, items: List[Dict[str, Any]]):
        return {"id": _id, "type": _type, "title": title_, "text": text, "cols": cols, "items": items or []}

    def item(_id: str, _type: str, title_: str, text: str, icon: str = "", img_query: str = ""):
        out = {"id": _id, "type": _type, "title": title_, "text": text, "imageUrl": ""}
        if icon:
            out["icon"] = icon
        if img_query:
            out["imgQuery"] = img_query
        return out

    # Some SyntaxMatrix-aware phrasing (works fine for other clients too)
    if kind == "services":
        hero_text = (
            "Practical AI engineering services: retrieval systems, data workflows, and deployable web UI components."
            if not site_blurb else site_blurb
        )
        return {
            "page": slug,
            "sections": [
                sec(
                    "sec_hero",
                    "hero",
                    title,
                    hero_text,
                    1,
                    [
                        item(
                            "item_hero_img",
                            "card",
                            "Build faster with confidence",
                            "From strategy to deployment, we ship production-grade features with clean, maintainable code.",
                            "rocket",
                            "ai dashboard software team",
                        ),
                    ],
                ),
                sec(
                    "sec_services",
                    "features",
                    "What we can deliver",
                    "Core capabilities tailored to your organisation and your users.",
                    3,
                    [
                        item("svc_1", "card", "RAG systems & search", "Chunking, embeddings, vector stores, and evaluation.", "stack", "vector database ai search"),
                        item("svc_2", "card", "AI assistants in your app", "Streaming chat, tools, history, and guardrails.", "spark", "chatbot interface ai assistant"),
                        item("svc_3", "card", "Admin panel & content ops", "Page management, media handling, audit trails.", "shield", "admin dashboard web app"),
                        item("svc_4", "card", "ML lab & analytics", "EDA, modelling, visualisations, downloadable results.", "chart", "data analytics dashboard charts"),
                        item("svc_5", "card", "Integrations", "SQL databases, storage buckets, PDFs, CSV, APIs.", "plug", "software integration api"),
                        item("svc_6", "card", "Deployment support", "Docker, Gunicorn, GCP Cloud Run patterns.", "rocket", "cloud deployment devops"),
                    ],
                ),
                sec(
                    "sec_process",
                    "features",
                    "How we work",
                    "A simple process that keeps delivery predictable.",
                    3,
                    [
                        item("step_1", "card", "Scope", "Clarify outcomes, constraints, and success checks.", "spark", ""),
                        item("step_2", "card", "Build", "Implement in small milestones with review points.", "stack", ""),
                        item("step_3", "card", "Ship", "Deploy and document so your team can operate it.", "rocket", ""),
                    ],
                ),
                sec(
                    "sec_gallery",
                    "gallery",
                    "In action",
                    "A few visuals that match the theme of this page.",
                    3,
                    [
                        item("gal_1", "card", "Product UI", "Example UI visual.", "", "modern web app interface"),
                        item("gal_2", "card", "Data work", "Example analytics visual.", "", "data visualisation charts"),
                        item("gal_3", "card", "Team", "Example team visual.", "", "software team working"),
                    ],
                ),
                sec(
                    "sec_faq",
                    "faq",
                    "FAQ",
                    "Common questions we get before starting.",
                    2,
                    [
                        item("faq_1", "faq", "Do you work with existing systems?", "Yes. We can integrate with your current stack and data sources.", "", ""),
                        item("faq_2", "faq", "Can we start small?", "Yes. We can begin with one page/module and scale from there.", "", ""),
                    ],
                ),
                sec(
                    "sec_cta",
                    "cta",
                    "Ready to start?",
                    "Tell us what you want this page or feature to achieve, and we'll propose the quickest path.",
                    2,
                    [
                        item("cta_1", "card", "Book a demo", "See a working flow end-to-end.", "arrow", ""),
                        item("cta_2", "card", "Contact us", "Share requirements and timelines.", "arrow", ""),
                    ],
                ),
            ],
        }

    # Generic page (still modern copy)
    hero_text = site_blurb or "A modern page generated from your website description and the page title."
    return {
        "page": slug,
        "sections": [
            sec("sec_hero", "hero", title, hero_text, 1, [
                item("item_hero_img", "card", "A clear headline that matches the page", "Add a short, action-focused summary here.", "spark", f"{title} hero background"),
            ]),
            sec("sec_features", "features", "Highlights", "Three to six key points for this page topic.", 3, [
                item("f1", "card", "Clear value", "Explain the benefit in one sentence.", "spark", f"{title} concept"),
                item("f2", "card", "Trust signals", "Show proof, experience, or credibility.", "shield", f"{title} professional"),
                item("f3", "card", "Next step", "Give people a simple action to take.", "arrow", f"{title} call to action"),
            ]),
            sec("sec_gallery", "gallery", "Gallery", "Relevant imagery for the topic.", 3, [
                item("g1", "card", "Image", "Drop or auto-fetch an image.", "", f"{title} abstract"),
                item("g2", "card", "Image", "Drop or auto-fetch an image.", "", f"{title} modern"),
                item("g3", "card", "Image", "Drop or auto-fetch an image.", "", f"{title} business"),
            ]),
            sec("sec_cta", "cta", "Continue", "A short call-to-action to guide the user.", 2, [
                item("c1", "card", "Get started", "Tell people what to do next.", "arrow", ""),
                item("c2", "card", "Learn more", "Point to documentation or contact.", "arrow", ""),
            ]),
        ],
    }


# ─────────────────────────────────────────────────────────
# Pixabay: search + download once + resize
# ─────────────────────────────────────────────────────────
def _is_pixabay_url(url: str) -> bool:
    u = (url or "").strip().lower()
    return u.startswith("https://") and ("pixabay.com" in u)


def _fetch_bytes(url: str, timeout: int = 20) -> bytes:
    if not _is_pixabay_url(url):
        raise ValueError("Only Pixabay URLs are allowed")
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()
    return r.content


def _save_image_bytes(img_bytes: bytes, out_path_no_ext: str, max_width: int = 1920) -> Tuple[str, int, int]:
    img = Image.open(io.BytesIO(img_bytes))
    img.load()

    if img.width > int(max_width or 1920):
        ratio = (int(max_width) / float(img.width))
        new_h = max(1, int(round(img.height * ratio)))
        img = img.resize((int(max_width), new_h), Image.LANCZOS)

    has_alpha = ("A" in img.getbands())
    ext = ".png" if has_alpha else ".jpg"
    out_path = out_path_no_ext + ext
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if ext == ".jpg":
        rgb = img.convert("RGB") if img.mode != "RGB" else img
        rgb.save(out_path, "JPEG", quality=85, optimise=True, progressive=True)
    else:
        img.save(out_path, "PNG", optimise=True)

    return out_path, int(img.width), int(img.height)


def _pixabay_search(api_key: str, query: str, *, per_page: int = 12, timeout: int = 15) -> List[Dict[str, Any]]:
    if not api_key:
        return []
    q = (query or "").strip()
    q = re.sub(r"\s+", " ", q)[:100]
    if not q:
        return []

    params = {
        "key": api_key,
        "q": q,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "editors_choice": "true",
        "order": "popular",
        "per_page": max(3, min(200, int(per_page or 12))),
        "page": 1,
    }
    r = requests.get(PIXABAY_API_URL, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json() or {}
    return data.get("hits") or []


def fill_layout_images_from_pixabay(
    layout: Dict[str, Any],
    *,
    api_key: str,
    client_dir: str,
    max_width: int = 1920,
    max_downloads: int = 8,
) -> Dict[str, Any]:
    """
    Mutates/returns layout: fills `imageUrl` fields by downloading images into:
      uploads/media/images/imported/
    Uses `imgQuery` if present.
    """
    if not api_key or not layout:
        return layout

    imported_dir = os.path.join(client_dir, "uploads", "media", "images", "imported")
    os.makedirs(imported_dir, exist_ok=True)

    used_ids = set()
    downloads = 0

    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    for s in sections:
        if downloads >= max_downloads:
            break
        items = s.get("items") if isinstance(s.get("items"), list) else []
        for it in items:
            if downloads >= max_downloads:
                break
            if (it.get("imageUrl") or "").strip():
                continue

            q = (it.get("imgQuery") or "").strip()
            if not q:
                continue

            hits = _pixabay_search(api_key, q)
            if not hits:
                continue

            # choose first unused hit
            chosen = None
            for h in hits:
                pid = int(h.get("id") or 0)
                if pid and pid not in used_ids:
                    chosen = h
                    break
            if not chosen:
                continue

            pid = int(chosen.get("id") or 0)
            used_ids.add(pid)

            web_u = str(chosen.get("webformatURL") or "").strip()
            large_u = str(chosen.get("largeImageURL") or "").strip()

            if not web_u:
                continue

            base = os.path.join(imported_dir, f"pixabay-{pid}")
            # download-once
            existing = None
            for ext in (".jpg", ".png"):
                p = base + ext
                if os.path.exists(p):
                    existing = p
                    break

            if existing:
                rel = os.path.relpath(existing, os.path.join(client_dir, "uploads", "media")).replace("\\", "/")
                it["imageUrl"] = f"/uploads/media/{rel}"
                continue

            # fetch webformat first; if it’s small and large exists, use the larger one
            try:
                b1 = _fetch_bytes(web_u)
                img1 = Image.open(io.BytesIO(b1))
                img1.load()
                chosen_bytes = b1

                if large_u:
                    try:
                        b2 = _fetch_bytes(large_u)
                        img2 = Image.open(io.BytesIO(b2))
                        img2.load()
                        if img2.width > img1.width:
                            chosen_bytes = b2
                    except Exception:
                        pass

                saved_path, _, _ = _save_image_bytes(chosen_bytes, base, max_width=max_width)
                rel = os.path.relpath(saved_path, os.path.join(client_dir, "uploads", "media")).replace("\\", "/")
                it["imageUrl"] = f"/uploads/media/{rel}"
                downloads += 1
            except Exception:
                continue

    return layout


import re
from typing import Dict, Any, Optional

def _extract_hero_image_url_from_layout(layout: Dict[str, Any]) -> str:
    """Find hero image URL from the saved layout JSON (builder)."""
    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    for s in sections:
        if not isinstance(s, dict):
            continue
        if (s.get("type") or "").lower() != "hero":
            continue

        img_url = (s.get("imageUrl") or "").strip()
        if img_url:
            return img_url

        items = s.get("items") if isinstance(s.get("items"), list) else []
        if items and isinstance(items[0], dict):
            img_url = (items[0].get("imageUrl") or "").strip()
            if img_url:
                return img_url

    return ""


def patch_first_background_image(html: str, new_url: str) -> str:
    """
    Patch ONLY the first background-image/background url(...) found in the existing HTML.
    This avoids regenerating HTML/CSS (which is what is changing your fonts/colours).
    """
    if not html or not new_url:
        return html

    # 1) background-image: url(...)
    pat1 = re.compile(r'background-image\s*:\s*url\((["\']?)[^)]*\1\)', re.IGNORECASE)
    out, n = pat1.subn(f'background-image:url("{new_url}")', html, count=1)
    if n:
        return out

    # 2) background: ... url(...)
    pat2 = re.compile(r'(background\s*:\s*[^;]*url\((["\']?))([^)]+)(\2\))', re.IGNORECASE)
    def _repl(m: re.Match) -> str:
        return m.group(1) + new_url + m.group(4)

    out, n = pat2.subn(_repl, html, count=1)
    if n:
        return out

    # 3) If nothing matched, inject a tiny override (best-effort)
    inject = (
        f'<style id="smx-hero-bg-override">'
        f'.hero-bg{{background-image:url("{new_url}") !important;}}'
        f'.hero{{background-image:url("{new_url}") !important;}}'
        f'</style>'
    )
    if "</head>" in html:
        return html.replace("</head>", inject + "</head>", 1)
    return inject + html


def _set_text(node, new_text: str) -> bool:
    if not node:
        return False
    new_text = (new_text or "").strip()
    if not new_text:
        return False
    node.clear()
    node.append(new_text)
    return True


def _html_escape(s: str) -> str:
    s = s or ""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )


def patch_section_titles_and_intros(existing_html: str, layout: Dict[str, Any]) -> str:
    """
    Patch ONLY section <h2> titles + the first <p> intro under each <h2>,
    across the whole page, matching sections BY ORDER.
    Does NOT regenerate HTML/CSS.
    """
    if not existing_html or not isinstance(layout, dict):
        return existing_html

    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    layout_non_hero = [
        s for s in sections
        if isinstance(s, dict) and (s.get("type") or "").lower() != "hero"
    ]
    if not layout_non_hero:
        return existing_html

    # Split into <section> blocks (non-greedy)
    sec_pat = re.compile(r"(<section\b[^>]*>)(.*?)(</section>)", re.IGNORECASE | re.DOTALL)
    blocks = list(sec_pat.finditer(existing_html))
    if not blocks:
        return existing_html

    out_parts = []
    last_end = 0
    nonhero_index = 0

    for m in blocks:
        open_tag = m.group(1)
        inner = m.group(2)
        close_tag = m.group(3)

        # Keep everything before this section unchanged
        out_parts.append(existing_html[last_end:m.start()])
        last_end = m.end()

        # Skip hero sections (don’t count them against non-hero layout sections)
        if "hero" in open_tag.lower():
            out_parts.append(open_tag + inner + close_tag)
            continue

        if nonhero_index >= len(layout_non_hero):
            out_parts.append(open_tag + inner + close_tag)
            continue

        s = layout_non_hero[nonhero_index]
        nonhero_index += 1

        new_title = (s.get("title") or "").strip()
        new_text = (s.get("text") or "").strip()

        patched_inner = inner

        # 1) Patch first <h2> inside this section
        if new_title:
            h2_pat = re.compile(r"(<h2\b[^>]*>)(.*?)(</h2>)", re.IGNORECASE | re.DOTALL)
            patched_inner, n_h2 = h2_pat.subn(
                lambda mm: mm.group(1) + _html_escape(new_title) + mm.group(3),
                patched_inner,
                count=1
            )

        # 2) Patch the first <p> AFTER </h2> (section intro)
        if new_text:
            # Only look in the region after the first </h2>, so we don’t edit card paragraphs
            split = re.split(r"(</h2>)", patched_inner, maxsplit=1, flags=re.IGNORECASE)
            if len(split) == 3:
                before_h2 = split[0] + split[1]
                after_h2 = split[2]

                p_pat = re.compile(r"(<p\b[^>]*>)(.*?)(</p>)", re.IGNORECASE | re.DOTALL)
                after_h2, n_p = p_pat.subn(
                    lambda mm: mm.group(1) + _html_escape(new_text) + mm.group(3),
                    after_h2,
                    count=1
                )

                patched_inner = before_h2 + after_h2

        out_parts.append(open_tag + patched_inner + close_tag)

    # Append trailing HTML after the last section
    out_parts.append(existing_html[last_end:])
    return "".join(out_parts)


def patch_page_from_layout(existing_html: str, layout: Dict[str, Any]) -> str:
    """
    Patch ONLY text/image values in the existing HTML using the builder layout JSON.
    Does NOT regenerate HTML/CSS, so it won’t change fonts/palette/structure.
    """
    if not existing_html or not isinstance(layout, dict):
        return existing_html

    soup = BeautifulSoup(existing_html, "html.parser")

    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []

    # ---------- HERO ----------
    hero_layout = None
    for s in sections:
        if isinstance(s, dict) and (s.get("type") or "").lower() == "hero":
            hero_layout = s
            break

    if hero_layout:
        hero_title = (hero_layout.get("title") or "").strip()
        hero_text = (hero_layout.get("text") or "").strip()
        hero_img = (hero_layout.get("imageUrl") or "").strip()

        # Prefer patching hero background first (your existing logic)
        if hero_img:
            from syntaxmatrix.page_builder_generation import patch_first_background_image
            existing_html = patch_first_background_image(str(soup), hero_img)
            soup = BeautifulSoup(existing_html, "html.parser")

        # Patch hero headline + hero paragraph (without changing structure)
        h1 = soup.find("h1")
        if hero_title and h1:
            _set_text(h1, hero_title)

        # Find the first <p> after the <h1> within the same container
        if hero_text and h1:
            p = None
            for sib in h1.find_all_next(["p"], limit=6):
                # ignore very short “kicker” lines
                txt = sib.get_text(" ", strip=True)
                if len(txt) >= 25:
                    p = sib
                    break
            if p:
                _set_text(p, hero_text)

    # ---------- OTHER SECTIONS (titles + intro text only) ----------
    layout_non_hero = [s for s in sections if isinstance(s, dict) and (s.get("type") or "").lower() != "hero"]

    # Collect candidate section headings in the existing HTML
    headings = []
    for h in soup.find_all(["h2", "h3"]):
        if h.find_parent(["header", "nav", "footer"]) is not None:
            continue
        if not h.get_text(strip=True):
            continue
        headings.append(h)

    for i, s in enumerate(layout_non_hero):
        if i >= len(headings):
            break

        title = (s.get("title") or "").strip()
        text = (s.get("text") or "").strip()

        h = headings[i]
        if title:
            _set_text(h, title)

        if text:
            # patch the first <p> after this heading (within the same section container)
            p = None
            for sib in h.find_all_next(["p"], limit=8):
                if sib.find_parent(["header", "nav", "footer"]) is not None:
                    continue
                # stop if we hit the next heading before finding a paragraph
                if sib.find_previous(["h2", "h3"]) is not h:
                    break
                p = sib
                break
            if p:
                _set_text(p, text)

    return str(soup)


def _css_safe_hex(c: str) -> str:
    c = (c or "").strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", c)
    if not m:
        return ""
    hx = m.group(0).lower()
    if len(hx) == 4:
        hx = "#" + "".join([ch * 2 for ch in hx[1:]])
    return hx


def _hex_to_rgba(hx: str, a: float) -> str:
    hx = _css_safe_hex(hx)
    if not hx:
        return ""
    r = int(hx[1:3], 16)
    g = int(hx[3:5], 16)
    b = int(hx[5:7], 16)
    a = float(a)
    if a < 0:
        a = 0.0
    if a > 1:
        a = 1.0
    return f"rgba({r},{g},{b},{a:.3f})"


def _css_safe_font(ff: str) -> str:
    ff = (ff or "").strip()
    if not ff:
        return ""
    bad = ["{", "}", ";", "<", ">", "\n", "\r"]
    if any(b in ff for b in bad):
        return ""
    return ff


def _theme_style_from_layout(layout: Dict[str, Any]) -> str:
    theme = layout.get("theme") if isinstance(layout.get("theme"), dict) else {}
    if not theme:
        return ""

    font_body = _css_safe_font(theme.get("fontBody") or theme.get("bodyFont") or theme.get("font_body") or "")
    font_head = _css_safe_font(theme.get("fontHeading") or theme.get("headingFont") or theme.get("font_heading") or "")

    accent = _css_safe_hex(theme.get("accent") or "")
    fg = _css_safe_hex(theme.get("fg") or "")
    mut = _css_safe_hex(theme.get("mut") or "")
    bg = _css_safe_hex(theme.get("bg") or "")

    if not any([font_body, font_head, accent, fg, mut, bg]):
        return ""

    lines = []
    lines.append(".smxp{")
    if fg:
        lines.append(f"  --fg:{fg};")
        lines.append("  color:var(--fg);")
    if mut:
        lines.append(f"  --mut:{mut};")
    if bg:
        lines.append(f"  --bg:{bg};")
        lines.append("  background:var(--bg);")
    if font_body:
        lines.append(f"  font-family:{font_body};")
    lines.append("}")

    if font_head:
        lines.append(f".smxp h1,.smxp h2,.smxp h3{{font-family:{font_head};}}")

    if accent:
        soft = _hex_to_rgba(accent, 0.12)
        if soft:
            lines.append(f".smxp .btn{{background:{soft};}}")
        lines.append(f".smxp a{{color:{accent};}}")

    css = "\n".join(lines)
    return f'<style id="smx-theme" data-smx="theme">\\n{css}\\n</style>'

# ─────────────────────────────────────────────────────────
# Compile layout JSON → modern HTML with animations
# ─────────────────────────────────────────────────────────
def compile_layout_to_html(layout: Dict[str, Any], *, page_slug: str) -> str:
    page_id = re.sub(r"[^a-z0-9\-]+", "-", (page_slug or "page").lower()).strip("-") or "page"

    css = """
    <style>
        .smxp{--r:18px;--bd:rgba(148,163,184,.28);--mut:#94a3b8;--fg:#0f172a;--card:rgba(255,255,255,.72);
        .smxp{
            --r:18px;
            --bd: rgba(148,163,184,.25);
            --fg: #0f172a;
            --mut: #475569;                 /* <- darker, readable */
            --card: rgba(255,255,255,.78);
            --bg: #f8fafc;
            font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
            background: var(--bg);
            color: var(--fg);
            overflow-x: clip;
        }
        @media (prefers-color-scheme: dark){
            .smxp{
                --fg:#e2e8f0;
                --mut:#a7b3c6;
                --card:rgba(2,6,23,.45);
                --bg: radial-gradient(circle at 20% 10%, rgba(30,64,175,.25), rgba(2,6,23,.95) 55%);
                --bd: rgba(148,163,184,.18);
            }
        }

        font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; color: var(--fg); }
        @media (prefers-color-scheme: dark){
        .smxp{--fg:#e2e8f0;--card:rgba(2,6,23,.45);--bd:rgba(148,163,184,.18);--mut:#a7b3c6;}
        }
        .smxp a{color:inherit}
        .smxp .wrap{max-width:1120px;margin:0 auto;padding:0 18px}
        .smxp .sec{padding:56px 0}
        .smxp .kicker{color:var(--mut);font-size:.95rem;margin:0 0 8px}
        .smxp h1{font-size:clamp(2rem,3.4vw,3.2rem);line-height:1.08;margin:0 0 12px}
        .smxp h2{font-size:clamp(1.4rem,2.2vw,2rem);margin:0 0 10px}
        .smxp p{margin:0;color:var(--mut);line-height:1.6}
        .smxp .hero{padding:72px 0 46px}
        .smxp .heroGrid{display:grid;grid-template-columns:1.15fr .85fr;gap:18px;align-items:center}
        @media (max-width: 860px){.smxp .heroGrid{grid-template-columns:1fr}}
        .smxp .heroCard{border:1px solid var(--bd);border-radius:var(--r);background:var(--card);padding:14px}
        .smxp .btnRow{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
        .smxp .btn{display:inline-flex;gap:8px;align-items:center;border-radius:999px;padding:10px 14px;
        border:1px solid var(--bd);text-decoration:none;background:rgba(99,102,241,.12)}
        .smxp .btn:hover{transform:translateY(-1px)}
        .smxp .grid{display:grid;gap:12px}
        .smxp .card{border:1px solid var(--bd);border-radius:var(--r);background:var(--card);padding:14px;min-width:0}
        .smxp .card h3{margin:10px 0 6px;font-size:1.05rem}
        .smxp .icon{width:20px;height:20px;opacity:.9}
        .smxp img{width:100%;height:auto;border-radius:calc(var(--r) - 6px);display:block}
        .smxp .reveal{opacity:0;transform:translateY(14px);transition:opacity .55s ease, transform .55s ease}
        .smxp .reveal.in{opacity:1;transform:none}

        .smxp .hero{ padding:0; }
        .smxp .hero-banner{
        position:relative;
        width:100%;
        min-height:clamp(380px, 60vh, 680px);
        display:flex;
        align-items:flex-end;
        overflow:hidden;
        }
        .smxp .hero-bg{
        position:absolute; inset:0;
        background-position:center;
        background-size:cover;
        background-repeat:no-repeat;
        transform:scale(1.02);
        filter:saturate(1.02);
        }
        .smxp .hero-overlay{
            position:absolute; inset:0;
            background:linear-gradient(90deg,
                rgba(2,6,23,.62) 0%,
                rgba(2,6,23,.40) 42%,
                rgba(2,6,23,.14) 72%,
                rgba(2,6,23,.02) 100%
            );
        }
        @media (max-width: 860px){
            .smxp .hero-overlay{
                background:linear-gradient(180deg,
                rgba(2,6,23,.16) 0%,
                rgba(2,6,23,.55) 70%,
                rgba(2,6,23,.70) 100%
                );
            }
        }
        .smxp .hero-content{ position:relative; width:100%; padding:72px 18px 48px; }
        .smxp .hero-panel{
        max-width:760px;
        border:1px solid var(--bd);
        background:rgba(255,255,255,.80);
        border-radius:var(--r);
        padding:18px;
        backdrop-filter: blur(10px);
        }
        @media (prefers-color-scheme: dark){
        .smxp .hero-panel{ background:rgba(2,6,23,.58); }
        }
        .smxp .lead{ margin-top:10px; font-size:1.05rem; line-height:1.65; }

    </style>
    """.strip()

    js = f"""
    <script>
        (function(){{
        const root = document.getElementById("smxp-{page_id}");
        if(!root) return;
        const els = root.querySelectorAll(".reveal");
        const io = new IntersectionObserver((entries)=>{{
            entries.forEach(e=>{{ if(e.isIntersecting) e.target.classList.add("in"); }});
        }}, {{ threshold: 0.12 }});
        els.forEach(el=>io.observe(el));
        }})();
    </script>
    """.strip()

    def esc(s: str) -> str:
        s = s or ""
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s = s.replace('"', "&quot;").replace("'", "&#39;")
        return s

    def icon_svg(name: str) -> str:
        svg = _ICON_SVGS.get((name or "").strip().lower())
        if not svg:
            return ""
        return f'<span class="icon">{svg}</span>'

    parts: List[str] = [f'<div class="smxp" id="smxp-{page_id}">', css]
    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []

    # Map first section id by type (used for default Hero CTA anchors)
    sec_id_by_type: Dict[str, str] = {}
    for _s in sections:
        if not isinstance(_s, dict):
            continue
        _t = str(_s.get("type") or "").lower().strip()
        if not _t or _t in sec_id_by_type:
            continue
        _sid = str(_s.get("id") or "").strip() or f"sec_{_t}"
        sec_id_by_type[_t] = _sid

    def safe_href(h: str) -> str:
        h = (h or "").strip()
        if not h:
            return ""
        low = h.lower()
        if low.startswith("javascript:") or low.startswith("data:"):
            return ""
        return h

    for s in sections:
        stype = (s.get("type") or "section").lower()
        title = esc(s.get("title") or "")
        text = esc(s.get("text") or "")
        items = s.get("items") if isinstance(s.get("items"), list) else []
        sec_dom_id = (s.get("id") or "").strip()
        if not sec_dom_id:
            sec_dom_id = "sec_hero" if stype == "hero" else f"sec_{stype}"

        #############################################################################################################
        # Ensure every section has a stable DOM id so patch_page_publish can target it.
        sec_dom_id = (s.get("id") or "").strip()
        if not sec_dom_id:
            sec_dom_id = "sec_hero" if stype == "hero" else f"sec_{stype}"
        sec_id_attr = f' id="{esc(sec_dom_id)}"'
        
        # HERO
        if stype == "hero":
            img_url = (s.get("imageUrl") or "").strip()
            if not img_url and items and isinstance(items[0], dict):
                img_url = (items[0].get("imageUrl") or "").strip()

            bg_style = f' style="background-image:url(\'{esc(img_url)}\')"' if img_url else ""

            # ---------------------------
            # HERO CTA buttons (NO /admin links)
            # ---------------------------
            # --- Hero CTAs: render ONLY if user explicitly set hrefs ---
            cta1_label = (s.get("heroCta1Label") or "").strip()
            cta2_label = (s.get("heroCta2Label") or "").strip()

            cta1_href = safe_href(str(s.get("heroCta1Href") or "")) if "heroCta1Href" in s else ""
            cta2_href = safe_href(str(s.get("heroCta2Href") or "")) if "heroCta2Href" in s else ""

            btns = []
            if cta1_href:
                btns.append(
                    f'<a class="btn" data-smx="hero-cta" data-cta="1" href="{esc(cta1_href)}">'
                    f'<span class="icon">{_ICON_SVGS["arrow"]}</span>{esc(cta1_label or "Button")}</a>'
                )
            if cta2_href:
                btns.append(
                    f'<a class="btn" data-smx="hero-cta" data-cta="2" href="{esc(cta2_href)}">'
                    f'<span class="icon">{_ICON_SVGS["arrow"]}</span>{esc(cta2_label or "Button")}</a>'
                )

            btn_row_html = f'<div class="btnRow">{"".join(btns)}</div>' if btns else ""

            parts.append(
                f'''
                <section id="{esc(sec_dom_id)}" class="hero hero-banner">
                    <div class="hero-bg"{bg_style}></div>
                    <div class="hero-overlay"></div>
                    <div class="wrap hero-content">
                        <div class="hero-panel reveal">
                            <p class="kicker">Generated page</p>
                            <h1>{title}</h1>
                            <p class="lead">{text}</p>
                            {btn_row_html}
                        </div>
                    </div>
                </section>
                '''.strip()
            )
            continue
        ####################################################################################################
        # Others
        try:
            cols = int(s.get("cols") or 3)
        except Exception:
            cols = 3
        cols = max(1, min(5, cols))

        cards: List[str] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            it_title = esc(it.get("title") or "")
            it_text = esc(it.get("text") or "")
            img = (it.get("imageUrl") or "").strip()
            ic = icon_svg(it.get("icon") or "")

            img_html = f'<img loading="lazy" decoding="async" src="{esc(img)}" alt="{it_title}">' if img else ""
            cards.append(
                f'''
                <div class="card reveal">
                {img_html}
                <div style="display:flex;gap:10px;align-items:center;margin-top:{'10px' if img_html else '0'};">
                    {ic}
                    <h3 style="margin:0">{it_title}</h3>
                </div>
                <p style="margin-top:8px">{it_text}</p>
                </div>
                '''.strip()
            )

        grid_html = (
            f'<div class="grid" style="grid-template-columns:repeat({cols}, minmax(0, 1fr));">'
            + "\n".join(cards) +
            "</div>"
        ) if cards else ""

        parts.append(
            f'''
            <section id="{esc(sec_dom_id)}" class="sec">
            <div class="wrap">
                <h2 class="reveal">{title}</h2>
                {'<p class="reveal" style="margin-bottom:14px;">'+text+'</p>' if text else ''}
                {grid_html}
            </div>
            </section>
            '''.strip()
        )

    parts.append(js)
    parts.append("</div>")
    return "\n\n".join(parts)


from bs4 import BeautifulSoup
from typing import Dict, Any, List, Tuple

def _layout_non_hero_sections(layout: Dict[str, Any]) -> List[Dict[str, Any]]:
    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    out = []
    for s in sections:
        if not isinstance(s, dict):
            continue
        if (s.get("type") or "").lower() == "hero":
            continue
        out.append(s)
    return out


def _layout_hero_section(layout: Dict[str, Any]) -> Dict[str, Any] | None:
    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    for s in sections:
        if isinstance(s, dict) and (s.get("type") or "").lower() == "hero":
            return s
    return None


def patch_hero_bg_precise(existing_html: str, new_url: str) -> str:
    """
    Patch ONLY the hero background image. Never touches other page content/CSS.
    Looks for:
      1) <div class="hero-bg" style="background-image:...">
      2) <section class="hero ..."> style="background-image:..."
    """
    if not existing_html or not new_url:
        return existing_html

    soup = BeautifulSoup(existing_html, "html.parser")

    # Case 1: hero-bg div
    hero_bg = soup.select_one(".hero-bg")
    if hero_bg:
        style = hero_bg.get("style") or ""
        # remove any prior background-image declarations
        style_parts = [p.strip() for p in style.split(";") if p.strip() and not p.strip().lower().startswith("background-image")]
        style_parts.append(f'background-image:url("{new_url}")')
        hero_bg["style"] = "; ".join(style_parts) + ";"
        return str(soup)

    # Case 2: hero section itself
    hero_sec = None
    for sec in soup.find_all("section"):
        cls = " ".join(sec.get("class") or [])
        if "hero" in cls.split():
            hero_sec = sec
            break

    if hero_sec:
        style = hero_sec.get("style") or ""
        style_parts = [p.strip() for p in style.split(";") if p.strip() and not p.strip().lower().startswith("background-image")]
        style_parts.append(f'background-image:url("{new_url}")')
        hero_sec["style"] = "; ".join(style_parts) + ";"
        return str(soup)

    return existing_html


def patch_section_titles_intros_changed_only(
    existing_html: str,
    old_layout: Dict[str, Any],
    new_layout: Dict[str, Any],
) -> str:
    """
    Patch ONLY section <h2> title + the first intro <p> under it,
    and ONLY for sections whose title/text changed in the layout.
    Mapping is by non-hero section order.
    """
    if not existing_html:
        return existing_html

    old_secs = _layout_non_hero_sections(old_layout or {})
    new_secs = _layout_non_hero_sections(new_layout or {})
    if not new_secs:
        return existing_html

    soup = BeautifulSoup(existing_html, "html.parser")

    # HTML non-hero <section> blocks (skip obvious hero sections)
    html_secs = []
    for sec in soup.find_all("section"):
        cls = " ".join(sec.get("class") or [])
        if "hero" in cls.split():
            continue
        html_secs.append(sec)

    n = min(len(html_secs), len(new_secs))
    if n <= 0:
        return existing_html

    for i in range(n):
        old_s = old_secs[i] if i < len(old_secs) and isinstance(old_secs[i], dict) else {}
        new_s = new_secs[i] if isinstance(new_secs[i], dict) else {}

        old_title = (old_s.get("title") or "").strip()
        new_title = (new_s.get("title") or "").strip()

        old_text = (old_s.get("text") or "").strip()
        new_text = (new_s.get("text") or "").strip()

        sec_tag = html_secs[i]

        # Patch title only if changed and non-empty
        if new_title and new_title != old_title:
            h2 = sec_tag.find("h2")
            if h2:
                h2.clear()
                h2.append(new_title)

        # Patch intro text only if changed and non-empty
        if new_text and new_text != old_text:
            h2 = sec_tag.find("h2")
            if h2:
                p = h2.find_next("p")
                # ensure this <p> is still inside the same section
                if p and p.find_parent("section") is sec_tag:
                    p.clear()
                    p.append(new_text)

    return str(soup)
