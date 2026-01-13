from __future__ import annotations

import hashlib
import io
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from PIL import Image


PIXABAY_API_URL = "https://pixabay.com/api/"


@dataclass
class PixabayHit:
    id: int
    page_url: str
    tags: str
    user: str
    preview_url: str
    webformat_url: str
    large_image_url: str
    width: int
    height: int
    image_type: str


def _clean_query(q: str) -> str:
    q = (q or "").strip()
    q = re.sub(r"\s+", " ", q)
    return q[:100]


def pixabay_search(
    api_key: str,
    query: str,
    *,
    image_type: str = "photo",
    orientation: str = "horizontal",
    per_page: int = 24,
    page: int = 1,
    safesearch: bool = True,
    editors_choice: bool = False,
    min_width: int = 0,
    min_height: int = 0,
    timeout: int = 15,
) -> List[PixabayHit]:
    """Search Pixabay and return normalised hits."""
    if not api_key:
        return []

    q = _clean_query(query)
    if not q:
        return []

    per_page = max(3, min(200, int(per_page or 24)))
    page = max(1, int(page or 1))

    params = {
        "key": api_key,
        "q": q,
        "image_type": image_type or "photo",
        "orientation": orientation or "all",
        "per_page": per_page,
        "page": page,
        "safesearch": "true" if safesearch else "false",
        "editors_choice": "true" if editors_choice else "false",
        "min_width": int(min_width or 0),
        "min_height": int(min_height or 0),
        "order": "popular",
    }

    r = requests.get(PIXABAY_API_URL, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json() or {}
    hits = data.get("hits") or []

    out: List[PixabayHit] = []
    for h in hits:
        try:
            out.append(
                PixabayHit(
                    id=int(h.get("id")),
                    page_url=str(h.get("pageURL") or ""),
                    tags=str(h.get("tags") or ""),
                    user=str(h.get("user") or ""),
                    preview_url=str(h.get("previewURL") or ""),
                    webformat_url=str(h.get("webformatURL") or ""),
                    large_image_url=str(h.get("largeImageURL") or ""),
                    width=int(h.get("imageWidth") or 0),
                    height=int(h.get("imageHeight") or 0),
                    image_type=str(h.get("type") or image_type or "photo"),
                )
            )
        except Exception:
            continue

    return out


def _is_pixabay_url(url: str) -> bool:
    url = (url or "").strip().lower()
    return url.startswith("https://") and ("pixabay.com" in url)


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _dhash_hex(img: Image.Image, size: int = 8) -> str:
    g = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    rows = [px[i * (size + 1):(i + 1) * (size + 1)] for i in range(size)]
    bits = []
    for row in rows:
        for x in range(size):
            bits.append(1 if row[x] > row[x + 1] else 0)

    val = 0
    for b in bits:
        val = (val << 1) | b
    return f"{val:0{size*size//4}x}"


def download_and_store_image(
    url: str,
    *,
    out_path_no_ext: str,
    max_width: int = 1920,
    thumb_dir: Optional[str] = None,
    thumb_width: int = 800,
    timeout: int = 20,
    min_width: int = 0,
    fallback_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Downloads an image from Pixabay.

    Rule:
      - Always try `url` first (webformat).
      - If `min_width` is set and the downloaded image is narrower than min_width,
        then try `fallback_url` (large) once, and keep it only if it's larger.
      - Then resize down to max_width (1920).
      - Save as JPG unless image has alpha channel (then PNG).
      - Create thumbnail only if width > 800px (your rule).
    """

    def _fetch(u: str) -> bytes:
        if not _is_pixabay_url(u):
            raise ValueError("Only Pixabay URLs are allowed")
        rr = requests.get(u, stream=True, timeout=timeout)
        rr.raise_for_status()
        return rr.content

    # 1) Fetch webformat first
    content = _fetch(url)
    img = Image.open(io.BytesIO(content))
    img.load()

    # 2) If too small (e.g., hero) try large variant once
    if min_width and img.width < int(min_width) and fallback_url:
        try:
            content2 = _fetch(fallback_url)
            img2 = Image.open(io.BytesIO(content2))
            img2.load()
            if img2.width > img.width:
                content = content2
                img = img2
        except Exception:
            # If large fetch fails, keep webformat result
            pass

    # 3) Resize down to max_width (never upsample)
    if img.width > int(max_width or 1920):
        ratio = (int(max_width) / float(img.width))
        new_h = max(1, int(round(img.height * ratio)))
        img = img.resize((int(max_width), new_h), Image.LANCZOS)

    # 4) Decide output format
    has_alpha = ("A" in img.getbands())
    ext = ".png" if has_alpha else ".jpg"
    out_path = out_path_no_ext + ext
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # 5) Encode + save
    buf = io.BytesIO()
    if ext == ".jpg":
        rgb = img.convert("RGB") if img.mode != "RGB" else img
        rgb.save(buf, "JPEG", quality=85, optimize=True, progressive=True)
        mime = "image/jpeg"
    else:
        img.save(buf, "PNG", optimize=True)
        mime = "image/png"

    data = buf.getvalue()
    with open(out_path, "wb") as f:
        f.write(data)

    meta = {
        "file_path": out_path,
        "width": img.width,
        "height": img.height,
        "sha256": _sha256_bytes(data),
        "dhash": _dhash_hex(img),
        "mime": mime,
    }

    # 6) Thumbnail only if width > 800px (your rule)
    if thumb_dir and img.width > int(thumb_width or 800):
        os.makedirs(thumb_dir, exist_ok=True)
        thumb = img.copy()
        ratio = (int(thumb_width) / float(thumb.width))
        new_h = max(1, int(round(thumb.height * ratio)))
        thumb = thumb.resize((int(thumb_width), new_h), Image.LANCZOS)

        thumb_path = os.path.join(
            thumb_dir,
            os.path.basename(out_path_no_ext) + f"-t{int(thumb_width)}.jpg"
        )

        tb = io.BytesIO()
        thumb_rgb = thumb.convert("RGB") if thumb.mode != "RGB" else thumb
        thumb_rgb.save(tb, "JPEG", quality=82, optimize=True, progressive=True)
        with open(thumb_path, "wb") as f:
            f.write(tb.getvalue())

        meta["thumb_path"] = thumb_path

    return meta

def import_pixabay_hit(
    hit: PixabayHit,
    *,
    media_images_dir: str,
    thumbs_dir: Optional[str] = None,
    max_width: int = 1920,
    thumb_width: int = 800,
    min_width: int = 0,
) -> Dict[str, Any]:
    # Efficient by default: use webformat first.
    url = hit.webformat_url or hit.large_image_url
    if not url:
        raise ValueError("No image url")

    if not _is_pixabay_url(url):
        raise ValueError("Only Pixabay URLs are allowed")

    # Only use large as fallback when webformat is too small for the use-case (e.g., hero)
    fallback = None
    if url == hit.webformat_url and hit.large_image_url and hit.large_image_url != hit.webformat_url:
        fallback = hit.large_image_url

    out_base = os.path.join(media_images_dir, f"pixabay-{hit.id}")

    meta = download_and_store_image(
        url,
        out_path_no_ext=out_base,
        max_width=max_width,
        thumb_dir=thumbs_dir,
        thumb_width=thumb_width,
        min_width=min_width,
        fallback_url=fallback,
    )

    meta.update(
        {
            "source": "pixabay",
            "source_url": hit.page_url,
            "author": hit.user,
            "tags": hit.tags,
            "pixabay_id": hit.id,
        }
    )
    return meta
