from __future__ import annotations
import re
from typing import Any, Dict, Tuple, List, Optional
from bs4 import BeautifulSoup


_SECTION_BY_ID_RE = r'(<section\b[^>]*\bid="{sid}"[^>]*>)(.*?)(</section>)'
_SECTION_OPEN_RE = re.compile(r"<section\b[^>]*\bid=['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE)

def _safe_href(h: str) -> str:
    """
    Sanitise optional links.
    IMPORTANT: empty/unsafe must return "" so CTAs are NOT created by default.
    """
    h = (h or "").strip()
    if not h:
        return ""
    low = h.lower().strip()
    if low.startswith("javascript:") or low.startswith("data:"):
        return ""
    return h


def _is_button_item(it: Dict[str, Any]) -> bool:
    return ((it.get("type") or "").strip().lower() == "button")


def _button_node(soup, it: Dict[str, Any]):
    label = (it.get("title") or "").strip() or "Button"
    href = _safe_href(it.get("href") or it.get("url") or it.get("link") or "#")

    wrap = soup.new_tag("div")
    wrap["class"] = ["smx-action", "reveal"]

    a = soup.new_tag("a")
    a["class"] = ["smx-btn", "primary"]
    a["data-smx"] = "button"
    a["href"] = href
    a.string = label

    wrap.append(a)
    return wrap


def _build_empty_section(soup, s: Dict[str, Any]) -> Any:
    sid = (s.get("id") or "").strip() or "sec_new"
    title = (s.get("title") or "").strip() or "New section"
    text = (s.get("text") or "").strip()

    sec = soup.new_tag("section")
    sec["id"] = sid
    sec["class"] = ["sec"]

    wrap = soup.new_tag("div")
    wrap["class"] = ["wrap"]
    sec.append(wrap)

    h2 = soup.new_tag("h2")
    h2["class"] = ["reveal"]
    h2.string = title
    wrap.append(h2)

    if text:
        p = soup.new_tag("p")
        p["class"] = ["reveal"]
        p["style"] = "margin-bottom:14px;"
        p.string = text
        wrap.append(p)

    grid = soup.new_tag("div")
    grid["class"] = ["grid"]
    grid["style"] = "grid-template-columns:repeat(3, minmax(0,1fr));"
    wrap.append(grid)

    return sec


def _esc_html(s: str) -> str:
    s = s or ""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )


def _is_button_item(it: Dict[str, Any]) -> bool:
    return ((it.get("type") or "").strip().lower() == "button")

def _button_node(soup, it: Dict[str, Any]):
    label = (it.get("title") or "").strip() or "Read more"
    href = _safe_href(it.get("href") or "#") or "#"

    box = soup.new_tag("div")
    box["class"] = ["reveal"]
    box["data-smx"] = "action"

    a = soup.new_tag("a")
    a["href"] = href
    a["data-smx"] = "button"
    a["style"] = (
        "display:inline-flex;align-items:center;justify-content:center;"
        "border-radius:999px;padding:10px 16px;"
        "border:1px solid rgba(129,140,248,.7);"
        "background:rgba(79,70,229,.95);"
        "color:#e5e7eb;text-decoration:none;font-weight:600;"
    )
    a.string = label
    box.append(a)
    return box


def _existing_section_ids(html: str) -> set:
    if not html:
        return set()
    return set(m.group(1) for m in _SECTION_OPEN_RE.finditer(html))


def _find_section_block_span(html: str, sid: str) -> Tuple[int, int]:
    """
    Returns (start, end) span of <section ... id="sid">...</section> if found, else (-1, -1).
    Non-greedy to avoid eating across sections.
    """
    if not html or not sid:
        return (-1, -1)
    pat = re.compile(
        r"(<section\b[^>]*\bid=['\"]" + re.escape(sid) + r"['\"][^>]*>.*?</section>)",
        re.IGNORECASE | re.DOTALL,
    )
    m = pat.search(html)
    if not m:
        return (-1, -1)
    return (m.start(1), m.end(1))


def _insert_before_wrapper_close(html: str, chunk: str) -> str:
    """
    Best-effort insert inside the outer smx wrapper if present, else before </body>, else append.
    Assumes typical stored pages end with the wrapper closing </div>.
    """
    if not html:
        return chunk

    # Prefer inserting before the LAST closing </div> if we see an smx wrapper.
    if re.search(r"<div\b[^>]*\bid=['\"]smx-page-[^'\"]+['\"]", html, re.IGNORECASE):
        idx = html.rfind("</div>")
        if idx != -1:
            return html[:idx] + "\n" + chunk + "\n" + html[idx:]

    # Fallback: before </body>
    idx = html.lower().rfind("</body>")
    if idx != -1:
        return html[:idx] + "\n" + chunk + "\n" + html[idx:]

    return html + "\n" + chunk


