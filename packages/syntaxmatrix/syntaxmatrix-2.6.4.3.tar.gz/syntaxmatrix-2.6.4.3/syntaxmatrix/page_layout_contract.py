# syntaxmatrix/page_layout_contract.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup


# ─────────────────────────────────────────────────────────────
# Config: categories, templates, and allowed section types
# ─────────────────────────────────────────────────────────────

KNOWN_CATEGORIES = {"about", "services", "blog", "landing", "contact", "docs", "careers"}

# Template → allowed section types
TEMPLATE_ALLOWED_TYPES: Dict[str, set[str]] = {
    "about_glass_hero_v1": {
        "hero", "story", "values", "logos", "team", "testimonials", "faq", "cta"
    },
    "services_grid_v1": {
        "hero", "services", "process", "proof", "faq", "cta"
    },
    "services_detail_v1": {
        "hero", "offers", "comparison", "process", "case_studies", "faq", "cta"
    },

    # Add more templates later...
}

# Template → canonical order (unknown types appended)
TEMPLATE_SECTION_ORDER: Dict[str, List[str]] = {
    "about_glass_hero_v1": [
        "sec_hero",
        "sec_story",
        "sec_values",
        "sec_logos",
        "sec_team",
        "sec_testimonials",
        "sec_faq",
        "sec_cta",
    ],
    "services_grid_v1": [
        "sec_hero", "sec_services", "sec_process", "sec_proof", "sec_faq", "sec_cta"
    ],
    "services_detail_v1": [
        "sec_hero", "sec_offers", "sec_comparison", "sec_process", "sec_case_studies", "sec_faq", "sec_cta"
    ],

}

# Grid defaults by section type
DEFAULT_COLS_BY_TYPE = {
    "values": 3,
    "team": 3,
    "logos": 5,
    "testimonials": 3,
    "faq": 2,
    "cta": 2,
    "services": 3,
    "offers": 2,
    "comparison": 3,
    "process": 3,
    "proof": 4,
    "case_studies": 3,
    "offers": 2,
}

# “Grid-ish” sections should have .grid in HTML (for your patcher)
GRID_SECTION_TYPES = {"values", "team", "logos", "testimonials", "faq", "cta", "features", "gallery", 
                      "richtext", "services", "offers", "comparison", "process", "proof", "case_studies"
                    }


# Aliases → canonical section ids (About v1)
SECTION_ID_ALIASES = {
    "hero": "sec_hero",
    "header": "sec_hero",
    "top": "sec_hero",

    "about": "sec_story",
    "intro": "sec_story",
    "story": "sec_story",

    "principles": "sec_values",
    "highlights": "sec_values",
    "values": "sec_values",

    "clients": "sec_logos",
    "partners": "sec_logos",
    "logos": "sec_logos",

    "people": "sec_team",
    "founders": "sec_team",
    "team": "sec_team",

    "reviews": "sec_testimonials",
    "testimonials": "sec_testimonials",

    "questions": "sec_faq",
    "faq": "sec_faq",

    "contact": "sec_cta",
    "next_steps": "sec_cta",
    "cta": "sec_cta",
    "services": "sec_services",

    "offerings": "sec_services",
    "process": "sec_process",
    "how_we_work": "sec_process",
    "proof": "sec_proof",
    "results": "sec_proof",
    "case_studies": "sec_case_studies",
    "cases": "sec_case_studies",
    "offers": "sec_offers",
    "comparison": "sec_comparison",
    "pricing": "sec_comparison",
    "packages": "sec_offers",
    "tiers": "sec_comparison",

}

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$", re.ASCII)
SAFE_ID_RE = re.compile(r"[^a-z0-9_:\-]+", re.ASCII)
DANGEROUS_RE = re.compile(
    r"(<\s*script\b|javascript:|\bon\w+\s*=)", re.IGNORECASE
)


@dataclass
class Issue:
    level: str  # "error" | "warning"
    path: str
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {"level": self.level, "path": self.path, "message": self.message}


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _is_str(x: Any) -> bool:
    return isinstance(x, str)

def _s(x: Any) -> str:
    return x.strip() if isinstance(x, str) else ""

