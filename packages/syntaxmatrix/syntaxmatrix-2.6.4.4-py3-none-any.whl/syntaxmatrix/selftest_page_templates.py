# syntaxmatrix/selftest_page_templates.py
from __future__ import annotations
from bs4 import BeautifulSoup
import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Your new contract utilities (from the previous step)
from syntaxmatrix.page_layout_contract import (
    normalise_layout,
    validate_layout,
    validate_compiled_html,
)

# Your existing patch-only publisher
from syntaxmatrix.page_patch_publish import patch_page_publish

def _pick_section_for_title_patch(sections):
    """
    Prefer a non-hero section that has both title+text, so we can assert the intro paragraph.
    Fallback: first non-hero section.
    """
    non_hero = [s for s in sections if isinstance(s, dict) and (s.get("type") or "").lower() != "hero"]
    for s in non_hero:
        if (s.get("title") or "").strip() and (s.get("text") or "").strip():
            return s
    return non_hero[0] if non_hero else None


def _pick_section_for_item_patch(sections):
    """
    Prefer a grid-ish section with at least one item.
    """
    grid_types = {"values", "team", "logos", "testimonials", "faq", "cta",
                  "services", "offers", "comparison", "process", "proof", "case_studies"}
    for s in sections:
        if not isinstance(s, dict):
            continue
        st = (s.get("type") or "").lower()
        items = s.get("items") if isinstance(s.get("items"), list) else []
        if st in grid_types and len(items) > 0:
            return s
    return None


def _default_fixture_about_v1() -> Dict[str, Any]:
    return {
        "page": "about",
        "category": "about",
        "template": {"id": "about_glass_hero_v1", "version": "1.0.0"},
        "meta": {
            "pageTitle": "About SyntaxMatrix",
            "summary": "AI platform framework for developer teams to provision client-ready AI platforms.",
            "primaryCta": {"label": "Request a demo", "href": "#sec_cta"},
            "secondaryCta": {"label": "See capabilities", "href": "#sec_values"},
        },
        "sections": [
            {
                "id": "sec_hero",
                "type": "hero",
                "title": "Build client-ready AI platforms with confidence",
                "text": "SyntaxMatrix helps teams provision, customise, and ship robust AI products faster.",
                "imageUrl": "https://example.com/hero-a.jpg",
                "items": [],
            },
            {
                "id": "sec_story",
                "type": "story",
                "title": "Our story",
                "text": "We built SyntaxMatrix to remove repetitive engineering work that slows down AI delivery.",
            },
            {
                "id": "sec_values",
                "type": "values",
                "title": "What we stand for",
                "text": "Principles that guide how we design and ship.",
                "cols": 3,
                "items": [
                    {
                        "id": "val_1",
                        "type": "card",
                        "title": "Engineering rigour",
                        "text": "Clear architecture, safe defaults, predictable behaviour.",
                    },
                    {
                        "id": "val_2",
                        "type": "card",
                        "title": "Client readiness",
                        "text": "Provisioning, admin tooling, audit trails, deployment patterns.",
                    },
                    {
                        "id": "val_3",
                        "type": "card",
                        "title": "Practical AI",
                        "text": "RAG, analytics, and automation that supports real teams.",
                    },
                ],
            },
            {
                "id": "sec_cta",
                "type": "cta",
                "title": "Ready to talk?",
                "text": "Tell us what you’re building and we’ll suggest a path to a production-ready setup.",
                "cols": 2,
                "items": [
                    {"id": "cta_1", "type": "card", "title": "Book a demo", "text": "See it in action."},
                    {"id": "cta_2", "type": "card", "title": "Discuss requirements", "text": "We’ll map your use-case."},
                ],
            },
        ],
    }


def _compile_html(layout: Dict[str, Any]) -> Tuple[str, str]:
    """
    Prefer page_builder first (lighter deps). Print real import errors if compilers fail.
    Returns: (html, compiler_name)
    """
    import importlib
    import traceback

    errors = []

    # 1) Page builder compiler (preferred)
    try:
        mod = importlib.import_module("syntaxmatrix.page_builder_generation")
        fn = getattr(mod, "compile_layout_to_html", None)
        if callable(fn):
            slug = (layout.get("page") or layout.get("category") or "page")
            return fn(layout, page_slug=str(slug)), "page_builder.compile_layout_to_html"
        errors.append("page_builder: compile_layout_to_html not found/callable")
    except Exception:
        errors.append("page_builder import failed:\n" + traceback.format_exc())

    # 2) Agentic compiler (optional; may require extra deps like google.genai)
    try:
        mod = importlib.import_module("syntaxmatrix.agentic.agents")
        fn = getattr(mod, "compile_plan_to_html", None)
        if callable(fn):
            return fn(layout), "agentic.compile_plan_to_html"
        errors.append("agentic: compile_plan_to_html not found/callable")
    except Exception:
        errors.append("agentic import failed:\n" + traceback.format_exc())

    raise RuntimeError(
        "Could not import a compiler.\n\n" + "\n\n".join(errors)
    )