def _patch_section_by_id(html: str, sid: str, *, title: str | None, text: str | None) -> Tuple[str, bool]:
    """
    Patch one section's <h2> and the first intro <p> under it, but ONLY inside <section id="sid">.
    If the intro <p> doesn't exist and text is provided, insert it after the first </h2>.
    """
    if not html or not sid:
        return html, False

    sid_esc = re.escape(sid)
    pat = re.compile(_SECTION_BY_ID_RE.format(sid=sid_esc), re.IGNORECASE | re.DOTALL)
    m = pat.search(html)
    if not m:
        return html, False

    open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
    changed = False

    # Patch H2 title
    if title is not None:
        title = title.strip()
        if title:
            h2_pat = re.compile(r'(<h2\b[^>]*>)(.*?)(</h2>)', re.IGNORECASE | re.DOTALL)
            def _h2_repl(mm):
                nonlocal changed
                changed = True
                return mm.group(1) + _esc_html(title) + mm.group(3)
            inner2, n = h2_pat.subn(_h2_repl, inner, count=1)
            inner = inner2 if n else inner

    # Patch / insert intro paragraph right after first </h2>
    if text is not None:
        text = text.strip()
        if text:
            parts = re.split(r'(</h2>)', inner, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) == 3:
                before = parts[0] + parts[1]
                after = parts[2]

                p_pat = re.compile(r'(<p\b[^>]*>)(.*?)(</p>)', re.IGNORECASE | re.DOTALL)
                def _p_repl(mm):
                    nonlocal changed
                    changed = True
                    return mm.group(1) + _esc_html(text) + mm.group(3)

                after2, n2 = p_pat.subn(_p_repl, after, count=1)

                if n2 == 0:
                    # No intro paragraph existed, insert a safe one
                    changed = True
                    ins = f'<p class="reveal" style="margin-bottom:14px;">{_esc_html(text)}</p>'
                    inner = before + ins + after
                else:
                    inner = before + after2

    new_block = open_tag + inner + close_tag
    new_html = html[:m.start()] + new_block + html[m.end():]
    return new_html, changed


def _ensure_grid(sec, soup, cols: int):
    wrap = sec.select_one(".wrap") or sec
    grid = sec.select_one(".grid")
    if grid is None:
        grid = soup.new_tag("div")
        grid["class"] = ["grid"]
        wrap.append(grid)

    cols = max(1, min(int(cols or 3), 5))
    style = (grid.get("style") or "")
    parts = [p.strip() for p in style.split(";") if p.strip() and not p.strip().lower().startswith("grid-template-columns")]
    parts.append(f"grid-template-columns:repeat({cols}, minmax(0,1fr))")
    grid["style"] = "; ".join(parts) + ";"
    return grid


def _build_blank_section(soup, sid: str, stype: str, title: str, text: str, cols: int):
    sec = soup.new_tag("section")
    sec["id"] = sid
    sec["class"] = ["sec"]
    sec["data-section-type"] = (stype or "section")

    wrap = soup.new_tag("div")
    wrap["class"] = ["wrap"]
    sec.append(wrap)

    h2 = soup.new_tag("h2")
    h2["class"] = ["reveal"]
    h2.string = (title or "New section").strip()
    wrap.append(h2)

    if (text or "").strip():
        p = soup.new_tag("p")
        p["class"] = ["reveal"]
        p["style"] = "margin-bottom:14px;"
        p.string = text.strip()
        wrap.append(p)

    grid = soup.new_tag("div")
    grid["class"] = ["grid"]
    grid["style"] = f"grid-template-columns:repeat({max(1, min(int(cols or 3), 5))}, minmax(0,1fr));"
    wrap.append(grid)

    return sec


def _default_card_node(soup, it: Dict[str, Any]):
    it_type = (it.get("type") or "card").strip().lower()
    it_title = (it.get("title") or "").strip()
    it_text = (it.get("text") or "").strip()
    it_img = (it.get("imageUrl") or "").strip()

    # Button item: render as a card containing an anchor
    if it_type == "button":
        href = _safe_href(it.get("href") or it.get("url") or it.get("link") or "#")
        card = soup.new_tag("div")
        card["class"] = ["card", "reveal"]

        a = soup.new_tag("a")
        a["class"] = ["btn", "primary", "smx-btn"]
        a["href"] = href
        a["data-smx"] = "button"
        a.string = it_title or "Button"
        card.append(a)

        if it_text:
            p = soup.new_tag("p")
            p["style"] = "margin-top:8px;"
            p.string = it_text
            card.append(p)

        return card

    # Normal card
    card = soup.new_tag("div")
    card["class"] = ["card", "reveal"]

    if it_img:
        img = soup.new_tag("img")
        img["loading"] = "lazy"
        img["decoding"] = "async"
        img["src"] = it_img
        img["alt"] = it_title
        card.append(img)

    row = soup.new_tag("div")
    row["style"] = "display:flex; gap:10px; align-items:center; margin-top:" + ("10px" if it_img else "0") + ";"
    h3 = soup.new_tag("h3")
    h3["style"] = "margin:0; font-size:1.05rem;"
    h3.string = it_title
    row.append(h3)
    card.append(row)

    p = soup.new_tag("p")
    p["style"] = "margin-top:8px;"
    p.string = it_text
    card.append(p)

    return card


