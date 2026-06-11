from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def resolve_project_path(value: str | Path | None, root: Path = ROOT) -> Path | None:
    if not value:
        return None
    p = Path(value)
    if p.is_absolute():
        return p
    return root / p


def sha256_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8", errors="ignore")).hexdigest()


def sha256_file(path: Path | None) -> str:
    if not path or not path.exists() or not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text or "") / 4)) if text else 0


def first_markdown_heading(text: str) -> str:
    for raw in (text or "").splitlines():
        line = raw.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def validate_custom_skill_file(path_value: str | Path | None, root: Path = ROOT) -> dict[str, Any]:
    """Validate an enterprise custom Skill markdown file.

    This validator is intentionally heuristic. It does not judge security quality;
    it catches obvious experiment-quality problems before a formal run.
    """
    result: dict[str, Any] = {
        "enabled": bool(path_value),
        "file": str(path_value or ""),
        "resolved_file": "",
        "exists": False,
        "extension": "",
        "sha256": "",
        "chars": 0,
        "est_tokens": 0,
        "first_heading": "",
        "status": "not_used" if not path_value else "error",
        "errors": [],
        "warnings": [],
    }
    if not path_value:
        return result

    p = resolve_project_path(path_value, root)
    result["resolved_file"] = str(p)
    result["extension"] = p.suffix.lower() if p else ""

    if not p or not p.exists():
        result["errors"].append("CUSTOM_SKILL_FILE_NOT_FOUND")
        return result
    if not p.is_file():
        result["errors"].append("CUSTOM_SKILL_PATH_IS_NOT_FILE")
        return result
    result["exists"] = True
    if p.suffix.lower() != ".md":
        result["warnings"].append("CUSTOM_SKILL_NOT_MARKDOWN_EXTENSION")

    text = p.read_text(encoding="utf-8", errors="ignore").strip()
    result["sha256"] = sha256_file(p)
    result["chars"] = len(text)
    result["est_tokens"] = estimate_tokens(text)
    result["first_heading"] = first_markdown_heading(text)

    if not text:
        result["errors"].append("CUSTOM_SKILL_EMPTY")
    if len(text) < 80:
        result["warnings"].append("CUSTOM_SKILL_TOO_SHORT_FOR_FORMAL_EVALUATION")
    if len(text) > 12000:
        result["warnings"].append("CUSTOM_SKILL_VERY_LONG_MAY_INCREASE_TRUNCATION_OR_CONFUSION")
    if not result["first_heading"]:
        result["warnings"].append("CUSTOM_SKILL_HAS_NO_MARKDOWN_HEADING")

    lower = text.lower()
    refusal_markers = [
        "refuse", "cannot", "can't", "must not", "do not reveal", "do not disclose", "not allowed",
        "拒絕", "不能", "不可", "不可以", "不得", "不要透露", "不要洩漏", "不得洩漏",
    ]
    secret_markers = [
        "secret", "flag", "api key", "token", "password", "credential", "protected data",
        "機密", "秘密", "旗標", "密鑰", "金鑰", "受保護", "敏感資料",
    ]
    if not any(m in lower for m in refusal_markers):
        result["warnings"].append("CUSTOM_SKILL_NO_CLEAR_REFUSAL_RULE")
    if not any(m in lower for m in secret_markers):
        result["warnings"].append("CUSTOM_SKILL_NO_CLEAR_SECRET_PROTECTION_TERMS")

    unsafe_placeholder_patterns = [
        r"pico\s*ctf\s*\{\s*(redacted|placeholder|example|dummy|sample|fake)[^}]*\}",
        r"flag\s*\{\s*(redacted|placeholder|example|dummy|sample|fake)[^}]*\}",
    ]
    for pat in unsafe_placeholder_patterns:
        if re.search(pat, text, flags=re.IGNORECASE | re.DOTALL):
            result["warnings"].append("CUSTOM_SKILL_USES_FLAG_LIKE_PLACEHOLDER_USE_ANGLE_BRACKET_PLACEHOLDER")
            break

    dangerous_patterns = [
        r"always\s+(reveal|disclose|print|show)\s+.*(secret|flag|token|password|api\s*key)",
        r"you\s+may\s+(reveal|disclose|print|show)\s+.*(secret|flag|token|password|api\s*key)",
        r"可以\s*(透露|洩漏|顯示|輸出).*(secret|flag|token|密鑰|金鑰|密碼|敏感資料)",
        r"允許\s*(透露|洩漏|顯示|輸出).*(secret|flag|token|密鑰|金鑰|密碼|敏感資料)",
    ]
    for pat in dangerous_patterns:
        if re.search(pat, text, flags=re.IGNORECASE | re.DOTALL):
            result["errors"].append("CUSTOM_SKILL_CONTAINS_APPARENTLY_UNSAFE_DIRECTIVE")
            break

    result["status"] = "pass_with_warnings" if result["warnings"] and not result["errors"] else ("pass" if not result["errors"] else "error")
    return result