def _issues_to_text(issues) -> str:
    lines = []
    for it in issues:
        d = it.to_dict() if hasattr(it, "to_dict") else dict(it)
        lines.append(f"- [{d.get('level')}] {d.get('path')}: {d.get('message')}")
    return "\n".join(lines)


def run_page_template_selftest(
    fixture_path: Optional[str] = None,
    *,
    verbose: bool = True,
) -> int:
    """
    Self-test:
      1) Load fixture JSON (or use built-in About v1 fixture)
      2) normalise + validate layout
      3) compile HTML
      4) validate compiled HTML anchors
      5) patch publish with a modified layout
      6) assert that hero + section titles/intros + grid items changed

    Returns 0 if pass, non-zero if fail.
    """
    try:
        # ── 1) Load fixture
        if fixture_path:
            raw = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
        else:
            raw = _default_fixture_about_v1()

        # ── 2) Normalise + validate layout
        layout = normalise_layout(raw, mode="draft")
        issues = validate_layout(layout)
        errors = [i for i in issues if i.level == "error"]
        warns = [i for i in issues if i.level == "warning"]

        if verbose and warns:
            print("Layout warnings:")
            print(_issues_to_text(warns))

        if errors:
            print("Layout errors:")
            print(_issues_to_text(errors))
            return 2

        # ── 3) Compile HTML
        html, compiler_name = _compile_html(layout)
        if verbose:
            print(f"Compiled using: {compiler_name}")
            print(f"HTML length: {len(html)} chars")

        # ── 4) Validate compiled HTML anchors
        html_issues = validate_compiled_html(html, layout)
        html_errors = [i for i in html_issues if i.level == "error"]
        html_warns = [i for i in html_issues if i.level == "warning"]

        if verbose and html_warns:
            print("HTML warnings:")
            print(_issues_to_text(html_warns))

        if html_errors:
            print("HTML errors:")
            print(_issues_to_text(html_errors))
            return 3

        # ── 5) Patch publish with a modified layout
        mutated = copy.deepcopy(layout)

        # Change hero fields
        hero = next(s for s in mutated["sections"] if (s.get("type") or "").lower() == "hero")
        old_hero_title = hero.get("title", "")
        old_hero_text = hero.get("text", "")
        old_hero_img = hero.get("imageUrl", "")

        hero["title"] = "About SyntaxMatrix (Patched)"
        hero["text"] = "This hero lead was patched successfully."
        hero["imageUrl"] = "https://example.com/hero-b.jpg"

        # ── 5) Patch publish with a modified layout
        mutated = copy.deepcopy(layout)

        # Change hero fields (always)
        hero = next(s for s in mutated["sections"] if (s.get("type") or "").lower() == "hero")
        old_hero_title = hero.get("title", "")
        old_hero_text = hero.get("text", "")
        old_hero_img = hero.get("imageUrl", "")

        hero["title"] = "Hero (Patched)"
        hero["text"] = "This hero lead was patched successfully."
        hero["imageUrl"] = "https://example.com/hero-b.jpg"

        # Pick a non-hero section to patch title + intro
        target_sec = _pick_section_for_title_patch(mutated["sections"])
        if target_sec is None:
            raise RuntimeError("No non-hero section available to test section title/intro patching.")

        target_id = target_sec.get("id")
        old_target_title = target_sec.get("title", "")
        old_target_text = target_sec.get("text", "")

        target_sec["title"] = f"{old_target_title} (Patched)".strip() if old_target_title else "Section (Patched)"
        target_sec["text"] = "This intro paragraph was patched successfully."

        # Pick a grid section to patch first item
        items_sec = _pick_section_for_item_patch(mutated["sections"])
        if items_sec is None:
            raise RuntimeError("No grid-like section with items found to test item patching.")

        items_sec_id = items_sec.get("id")
        items_list = items_sec.get("items") if isinstance(items_sec.get("items"), list) else []
        old_item_title = (items_list[0].get("title", "") if items_list else "")

        items_list[0]["title"] = f"{old_item_title} (Patched)".strip() if old_item_title else "Item (Patched)"
        items_list[0]["text"] = "This card body was patched successfully."

        patched_html, stats = patch_page_publish(html, mutated)

        if verbose:
            print("Patch stats:", stats)

        patched_html, stats = patch_page_publish(html, mutated)

        if verbose:
            print("Patch stats:", stats)

        # ── 6) Assertions: ensure old content removed, new content present
        # ── 6) Assertions: verify the *target nodes* changed (not substring checks)
        soup = BeautifulSoup(patched_html, "html.parser")

        def text_of(selector: str) -> str:
            el = soup.select_one(selector)
            return el.get_text(strip=True) if el else ""

        # Hero checks
        hero_id = hero.get("id") or "sec_hero"
        hero_h1 = text_of(f"section#{hero_id} h1")
        if hero_h1 != "Hero (Patched)":
            raise AssertionError(f"Hero <h1> not patched. Got: {hero_h1!r}")

        hero_lead = (
            text_of(f"section#{hero_id} p.lead")
            or text_of(f"section#{hero_id} .lead")
            or text_of(f"section#{hero_id} p")
        )
        if hero_lead != "This hero lead was patched successfully.":
            raise AssertionError(f"Hero lead not patched. Got: {hero_lead!r}")

        hero_bg = soup.select_one(f"section#{hero_id} .hero-bg")
        if hero_bg is None:
            raise AssertionError("Hero .hero-bg not found after patch.")
        style = hero_bg.get("style") or ""
        if "https://example.com/hero-b.jpg" not in style:
            raise AssertionError(f"Hero bg not patched. style={style!r}")

        # Section title + intro checks (dynamic)
        sec_tag = soup.select_one(f"section#{target_id}")
        if sec_tag is None:
            raise AssertionError(f"Target section '{target_id}' not found after patch.")
        h2 = sec_tag.find("h2")
        if h2 is None:
            raise AssertionError(f"Target section '{target_id}' has no <h2> after patch.")
        if h2.get_text(strip=True) != target_sec["title"]:
            raise AssertionError(f"Target section title not patched. Got: {h2.get_text(strip=True)!r}")

        p_after = h2.find_next_sibling()
        intro_text = p_after.get_text(strip=True) if (p_after is not None and p_after.name == "p") else ""
        if intro_text != "This intro paragraph was patched successfully.":
            # fallback: accept if the text exists somewhere in the section
            if "This intro paragraph was patched successfully." not in sec_tag.get_text(" ", strip=True):
                raise AssertionError(f"Target section intro not patched. Got: {intro_text!r}")

        # Item patch checks (dynamic)
        items_sec_tag = soup.select_one(f"section#{items_sec_id}")
        if items_sec_tag is None:
            raise AssertionError(f"Items section '{items_sec_id}' not found after patch.")
        card_h3 = items_sec_tag.select_one(".card h3") or items_sec_tag.find("h3")
        if card_h3 is None:
            raise AssertionError(f"Items section '{items_sec_id}' has no item <h3> to assert.")
        if card_h3.get_text(strip=True) != items_list[0]["title"]:
            raise AssertionError(f"First item title not patched. Got: {card_h3.get_text(strip=True)!r}")

        # Optional: re-validate anchors still OK after patch
        post_issues = validate_compiled_html(patched_html, mutated)
        post_errors = [i for i in post_issues if i.level == "error"]
        if post_errors:
            print("Post-patch HTML errors:")
            print(_issues_to_text(post_errors))
            return 4

        if verbose:
            print("✅ Self-test passed.")
        return 0

    except AssertionError as e:
        print(f"❌ Self-test assertion failed: {e}")
        return 10
    except Exception as e:
        print(f"❌ Self-test crashed: {type(e).__name__}: {e}")
        return 11


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SyntaxMatrix page template self-test")
    parser.add_argument("--fixture", default=None, help="Path to fixture JSON (optional)")
    parser.add_argument("--quiet", action="store_true", help="Less output")
    args = parser.parse_args()

    code = run_page_template_selftest(args.fixture, verbose=not args.quiet)
    raise SystemExit(code)