def _patch_default_cards(sec, soup, items: List[Dict[str, Any]], cols: int) -> bool:
    grid = _ensure_grid(sec, soup, cols)

    # direct children represent items (cards OR actions)
    children = [c for c in grid.find_all(True, recursive=False)]
    changed = False
    n = len(items)

    def make_node(it: Dict[str, Any]):
        if _is_button_item(it):
            return _button_node(soup, it)
        return _default_card_node(soup, it)

    # sync count
    if len(children) < n:
        for i in range(len(children), n):
            grid.append(make_node(items[i] if isinstance(items[i], dict) else {}))
            changed = True
        children = [c for c in grid.find_all(True, recursive=False)]

    if len(children) > n:
        for extra in children[n:]:
            extra.decompose()
            changed = True
        children = [c for c in grid.find_all(True, recursive=False)]

    # patch each
    for i in range(n):
        it = items[i] if isinstance(items[i], dict) else {}
        node = children[i]

        if _is_button_item(it):
            # ensure button node
            a = node.find("a", attrs={"data-smx": "button"}) or node.find("a")
            if a is None:
                node.replace_with(make_node(it))
                changed = True
                continue

            label = (it.get("title") or "").strip() or "Read more"
            href = _safe_href(it.get("href") or "#") or "#"

            if a.get_text(strip=True) != label:
                a.clear(); a.append(label); changed = True
            if a.get("href") != href:
                a["href"] = href; changed = True
            continue

        # normal card patch (existing behaviour)
        it_title = (it.get("title") or "").strip()
        it_text  = (it.get("text") or "").strip()
        it_img   = (it.get("imageUrl") or "").strip()
        it_href  = _safe_href(it.get("href") or "")
        cta_lbl  = (it.get("ctaLabel") or "Read more").strip() or "Read more"

        # image
        img = node.find("img")
        if it_img:
            if img is None:
                img = soup.new_tag("img")
                img["loading"] = "lazy"
                img["decoding"] = "async"
                node.insert(0, img)
                changed = True
            if img.get("src") != it_img:
                img["src"] = it_img; changed = True
            if it_title and img.get("alt") != it_title:
                img["alt"] = it_title; changed = True
        else:
            if img is not None:
                img.decompose(); changed = True

        # title
        h = node.find(["h3", "h4"]) or node.find(["h2", "h3", "h4"])
        if h and it_title and h.get_text(strip=True) != it_title:
            h.clear(); h.append(it_title); changed = True

        # text
        p = node.find("p") or node.select_one(".mut")
        if p and it_text and p.get_text(" ", strip=True) != it_text:
            p.clear(); p.append(it_text); changed = True

                # card CTA link (Read more) + alignment
        align = (it.get("ctaAlign") or it.get("cta_align") or "").strip().lower() or "left"
        if align == "centre":
            align = "center"
        if align not in ("left", "center", "right", "full"):
            align = "left"

        actions = node.find(attrs={"data-smx": "card-actions"})
        # card CTA link (Read more) + alignment (Sprint 3)
        cta_align = (it.get("ctaAlign") or it.get("cta_align") or "").strip().lower()
        if cta_align == "centre":
            cta_align = "center"
        if cta_align not in ("left", "center", "right", "full"):
            cta_align = ""

        justify = {"left": "flex-start", "center": "center", "right": "flex-end"}.get(cta_align or "left", "flex-start")


        actions = node.find("div", attrs={"data-smx": "card-actions"})
        if actions is None:
            actions = node.find("div", class_=lambda c: c and "smx-card-actions" in c.split())

        a = None
        if actions is not None:
            a = actions.find("a", attrs={"data-smx": "card-cta"})
        if a is None:
            a = node.find("a", attrs={"data-smx": "card-cta"})

        if it_href:
            if actions is None:
                actions = soup.new_tag("div")
                actions["data-smx"] = "card-actions"
                actions["class"] = ["smx-card-actions", f"align-{cta_align or 'left'}"]
                node.append(actions)
                changed = True

            cls = list(actions.get("class") or [])
            cls = [c for c in cls if not str(c).startswith("align-")]
            if "smx-card-actions" not in cls:
                cls.append("smx-card-actions")
            cls.append(f"align-{cta_align or 'left'}")
            if actions.get("class") != cls:
                actions["class"] = cls; changed = True

            desired_actions_style = f"display:flex; gap:10px; margin-top:12px; justify-content:{justify};"
            if (actions.get("style") or "") != desired_actions_style:
                actions["style"] = desired_actions_style
                changed = True

            if a is None:
                a = soup.new_tag("a")
                a["data-smx"] = "card-cta"
                a["class"] = ["btn", "ghost", "smx-card-cta"]
                actions.append(a)
                changed = True
            else:
                if a.parent is not actions:
                    a.extract()
                    actions.append(a)
                    changed = True

            # Sprint 3: full-width button
            if cta_align == "full":
                a_style = (a.get("style") or "")
                desired_a_style = "width:100%; display:flex; justify-content:center; box-sizing:border-box; text-align:center;"
                if a_style != desired_a_style:
                    a["style"] = desired_a_style
                    changed = True
            else:
                # remove full-width styling if switching away
                if a.has_attr("style") and "width:100%" in (a.get("style") or ""):
                    del a["style"]
                    changed = True

            if a.get("href") != it_href:
                a["href"] = it_href; changed = True
            if a.get_text(strip=True) != cta_lbl:
                a.clear(); a.append(cta_lbl); changed = True
        else:
            if a is not None:
                a.decompose(); changed = True
            if actions is not None and actions.find(True) is None:
                actions.decompose(); changed = True

                changed = True
            if actions is not None:
                # remove wrapper if empty
                if not actions.find(True):
                    actions.decompose()
                    changed = True

    return changed


def _faq_detail_node(soup, it: Dict[str, Any]):
    q = (it.get("title") or "").strip()
    a = (it.get("text") or "").strip()
    img_url = (it.get("imageUrl") or "").strip()

    d = soup.new_tag("details")
    d["class"] = ["reveal"]

    s = soup.new_tag("summary")
    s.string = q
    d.append(s)

    # optional image under the question
    if img_url:
        img = soup.new_tag("img")
        img["loading"] = "lazy"
        img["decoding"] = "async"
        img["src"] = img_url
        img["alt"] = q or "faq"
        img["style"] = "width:100%;height:auto;border-radius:14px;margin-top:10px;display:block;"
        img["data-smx"] = "faq-img"
        d.append(img)

    if a:
        ans = soup.new_tag("div")
        ans["class"] = ["mut"]
        ans["style"] = "margin-top:8px;"
        ans.string = a
        d.append(ans)

    return d