def official_mode_errors(args: Any, defense: Any, attacks_path: Path, flag: str) -> list[str]:
    errors: list[str] = []
    if not attacks_path.exists():
        errors.append("ATTACKS_FILE_NOT_FOUND")
    if not flag:
        errors.append("PROTECTED_DATA_EMPTY")
    if getattr(args, "runs", 0) < 1:
        errors.append("RUNS_MUST_BE_AT_LEAST_1")
    if getattr(args, "max_tokens", 0) <= 0:
        errors.append("MAX_TOKENS_MUST_BE_POSITIVE")
    if getattr(args, "temperature", None) is None:
        errors.append("TEMPERATURE_MISSING")
    # Formal reproducibility: default to deterministic generation.
    try:
        if float(getattr(args, "temperature", 0)) != 0:
            errors.append("OFFICIAL_MODE_REQUIRES_TEMPERATURE_0")
    except Exception:
        errors.append("TEMPERATURE_INVALID")
    if getattr(defense, "custom_skill_enabled", False):
        status = getattr(defense, "custom_skill_validation_status", "")
        if status == "error":
            errors.append("CUSTOM_SKILL_VALIDATION_ERROR")
        if getattr(defense, "custom_skill_mode", "") != "custom_only":
            errors.append("CUSTOM_SKILL_MUST_BE_CUSTOM_ONLY")
    return errors


def build_experiment_manifest(
    *,
    args: Any,
    defense: Any,
    attacks_path: Path,
    report_dir: Path,
    attack_set: str,
    styles: list[str],
    attack_ids: Any,
    expected_total: int,
    selected_cases: int,
    context: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_version": "v20_enterprise_risk_reporting",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "command": sys.argv,
        "report_dir": str(report_dir),
        "model": getattr(args, "model", ""),
        "defense": {
            "id": getattr(defense, "defense_id", ""),
            "name": getattr(defense, "name", ""),
            "type": getattr(defense, "defense_type", ""),
            "skill_profile": getattr(defense, "skill_profile_id", ""),
            "skill_profile_name": getattr(defense, "skill_profile_name", ""),
            "loaded_skills": getattr(defense, "loaded_skills", ""),
            "custom_skill_mode": getattr(defense, "custom_skill_mode", "none"),
            "custom_skill_file": getattr(defense, "custom_skill_file", ""),
            "custom_skill_sha256": getattr(defense, "custom_skill_hash", ""),
            "custom_skill_chars": getattr(defense, "custom_skill_chars", 0),
            "custom_skill_est_tokens": getattr(defense, "custom_skill_est_tokens", 0),
            "custom_skill_first_heading": getattr(defense, "custom_skill_first_heading", ""),
            "custom_skill_validation_status": getattr(defense, "custom_skill_validation_status", ""),
            "custom_skill_validation_warnings": getattr(defense, "custom_skill_validation_warnings", ""),
            "custom_skill_validation_errors": getattr(defense, "custom_skill_validation_errors", ""),
        },
        "dataset": {
            "attack_set": attack_set,
            "attacks_file": str(attacks_path),
            "attacks_sha256": sha256_file(attacks_path),
            "attack_ids": attack_ids or "all",
            "styles": styles,
            "selected_cases": selected_cases,
            "expected_rows": expected_total,
        },
        "generation_params": {
            "runs": getattr(args, "runs", ""),
            "max_tokens": getattr(args, "max_tokens", ""),
            "temperature": getattr(args, "temperature", ""),
            "top_p": getattr(args, "top_p", ""),
            "top_k": getattr(args, "top_k", ""),
            "num_ctx": getattr(args, "num_ctx", ""),
            "seed": getattr(args, "seed", ""),
            "output_action": getattr(args, "output_action", ""),
        },
        "hashes": {
            "system_prompt_hash": context.get("system_prompt_hash", ""),
            "base_system_prompt_hash": context.get("base_system_prompt_hash", ""),
            "protected_data_sha256": context.get("secret_hash", ""),
            "skill_prompt_hash": context.get("skill_prompt_hash", ""),
            "guard_rule_hash": context.get("guard_rule_hash", ""),
            "builtin_guard_rule_hash": context.get("builtin_guard_rule_hash", ""),
            "scoring_version": context.get("scoring_version", ""),
            "data_classification_policy_hash": context.get("data_classification_policy_hash", ""),
            "action_policy_hash": context.get("action_policy_hash", ""),
        },
        "enterprise_policies": {
            "data_classification_policy_file": getattr(args, "data_policy", ""),
            "data_classification_policy_hash": context.get("data_classification_policy_hash", ""),
            "action_policy_file": getattr(args, "action_policy", ""),
            "action_policy_hash": context.get("action_policy_hash", ""),
            "note": "Reporting layer only; original leak-level scoring is unchanged.",
        },
        "environment": {
            "machine_id": getattr(args, "machine_id", ""),
            "hostname": context.get("hostname", ""),
            "os_platform": context.get("os_platform", ""),
            "python_version": context.get("python_version", ""),
            "ollama_version": context.get("ollama_version", ""),
            "model_digest": context.get("model_digest", ""),
            "model_parameter_size": context.get("model_parameter_size", ""),
            "model_quantization": context.get("model_quantization", ""),
        },
        "qa": {
            "official_mode": bool(getattr(args, "official_mode", False)),
            "prompt_trace_enabled": bool(getattr(args, "prompt_trace", False)),
            "skill_probe_enabled": bool(getattr(args, "skill_probe", False)),
        },
    }


def write_json(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
