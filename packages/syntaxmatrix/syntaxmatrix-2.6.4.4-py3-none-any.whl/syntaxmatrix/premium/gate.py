from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


def _safe_json_loads(raw: str, *, default: Any) -> Any:
    try:
        return json.loads(raw)
    except Exception:
        return default


@dataclass
class GateSources:
    """Where the gate reads entitlements from.

    Precedence (highest first):
      1) env_json
      2) db_setting_key
      3) licence_file
    """

    env_json: str = "SMX_PREMIUM_ENTITLEMENTS"
    db_setting_key: str = "premium.entitlements"
    licence_file_relpath: str = os.path.join("premium", "licence.json")


class FeatureGate:
    """Runtime entitlement checks for premium features.

    This is intentionally small, dependency-free, and safe:
    - If anything fails, it returns 'not entitled' rather than crashing the app.
    """

    def __init__(
        self,
        *,
        client_dir: str,
        db: Optional[object] = None,
        sources: Optional[GateSources] = None,
    ):
        self._client_dir = client_dir
        self._db = db
        self._sources = sources or GateSources()
        self._cache: Optional[Dict[str, Any]] = None

    def _load_from_env(self) -> Optional[Dict[str, Any]]:
        raw = os.environ.get(self._sources.env_json)
        if not raw:
            return None
        data = _safe_json_loads(raw, default=None)
        return data if isinstance(data, dict) else None

    def _load_from_db(self) -> Optional[Dict[str, Any]]:
        if not self._db:
            return None
        get_setting = getattr(self._db, "get_setting", None)
        if not callable(get_setting):
            return None

        raw = get_setting(self._sources.db_setting_key, "{}")
        data = _safe_json_loads(str(raw or "{}"), default={})
        return data if isinstance(data, dict) else None

    def _load_from_file(self) -> Optional[Dict[str, Any]]:
        p = os.path.join(self._client_dir, self._sources.licence_file_relpath)
        if not os.path.exists(p):
            return None
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def entitlements(self, *, refresh: bool = False) -> Dict[str, Any]:
        """Returns entitlement dict (possibly empty)."""
        if self._cache is not None and not refresh:
            return self._cache

        ent = self._load_from_env()
        if ent is None:
            ent = self._load_from_db()
        if ent is None:
            ent = self._load_from_file()
        if ent is None:
            ent = {}

        self._cache = ent
        return ent

    def enabled(self, key: str) -> bool:
        """True if entitlement exists and is truthy."""
        key = (key or "").strip()
        if not key:
            return False
        ent = self.entitlements()
        return bool(ent.get(key))

    def get(self, key: str, default: Any = None) -> Any:
        key = (key or "").strip()
        if not key:
            return default
        return self.entitlements().get(key, default)