def _patch_faq(sec, soup, items: List[Dict[str, Any]]) -> bool:
    """
    Generator FAQ structure: <details><summary>Q</summary><div class="mut">A</div></details>
    Supports adding/removing FAQ items.
    """
    changed = False
    wrap = sec.select_one(".wrap") or sec

    details = wrap.find_all("details", recursive=True)

    # Adjust count
    n = len(items)
    if len(details) < n:
        for i in range(len(details), n):
            wrap.append(_faq_detail_node(soup, items[i] if isinstance(items[i], dict) else {}))
            changed = True
        details = wrap.find_all("details", recursive=True)

    if len(details) > n:
        for extra in details[n:]:
            extra.decompose()
            changed = True
        details = wrap.find_all("details", recursive=True)

    # Patch content
    for i in range(min(len(details), n)):
        it = items[i] if isinstance(items[i], dict) else {}
        q = (it.get("title") or "").strip()
        a = (it.get("text") or "").strip()

        det = details[i]
        summ = det.find("summary")
        if summ and q and summ.get_text(strip=True) != q:
            summ.clear()
            summ.append(q)
            changed = True

        ans = det.select_one(".mut") or det.find("div")
        if a:
            if ans is None:
                ans = soup.new_tag("div")
                ans["class"] = ["mut"]
                ans["style"] = "margin-top:8px;"
                det.append(ans)
                changed = True
            if ans.get_text(" ", strip=True) != a:
                ans.clear()
                ans.append(a)
                changed = True
        else:
            if ans is not None:
                ans.decompose()
                changed = True
        
        img_url = (it.get("imageUrl") or "").strip()
        img = det.find("img", attrs={"data-smx": "faq-img"}) or det.find("img")

        if img_url:
            if img is None:
                img = soup.new_tag("img")
                img["loading"] = "lazy"
                img["decoding"] = "async"
                img["style"] = "width:100%;height:auto;border-radius:14px;margin-top:10px;display:block;"
                img["data-smx"] = "faq-img"
                # insert right after summary
                summ = det.find("summary")
                if summ:
                    summ.insert_after(img)
                else:
                    det.insert(0, img)
                changed = True

            if img.get("src") != img_url:
                img["src"] = img_url
                changed = True
            if q and img.get("alt") != q:
                img["alt"] = q
                changed = True
        else:
            if img is not None:
                img.decompose()
                changed = True

    return changed


def _testimonial_card_node(soup, it: Dict[str, Any]):
    quote = (it.get("text") or "").strip()
    who = (it.get("title") or "").strip()
    img_url = (it.get("imageUrl") or "").strip()

    card = soup.new_tag("div")
    card["class"] = ["card", "reveal"]

    # optional avatar/photo
    if img_url:
        img = soup.new_tag("img")
        img["loading"] = "lazy"
        img["decoding"] = "async"
        img["src"] = img_url
        img["alt"] = who or "testimonial"
        img["style"] = "width:64px;height:64px;border-radius:999px;object-fit:cover;"
        card.append(img)

    qd = soup.new_tag("div")
    qd["class"] = ["quote"]
    qd.string = f"“{quote}”" if quote else ""
    qd["style"] = "margin-top:10px;" if img_url else ""
    card.append(qd)

    if who:
        wd = soup.new_tag("div")
        wd["class"] = ["mut"]
        wd["style"] = "margin-top:10px;font-weight:600;"
        wd.string = who
        card.append(wd)

    return card


def _patch_testimonials(sec, soup, items: List[Dict[str, Any]], cols: int) -> bool:
    """
    Generator testimonials structure:
      <div class="grid"> <div class="card"><div class="quote">…</div><div class="mut">Name</div></div> … </div>
    Supports adding/removing testimonials.
    """
    changed = False
    grid = sec.select_one(".grid")
    if grid is None:
        grid = _ensure_grid(sec, soup, max(1, min(cols, 3)))

    cards = grid.select(":scope > .card")
    n = len(items)

    # Adjust count
    if len(cards) < n:
        for i in range(len(cards), n):
            grid.append(_testimonial_card_node(soup, items[i] if isinstance(items[i], dict) else {}))
            changed = True
        cards = grid.select(":scope > .card")

    if len(cards) > n:
        for extra in cards[n:]:
            extra.decompose()
            changed = True
        cards = grid.select(":scope > .card")

    # Patch content
    for i in range(min(len(cards), n)):
        it = items[i] if isinstance(items[i], dict) else {}
        quote = (it.get("text") or "").strip()
        who = (it.get("title") or "").strip()

        card = cards[i]
        img_url = (it.get("imageUrl") or "").strip()
        img = card.find("img")
        if img_url:
            if img is None:
                img = soup.new_tag("img")
                img["loading"] = "lazy"
                img["decoding"] = "async"
                img["style"] = "width:64px;height:64px;border-radius:999px;object-fit:cover;"
                card.insert(0, img)
                changed = True
            if img.get("src") != img_url:
                img["src"] = img_url
                changed = True
            if who and img.get("alt") != who:
                img["alt"] = who
                changed = True
        else:
            if img is not None:
                img.decompose()
        changed = True
        qd = card.select_one(".quote") or card.find("div")
        if qd and quote:
            want = f"“{quote}”"
            if qd.get_text(strip=True) != want:
                qd.clear()
                qd.append(want)
                changed = True

        wd = card.select_one(".mut")
        if who:
            if wd is None:
                wd = soup.new_tag("div")
                wd["class"] = ["mut"]
                wd["style"] = "margin-top:10px;font-weight:600;"
                card.append(wd)
                changed = True
            if wd.get_text(" ", strip=True) != who:
                wd.clear()
                wd.append(who)
                changed = True
        else:
            if wd is not None:
                wd.decompose()
                changed = True

    # Keep columns sensible
    grid["style"] = f"grid-template-columns:repeat({max(1, min(cols, 3))}, minmax(0,1fr));"
    return changed