def _clean_ws(s: str) -> str:
    s = s.replace("\x00", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _has_dangerous(s: str) -> bool:
    return bool(DANGEROUS_RE.search(s or ""))

def _urlish(url: str) -> bool:
    """
    Accept:
      - http/https URLs
      - root-relative (/uploads/.., /static/..)
      - fragment (#sec_cta)
      - relative (uploads/media/..., media/..., ./..., ../...)
    """
    u = _s(url)
    if not u:
        return False
    if u.startswith("#"):
        return True
    if u.startswith(("/", "./", "../")):
        return True
    if u.startswith(("uploads/", "media/", "static/")):
        return True
    p = urlparse(u)
    return p.scheme in ("http", "https") and bool(p.netloc)

def _safe_id(raw: str) -> str:
    s = _s(raw).lower()
    s = s.replace(" ", "_")
    s = SAFE_ID_RE.sub("", s)
    s = s.strip("_")
    return s

def _make_unique(existing_lower: set[str], base: str) -> str:
    b = base
    if b.lower() not in existing_lower:
        existing_lower.add(b.lower())
        return b
    i = 2
    while f"{b}_{i}".lower() in existing_lower:
        i += 1
    new_id = f"{b}_{i}"
    existing_lower.add(new_id.lower())
    return new_id


# ─────────────────────────────────────────────────────────────
# Normaliser
# ─────────────────────────────────────────────────────────────

def normalise_layout(
    layout: Any,
    *,
    default_category: str = "about",
    default_template_id: str = "about_glass_hero_v1",
    default_template_version: str = "1.0.0",
    mode: str = "prod",  # "prod" | "draft"
) -> Dict[str, Any]:
    """
    Bring any agent/editor output into a stable contract shape.
    This should run BEFORE validate_layout().
    """
    if not isinstance(layout, dict):
        layout = {}

    out: Dict[str, Any] = dict(layout)

    # Root defaults
    out["category"] = _clean_ws(_s(out.get("category"))) or default_category
    out["page"] = _clean_ws(_s(out.get("page"))) or out["category"]

    tpl = out.get("template")
    if not isinstance(tpl, dict):
        tpl = {}
    tpl_id = _clean_ws(_s(tpl.get("id"))) or default_template_id
    tpl_ver = _clean_ws(_s(tpl.get("version"))) or default_template_version
    tpl["id"] = tpl_id
    tpl["version"] = tpl_ver
    out["template"] = tpl

    # Meta normalisation
    meta = out.get("meta")
    if not isinstance(meta, dict):
        meta = {}
    for k in ("pageTitle", "summary"):
        if k in meta:
            meta[k] = _clean_ws(_s(meta.get(k)))
    # CTA defaults (safe)
    def _norm_cta(cta: Any) -> Dict[str, str]:
        if not isinstance(cta, dict):
            return {}
        return {"label": _clean_ws(_s(cta.get("label"))), "href": _clean_ws(_s(cta.get("href")))}
    if "primaryCta" in meta:
        meta["primaryCta"] = _norm_cta(meta["primaryCta"])
    if "secondaryCta" in meta:
        meta["secondaryCta"] = _norm_cta(meta["secondaryCta"])
    out["meta"] = meta

    # Sections list
    secs = out.get("sections")
    if not isinstance(secs, list):
        secs = []
    secs2: List[Dict[str, Any]] = []
    existing_ids_lower: set[str] = set()

    # First pass: normalise section objects
    for idx, s in enumerate(secs):
        if not isinstance(s, dict):
            continue
        s2 = dict(s)

        stype = _safe_id(_s(s2.get("type")))
        if not stype:
            stype = "hero" if idx == 0 else "story"
        s2["type"] = stype

        # Id: alias mapping, then safe id, then ensure unique
        raw_id = _s(s2.get("id"))
        if raw_id:
            sid = _safe_id(raw_id)
        else:
            sid = f"sec_{stype}"

        # Apply alias mapping (only if canonical isn't already present later)
        alias_key = _safe_id(raw_id) or stype
        if alias_key in SECTION_ID_ALIASES:
            sid = SECTION_ID_ALIASES[alias_key]

        sid = _make_unique(existing_ids_lower, sid)
        s2["id"] = sid

        # Strings
        s2["title"] = _clean_ws(_s(s2.get("title")))
        s2["text"] = _clean_ws(_s(s2.get("text")))

        # Items
        items = s2.get("items")
        if not isinstance(items, list):
            items = []
        items2: List[Dict[str, Any]] = []
        for j, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            it2 = dict(it)
            it2["id"] = _safe_id(_s(it2.get("id"))) or f"item_{sid}_{j+1}"
            it2["type"] = _safe_id(_s(it2.get("type"))) or "card"
            it2["title"] = _clean_ws(_s(it2.get("title")))
            it2["text"] = _clean_ws(_s(it2.get("text")))
            if "imageUrl" in it2:
                it2["imageUrl"] = _clean_ws(_s(it2.get("imageUrl")))
            items2.append(it2)
        s2["items"] = items2

        # Cols
        cols = s2.get("cols")
        if isinstance(cols, (int, float)):
            cols_i = int(cols)
        else:
            cols_i = DEFAULT_COLS_BY_TYPE.get(stype, 0)
        if cols_i:
            s2["cols"] = max(1, min(5, cols_i))
        elif "cols" in s2:
            s2.pop("cols", None)

        # Hero canonical image
        if stype == "hero":
            img = _clean_ws(_s(s2.get("imageUrl")))
            if not img and items2 and isinstance(items2[0], dict):
                img = _clean_ws(_s(items2[0].get("imageUrl")))
            if img:
                s2["imageUrl"] = img
                # Back-compat: ensure items[0] exists and carries the image
                if not items2:
                    s2["items"] = [{"id": "hero_media", "type": "card", "title": "Hero image", "text": "", "imageUrl": img}]
                else:
                    if not _s(items2[0].get("imageUrl")):
                        items2[0]["imageUrl"] = img

        secs2.append(s2)

    # Enforce canonical ids for the About v1 hero if present
    # If we have a hero type but id isn't sec_hero, rename it (safe) when possible.
    hero_idxs = [i for i, s in enumerate(secs2) if (s.get("type") == "hero")]
    if hero_idxs:
        hi = hero_idxs[0]
        if secs2[hi].get("id") != "sec_hero":
            # Only rename if sec_hero not already taken
            taken = {s.get("id") for s in secs2}
            if "sec_hero" not in taken:
                secs2[hi]["id"] = "sec_hero"

    # Reorder using template canonical order (append unknowns)
    order = TEMPLATE_SECTION_ORDER.get(tpl_id) or []
    if order:
        by_id = {s.get("id"): s for s in secs2}
        ordered: List[Dict[str, Any]] = []
        for sid in order:
            if sid in by_id:
                ordered.append(by_id.pop(sid))
        # append whatever is left (original relative order)
        for s in secs2:
            sid = s.get("id")
            if sid in by_id:
                ordered.append(by_id.pop(sid))
        secs2 = ordered

    out["sections"] = secs2
    return out


# ─────────────────────────────────────────────────────────────
# Layout validator (15 checks)
# ─────────────────────────────────────────────────────────────

def validate_layout(layout: Dict[str, Any]) -> List[Issue]:
    issues: List[Issue] = []

    if not isinstance(layout, dict):
        return [Issue("error", "$", "Layout must be an object.")]

    # 1) Root shape
    if not _is_str(layout.get("category")):
        issues.append(Issue("error", "$.category", "Missing or invalid category (string required)."))

    if not isinstance(layout.get("template"), dict):
        issues.append(Issue("error", "$.template", "Missing or invalid template object."))

    if not isinstance(layout.get("sections"), list):
        issues.append(Issue("error", "$.sections", "Missing or invalid sections list."))
        return issues

    category = _s(layout.get("category"))
    tpl = layout.get("template") if isinstance(layout.get("template"), dict) else {}
    tpl_id = _s(tpl.get("id"))
    tpl_ver = _s(tpl.get("version"))

    # 2) Template identity
    if not tpl_id:
        issues.append(Issue("error", "$.template.id", "template.id must be a non-empty string."))
    if tpl_ver and not VERSION_RE.match(tpl_ver):
        issues.append(Issue("error", "$.template.version", "template.version must match X.Y.Z (e.g. 1.0.0)."))
    if not tpl_ver:
        issues.append(Issue("warning", "$.template.version", "template.version missing; defaulting is recommended."))

    # 3) Category known
    if category and category not in KNOWN_CATEGORIES:
        issues.append(Issue("warning", "$.category", f"Unknown category '{category}'. Allowed: {sorted(KNOWN_CATEGORIES)}"))

    secs: List[Any] = layout.get("sections") or []

    # 4) Sections list length
    if len(secs) < 1:
        issues.append(Issue("error", "$.sections", "At least 1 section is required."))

    # 5) Unique section ids
    ids_lower: set[str] = set()
    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            issues.append(Issue("error", f"$.sections[{i}]", "Each section must be an object."))
            continue
        sid = _s(s.get("id"))
        if not sid:
            issues.append(Issue("error", f"$.sections[{i}].id", "Section id is required."))
            continue
        if sid.lower() in ids_lower:
            issues.append(Issue("error", f"$.sections[{i}].id", f"Duplicate section id '{sid}'."))
        ids_lower.add(sid.lower())

    # 6) Valid section type (template-aware)
    allowed_types = TEMPLATE_ALLOWED_TYPES.get(tpl_id)
    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            continue
        st = _s(s.get("type")).lower()
        if not st:
            issues.append(Issue("error", f"$.sections[{i}].type", "Section type is required."))
            continue
        if allowed_types and st not in allowed_types:
            issues.append(Issue("warning", f"$.sections[{i}].type", f"Type '{st}' not in allowed set for {tpl_id}."))

    # 7) Exactly one hero
    hero_secs = [s for s in secs if isinstance(s, dict) and _s(s.get("type")).lower() == "hero"]
    if len(hero_secs) != 1:
        issues.append(Issue("error", "$.sections", f"Exactly 1 hero section is required; found {len(hero_secs)}."))

    # 8) Hero required fields
    if hero_secs:
        hero = hero_secs[0]
        if not _s(hero.get("title")):
            issues.append(Issue("error", "$.sections[hero].title", "Hero title is required."))
        if not _s(hero.get("text")):
            issues.append(Issue("error", "$.sections[hero].text", "Hero text is required."))
        img = _s(hero.get("imageUrl"))
        if not img:
            # your patcher can fall back to items[0].imageUrl, but we still prefer hero.imageUrl
            issues.append(Issue("error", "$.sections[hero].imageUrl", "Hero imageUrl is required."))
        elif not _urlish(img):
            issues.append(Issue("warning", "$.sections[hero].imageUrl", "Hero imageUrl does not look like a URL/path."))

    # 9) Meta sanity + CTA fields
    meta = layout.get("meta")
    if meta is not None and not isinstance(meta, dict):
        issues.append(Issue("error", "$.meta", "meta must be an object if present."))
    if isinstance(meta, dict):
        pt = _s(meta.get("pageTitle"))
        if pt and len(pt) > 80:
            issues.append(Issue("warning", "$.meta.pageTitle", "pageTitle is quite long (>80 chars)."))
        for k in ("primaryCta", "secondaryCta"):
            if k in meta:
                cta = meta.get(k)
                if not isinstance(cta, dict):
                    issues.append(Issue("error", f"$.meta.{k}", f"{k} must be an object with label/href."))
                else:
                    if not _s(cta.get("label")) or not _s(cta.get("href")):
                        issues.append(Issue("error", f"$.meta.{k}", f"{k} requires non-empty label and href."))

    # 10) Section title/text presence
    title_optional_types = {"logos"}  # adjust per template
    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            continue
        st = _s(s.get("type")).lower()
        title = s.get("title")
        text = s.get("text")
        if st != "hero" and st not in title_optional_types:
            if not _is_str(title) or not _s(title):
                issues.append(Issue("warning", f"$.sections[{i}].title", "Section title is missing or empty."))
        if text is not None and not _is_str(text):
            issues.append(Issue("error", f"$.sections[{i}].text", "Section text must be a string."))

    # 11) Grid constraints (cols + items list)
    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            continue
        cols = s.get("cols")
        if cols is not None:
            if not isinstance(cols, int) or not (1 <= cols <= 5):
                issues.append(Issue("error", f"$.sections[{i}].cols", "cols must be an integer between 1 and 5."))
        items = s.get("items")
        if _s(s.get("type")).lower() in GRID_SECTION_TYPES:
            if items is None or not isinstance(items, list):
                issues.append(Issue("error", f"$.sections[{i}].items", "Grid-like section requires items as a list."))
            elif len(items) == 0:
                issues.append(Issue("warning", f"$.sections[{i}].items", "Section has no items."))

    # 12) Items shape
    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            continue
        items = s.get("items")
        if not isinstance(items, list):
            continue
        for j, it in enumerate(items):
            if not isinstance(it, dict):
                issues.append(Issue("error", f"$.sections[{i}].items[{j}]", "Item must be an object."))
                continue
            for k in ("title", "text"):
                if k in it and not _is_str(it.get(k)):
                    issues.append(Issue("error", f"$.sections[{i}].items[{j}].{k}", f"{k} must be a string."))
            if "imageUrl" in it and it.get("imageUrl") is not None and not _is_str(it.get("imageUrl")):
                issues.append(Issue("error", f"$.sections[{i}].items[{j}].imageUrl", "imageUrl must be a string."))

    # 13) Item count guidelines (warnings)
    def _warn_count(stype: str, mn: int, mx: int):
        for i, s in enumerate(secs):
            if not isinstance(s, dict):
                continue
            if _s(s.get("type")).lower() != stype:
                continue
            items = s.get("items") if isinstance(s.get("items"), list) else []
            n = len(items)
            if n < mn or n > mx:
                issues.append(Issue("warning", f"$.sections[{i}].items", f"{stype} item count {n} outside recommended {mn}–{mx}."))

    _warn_count("values", 2, 6)
    _warn_count("logos", 2, 12)
    _warn_count("team", 1, 12)
    _warn_count("faq", 2, 12)
    _warn_count("testimonials", 1, 9)

    # 14) Dangerous HTML checks (errors)
    def _scan_value(path: str, v: Any):
        if isinstance(v, str) and _has_dangerous(v):
            issues.append(Issue("error", path, "Potentially unsafe HTML/JS content detected."))
        elif isinstance(v, dict):
            for kk, vv in v.items():
                _scan_value(f"{path}.{kk}", vv)
        elif isinstance(v, list):
            for idx, vv in enumerate(v):
                _scan_value(f"{path}[{idx}]", vv)

    _scan_value("$", layout)

    # 15) Stable IDs for patching (warnings)
    # If you want strict enforcement per template, change warnings → errors.
    if tpl_id in TEMPLATE_SECTION_ORDER:
        canonical = set(TEMPLATE_SECTION_ORDER[tpl_id])
        for i, s in enumerate(secs):
            if not isinstance(s, dict):
                continue
            sid = _s(s.get("id"))
            if sid.startswith("sec_") and sid not in canonical and _s(s.get("type")).lower() != "hero":
                issues.append(Issue("warning", f"$.sections[{i}].id", f"Non-canonical section id '{sid}' for template {tpl_id}."))

    return issues


# ─────────────────────────────────────────────────────────────
# Compiled HTML validator (anchors your patcher needs)
# ─────────────────────────────────────────────────────────────

def validate_compiled_html(html: str, layout: Dict[str, Any]) -> List[Issue]:
    issues: List[Issue] = []
    if not isinstance(html, str) or not html.strip():
        return [Issue("error", "$html", "Compiled HTML is empty or invalid.")]

    soup = BeautifulSoup(html, "html.parser")

    # A) hero anchors
    hero = None
    secs = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    for s in secs:
        if isinstance(s, dict) and _s(s.get("type")).lower() == "hero":
            hero = s
            break

    if hero:
        hero_id = _s(hero.get("id"))
        hero_tag = soup.find("section", id=hero_id) if hero_id else None
        if hero_tag is None:
            issues.append(Issue("error", "$html.hero", f"Hero <section id=\"{hero_id}\"> not found in HTML."))
        else:
            has_bg = hero_tag.select_one(".hero-bg") is not None
            has_img = hero_tag.find("img") is not None
            if not (has_bg or has_img):
                issues.append(Issue("error", "$html.hero.image", "Hero must contain .hero-bg or an <img>."))

            if hero_tag.find("h1") is None:
                issues.append(Issue("error", "$html.hero.h1", "Hero must contain an <h1>."))

            if hero_tag.select_one("p.lead") is None:
                issues.append(Issue("warning", "$html.hero.lead", "Hero should contain <p class=\"lead\"> for reliable patching."))

    # B) section ids exist
    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            continue
        sid = _s(s.get("id"))
        if not sid:
            continue
        if soup.find("section", id=sid) is None:
            issues.append(Issue("error", f"$html.sections[{i}]", f"<section id=\"{sid}\"> not found in HTML."))

    # C) non-hero patch targets: h2 + intro p (warn if missing)
    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            continue
        if _s(s.get("type")).lower() == "hero":
            continue
        sid = _s(s.get("id"))
        sec_tag = soup.find("section", id=sid) if sid else None
        if sec_tag is None:
            continue
        h2 = sec_tag.find("h2")
        if h2 is None:
            issues.append(Issue("warning", f"$html.sections[{i}].h2", f"Section '{sid}' has no <h2> (patcher may skip title)."))
            continue
        # intro paragraph right after h2 is ideal, but patcher can insert if missing
        # so keep this as warning
        expected_text = _s(s.get("text"))
        nxt = h2.find_next_sibling()
        if expected_text:
            if nxt is None or nxt.name != "p":
                issues.append(Issue("warning", f"$html.sections[{i}].intro_p",
                                    f"Section '{sid}' has no <p> immediately after <h2>."))

    # D) grid container exists for grid sections
    for i, s in enumerate(secs):
        if not isinstance(s, dict):
            continue
        st = _s(s.get("type")).lower()
        if st not in GRID_SECTION_TYPES:
            continue
        sid = _s(s.get("id"))
        sec_tag = soup.find("section", id=sid) if sid else None
        if sec_tag is None:
            continue
        if sec_tag.select_one(".grid") is None:
            issues.append(Issue("warning", f"$html.sections[{i}].grid", f"Grid-like section '{sid}' has no .grid container."))

    return issues
