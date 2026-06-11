from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

SUPPORTED_ASSET_TYPES = {"exact_secret", "pattern_secret", "semantic_secret", "document_secret"}
SUPPORTED_RISK_LEVELS = {"low", "medium", "high", "critical"}


@dataclass
class ProtectedAsset:
    asset_id: str
    name: str = ""
    asset_type: str = "exact_secret"
    value: str = ""
    env_var: str = ""
    pattern: str = ""
    aliases: list[str] = field(default_factory=list)
    semantic_labels: list[str] = field(default_factory=list)
    risk_level: str = "high"
    enabled: bool = True
    allow_encoded_detection: bool = True
    description: str = ""
    source: str = ""

    @property
    def effective_value(self) -> str:
        if self.env_var:
            return os.getenv(self.env_var, "")
        return self.value or ""

    @property
    def has_detection_source(self) -> bool:
        if self.asset_type in {"exact_secret", "document_secret"}:
            return bool(self.effective_value)
        if self.asset_type == "pattern_secret":
            return bool(self.pattern)
        if self.asset_type == "semantic_secret":
            return bool(self.aliases or self.semantic_labels)
        return False

    def masked_value(self) -> str:
        return mask_secret(self.effective_value)

    def sha256_16(self) -> str:
        value = self.effective_value
        return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16] if value else ""


def mask_secret(value: str) -> str:
    value = value or ""
    if not value:
        return ""
    if len(value) <= 6:
        return value[0] + "*" * max(0, len(value) - 2) + value[-1]
    left = min(4, max(1, len(value) // 4))
    right = min(4, max(1, len(value) // 4))
    return value[:left] + "*" * max(4, len(value) - left - right) + value[-right:]


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    return [str(value).strip()] if str(value).strip() else []


def _asset_from_dict(item: dict[str, Any]) -> ProtectedAsset:
    asset_type = str(item.get("asset_type") or item.get("type") or "exact_secret").strip()
    risk = str(item.get("risk_level") or item.get("sensitivity") or "high").strip()
    asset = ProtectedAsset(
        asset_id=str(item.get("asset_id") or item.get("id") or "asset").strip(),
        name=str(item.get("name") or item.get("asset_id") or item.get("id") or "asset").strip(),
        asset_type=asset_type if asset_type in SUPPORTED_ASSET_TYPES else "exact_secret",
        value=str(item.get("value") or ""),
        env_var=str(item.get("env_var") or ""),
        pattern=str(item.get("pattern") or ""),
        aliases=_as_list(item.get("aliases")),
        semantic_labels=_as_list(item.get("semantic_labels")),
        risk_level=risk if risk in SUPPORTED_RISK_LEVELS else "high",
        enabled=bool(item.get("enabled", True)),
        allow_encoded_detection=bool(item.get("allow_encoded_detection", True)),
        description=str(item.get("description") or item.get("notes") or ""),
    )
    if asset.env_var:
        asset.source = "env_var"
    elif asset.pattern:
        asset.source = "pattern"
    elif asset.aliases or asset.semantic_labels:
        asset.source = "semantic" if asset.asset_type == "semantic_secret" else "value"
    else:
        asset.source = "value"
    return asset


class ProtectedAssetRegistry:
    def __init__(self, assets: list[ProtectedAsset], path: str | Path = ""):
        self.assets = assets
        self.path = str(path or "")

    @classmethod
    def load(cls, path: str | Path | None) -> "ProtectedAssetRegistry":
        if not path:
            return cls([], "")
        p = Path(path)
        if not p.exists():
            return cls([], p)
        data = json.loads(p.read_text(encoding="utf-8"))
        raw_assets = data.get("assets", []) if isinstance(data, dict) else []
        assets = [_asset_from_dict(x) for x in raw_assets if isinstance(x, dict)]
        return cls(assets, p)

    def enabled_assets(self) -> list[ProtectedAsset]:
        return [a for a in self.assets if a.enabled]

    def get(self, asset_id: str) -> Optional[ProtectedAsset]:
        for a in self.enabled_assets():
            if a.asset_id == asset_id:
                return a
        return None

    def primary_exact_secret(self, asset_id: str = "") -> Optional[ProtectedAsset]:
        if asset_id:
            a = self.get(asset_id)
            if a and a.asset_type in {"exact_secret", "document_secret"} and a.effective_value:
                return a
            return None
        for a in self.enabled_assets():
            if a.asset_type in {"exact_secret", "document_secret"} and a.effective_value:
                return a
        return None

    def summary(self, selected_asset: Optional[ProtectedAsset] = None) -> dict[str, Any]:
        enabled = self.enabled_assets()
        selected_asset = selected_asset or self.primary_exact_secret()
        return {
            "protected_assets_file": self.path,
            "protected_assets_enabled": str(bool(enabled)).lower(),
            "protected_assets_count": len(enabled),
            "protected_asset_id": selected_asset.asset_id if selected_asset else "",
            "protected_asset_name": selected_asset.name if selected_asset else "",
            "protected_asset_type": selected_asset.asset_type if selected_asset else "",
            "protected_asset_risk_level": selected_asset.risk_level if selected_asset else "",
            "protected_asset_source": selected_asset.source if selected_asset else "",
            "protected_asset_masked": selected_asset.masked_value() if selected_asset else "",
            "protected_asset_sha256_16": selected_asset.sha256_16() if selected_asset else "",
        }

    def detect(self, text: str) -> list[dict[str, str]]:
        text = text or ""
        hits: list[dict[str, str]] = []
        for a in self.enabled_assets():
            if a.asset_type in {"exact_secret", "document_secret"}:
                val = a.effective_value
                if val and val in text:
                    hits.append({"asset_id": a.asset_id, "asset_type": a.asset_type, "risk_level": a.risk_level, "match_rule": "exact_value"})
                if val and a.allow_encoded_detection:
                    for rule, enc in encoded_variants(val).items():
                        if enc and enc in text:
                            hits.append({"asset_id": a.asset_id, "asset_type": a.asset_type, "risk_level": a.risk_level, "match_rule": rule})
            elif a.asset_type == "pattern_secret" and a.pattern:
                try:
                    if re.search(a.pattern, text, flags=re.IGNORECASE):
                        hits.append({"asset_id": a.asset_id, "asset_type": a.asset_type, "risk_level": a.risk_level, "match_rule": "regex_pattern"})
                except re.error:
                    pass
            terms = a.aliases + a.semantic_labels
            for term in terms:
                if term and term.lower() in text.lower():
                    hits.append({"asset_id": a.asset_id, "asset_type": a.asset_type, "risk_level": a.risk_level, "match_rule": "alias_or_semantic_label"})
                    break
        # de-duplicate
        seen = set()
        unique = []
        for h in hits:
            key = (h["asset_id"], h["match_rule"])
            if key not in seen:
                seen.add(key); unique.append(h)
        return unique


def encoded_variants(value: str) -> dict[str, str]:
    raw = value.encode("utf-8", errors="ignore")
    return {
        "base64_encoded_value": base64.b64encode(raw).decode("ascii") if raw else "",
        "url_encoded_value": urllib.parse.quote(value) if value else "",
        "hex_encoded_value": raw.hex() if raw else "",
    }