def _patch_items_in_section_by_id(
    html: str,
    sid: str,
    stype: str,
    items: List[Dict[str, Any]],
    cols: int
) -> Tuple[str, bool]:
    """
    Dispatcher: patch items according to widget type, within <section id="sid"> only.
    """
    if not html or not sid:
        return html, False

    soup = BeautifulSoup(html, "html.parser")
    sec = soup.find("section", id=sid)
    if sec is None:
        return html, False

    st = (stype or "").lower().strip()

    if st == "faq":
        changed = _patch_faq(sec, soup, items)
        return str(soup), changed

    if st == "testimonials":
        changed = _patch_testimonials(sec, soup, items, cols=cols)
        return str(soup), changed

    # default cards grid: features/gallery/cta/richtext/anything else that uses cards
    changed = _patch_default_cards(sec, soup, items, cols=cols)
    return str(soup), changed


def _patch_hero(html: str, hero_section: Dict[str, Any]) -> Tuple[str, bool]:
    """
    Patch hero bg image + <h1> + lead paragraph inside the hero section.
    Handles both:
      - <div class="hero-bg" style="background-image:...">
      - <img ...> used as hero media
    """
    if not html or not isinstance(hero_section, dict):
        return html, False

    sid = (hero_section.get("id") or "").strip()
    title = (hero_section.get("title") or "").strip()
    text = (hero_section.get("text") or "").strip()

    img_url = (hero_section.get("imageUrl") or "").strip()
    items = hero_section.get("items") if isinstance(hero_section.get("items"), list) else []
    if not img_url and items and isinstance(items[0], dict):
        img_url = (items[0].get("imageUrl") or "").strip()

    soup = BeautifulSoup(html, "html.parser")

    # Locate hero section
    hero_tag = None
    if sid:
        hero_tag = soup.find("section", id=sid)

    if hero_tag is None:
        # fallback: first section with class containing 'hero'
        for sec in soup.find_all("section"):
            cls = " ".join(sec.get("class") or [])
            if "hero" in cls.split():
                hero_tag = sec
                break

    if hero_tag is None:
        return html, False

    changed = False

    # Patch hero image
    if img_url:
        # 1) background div
        bg = hero_tag.select_one(".hero-bg")
        if bg is not None:
            style = bg.get("style") or ""
            parts = [p.strip() for p in style.split(";") if p.strip() and not p.strip().lower().startswith("background-image")]
            parts.append(f'background-image:url("{img_url}")')
            bg["style"] = "; ".join(parts) + ";"
            changed = True
        else:
            # 2) hero img fallback
            im = hero_tag.find("img")
            if im is not None:
                im["src"] = img_url
                # also update srcset if present (best-effort)
                if im.has_attr("srcset"):
                    im["srcset"] = img_url
                changed = True

    # Patch hero H1
    if title:
        h1 = hero_tag.find("h1")
        if h1 is not None:
            h1.clear()
            h1.append(title)
            changed = True

    # Patch lead paragraph (class 'lead' preferred; fallback: first long <p> inside hero)
    if text:
        lead = hero_tag.select_one("p.lead")
        if lead is None:
            # fallback: first paragraph with enough text
            for p in hero_tag.find_all("p"):
                t = p.get_text(" ", strip=True)
                if len(t) >= 15:
                    lead = p
                    break
        if lead is not None:
            lead.clear()
            lead.append(text)
            changed = True
    
    # Patch hero buttons (btnRow) if heroCta fields exist in layout
    has_cta_fields = any(k in hero_section for k in ("heroCta1Label", "heroCta1Href", "heroCta2Label", "heroCta2Href"))
    if has_cta_fields:
        row = hero_tag.select_one(".btnRow")

        # If missing, create it inside the hero panel (best-effort)
        if row is None:
            panel = hero_tag.select_one(".hero-panel") or hero_tag
            row = soup.new_tag("div")
            row["class"] = ["btnRow"]
            panel.append(row)

        # Rebuild buttons from layout (blank/unsafe href => remove button)
        row.clear()

        def _add_btn(label_key: str, href_key: str, cta_no: int):
            nonlocal changed
            label = (hero_section.get(label_key) or "").strip() or "Button"
            href_raw = hero_section.get(href_key, "")
            href = _safe_href(str(href_raw))
            if not href:
                return
            a = soup.new_tag("a")
            a["class"] = ["btn"]
            a["data-smx"] = "hero-cta"
            a["data-cta"] = str(cta_no)
            a["href"] = href
            a.string = label
            row.append(a)
            changed = True

        _add_btn("heroCta1Label", "heroCta1Href", 1)
        _add_btn("heroCta2Label", "heroCta2Href", 2)

        # If user removed both, remove the row entirely
        if not row.find("a"):
            row.decompose()
            changed = True
    
        # Strip legacy Admin/Edit hero buttons from older generated pages
        for a in list(hero_tag.find_all("a")):
            href = (a.get("href") or "").strip()
            if href == "/admin" or href.startswith("/admin/edit/"):
                parent = a.parent
                a.decompose()
                changed = True

                # If the parent btnRow becomes empty, remove it
                if parent is not None and getattr(parent, "name", None):
                    if "btnRow" in (parent.get("class") or []) and not parent.find("a"):
                        parent.decompose()
                        changed = True
                        
    # If layout has no explicit hero CTA hrefs, remove any existing btnRow from the hero
    cta1 = hero_section.get("heroCta1Href") if isinstance(hero_section, dict) else None
    cta2 = hero_section.get("heroCta2Href") if isinstance(hero_section, dict) else None
    cta1_ok = bool(_safe_href(str(cta1 or ""))) if cta1 is not None else False
    cta2_ok = bool(_safe_href(str(cta2 or ""))) if cta2 is not None else False

    if not (cta1_ok or cta2_ok):
        for row in list(hero_tag.select(".btnRow")):
            row.decompose()
            changed = True

    return str(soup), changed


