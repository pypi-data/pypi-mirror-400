from __future__ import annotations

import importlib
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


def _safe_json_loads(raw: str, *, default: Any) -> Any:
    try:
        return json.loads(raw)
    except Exception:
        return default


@dataclass
class PluginSpec:
    """A single plugin to load.

    module: python module path (e.g. 'syntaxmatrix_premium_cloud_db')
    name: entitlement key (e.g. 'cloud_db')
    """

    name: str
    module: str


class PluginManager:
    """Loads optional plugins (typically premium) in a controlled, safe way."""

    ENV_PLUGINS = "SMX_PREMIUM_PLUGINS"          # JSON list of {name,module}
    DB_PLUGINS_KEY = "premium.plugins"          # JSON list of {name,module}

    def __init__(self, smx: object, *, gate: Optional[object] = None, db: Optional[object] = None):
        self._smx = smx
        self._gate = gate
        self._db = db
        self.loaded: Dict[str, str] = {}   # name -> module
        self.errors: List[str] = []

    def _specs_from_env(self) -> List[PluginSpec]:
        raw = os.environ.get(self.ENV_PLUGINS, "").strip()
        if not raw:
            return []
        data = _safe_json_loads(raw, default=[])
        return self._coerce_specs(data)

    def _specs_from_db(self) -> List[PluginSpec]:
        if not self._db:
            return []
        get_setting = getattr(self._db, "get_setting", None)
        if not callable(get_setting):
            return []
        raw = get_setting(self.DB_PLUGINS_KEY, "[]")
        data = _safe_json_loads(str(raw or "[]"), default=[])
        return self._coerce_specs(data)

    def _coerce_specs(self, data: Any) -> List[PluginSpec]:
        out: List[PluginSpec] = []
        if isinstance(data, list):
            for row in data:
                if not isinstance(row, dict):
                    continue
                name = str(row.get("name") or "").strip()
                module = str(row.get("module") or "").strip()
                if name and module:
                    out.append(PluginSpec(name=name, module=module))
        return out

    def _entitled(self, name: str) -> bool:
        if not self._gate:
            return True  # if no gate configured, don't block
        enabled = getattr(self._gate, "enabled", None)
        if not callable(enabled):
            return True
        try:
            return bool(enabled(name))
        except Exception:
            return False

    def load_all(self) -> Tuple[Dict[str, str], List[str]]:
        """Load all configured plugins. Returns (loaded, errors)."""
        specs = self._specs_from_env()
        if not specs:
            specs = self._specs_from_db()

        for spec in specs:
            if not self._entitled(spec.name):
                continue
            if spec.name in self.loaded:
                continue
            self._load_one(spec)

        return self.loaded, self.errors

    def _load_one(self, spec: PluginSpec) -> None:
        try:
            mod = importlib.import_module(spec.module)
        except Exception as e:
            self.errors.append(f"{spec.name}: import failed: {e}")
            return

        # Plugin contract: module exposes register(smx) -> None
        reg = getattr(mod, "register", None)
        if not callable(reg):
            self.errors.append(f"{spec.name}: missing register(smx) function")
            return

        try:
            reg(self._smx)
            self.loaded[spec.name] = spec.module
        except Exception as e:
            self.errors.append(f"{spec.name}: register() failed: {e}")