def _fallback_section_fragment(soup, s: Dict[str, Any]) -> Any:
    sid = (s.get("id") or "").strip() or "sec_new"
    title = (s.get("title") or "").strip()
    text = (s.get("text") or "").strip()

    sec = soup.new_tag("section")
    sec["id"] = sid
    sec["class"] = ["sec"]

    wrap = soup.new_tag("div")
    wrap["class"] = ["wrap"]
    sec.append(wrap)

    h2 = soup.new_tag("h2")
    h2["class"] = ["reveal"]
    h2.string = title or "New section"
    wrap.append(h2)

    if text:
        p = soup.new_tag("p")
        p["class"] = ["reveal"]
        p["style"] = "margin-bottom:14px;"
        p.string = text
        wrap.append(p)

    # grid placeholder (items patcher will fill it)
    grid = soup.new_tag("div")
    grid["class"] = ["grid"]
    grid["style"] = "grid-template-columns:repeat(3, minmax(0,1fr));"
    wrap.append(grid)

    return sec


def ensure_sections_exist(existing_html: str, layout: Dict[str, Any], *, page_slug: Optional[str] = None) -> Tuple[str, int]:
    """
    If the layout contains sections that are missing from existing_html, insert them.
    We try to copy the section HTML from compile_layout_to_html(layout).
    Fallback: create a minimal section fragment.
    """
    if not existing_html or not isinstance(layout, dict):
        return existing_html, 0

    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    want_ids = []
    for s in sections:
        if not isinstance(s, dict):
            continue
        sid = (s.get("id") or "").strip()
        if sid:
            want_ids.append(sid)

    if not want_ids:
        return existing_html, 0

    soup = BeautifulSoup(existing_html, "html.parser")

    # Find where sections live (parent of first existing <section>, else <main>, else <body>)
    first_sec = soup.find("section")
    container = first_sec.parent if first_sec and first_sec.parent else (soup.find("main") or soup.body or soup)

    existing = {sec.get("id") for sec in soup.find_all("section") if sec.get("id")}

    # Build a source soup from compiler output (best-effort)
    src_soup = None
    try:
        from syntaxmatrix.page_builder_generation import compile_layout_to_html
        compiled = compile_layout_to_html(layout, page_slug=page_slug or (layout.get("page") or "page"))
        src_soup = BeautifulSoup(compiled, "html.parser")
    except Exception:
        src_soup = None

    inserted = 0
    prev_tag = None

    # Insert missing sections in layout order (after the last seen section)
    for s in sections:
        if not isinstance(s, dict):
            continue
        sid = (s.get("id") or "").strip()
        if not sid:
            continue

        already = soup.find("section", id=sid)
        if already is not None:
            prev_tag = already
            continue

        # Get section HTML from compiled output
        new_sec = src_soup.find("section", id=sid) if src_soup else None
        if new_sec is None:
            new_sec = _fallback_section_fragment(soup, s)
        else:
            frag = BeautifulSoup(str(new_sec), "html.parser").find("section")
            new_sec = frag if frag is not None else _fallback_section_fragment(soup, s)

        if prev_tag is not None:
            prev_tag.insert_after(new_sec)
        else:
            container.append(new_sec)

        prev_tag = new_sec
        inserted += 1
        existing.add(sid)

    return str(soup), inserted


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
    # refuse anything that can terminate / inject CSS
    bad = ["{", "}", ";", "<", ">", "\n", "\r"]
    if any(b in ff for b in bad):
        return ""
    return ff


def _safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\-]+", "-", s).strip("-")
    return s or "page"


def _build_theme_style(layout: dict, *, page_slug: str | None = None) -> str:
    theme = layout.get("theme") if isinstance(layout.get("theme"), dict) else {}
    if not theme:
        return ""

    font_body = _css_safe_font(theme.get("fontBody") or theme.get("bodyFont") or theme.get("font_body") or "")
    font_head = _css_safe_font(theme.get("fontHeading") or theme.get("headingFont") or theme.get("font_heading") or "")

    accent = _css_safe_hex(theme.get("accent") or "")
    fg = _css_safe_hex(theme.get("fg") or "")
    mut = _css_safe_hex(theme.get("mut") or "")
    bg = _css_safe_hex(theme.get("bg") or "")

    # If user sets text but not muted (or vice-versa), make it visibly change.
    if fg and not mut:
        mut = fg
    if mut and not fg:
        fg = mut

    if not any([font_body, font_head, accent, fg, mut, bg]):
        return ""

    slug = _safe_slug(page_slug or "")
    root_id = f"smx-page-{slug}"

    # Apply to the page id AND as a fallback to any SMX page wrapper.
    root_sel = f'#{root_id}, div[id^="smx-page-"]'

    lines: List[str] = []
    lines.append(f"{root_sel}{{")

    if fg:
        lines.append(f"  --fg:{fg} !important;")
        lines.append("  color:var(--fg) !important;")
    if mut:
        lines.append(f"  --mut:{mut} !important;")
    if bg:
        lines.append(f"  --bg:{bg} !important;")
        lines.append("  background:var(--bg) !important;")
    if font_body:
        lines.append(f"  font-family:{font_body} !important;")

    if accent:
        lines.append(f"  --accent:{accent} !important;")
        soft = _hex_to_rgba(accent, 0.12)
        if soft:
            lines.append(f"  --accentSoft:{soft} !important;")

    lines.append("}")

    # Make body text visibly change (your compiled templates often force p to --mut)
    if fg:
        lines.append(f'#{root_id} p, div[id^="smx-page-"] p{{ color:var(--fg) !important; }}')
    if mut:
        # preserve muted styling for explicit muted elements
        lines.append(f'#{root_id} .mut, #{root_id} .kicker, div[id^="smx-page-"] .mut, div[id^="smx-page-"] .kicker{{ color:var(--mut) !important; }}')

    if font_head:
        lines.append(
            f'#{root_id} h1, #{root_id} h2, #{root_id} h3, '
            f'div[id^="smx-page-"] h1, div[id^="smx-page-"] h2, div[id^="smx-page-"] h3'
            f'{{ font-family:{font_head} !important; }}'
        )

    if accent:
        lines.append(f'#{root_id} a, div[id^="smx-page-"] a{{ color:var(--accent) !important; }}')
        lines.append(f'#{root_id} .btn, div[id^="smx-page-"] .btn{{ background:var(--accentSoft, rgba(99,102,241,.12)) !important; }}')

    css = "\n".join(lines)
    return f'<style id="smx-theme" data-smx="theme">\n{css}\n</style>'


def _patch_theme(existing_html: str, layout: dict, *, page_slug: str | None = None) -> tuple[str, bool]:
    if not existing_html or not isinstance(layout, dict):
        return existing_html, False

    # 1) Remove ALL existing theme blocks (you currently have many duplicates)
    pat_all = re.compile(r'<style\b[^>]*\bid="smx-theme"[^>]*>.*?</style>\s*', re.IGNORECASE | re.DOTALL)
    cleaned = pat_all.sub("", existing_html)

    # 2) Build the new theme block
    new_style = _build_theme_style(layout, page_slug=page_slug)

    # If theme now empty, just return the cleaned HTML
    if not new_style:
        return cleaned, (cleaned != existing_html)

    # 3) Insert in a stable place: inside the page wrapper, right after the base <style> if present
    slug = _safe_slug(page_slug or "")
    root_id = f"smx-page-{slug}"

    # Find the wrapper open tag
    m = re.search(rf'<div\b[^>]*\bid=["\']{re.escape(root_id)}["\'][^>]*>', cleaned, re.IGNORECASE)
    if m:
        start = m.end()
        # Insert after the first </style> following the wrapper (this keeps it near the existing page CSS)
        lower = cleaned.lower()
        k = lower.find("</style>", start)
        if k != -1:
            insert_at = k + len("</style>")
            out = cleaned[:insert_at] + "\n" + new_style + cleaned[insert_at:]
            return out, True

        # Otherwise insert immediately after wrapper open
        out = cleaned[:start] + "\n" + new_style + cleaned[start:]
        return out, True

    # Fallback: insert before </head> if it exists
    lower = cleaned.lower()
    kh = lower.find("</head>")
    if kh != -1:
        out = cleaned[:kh] + new_style + "\n" + cleaned[kh:]
        return out, True

    # Final fallback: prepend
    return new_style + "\n" + cleaned, True


def _style_to_dict(style: str) -> dict:
    """
    Parse inline style="a:b; c:d" -> {"a":"b", "c":"d"}
    """
    out = {}
    for part in (style or "").split(";"):
        part = part.strip()
        if not part or ":" not in part:
            continue
        k, v = part.split(":", 1)
        k = k.strip().lower()
        v = v.strip()
        if k:
            out[k] = v
    return out


def _dict_to_style(d: dict) -> str:
    """
    {"a":"b","c":"d"} -> "a:b; c:d;"
    """
    if not d:
        return ""
    return "; ".join([f"{k}:{v}" for k, v in d.items() if k and v]) + ";"


def _merge_inline_style(existing: str, set_kv: dict | None = None, remove_keys: list[str] | None = None) -> str:
    d = _style_to_dict(existing or "")
    for k in (remove_keys or []):
        d.pop((k or "").strip().lower(), None)
    for k, v in (set_kv or {}).items():
        kk = (k or "").strip().lower()
        vv = (v or "").strip()
        if not kk:
            continue
        if not vv:
            d.pop(kk, None)
        else:
            d[kk] = vv
    return _dict_to_style(d)


def _sec_style_parse(section: dict) -> dict:
    """
    Normalise supported section style inputs from layout JSON.

    Expected layout shape (example):
      section["style"] = {
        "bg": "#ffffff",
        "pad": "compact" | "normal" | "spacious",
        "align": "left" | "center" | "right"
      }
    """
    raw = section.get("style")
    if not isinstance(raw, dict):
        raw = {}

    bg = _css_safe_hex(raw.get("bg") or raw.get("background") or "")
    pad = (raw.get("pad") or raw.get("padding") or "").strip().lower()
    align = (raw.get("align") or raw.get("textAlign") or raw.get("text_align") or "").strip().lower()

    if pad not in {"compact", "normal", "spacious"}:
        pad = ""
    if align not in {"left", "center", "right"}:
        align = ""

    return {"bg": bg, "pad": pad, "align": align}


def _sec_style_dump(style: dict) -> tuple[dict, dict]:
    """
    Returns:
      (section_style_kv, wrap_style_kv)
    """
    sec_kv = {}
    wrap_kv = {}

    bg = (style or {}).get("bg") or ""
    pad = (style or {}).get("pad") or ""
    align = (style or {}).get("align") or ""

    # Background on <section>
    if bg:
        sec_kv["background"] = bg

    # Padding override on <section> (base CSS is .sec{ padding:56px 0; })
    # normal = no override (remove any previous override)
    if pad == "compact":
        sec_kv["padding"] = "36px 0"
    elif pad == "spacious":
        sec_kv["padding"] = "84px 0"

    # Text alignment: safer to apply to the section's inner ".wrap"
    if align in {"left", "center", "right"} and align != "left":
        wrap_kv["text-align"] = align

    return sec_kv, wrap_kv


def _patch_section_styles(existing_html: str, layout: dict) -> tuple[str, bool]:
    """
    Applies per-section styles to:
      <section id="{sid}"> ... <div class="wrap"> ... </div> </section>

    - Sets/removes inline background + padding on section
    - Sets/removes text-align on the section's first .wrap
    """
    if not existing_html or not isinstance(layout, dict):
        return existing_html, False

    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    if not sections:
        return existing_html, False

    soup = BeautifulSoup(existing_html, "html.parser")
    changed = False

    for s in sections:
        if not isinstance(s, dict):
            continue

        sid = (s.get("id") or "").strip()
        if not sid:
            continue

        # Find the section node by id
        sec = soup.find(id=sid)
        if not sec:
            continue

        # We only want the <section> element; if the id is on something else, try to find a <section id="sid">
        if sec.name != "section":
            sec2 = soup.find("section", attrs={"id": sid})
            if not sec2:
                continue
            sec = sec2

        style = _sec_style_parse(s)
        sec_kv, wrap_kv = _sec_style_dump(style)

        # Always remove keys if they were previously set, so "reset to default" works
        sec_remove = ["background", "padding"]
        wrap_remove = ["text-align"]

        # Apply section inline styles
        before = sec.get("style") or ""
        after = _merge_inline_style(before, set_kv=sec_kv, remove_keys=sec_remove)
        if after != before:
            if after:
                sec["style"] = after
            else:
                sec.attrs.pop("style", None)
            changed = True

        # Apply wrap alignment (first .wrap inside the section)
        wrap = sec.find("div", class_="wrap")
        if wrap:
            w_before = wrap.get("style") or ""
            w_after = _merge_inline_style(w_before, set_kv=wrap_kv, remove_keys=wrap_remove)
            if w_after != w_before:
                if w_after:
                    wrap["style"] = w_after
                else:
                    wrap.attrs.pop("style", None)
                changed = True

    out = str(soup)
    return out, changed


def patch_page_publish(existing_html: str, layout: Dict[str, Any], page_slug: Optional[str] = None) -> Tuple[str, Dict[str, int]]:
    """
    Patch-only publish:
      - hero bg + hero title + hero lead
      - each non-hero section <h2> + intro <p>, matched by section id
    """
    stats = {"hero": 0, "sections": 0, "skipped": 0}

    if not existing_html or not isinstance(layout, dict):
        return existing_html, stats

    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []

    # Without this, patch-only publish can only *update* existing HTML, not remove stale blocks.
    existing_html, removed = _remove_deleted_sections(existing_html, layout, page_slug=page_slug)
    if removed:
        stats["removed_sections"] = removed

    # NEW: insert any missing widget sections so patching can update them
    existing_html, inserted = ensure_sections_exist(existing_html, layout)
    if inserted:
        stats["inserted_sections"] = inserted

    existing_html, theme_changed = _patch_theme(existing_html, layout, page_slug=page_slug)
    if theme_changed:
        stats["theme"] = 1

    # hero
    hero = next((s for s in sections if isinstance(s, dict) and (s.get("type") or "").lower() == "hero"), None)
    if hero:
        existing_html, hero_changed = _patch_hero(existing_html, hero)
        if hero_changed:
            stats["hero"] = 1

    # other sections by id
    for s in sections:
        if not isinstance(s, dict):
            continue
        if (s.get("type") or "").lower() == "hero":
            continue

        sid = (s.get("id") or "").strip()
        if not sid:
            stats["skipped"] += 1
            continue

        title = s.get("title")
        text = s.get("text")

        existing_html, ok = _patch_section_by_id(existing_html, sid, title=title, text=text)
        if ok:
            stats["sections"] += 1

        items = s.get("items") if isinstance(s.get("items"), list) else []
        stype = (s.get("type") or "").lower()
        try:
            cols = int(s.get("cols") or 3)
        except Exception:
            cols = 3
        cols = max(1, min(5, cols))

        # Patch items even if empty (empty means "remove extras" for that widget)
        existing_html, ok_items = _patch_items_in_section_by_id(existing_html, sid, stype, items, cols)
        if ok_items:
            stats[f"items_{stype or 'section'}"] = stats.get(f"items_{stype or 'section'}", 0) + 1

        # Sprint 4: apply per-section styles (bg/padding/align)
        existing_html, sec_style_changed = _patch_section_styles(existing_html, layout)
        if sec_style_changed:
            stats["section_styles"] = stats.get("section_styles", 0) + 1


    return existing_html, stats


def _remove_deleted_sections(existing_html: str, layout: Dict[str, Any], *, page_slug: Optional[str] = None) -> Tuple[str, int]:
    """Remove <section> blocks that exist in HTML but no longer exist in the saved layout.

    Patch-only publish updates content in-place. Without this step, deleting a section in the
    builder will not remove the old <section> from the previously generated HTML, so it will
    still show on the live page.
    """
    if not existing_html or not isinstance(layout, dict):
        return existing_html, 0

    sections = layout.get("sections") if isinstance(layout.get("sections"), list) else []
    keep_ids = set()
    for s in sections:
        if isinstance(s, dict):
            sid = (s.get("id") or "").strip()
            if sid:
                keep_ids.add(sid)

    soup = BeautifulSoup(existing_html, "html.parser")

    # Restrict removals to the page wrapper if we can find it.
    root = None
    if page_slug:
        raw = str(page_slug).strip()
        safe = re.sub(r"[^a-z0-9\-]+", "-", raw.lower()).strip("-")
        for rid in (f"smx-page-{raw}", f"smx-page-{safe}"):
            root = soup.find("div", id=rid)
            if root:
                break

    if not root:
        root = soup.find("div", id=re.compile(r"^smx-page-", re.IGNORECASE))

    # Fallback: if wrapper not found, operate on body (still safe because we only remove
    # builder-style sections).
    if not root:
        root = soup.body or soup

    removed = 0
    for sec in list(root.find_all("section")):
        sid = (sec.get("id") or "").strip()
        if not sid:
            continue

        # Only touch builder sections.
        is_builder_section = sid.startswith("sec_") or sec.has_attr("data-section-type")
        if not is_builder_section:
            continue

        if sid not in keep_ids:
            sec.decompose()
            removed += 1

    return str(soup), removed
