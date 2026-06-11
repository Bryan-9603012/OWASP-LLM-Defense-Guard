"""
LLM Secret Guard - 一鍵互動式 Ollama 測試工具。

Design:
- Windows double-click entry: install.bat -> install_and_run.ps1 -> this script.
- Arrow-key menu, Enter confirm, Esc returns to previous layer.
- First enter one or more target models, then select benchmark scope.
- Benchmark scopes include full 20x4, selected languages, selected attacks, quick smoke test, and custom test.
- Missing models are pulled automatically.
- Runtime/API/model errors are recorded in a problem list and the runner continues.
- After each model, markdown/json reports and charts are generated.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import requests

ROOT = Path(__file__).resolve().parent
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("MODEL", "qwen2.5:0.5b")
MODEL_GROUPS_PATH = ROOT / "configs" / "model_groups.json"
ATTACKS_PATH = ROOT / "attacks" / "attacks.json"
DEFENSE_CONFIG_PATH = ROOT / "defenses" / "defense_config.json"
SKILL_PROFILES_PATH = ROOT / "defenses" / "skill_profiles" / "profiles.json"
CUSTOM_DEFENSE_DIR = ROOT / "defenses" / "custom"
DEFAULT_SECRETS_REGISTRY_PATH = ROOT / "data" / "secrets_registry.json"
DISABLED_SECRETS_REGISTRY_PATH = ROOT / "data" / "registry_disabled.json"
DEFAULT_PROTECTED_ASSETS_PATH = ROOT / "configs" / "protected_assets.json"
SIMPLE_MODE = False

STYLE_CHOICES = [
    ("en_pure", "純英文", "純英文"),
    ("zh_pure", "繁體中文", "ZH_ONLY"),
    ("zh_main_en_mixed", "中文為主，少量英文", "中英混合"),
    ("en_main_zh_mixed", "英文為主，少量中文", "英中混合"),
]
STYLE_ALIASES = {
    "1": "en_pure", "en": "en_pure", "english": "en_pure", "en_pure": "en_pure", "EN_ONLY": "en_pure",
    "2": "zh_pure", "zh": "zh_pure", "chinese": "zh_pure", "zh_pure": "zh_pure", "ZH_ONLY": "zh_pure",
    "3": "zh_main_en_mixed", "zh_en": "zh_main_en_mixed", "mix_zh": "zh_main_en_mixed", "zh_main_en_mixed": "zh_main_en_mixed", "ZH_EN_MIX": "zh_main_en_mixed",
    "4": "en_main_zh_mixed", "en_zh": "en_main_zh_mixed", "mix_en": "en_main_zh_mixed", "en_main_zh_mixed": "en_main_zh_mixed", "EN_ZH_MIX": "en_main_zh_mixed",
}


@dataclass
class TestScope:
    label: str
    run_name_suffix: str
    styles: str = "all"
    attack_ids: str = "all"
    limit_base_attacks: Optional[int] = None

    def to_cli_args(self) -> List[str]:
        args = ["--styles", self.styles, "--attack-ids", self.attack_ids]
        if self.limit_base_attacks:
            args += ["--limit-base-attacks", str(self.limit_base_attacks)]
        return args


@dataclass
class ProtectedAssetChoice:
    enabled: bool = False
    config_path: str = ""
    asset_id: str = ""
    name: str = "使用 data/protected_data.txt"
    masked: str = ""
    risk_level: str = ""

    def to_cli_args(self) -> List[str]:
        if not self.enabled or not self.config_path:
            return []
        args = ["--protected-assets", self.config_path]
        if self.asset_id:
            args += ["--protected-asset-id", self.asset_id]
        return args

    def summary(self) -> str:
        if not self.enabled:
            return "legacy data/protected_data.txt"
        tail = f" | {self.masked}" if self.masked else ""
        risk = f" | risk={self.risk_level}" if self.risk_level else ""
        return f"{self.asset_id} / {self.name}{risk}{tail}"




@dataclass
class DefenseChoice:
    defense_id: str
    name: str
    defense_type: str
    prompt_file: str = ""
    group_id: str = ""
    group_name: str = ""
    review_level_override: str = ""
    output_action_override: str = ""
    secrets_registry_path: str = ""

    @property
    def uses_skill(self) -> bool:
        return self.defense_id in {"skill_only", "full_guard", "prompt_defense", "skill_defense"} or self.defense_type in {"skill_only", "full_guard", "inner_prompt", "inner_skill", "skill"}

    @property
    def display_id(self) -> str:
        return self.group_id or self.defense_id

    @property
    def display_name(self) -> str:
        return self.group_name or self.name

    def to_cli_args(self, skill_profile: Optional["SkillProfileChoice"] = None, custom_rules: Optional["CustomDefenseRules"] = None) -> List[str]:
        args = ["--defense", self.defense_id, "--defense-config", str(DEFENSE_CONFIG_PATH)]
        if skill_profile and self.uses_skill:
            args += ["--skill-profile", skill_profile.profile_id]
        if custom_rules:
            args += custom_rules.to_cli_args()
        return args


@dataclass
class DefenseTestPlan:
    mode_id: str
    name: str
    defenses: List[DefenseChoice]

    @property
    def uses_skill(self) -> bool:
        return any(d.uses_skill for d in self.defenses)

    @property
    def defense_count(self) -> int:
        return len(self.defenses)

    def label(self) -> str:
        return ", ".join(f"{d.display_name}[{d.display_id}]" for d in self.defenses)


@dataclass
class CustomDefenseRules:
    custom_skill_file: str = ""
    custom_skill_mode: str = "custom_only"
    custom_input_patterns_file: str = ""
    custom_output_patterns_file: str = ""
    custom_skill_count: int = 0
    custom_input_rule_count: int = 0
    custom_output_rule_count: int = 0

    @property
    def enabled(self) -> bool:
        return bool(self.custom_skill_file or self.custom_input_patterns_file or self.custom_output_patterns_file)

    @property
    def total_count(self) -> int:
        return self.custom_skill_count + self.custom_input_rule_count + self.custom_output_rule_count

    def to_cli_args(self) -> List[str]:
        args: List[str] = []
        if self.custom_skill_file:
            args += ["--custom-skill-file", self.custom_skill_file]
        if self.custom_input_patterns_file:
            args += ["--custom-input-patterns-file", self.custom_input_patterns_file]
        if self.custom_output_patterns_file:
            args += ["--custom-output-patterns-file", self.custom_output_patterns_file]
        return args


@dataclass
class OutputActionChoice:
    action_id: str
    name: str
    description: str = ""

    def to_cli_args(self) -> List[str]:
        return ["--output-action", self.action_id]


@dataclass
class ReviewLevelChoice:
    level_id: str
    name: str
    description: str = ""

    def to_cli_args(self) -> List[str]:
        return ["--review-level", self.level_id]


@dataclass
class VerificationChoice:
    mode_id: str = "none"
    name: str = "不啟用"
    prompt_trace: bool = False
    skill_probe: bool = False

    @property
    def enabled(self) -> bool:
        return self.prompt_trace or self.skill_probe

    def to_cli_args(self) -> List[str]:
        args: List[str] = []
        if self.prompt_trace:
            args.append("--prompt-trace")
        if self.skill_probe:
            args.append("--skill-probe")
        return args


@dataclass
class SkillProfileChoice:
    profile_id: str
    name: str
    description: str = ""
    skill_files: List[str] = None

    def __post_init__(self):
        if self.skill_files is None:
            self.skill_files = []

    @property
    def skill_count(self) -> int:
        return len(self.skill_files or [])


@dataclass
class GenerationParams:
    max_tokens: int = 300
    temperature: float = 0.0
    top_p: float = 1.0
    top_k: int = 40
    num_ctx: int = 4096
    seed: int = 42

    def to_cli_args(self) -> List[str]:
        return [
            "--max-tokens", str(self.max_tokens),
            "--temperature", str(self.temperature),
            "--top-p", str(self.top_p),
            "--top-k", str(self.top_k),
            "--num-ctx", str(self.num_ctx),
            "--seed", str(self.seed),
        ]


class BackToMenu(Exception):
    pass


@dataclass
class SelectOption:
    label: str
    value: str
    hint: str = ""


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def supports_tui() -> bool:
    if SIMPLE_MODE:
        return False
    return sys.stdin.isatty() and sys.stdout.isatty()


def read_key() -> str:
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            return {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT"}.get(ch2, "")
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == "\x1b":
            return "ESC"
        return ch.lower()

    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = sys.stdin.read(2)
            if seq == "[A":
                return "UP"
            if seq == "[B":
                return "DOWN"
            return "ESC"
        if ch in ("\r", "\n"):
            return "ENTER"
        return ch.lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def esc_input(prompt: str, default: Optional[str] = None) -> Optional[str]:
    if default is not None:
        prompt = f"{prompt} [{default}]"
    if not prompt.endswith(" "):
        prompt += " "
    if not sys.stdin.isatty():
        value = input(prompt).strip()
        return default if value == "" and default is not None else value

    print(prompt, end="", flush=True)
    chars: List[str] = []
    if os.name == "nt":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch == "\x1b":
                print("\n[返回]")
                return None
            if ch in ("\r", "\n"):
                print()
                value = "".join(chars).strip()
                return default if value == "" and default is not None else value
            if ch in ("\b", "\x7f"):
                if chars:
                    chars.pop(); print("\b \b", end="", flush=True)
                continue
            if ch in ("\x00", "\xe0"):
                _ = msvcrt.getwch(); continue
            if ch.isprintable():
                chars.append(ch); print(ch, end="", flush=True)
        
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch == "\x1b":
                print("\n[返回]")
                return None
            if ch in ("\r", "\n"):
                print()
                value = "".join(chars).strip()
                return default if value == "" and default is not None else value
            if ch in ("\b", "\x7f"):
                if chars:
                    chars.pop(); print("\b \b", end="", flush=True)
                continue
            if ch.isprintable():
                chars.append(ch); print(ch, end="", flush=True)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def numeric_select(title: str, options: List[SelectOption], default_index: int = 0) -> SelectOption:
    print("\n" + title)
    for i, opt in enumerate(options, 1):
        hint = f"  {opt.hint}" if opt.hint else ""
        print(f"  {i}. {opt.label}{hint}")
    raw = esc_input(f"請輸入數字 [{default_index + 1}]：")
    if raw is None:
        return SelectOption("返回", "__cancel__")
    raw = raw.strip()
    if not raw:
        return options[default_index]
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            return options[idx]
    except ValueError:
        pass
    print("[WARN] 選項無效，使用預設值。")
    return options[default_index]


def tui_select(title: str, options: List[SelectOption], default_index: int = 0) -> SelectOption:
    """Clean arrow-key selector.

    The old UI printed every hint inline, which made the screen noisy.
    This version keeps the list short and shows only the selected item's hint.
    """
    if not options:
        raise ValueError("options is empty")
    if not supports_tui():
        return numeric_select(title, options, default_index)
    idx = max(0, min(default_index, len(options) - 1))
    while True:
        clear_screen()
        print(f"\n{title}")
        print("═" * 54)
        for i, opt in enumerate(options):
            pointer = "❯" if i == idx else " "
            print(f"{pointer} {opt.label}")
        print("─" * 54)
        selected_hint = options[idx].hint.strip()
        if selected_hint:
            print(f"說明：{selected_hint}")
        print("操作：↑/↓ 選擇｜Enter 確認｜Esc 返回")
        try:
            key = read_key()
        except Exception as exc:
            print(f"[WARN] 互動式選單失敗，改用數字選單：{exc}")
            return numeric_select(title, options, default_index)
        if key in {"UP", "k"}:
            idx = (idx - 1) % len(options)
        elif key in {"DOWN", "j"}:
            idx = (idx + 1) % len(options)
        elif key == "ENTER":
            clear_screen(); return options[idx]
        elif key == "ESC":
            clear_screen(); return SelectOption("返回", "__cancel__")
        elif key.isdigit():
            n = int(key)
            if 1 <= n <= len(options):
                idx = n - 1

def wait_key(msg: str = "按 Enter 繼續，或 Esc 返回...") -> None:
    _ = esc_input(msg)


def safe_filename(name: str) -> str:
    return (name.replace(":", "_").replace("/", "_").replace("\\", "_")
            .replace(" ", "_").replace("|", "_").replace("<", "_")
            .replace(">", "_").replace("?", "_").replace("*", "_").replace('"', "_"))


def load_groups() -> Dict[str, List[str]]:
    if not MODEL_GROUPS_PATH.exists():
        return {"medium_models": ["qwen2.5:7b", "llama3.1:8b", "deepseek-r1:7b"],
                "small_models": ["qwen2.5:0.5b", "qwen2.5:1.5b", "llama3.2:1b"]}
    return json.loads(MODEL_GROUPS_PATH.read_text(encoding="utf-8"))


def save_groups(groups: Dict[str, List[str]]) -> None:
    MODEL_GROUPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_GROUPS_PATH.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def load_attack_catalog() -> List[dict]:
    if not ATTACKS_PATH.exists():
        return []
    try:
        data = json.loads(ATTACKS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    seen = set()
    catalog = []
    for item in data:
        base_id = str(item.get("attack_id") or item.get("id", "").split("-", 1)[0]).upper()
        if not base_id or base_id in seen:
            continue
        seen.add(base_id)
        catalog.append({
            "attack_id": base_id,
            "category": item.get("category", ""),
            "category_zh": item.get("category_zh", ""),
            "description": item.get("description", ""),
        })
    return catalog


def show_attack_catalog() -> None:
    catalog = load_attack_catalog()
    if not catalog:
        print("[WARN] 無法讀取 attacks.json 或攻擊清單為空。")
        return
    print("\n可選攻擊 ID：")
    for item in catalog:
        label = item.get("category_zh") or item.get("category") or item.get("description") or ""
        print(f"  {item['attack_id']:<4} {label}")


def normalize_attack_ids(raw: str) -> Optional[str]:
    raw = (raw or "").strip()
    if not raw or raw.lower() == "all":
        return "all"
    out: List[str] = []
    valid = {a["attack_id"] for a in load_attack_catalog()}
    for part in raw.split(","):
        part = part.strip().upper()
        if not part:
            continue
        if part.isdigit():
            part = f"A{int(part):02d}"
        if not part.startswith("A") and part[1:].isdigit():
            part = "A" + part[1:].zfill(2)
        if part not in valid:
            print(f"[WARN] 攻擊 ID 不存在，已忽略：{part}")
            continue
        if part not in out:
            out.append(part)
    return ",".join(out) if out else None


def normalize_styles(raw: str) -> Optional[str]:
    raw = (raw or "").strip()
    if not raw or raw.lower() == "all":
        return "all"
    out: List[str] = []
    for part in raw.split(","):
        key = part.strip()
        if not key:
            continue
        style = STYLE_ALIASES.get(key) or STYLE_ALIASES.get(key.lower()) or STYLE_ALIASES.get(key.upper())
        if not style:
            print(f"[WARN] 語言種類不支援，已忽略：{part}")
            continue
        if style not in out:
            out.append(style)
    return ",".join(out) if out else None


def ask_styles(default: str = "all") -> Optional[str]:
    print("\n語言種類：")
    print("  all = 完整四種語言")
    for idx, (style, label, mode) in enumerate(STYLE_CHOICES, 1):
        print(f"  {idx}. {style:<20} {label:<28} {mode}")
    raw = esc_input("請輸入語言代號，可用逗號多選，例如 all 或 1,2 或 en_pure,zh_pure，Esc 返回", default)
    if raw is None:
        return None
    styles = normalize_styles(raw)
    if styles is None:
        print("[WARN] 沒有有效語言，請重新選擇。")
        return ask_styles(default)
    return styles


def ask_attack_ids(default: str = "all") -> Optional[str]:
    show_attack_catalog()
    raw = esc_input("請輸入攻擊 ID，可用逗號多選，例如 all 或 A01,A03,A19，Esc 返回", default)
    if raw is None:
        return None
    attack_ids = normalize_attack_ids(raw)
    if attack_ids is None:
        print("[WARN] 沒有有效攻擊 ID，請重新選擇。")
        return ask_attack_ids(default)
    return attack_ids


def scope_slug(value: str) -> str:
    return safe_filename(value.replace(",", "_")) if value and value != "all" else "all"


def choose_test_scope() -> TestScope:
    while True:
        sel = tui_select("測試範圍", [
            SelectOption("快速測試", "quick", "前 5 個攻擊 × 純英文；用來確認模型與防禦流程。"),
            SelectOption("完整測試", "full", "20 種攻擊 × 4 種語言；正式實驗用。"),
            SelectOption("依語言測試", "language", "指定一種或多種語言，攻擊全跑。"),
            SelectOption("依攻擊測試", "attack", "指定攻擊 ID，例如 A01 或 A01,A03。"),
            SelectOption("自訂測試", "custom", "手動指定攻擊、語言與前 N 個攻擊限制。"),
            SelectOption("返回", "__cancel__"),
        ], 0)
        if sel.value == "__cancel__":
            raise BackToMenu
        if sel.value == "quick":
            return TestScope("快速測試：前 5 個攻擊 × 純英文", "quick_5x1", "en_pure", "all", 5)
        if sel.value == "full":
            return TestScope("完整測試：20×4", "full_20x4", "all", "all", None)
        if sel.value == "language":
            styles = ask_styles("all")
            if styles is None:
                continue
            return TestScope(f"語言測試：{styles}", f"lang_{scope_slug(styles)}", styles, "all", None)
        if sel.value == "attack":
            attack_ids = ask_attack_ids("A01")
            if attack_ids is None:
                continue
            styles = ask_styles("all")
            if styles is None:
                continue
            return TestScope(f"攻擊測試：{attack_ids} / {styles}", f"atk_{scope_slug(attack_ids)}__lang_{scope_slug(styles)}", styles, attack_ids, None)
        if sel.value == "custom":
            attack_ids = ask_attack_ids("all")
            if attack_ids is None:
                continue
            styles = ask_styles("all")
            if styles is None:
                continue
            limit_raw = esc_input("限制前 N 個基礎攻擊；空白代表不限制", "")
            if limit_raw is None:
                continue
            limit = None
            if limit_raw.strip():
                try:
                    limit = max(1, min(20, int(limit_raw.strip())))
                except ValueError:
                    print("[WARN] N 格式錯誤，改為不限制。")
                    limit = None
            suffix = f"custom_atk_{scope_slug(attack_ids)}__lang_{scope_slug(styles)}"
            if limit:
                suffix += f"__base{limit}"
            return TestScope(f"自訂測試：{attack_ids} / {styles} / base_limit={limit or '無'}", suffix, styles, attack_ids, limit)


def load_defense_choices() -> List[DefenseChoice]:
    fallback = [
        DefenseChoice("none", "無防禦", "none", "defenses/no_defense.txt"),
        DefenseChoice("prompt_defense", "提示詞防禦", "inner_prompt", "defenses/prompt_defense.txt"),
        DefenseChoice("skill_defense", "Skill 防禦", "inner_skill", "defenses/skill_defense.txt"),
    ]
    if not DEFENSE_CONFIG_PATH.exists():
        return fallback
    try:
        data = json.loads(DEFENSE_CONFIG_PATH.read_text(encoding="utf-8"))
        out: List[DefenseChoice] = []
        for item in data.get("defenses", []):
            did = str(item.get("id") or "").strip()
            if not did:
                continue
            out.append(DefenseChoice(
                defense_id=did,
                name=str(item.get("name") or did),
                defense_type=str(item.get("type") or "unknown"),
                prompt_file=str(item.get("prompt_file") or ""),
            ))
        return out or fallback
    except Exception as exc:
        print(f"[WARN] 無法讀取 defense_config.json，使用預設防禦選項：{exc}")
        return fallback



def zh_defense_type(defense_type: str) -> str:
    mapping = {
        "none": "不加任何防禦，作為基準組",
        "skill_only": "只加入防禦規則，不做程式攔截",
        "input_guard": "只在送進模型前檢查輸入",
        "output_guard": "只在模型輸出後檢查洩漏",
        "full_guard": "Skill 防禦 + 輸入檢查 + 輸出檢查",
        "inner_prompt": "舊版提示詞防禦相容模式",
        "inner_skill": "舊版 Skill 防禦相容模式",
    }
    return mapping.get(defense_type, defense_type)

def _read_multiline_until_dot(title: str) -> str:
    print("\n" + title)
    print("每行輸入一條規則；輸入單獨一個 . 結束；直接輸入 . 代表不新增。")
    lines: List[str] = []
    while True:
        raw = input("> ").rstrip("\n")
        if raw.strip() == ".":
            break
        if raw.strip():
            lines.append(raw)
    return "\n".join(lines).strip()


def _write_custom_file(filename: str, text: str) -> str:
    CUSTOM_DEFENSE_DIR.mkdir(parents=True, exist_ok=True)
    path = CUSTOM_DEFENSE_DIR / filename
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return str(path)


def _count_nonempty_rule_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))


def choose_custom_rules(defense: DefenseChoice) -> CustomDefenseRules:
    opts = [
        SelectOption("不使用", "none", "使用預設 Skill Profile 與內建 Guard 規則。"),
        SelectOption("自訂 Skill（取代內建 Skill）", "skill", "真正自訂：模型只掛你輸入的 Skill，不再掛預設 Skill Profile。"),
        SelectOption("追加 Input Guard Regex", "input", "補充輸入攔截規則；一行一條 regex。"),
        SelectOption("追加 Output Guard Regex", "output", "補充輸出攔截規則；一行一條 regex。"),
        SelectOption("全部自訂", "all", "自訂 Skill 會取代內建 Skill；Input/Output Guard Regex 仍作為額外規則。"),
        SelectOption("返回", "__cancel__"),
    ]
    selected = tui_select("自訂規則（進階）", opts, 0)
    if selected.value == "__cancel__":
        raise BackToMenu
    if selected.value == "none":
        return CustomDefenseRules()

    custom = CustomDefenseRules()
    if selected.value in {"skill", "all"}:
        if defense.uses_skill:
            text = _read_multiline_until_dot("輸入自訂 Skill 規則")
            if text:
                custom.custom_skill_file = _write_custom_file("custom_skill.md", "# Custom Skill\n\n" + text)
                custom.custom_skill_mode = "custom_only"
                custom.custom_skill_count = _count_nonempty_rule_lines(text)
        else:
            print("[提示] 目前防禦模式不包含 Skill，略過自訂 Skill。")
    if selected.value in {"input", "all"}:
        text = _read_multiline_until_dot("輸入自訂 Input Guard Regex")
        if text:
            custom.custom_input_patterns_file = _write_custom_file("custom_input_patterns.txt", text)
            custom.custom_input_rule_count = _count_nonempty_rule_lines(text)
    if selected.value in {"output", "all"}:
        text = _read_multiline_until_dot("輸入自訂 Output Guard Regex")
        if text:
            custom.custom_output_patterns_file = _write_custom_file("custom_output_patterns.txt", text)
            custom.custom_output_rule_count = _count_nonempty_rule_lines(text)
    if custom.enabled:
        print(f"[OK] 已保存自訂規則：{custom.total_count} 條")
    return custom



def _mask_secret_for_ui(value: str) -> str:
    value = value or ""
    if not value:
        return ""
    if len(value) <= 6:
        return value[0] + "*" * max(0, len(value) - 2) + value[-1]
    return value[:4] + "*" * max(4, len(value) - 8) + value[-4:]


def _load_protected_asset_options(path: Path = DEFAULT_PROTECTED_ASSETS_PATH) -> List[ProtectedAssetChoice]:
    choices: List[ProtectedAssetChoice] = []
    if not path.exists():
        return choices
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get("assets", []):
            if not isinstance(item, dict) or not item.get("enabled", True):
                continue
            asset_type = str(item.get("asset_type") or item.get("type") or "")
            if asset_type not in {"exact_secret", "document_secret"}:
                continue
            value = str(item.get("value") or "")
            env_var = str(item.get("env_var") or "")
            if env_var:
                value = os.getenv(env_var, "")
            if not value:
                continue
            choices.append(ProtectedAssetChoice(
                enabled=True,
                config_path=str(path),
                asset_id=str(item.get("asset_id") or item.get("id") or ""),
                name=str(item.get("name") or item.get("asset_id") or item.get("id") or ""),
                masked=_mask_secret_for_ui(value),
                risk_level=str(item.get("risk_level") or item.get("sensitivity") or "high"),
            ))
    except Exception as exc:
        print(f"[WARN] protected_assets.json 讀取失敗：{exc}")
    return choices


def choose_protected_asset() -> ProtectedAssetChoice:
    """Select the primary protected asset for this run.

    This is the value injected into prompts/system_prompt.txt as {flag} and used
    by leak scoring. Pattern/semantic assets remain useful for guard/reporting,
    but formal leak scoring requires one exact/document secret.
    """
    while True:
        assets = _load_protected_asset_options(DEFAULT_PROTECTED_ASSETS_PATH)
        opts = [SelectOption("使用舊版 protected_data.txt", "__legacy__", "維持原本 data/protected_data.txt，不使用自訂敏感資料。")]
        for a in assets:
            opts.append(SelectOption(f"{a.name} [{a.asset_id}]", a.asset_id, f"risk={a.risk_level}｜{a.masked}"))
        opts.append(SelectOption("管理 / 新增敏感資料", "__manage__", "開啟 protected asset manager 後再回來選擇。"))
        opts.append(SelectOption("返回", "__cancel__"))
        selected = tui_select("選擇本次測試要保護的敏感資料", opts, 1 if assets else 0)
        if selected.value == "__cancel__":
            raise BackToMenu
        if selected.value == "__legacy__":
            return ProtectedAssetChoice()
        if selected.value == "__manage__":
            manager = ROOT / "tools" / "manage_protected_assets.py"
            if not manager.exists():
                print("[WARN] 找不到 tools/manage_protected_assets.py。")
                wait_key()
                continue
            subprocess.run([sys.executable, str(manager), str(DEFAULT_PROTECTED_ASSETS_PATH)], cwd=str(ROOT))
            continue
        for a in assets:
            if a.asset_id == selected.value:
                return a
        print("[WARN] 找不到選擇的 asset，請重選。")
        wait_key()

def _defense_by_id(choices: List[DefenseChoice], defense_id: str) -> Optional[DefenseChoice]:
    for d in choices:
        if d.defense_id == defense_id:
            return d
    return None


def _clone_defense_as_group(base: DefenseChoice, group_id: str, group_name: str, review_level: str, output_action: str, registry_enabled: bool) -> DefenseChoice:
    return DefenseChoice(
        defense_id=base.defense_id,
        name=base.name,
        defense_type=base.defense_type,
        prompt_file=base.prompt_file,
        group_id=group_id,
        group_name=group_name,
        review_level_override=review_level,
        output_action_override=output_action,
        secrets_registry_path=str(DEFAULT_SECRETS_REGISTRY_PATH if registry_enabled else DISABLED_SECRETS_REGISTRY_PATH),
    )


def build_host_llm_groups(choices: List[DefenseChoice], group_ids: List[str]) -> List[DefenseChoice]:
    mapping = {d.defense_id: d for d in choices}
    # v25.3: keep the interactive CLI aligned with Web UI / defense_config.
    # Formal Host-LLM groups are G0-G6 only.  Registry-enhanced G7 from v24 is
    # intentionally removed from the standard compare paths to avoid mixing
    # different experimental definitions under the same G-group names.
    specs = {
        "G0": ("none", "G0 No Defense", "standard", "block", False),
        "G1": ("skill_only", "G1 Skill-only", "standard", "block", False),
        "G2": ("input_boundary", "G2 Input Boundary", "standard", "block", False),
        "G3": ("input_guard", "G3 Input Guard", "standard", "block", False),
        "G4": ("output_guard", "G4 Output Guard", "standard", "redact", False),
        "G5": ("io_guard", "G5 IO Guard", "attack_aware", "redact", False),
        "G6": ("full_guard", "G6 Full Guard", "attack_aware", "redact", False),
    }
    selected: List[DefenseChoice] = []
    missing: List[str] = []
    for gid in group_ids:
        defense_id, name, review, action, registry_enabled = specs[gid]
        base = mapping.get(defense_id)
        if not base:
            missing.append(f"{gid}:{defense_id}")
            continue
        selected.append(_clone_defense_as_group(base, gid, name, review, action, registry_enabled))
    if missing:
        print("[WARN] 找不到部分實驗組別對應的 defense_config：" + ", ".join(missing))
    return selected


def choose_defense_plan() -> DefenseTestPlan:
    choices = load_defense_choices()
    mode = tui_select("防禦測試方式", [
        SelectOption("單一防禦", "single", "只測一種原始防禦模式。"),
        SelectOption("Host LLM 核心比較（G0/G1/G5/G6）", "host_core", "正式主實驗推薦；比較無防禦、Skill、外部 IO Guard 與完整防禦。"),
        SelectOption("Host LLM 完整比較（G0-G6）", "host_full", "包含 Skill、Input Boundary、Input Guard、Output Guard、IO Guard 與 Full Guard。"),
        SelectOption("舊版基本比較", "compare_basic", "相容舊流程：none + skill_only + output_guard + full_guard。"),
        SelectOption("舊版完整比較", "compare_all", "相容舊流程：none + skill_only + input_guard + output_guard + full_guard。"),
        SelectOption("返回", "__cancel__"),
    ], 0)
    if mode.value == "__cancel__":
        raise BackToMenu
    if mode.value == "single":
        defense = choose_defense()
        return DefenseTestPlan("single", "單一防禦", [defense])
    if mode.value == "host_core":
        selected = build_host_llm_groups(choices, ["G0", "G1", "G5", "G6"])
        if not selected:
            raise RuntimeError("找不到 Host LLM 核心比較需要的防禦模式，請檢查 defenses/defense_config.json")
        return DefenseTestPlan("host_core_g0_g1_g5_g6", "Host LLM 核心比較", selected)
    if mode.value == "host_full":
        selected = build_host_llm_groups(choices, ["G0", "G1", "G2", "G3", "G4", "G5", "G6"])
        if not selected:
            raise RuntimeError("找不到 Host LLM 完整比較需要的防禦模式，請檢查 defenses/defense_config.json")
        return DefenseTestPlan("host_full_g0_to_g6", "Host LLM 完整比較", selected)

    ids = ["none", "skill_only", "output_guard", "full_guard"]
    if mode.value == "compare_all":
        ids = ["none", "skill_only", "input_guard", "output_guard", "full_guard"]
    selected = [d for did in ids if (d := _defense_by_id(choices, did)) is not None]
    if not selected:
        raise RuntimeError("找不到可用防禦模式，請檢查 defenses/defense_config.json")
    return DefenseTestPlan(mode.value, "舊版基本比較" if mode.value == "compare_basic" else "舊版完整比較", selected)


def choose_defense() -> DefenseChoice:
    choices = load_defense_choices()
    preferred_order = ["none", "skill_only", "input_boundary", "input_guard", "output_guard", "io_guard", "full_guard", "prompt_defense", "skill_defense"]
    order = {k: i for i, k in enumerate(preferred_order)}
    choices = sorted(choices, key=lambda d: order.get(d.defense_id, 999))
    opts = [SelectOption(d.name, d.defense_id, f"ID：{d.defense_id}｜{zh_defense_type(d.defense_type)}") for d in choices]
    opts.append(SelectOption("返回", "__cancel__"))
    selected = tui_select("防禦模式", opts, 0)
    if selected.value == "__cancel__":
        raise BackToMenu
    for d in choices:
        if d.defense_id == selected.value:
            return d
    return choices[0]


def choose_output_action(plan: DefenseTestPlan) -> OutputActionChoice:
    has_output_guard = any(d.defense_id in {"output_guard", "full_guard"} or d.defense_type in {"output_guard", "full_guard"} for d in plan.defenses)
    if not has_output_guard:
        return OutputActionChoice("block", "整段阻擋", "未啟用 output guard 時，此設定不會影響結果。")
    selected = tui_select("輸出處置方式", [
        SelectOption("整段阻擋", "block", "偵測到敏感資料時，用安全拒答取代整段輸出。最安全，適合正式防禦。"),
        SelectOption("敏感資料遮蔽", "redact", "只將敏感片段替換成 [REDACTED]，保留其餘內容。較接近企業可用性需求。"),
        SelectOption("只記錄不阻擋", "shadow", "保留模型原始輸出，只在報表與 audit log 記錄風險。適合研究觀察。"),
        SelectOption("返回", "__cancel__"),
    ], 0)
    if selected.value == "__cancel__":
        raise BackToMenu
    names = {"block": "整段阻擋", "redact": "敏感資料遮蔽", "shadow": "只記錄不阻擋"}
    return OutputActionChoice(selected.value, names.get(selected.value, selected.value), selected.hint)


def auto_output_action(plan: DefenseTestPlan) -> OutputActionChoice:
    """Clean UI default for output handling.

    The interactive wizard should not ask every low-level guard parameter.
    CLI users can still override this through run_benchmark.py --output-action.
    """
    has_output_guard = any(
        d.defense_id in {"output_guard", "full_guard"} or d.defense_type in {"output_guard", "full_guard"}
        for d in plan.defenses
    )
    if has_output_guard:
        return OutputActionChoice("redact", "自動：敏感資料遮蔽", "Clean UI 預設；保留可用性並遮蔽敏感片段。")
    return OutputActionChoice("block", "自動：整段阻擋", "未啟用 output guard 時，此設定不會影響結果。")

def choose_review_level(plan: DefenseTestPlan) -> ReviewLevelChoice:
    selected = tui_select("審查強度（Risk-based Review）", [
        SelectOption("標準審查", "standard", "主實驗預設；檢查明顯 secret request、prompt injection、translation/encoding/split。"),
        SelectOption("嚴格審查", "strict", "加強偵測拆字、分段、逐字元、圖片/程式碼包裝、編碼重建類攻擊。"),
        SelectOption("企業嚴格審查", "enterprise", "在 strict 基礎上加入 customer data、credential、internal/config/database 類企業資料風險。"),
        SelectOption("攻擊感知審查", "attack_aware", "依 attack metadata / prompt 自動選 light、standard、strict、enterprise；最適合比較進階防禦。"),
        SelectOption("輕量審查", "light", "只做最低限度敏感資料檢查；適合 false positive / benign usability 觀察。"),
        SelectOption("返回", "__cancel__"),
    ], 0)
    if selected.value == "__cancel__":
        raise BackToMenu
    names = {
        "light": "輕量審查",
        "standard": "標準審查",
        "strict": "嚴格審查",
        "enterprise": "企業嚴格審查",
        "attack_aware": "攻擊感知審查",
    }
    return ReviewLevelChoice(selected.value, names.get(selected.value, selected.value), selected.hint)


def auto_review_level(plan: DefenseTestPlan) -> ReviewLevelChoice:
    """Clean UI default for guard review strength.

    The wizard exposes high-level experiment choices only. Review strength is derived
    from the defense plan, while CLI users can still specify --review-level directly.
    """
    ids = {d.defense_id for d in plan.defenses}
    types = {d.defense_type for d in plan.defenses}
    if "full_guard" in ids or "full_guard" in types:
        return ReviewLevelChoice("attack_aware", "自動：攻擊感知審查", "依 attack metadata / prompt 自動選 light、standard、strict、enterprise。")
    if ids & {"input_guard", "output_guard"} or types & {"input_guard", "output_guard"}:
        return ReviewLevelChoice("standard", "自動：標準審查", "主實驗預設；避免互動選單過度工程化。")
    return ReviewLevelChoice("standard", "自動：標準審查", "無 guard 時基本不影響結果，但保留報表欄位一致性。")


def choose_skill_verification(plan: DefenseTestPlan) -> VerificationChoice:
    if not plan.uses_skill:
        return VerificationChoice()
    selected = tui_select("Skill 掛載驗證（進階）", [
        SelectOption("不啟用", "none", "不額外保存 prompt，也不執行 probe。"),
        SelectOption("只保存 Prompt Trace", "trace", "保存實際送入模型的 messages，用來確認 Skill 是否真的掛上。注意：檔案可能包含測試 secret。"),
        SelectOption("只執行 Skill Probe", "probe", "正式測試前問一題安全規則檢查題，確認模型是否知道要拒絕。"),
        SelectOption("Prompt Trace + Skill Probe", "both", "同時保存 prompt trace 並執行 skill probe，最適合 debug。"),
        SelectOption("返回", "__cancel__"),
    ], 0)
    if selected.value == "__cancel__":
        raise BackToMenu
    mapping = {
        "none": VerificationChoice("none", "不啟用", False, False),
        "trace": VerificationChoice("trace", "Prompt Trace", True, False),
        "probe": VerificationChoice("probe", "Skill Probe", False, True),
        "both": VerificationChoice("both", "Prompt Trace + Skill Probe", True, True),
    }
    return mapping.get(selected.value, VerificationChoice())


def load_skill_profile_choices() -> List[SkillProfileChoice]:
    fallback = [
        SkillProfileChoice("minimal", "最小安全規則", "只載入 base_security_skill，適合小模型初測。", ["base_security_skill.md"]),
        SkillProfileChoice("secret_only", "敏感資料保護", "基礎規則 + secret 保護 + 拒答格式。", ["base_security_skill.md", "secret_protection_skill.md", "enterprise_refusal_style_skill.md"]),
        SkillProfileChoice("full_security", "完整安全規則", "載入全部安全 skill，適合正式測試。", []),
        SkillProfileChoice("enterprise_strict", "企業嚴格模式", "完整安全規則，作為企業嚴格 policy 預案。", []),
    ]
    if not SKILL_PROFILES_PATH.exists():
        return fallback
    try:
        data = json.loads(SKILL_PROFILES_PATH.read_text(encoding="utf-8"))
        out: List[SkillProfileChoice] = []
        for item in data.get("profiles", []):
            pid = str(item.get("id") or "").strip()
            if not pid:
                continue
            out.append(SkillProfileChoice(
                profile_id=pid,
                name=str(item.get("name") or pid),
                description=str(item.get("description") or ""),
                skill_files=[str(x) for x in item.get("skill_files", [])],
            ))
        return out or fallback
    except Exception as exc:
        print(f"[WARN] 無法讀取 skill profiles，使用預設 Skill Profile：{exc}")
        return fallback


def choose_skill_profile(defense) -> Optional[SkillProfileChoice]:
    if not defense.uses_skill:
        return None
    choices = load_skill_profile_choices()
    default_index = 0
    for i, c in enumerate(choices):
        if c.profile_id == "full_security":
            default_index = i
            break
    opts = [SelectOption(c.name, c.profile_id, f"ID：{c.profile_id}｜{c.description}｜skill 數：{c.skill_count}") for c in choices]
    opts.append(SelectOption("返回", "__cancel__"))
    selected = tui_select("Skill Profile", opts, default_index)
    if selected.value == "__cancel__":
        raise BackToMenu
    for c in choices:
        if c.profile_id == selected.value:
            return c
    return choices[default_index]


def check_ollama() -> Optional[List[str]]:
    url = f"{OLLAMA_URL}/api/tags"
    print(f"[檢查] Ollama API：{url}")
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as exc:
        print(f"[ERROR] Ollama 無法連線：{exc}")
        return None
    if r.status_code != 200:
        print(f"[ERROR] Ollama API 回傳 HTTP_{r.status_code}：{r.text[:300]}")
        return None
    data = r.json()
    models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    print(f"[OK] Ollama 已連線。已安裝模型數：{len(models)}")
    return models


def download_model(model: str) -> bool:
    print(f"[下載] ollama pull {model}")
    try:
        rc = subprocess.run(["ollama", "pull", model], cwd=str(ROOT)).returncode
    except FileNotFoundError:
        print("[ERROR] 找不到 ollama 指令。")
        return False
    except Exception as exc:
        print(f"[ERROR] ollama pull 執行失敗：{exc}")
        return False
    if rc != 0:
        print(f"[ERROR] ollama pull 失敗：exit code {rc}")
        return False
    print(f"[OK] 模型已就緒：{model}")
    return True


def ensure_model(model: str, installed: List[str]) -> bool:
    if model in installed:
        print(f"[OK] 已下載：{model}")
        return True
    print(f"[WARN] 未下載模型，將自動下載：{model}")
    ok = download_model(model)
    if ok:
        refreshed = check_ollama()
        if refreshed is not None:
            installed[:] = refreshed
    return ok




def _split_model_input(text: str) -> List[str]:
    """Parse user model input.

    Supports comma/semicolon/newline/whitespace separated values while keeping
    Ollama names such as gemma3:1b intact. Also accepts @file to load model
    names from a local text file.
    """
    if not text:
        return []
    text = text.strip()
    values: List[str] = []

    def add_piece(piece: str) -> None:
        piece = piece.strip().strip('"').strip("'")
        if piece and piece not in values:
            values.append(piece)

    for raw in text.replace("，", ",").replace("；", ";").replace("\n", ",").split(","):
        raw = raw.strip()
        if not raw:
            continue
        # If comma was not used, allow whitespace separated model names.
        # This keeps model tags like gemma3:1b intact because ':' is not a separator.
        if ";" in raw:
            parts = [x for block in raw.split(";") for x in block.split()]
        else:
            parts = raw.split()
        for part in parts:
            add_piece(part)
    return values


def _load_models_from_file(path_text: str) -> List[str]:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        print(f"[WARN] 找不到模型清單檔案：{path}")
        return []
    models: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for item in _split_model_input(line):
            if item not in models:
                models.append(item)
    return models


def parse_model_targets(raw: str, installed: List[str]) -> List[str]:
    """Resolve the first UI input into a model list.

    Supported forms:
    - gemma3:1b
    - gemma3:1b, qwen2.5:0.5b
    - gemma3:1b qwen2.5:0.5b
    - small_models / medium_models from configs/model_groups.json
    - @configs/model_list.txt
    - installed / 已安裝 / * to test all installed Ollama models
    """
    if not raw:
        return [DEFAULT_MODEL]
    groups = load_groups()
    out: List[str] = []
    for token in _split_model_input(raw):
        key = token.strip()
        low = key.lower()
        expanded: List[str]
        if key.startswith("@"):
            expanded = _load_models_from_file(key[1:])
        elif key in groups:
            expanded = list(groups.get(key, []))
        elif low in {"small", "small_models", "小模型"}:
            expanded = list(groups.get("small_models", []))
        elif low in {"medium", "medium_models", "中模型"}:
            expanded = list(groups.get("medium_models", []))
        elif low in {"installed", "已安裝", "all_installed", "*"}:
            expanded = list(installed)
        else:
            expanded = [key]
        for model in expanded:
            model = model.strip()
            if model and model not in out:
                out.append(model)
    return out or [DEFAULT_MODEL]


def ask_models(installed: List[str]) -> List[str]:
    clear_screen()
    print("\nLLM Secret Guard")
    print("═" * 58)
    print("請輸入要測試的 Ollama 模型。")
    print("支援單一模型、多模型、群組名稱與 @檔案。")
    print("─" * 58)
    print("範例：")
    print("  gemma3:1b")
    print("  gemma3:1b, qwen2.5:0.5b, qwen2.5:1.5b")
    print("  small_models")
    print("  @configs/model_list.txt")
    print("─" * 58)
    raw = esc_input("模型", DEFAULT_MODEL)
    if raw is None:
        raise BackToMenu
    models = parse_model_targets(raw.strip(), installed)
    print(f"[OK] 本次測試模型：{', '.join(models)}")
    wait_key()
    return models

def group_menu(group_key: str, title: str, installed: List[str]) -> Optional[List[str]]:
    while True:
        groups = load_groups()
        models = groups.get(group_key, [])
        lines = [SelectOption("開始測試", "start", f"目前 {len(models)} 個模型"),
                 SelectOption("新增模型到此清單", "add"),
                 SelectOption("從此清單移除模型", "remove"),
                 SelectOption("查看模型清單", "view"),
                 SelectOption("返回", "__cancel__")]
        sel = tui_select(title, lines, 0)
        if sel.value == "__cancel__":
            raise BackToMenu
        if sel.value == "start":
            if not models:
                print("[WARN] 清單是空的，請先新增模型。")
                wait_key(); continue
            return list(models)
        if sel.value == "add":
            value = esc_input("輸入模型名稱，例如 qwen2.5:7b，Esc 返回：")
            if value:
                value = value.strip()
                if value and value not in models:
                    models.append(value); groups[group_key] = models; save_groups(groups)
                    print(f"[OK] 已新增：{value}")
            wait_key()
        elif sel.value == "remove":
            if not models:
                print("[WARN] 清單是空的。")
                wait_key(); continue
            opts = [SelectOption(f"{m} : {'已下載' if m in installed else '未下載'}", m) for m in models]
            opts.append(SelectOption("返回", "__cancel__"))
            target = tui_select("選擇要從清單移除的模型", opts, 0)
            if target.value != "__cancel__":
                models = [m for m in models if m != target.value]
                groups[group_key] = models; save_groups(groups)
                print(f"[OK] 已移除：{target.value}")
                wait_key()
        elif sel.value == "view":
            print("\n目前模型清單：")
            for i, m in enumerate(models, 1):
                print(f"  {i}. {m} : {'已下載' if m in installed else '未下載'}")
            if not models: print("  [空]")
            wait_key()


def ask_run_count() -> int:
    value = esc_input("請輸入每個模型的測試次數", "1")
    if value is None:
        raise BackToMenu
    try:
        n = int(value)
    except ValueError:
        print("[WARN] 格式錯誤，改用 1。")
        return 1
    if n < 1: return 1
    if n > 50:
        print("[WARN] 上限 50，已改為 50。")
        return 50
    return n


def _ask_int(prompt: str, default: int, min_value: int, max_value: int) -> int:
    raw = esc_input(prompt, str(default))
    if raw is None:
        raise BackToMenu
    try:
        value = int(raw)
    except ValueError:
        print(f"[WARN] 格式錯誤，改用 {default}。")
        return default
    return max(min_value, min(max_value, value))


def _ask_float(prompt: str, default: float, min_value: float, max_value: float) -> float:
    raw = esc_input(prompt, str(default))
    if raw is None:
        raise BackToMenu
    try:
        value = float(raw)
    except ValueError:
        print(f"[WARN] 格式錯誤，改用 {default}。")
        return default
    return max(min_value, min(max_value, value))


def ask_generation_params() -> GenerationParams:
    mode = tui_select("生成參數", [
        SelectOption("使用正式預設", "default", "max_tokens=300｜temperature=0.0｜num_ctx=4096。"),
        SelectOption("自訂參數", "custom", "手動設定 max_tokens、temperature、top_p、top_k、num_ctx、seed。"),
        SelectOption("返回", "__cancel__"),
    ], 0)
    if mode.value == "__cancel__":
        raise BackToMenu
    if mode.value == "default":
        return GenerationParams()
    return GenerationParams(
        max_tokens=_ask_int("max_tokens", 300, 32, 8192),
        temperature=_ask_float("temperature", 0.0, 0.0, 2.0),
        top_p=_ask_float("top_p", 1.0, 0.01, 1.0),
        top_k=_ask_int("top_k", 40, 1, 200),
        num_ctx=_ask_int("num_ctx", 4096, 512, 32768),
        seed=_ask_int("seed", 42, 0, 2_147_483_647),
    )


def _count_csv_values(value: str, all_count: int) -> int:
    if not value or value == "all":
        return all_count
    return len([x for x in value.split(",") if x.strip()])


def estimate_samples(scope: TestScope, runs: int, model_count: int = 1) -> int:
    style_count = _count_csv_values(scope.styles, len(STYLE_CHOICES))
    if scope.attack_ids and scope.attack_ids != "all":
        attack_count = _count_csv_values(scope.attack_ids, 20)
    elif scope.limit_base_attacks:
        attack_count = scope.limit_base_attacks
    else:
        attack_count = 20
    return model_count * attack_count * style_count * runs




def count_benign_prompts_for_scope(scope: TestScope, benign_path: Path = ROOT / "data" / "benign_prompts.json") -> int:
    """Count benign prompts selected by the current language style for UI sample estimation."""
    try:
        if not benign_path.exists():
            return 0
        data = json.loads(benign_path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return 0
        selected_modes = set()
        styles = [x.strip() for x in (scope.styles or "").split(",") if x.strip()]
        style_to_mode = {
            "en_pure": "EN_ONLY",
            "zh_pure": "ZH_ONLY",
            "zh_dominant_mixed": "ZH_DOMINANT_MIXED",
            "en_dominant_mixed": "EN_DOMINANT_MIXED",
        }
        if not styles or "all" in styles:
            selected_modes = set(style_to_mode.values())
        else:
            selected_modes = {style_to_mode.get(x, x) for x in styles}
        return sum(1 for item in data if str(item.get("language_mode") or "") in selected_modes)
    except Exception:
        return 0


def _scope_execution_text(scope: TestScope) -> str:
    if scope.attack_ids == "all" and scope.limit_base_attacks:
        return f"前 {scope.limit_base_attacks} 個 base attack"
    if scope.attack_ids == "all":
        return "全部攻擊"
    return scope.attack_ids


def _param_summary(params: GenerationParams) -> str:
    return f"max_tokens={params.max_tokens}, temp={params.temperature}, ctx={params.num_ctx}, seed={params.seed}"


def _plan_defense_ids(plan: DefenseTestPlan) -> List[str]:
    return [d.display_id for d in plan.defenses]


def _expected_compare_ids(plan: DefenseTestPlan) -> List[str]:
    if plan.mode_id == "compare_basic":
        return ["none", "skill_only", "output_guard", "full_guard"]
    if plan.mode_id == "compare_all":
        return ["none", "skill_only", "input_guard", "output_guard", "full_guard"]
    if plan.mode_id == "host_core_g0_g1_g5_g6":
        return ["G0", "G1", "G5", "G6"]
    if plan.mode_id == "host_full_g0_to_g6":
        return ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]
    return _plan_defense_ids(plan)


def _validate_compare_plan(plan: DefenseTestPlan) -> List[str]:
    """Return human-readable warnings for compare plan expansion."""
    if not (plan.mode_id.startswith("compare") or plan.mode_id.startswith("host_")):
        return []
    actual = _plan_defense_ids(plan)
    expected = _expected_compare_ids(plan)
    missing = [x for x in expected if x not in actual]
    extra = [x for x in actual if x not in expected]
    warnings: List[str] = []
    if missing:
        warnings.append("compare plan 缺少防禦組：" + ", ".join(missing))
    if extra:
        warnings.append("compare plan 包含額外防禦組：" + ", ".join(extra))
    if len(actual) <= 1:
        warnings.append("compare plan 只有一個防禦組，將無法形成比較報告。")
    return warnings


def _short_registry_status(defense: DefenseChoice) -> str:
    path = effective_registry_path(defense) if 'effective_registry_path' in globals() else (defense.secrets_registry_path or str(DEFAULT_SECRETS_REGISTRY_PATH))
    return "on" if Path(path).name != DISABLED_SECRETS_REGISTRY_PATH.name else "off"


def _group_config_rows(plan: DefenseTestPlan) -> List[str]:
    rows: List[str] = []
    for d in plan.defenses:
        if not d.group_id:
            continue
        review = d.review_level_override or "default"
        action = d.output_action_override or "default"
        registry = _short_registry_status(d)
        rows.append(f"{d.display_id:<3} {d.display_name:<36} {d.defense_id:<12} {review:<13} {action:<7} registry={registry}")
    return rows


def _print_group_config_table(plan: DefenseTestPlan) -> None:
    rows = _group_config_rows(plan)
    if not rows:
        return
    print("G 組別設定")
    print("-" * 58)
    print(f"{'ID':<3} {'名稱':<36} {'底層模式':<12} {'審查':<13} {'輸出':<7} Registry")
    for row in rows:
        print(row)


def choose_benign_test() -> bool:
    selected = tui_select("正常樣本測試", [
        SelectOption("啟用", "yes", "追加 benign prompts，用來估算正常請求誤擋率。"),
        SelectOption("不啟用", "no", "只跑攻擊樣本。"),
        SelectOption("返回", "__cancel__"),
    ], 0)
    if selected.value == "__cancel__":
        raise BackToMenu
    return selected.value == "yes"


def confirm_experiment(models: List[str], scope: TestScope, plan: DefenseTestPlan, skill_profile: Optional[SkillProfileChoice], custom_rules: CustomDefenseRules, output_action: OutputActionChoice, review_level: ReviewLevelChoice, verification: VerificationChoice, include_benign: bool, run_count: int, params: GenerationParams, protected_asset: ProtectedAssetChoice) -> bool:
    print("\n" + "═" * 58)
    print("測試確認")
    print("═" * 58)
    print(f"模型        {', '.join(models)}")
    print(f"範圍        {_scope_execution_text(scope)} / {scope.styles}")
    print(f"實驗模式    {plan.name}")
    if plan.defense_count > 1:
        print(f"組別        {', '.join(_plan_defense_ids(plan))}")
        print(f"執行方式    依序執行 {plan.defense_count} 組防禦")
        print("說明        --defense 是底層模式；G 組別由 review / registry / output action 區分")
    else:
        only = plan.defenses[0]
        print(f"防禦        {only.display_name} [{only.display_id}] / 底層 {only.defense_id}")
    for warn in _validate_compare_plan(plan):
        print(f"[WARN] {warn}")
    if skill_profile:
        print(f"Skill       {skill_profile.name} [{skill_profile.profile_id}]，{skill_profile.skill_count} 個檔案")
    print(f"自訂規則    {'啟用 ' + str(custom_rules.total_count) + ' 條' if custom_rules.enabled else '未啟用'}" + ("，Skill模式=custom_only" if custom_rules.custom_skill_file else ""))
    if plan.defense_count > 1:
        print("輸出處置    依 G 組別自動設定")
        print("審查策略    依 G 組別自動設定")
    else:
        print(f"輸出處置    {output_action.name} [{output_action.action_id}]")
        print(f"審查策略    {review_level.name} [{review_level.level_id}]")
    print(f"Skill驗證   {verification.name} [{verification.mode_id}]")
    print(f"敏感資料    {protected_asset.summary()}")
    print(f"正常樣本    {'啟用，用於誤擋率' if include_benign else '未啟用'}")
    print(f"次數        {run_count}")
    print(f"參數        {_param_summary(params)}")
    base_est = estimate_samples(scope, run_count, len(models)) * max(1, plan.defense_count)
    benign_count = count_benign_prompts_for_scope(scope) if include_benign else 0
    benign_est = (benign_count * run_count * len(models) * max(1, plan.defense_count)) if include_benign else 0
    print(f"預估樣本    {base_est + benign_est}")
    if plan.defense_count > 1:
        print("─" * 58)
        _print_group_config_table(plan)
    print("─" * 58)
    raw = esc_input("開始測試？輸入 Y 確認", "Y")
    if raw is None:
        return False
    return raw.strip().lower() in {"y", "yes"}


def run_command(cmd: List[str]) -> bool:
    print("[執行] " + " ".join(cmd))
    try:
        rc = subprocess.run(cmd, cwd=str(ROOT)).returncode
    except Exception as exc:
        print(f"[ERROR] 執行程序崩潰：{exc}")
        return False
    if rc != 0:
        print(f"[ERROR] 執行程序失敗：exit code {rc}")
        return False
    return True


def _output_action_name(action_id: str) -> str:
    names = {
        "block": "整段阻擋",
        "redact": "敏感資料遮蔽",
        "shadow": "只偵測不阻擋",
    }
    return names.get(action_id, action_id)


def _review_level_name(level_id: str) -> str:
    names = {
        "light": "輕量審查",
        "standard": "標準審查",
        "strict": "嚴格審查",
        "enterprise": "企業嚴格審查",
        "attack_aware": "攻擊感知審查",
    }
    return names.get(level_id, level_id)


def effective_output_action(defense: DefenseChoice, default: OutputActionChoice) -> OutputActionChoice:
    action = defense.output_action_override or default.action_id
    if action == default.action_id and not defense.output_action_override:
        return default
    return OutputActionChoice(action, _output_action_name(action), "由 Host LLM 實驗組別自動指定。")


def effective_review_level(defense: DefenseChoice, default: ReviewLevelChoice) -> ReviewLevelChoice:
    level = defense.review_level_override or default.level_id
    if level == default.level_id and not defense.review_level_override:
        return default
    return ReviewLevelChoice(level, _review_level_name(level), "由 Host LLM 實驗組別自動指定。")


def effective_registry_path(defense: DefenseChoice) -> str:
    return defense.secrets_registry_path or str(DEFAULT_SECRETS_REGISTRY_PATH)


def _registry_status_text(defense: DefenseChoice) -> str:
    path = Path(effective_registry_path(defense))
    if path.name == DISABLED_SECRETS_REGISTRY_PATH.name:
        return "停用（v25.3 正式 G0-G6 比較預設不啟用 registry）"
    return f"啟用：{path.relative_to(ROOT) if path.is_absolute() and ROOT in path.parents else path}"


def result_path_for(model: str, run_name: str, defense_id: str) -> Path:
    expected = ROOT / "results" / f"results_{safe_filename('ollama:' + model)}__{safe_filename(run_name)}__def_{safe_filename(defense_id)}__{safe_filename(os.getenv('COMPUTERNAME') or os.getenv('HOSTNAME') or 'PC01')}.csv"
    if expected.exists():
        return expected
    candidates = sorted((ROOT / "results").glob(f"results_{safe_filename('ollama:' + model)}__{safe_filename(run_name)}__def_{safe_filename(defense_id)}__*.csv"))
    return candidates[-1] if candidates else expected


def read_results(model: str, run_name: str, defense_id: str) -> List[dict]:
    path = result_path_for(model, run_name, defense_id)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def summarize_rows(model: str, rows: List[dict]) -> Dict[str, object]:
    valid = [r for r in rows if str(r.get("valid_sample", "")).lower() == "true" and r.get("status") == "OK"]
    errors = [r for r in rows if r not in valid]
    critical = [r for r in valid if str(r.get("leak_level")) in {"3", "4"}]
    leaks = [r for r in valid if str(r.get("leak_level")) in {"2", "3", "4"}]
    score = 0.0
    if valid:
        score = round(sum(float(r.get("score") or 0) for r in valid) / len(valid), 2)
    error_counts = Counter(r.get("error_type") or "UNKNOWN" for r in errors)
    print("\n[結果摘要]")
    print(f"模型：{model}")
    print(f"有效樣本：{len(valid)} / {len(rows)}")
    print(f"洩漏樣本：{len(leaks)}")
    print(f"嚴重洩漏（Level>=3）：{len(critical)}")
    print(f"敏感資料保護分數：{score} / 100")
    if error_counts:
        print("錯誤摘要：")
        for k, v in error_counts.items():
            print(f"  - {k}: {v}")
    return {"valid": len(valid), "errors": len(errors), "critical": len(critical), "score": score, "error_counts": dict(error_counts)}


def run_model(model: str, installed: List[str], run_count: int, scope: TestScope, plan: DefenseTestPlan, skill_profile: Optional[SkillProfileChoice], custom_rules: CustomDefenseRules, output_action: OutputActionChoice, review_level: ReviewLevelChoice, verification: VerificationChoice, include_benign: bool, params: GenerationParams, protected_asset: ProtectedAssetChoice) -> bool:
    if not ensure_model(model, installed):
        return False
    success = True
    collected_csvs: List[Path] = []

    warnings = _validate_compare_plan(plan)
    if warnings:
        for warn in warnings:
            print(f"[WARN] {warn}")
    if plan.defense_count > 1:
        print("\n[比較模式展開]")
        print(f"模式：{plan.name} [{plan.mode_id}]")
        print(f"組別：{', '.join(_plan_defense_ids(plan))}")
        print("每一組會各自呼叫一次 run_benchmark.py；G 組別會寫入 run-name 與 compare_plan.json。")
        _print_group_config_table(plan)

    for defense_idx, defense in enumerate(plan.defenses, 1):
        group_output_action = effective_output_action(defense, output_action)
        group_review_level = effective_review_level(defense, review_level)
        group_registry_path = effective_registry_path(defense)
        for i in range(1, run_count + 1):
            active_skill_profile = skill_profile if defense.uses_skill else None
            skill_suffix = f"__skill_{active_skill_profile.profile_id}" if active_skill_profile else ""
            benign_suffix = "__benign" if include_benign else ""
            group_suffix = f"__group_{safe_filename(defense.display_id)}" if defense.group_id else ""
            base_name = f"{ATTACKS_PATH.stem}__{scope.run_name_suffix}__{plan.mode_id}{group_suffix}__def_{defense.defense_id}{skill_suffix}{benign_suffix}"
            run_name = base_name if run_count == 1 else f"{base_name}__run{i:02d}"
            print("\n" + "=" * 62)
            print(f"模型：{model}")
            print(f"防禦進度：{defense_idx}/{len(plan.defenses)} - {defense.display_name} [{defense.display_id}]")
            print(f"執行次數：{i}/{run_count}")
            print(f"測試範圍：{scope.label}")
            print(f"底層模式：{defense.name} [{defense.defense_id} / {defense.defense_type}]")
            if active_skill_profile:
                print(f"Skill Profile：{active_skill_profile.name} [{active_skill_profile.profile_id}]")
            if custom_rules.enabled:
                print(f"自訂規則：啟用，總計 {custom_rules.total_count} 條" + ("，Skill模式=custom_only" if custom_rules.custom_skill_file else ""))
            print(f"輸出處置：{group_output_action.name} [{group_output_action.action_id}]")
            print(f"審查強度：{group_review_level.name} [{group_review_level.level_id}]")
            print(f"Secret Registry：{_registry_status_text(defense)}")
            print(f"Skill 掛載驗證：{verification.name} [{verification.mode_id}]")
            print(f"敏感資料：{protected_asset.summary()}")
            print(f"正常樣本測試：{'啟用' if include_benign else '未啟用'}")
            print(f"攻擊資料集：{ATTACKS_PATH.relative_to(ROOT)}")
            print("=" * 62)
            if plan.defense_count > 1:
                print(f"[比較模式] 目前執行第 {defense_idx}/{len(plan.defenses)} 組：{defense.display_id} / 底層 {defense.defense_id}")
            cmd = [
                sys.executable, "src/run_benchmark.py",
                "--model", f"ollama:{model}",
                "--ollama-url", OLLAMA_URL,
                "--attacks", str(ATTACKS_PATH),
                "--run-name", run_name,
            ]
            cmd += scope.to_cli_args()
            cmd += defense.to_cli_args(active_skill_profile, custom_rules)
            cmd += group_output_action.to_cli_args()
            cmd += group_review_level.to_cli_args()
            cmd += ["--secrets-registry", group_registry_path]
            cmd += protected_asset.to_cli_args()
            if defense.group_id:
                cmd += ["--g-group-id", defense.display_id, "--g-group-name", defense.display_name]
            cmd += verification.to_cli_args()
            if include_benign:
                cmd += ["--include-benign", "--benign-file", "data/benign_prompts.json"]
            cmd += params.to_cli_args()
            ok = run_command(cmd)
            csv_path = result_path_for(model, run_name, defense.defense_id)
            if csv_path.exists():
                collected_csvs.append(csv_path)
            else:
                print(f"[WARN] 找不到此組結果 CSV：{csv_path}")
            rows = read_results(model, run_name, defense.defense_id)
            stats = summarize_rows(model, rows) if rows else {"errors": 999, "valid": 0, "error_counts": {"RESULT_NOT_FOUND": 1}}
            if (not ok) or stats.get("valid", 0) == 0 or stats.get("errors", 0) > 0:
                success = False
                print("[WARN] 此組測試有問題列入問題清單，流程會繼續下一組。")
    if collected_csvs:
        report_dir = ROOT / "reports" / f"compare_{safe_filename(model)}_{plan.mode_id}_{scope.run_name_suffix}"
        report_dir.mkdir(parents=True, exist_ok=True)
        compare_plan = {
            "model": model,
            "plan_mode": plan.mode_id,
            "plan_name": plan.name,
            "defense_ids": _plan_defense_ids(plan),
            "defense_count": plan.defense_count,
            "scope": {
                "label": scope.label,
                "styles": scope.styles,
                "attack_ids": scope.attack_ids,
                "limit_base_attacks": scope.limit_base_attacks,
            },
            "runs": run_count,
            "include_benign": include_benign,
            "protected_asset": {
                "enabled": protected_asset.enabled,
                "config_path": protected_asset.config_path,
                "asset_id": protected_asset.asset_id,
                "name": protected_asset.name,
                "risk_level": protected_asset.risk_level,
            },
            "output_action": output_action.action_id,
            "review_level": review_level.level_id,
            "skill_profile": skill_profile.profile_id if skill_profile else None,
            "groups": [
                {
                    "group_id": d.display_id,
                    "group_name": d.display_name,
                    "defense_id": d.defense_id,
                    "review_level": d.review_level_override or review_level.level_id,
                    "output_action": d.output_action_override or output_action.action_id,
                    "secrets_registry": effective_registry_path(d),
                }
                for d in plan.defenses
            ],
            "collected_csvs": [str(p) for p in collected_csvs],
            "note": "Compare mode is expanded by semi_auto_ollama.py. v25.3 formal Host-LLM groups are G0-G6 and match Web UI / defense_config: G5=io_guard and G6=full_guard.",
        }
        (report_dir / "compare_plan.json").write_text(json.dumps(compare_plan, ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [sys.executable, "src/report_generator.py", "--inputs"] + [str(p) for p in collected_csvs] + ["--report-dir", str(report_dir)]
        run_command(cmd)
        print(f"[報告] 已產生合併報告：{report_dir}")
        print(f"[報告] 比較模式計畫：{report_dir / 'compare_plan.json'}")
    return success

def main_menu(installed: List[str]) -> int:
    while True:
        try:
            models = ask_models(installed)
            scope = choose_test_scope()
            plan = choose_defense_plan()
            skill_profile = choose_skill_profile(plan)
            # 自訂規則可能影響 skill/input/output；若比較模式包含 Skill，允許輸入自訂 Skill。
            custom_rule_base = next((d for d in plan.defenses if d.uses_skill), plan.defenses[0] if plan.defenses else DefenseChoice("none", "無防禦", "none"))
            custom_rules = choose_custom_rules(custom_rule_base)
            output_action = auto_output_action(plan)
            review_level = auto_review_level(plan)
            verification = VerificationChoice()
            include_benign = choose_benign_test()
            run_count = ask_run_count()
            protected_asset = choose_protected_asset()
            params = ask_generation_params()
        except BackToMenu:
            leave = tui_select("要離開工具嗎？", [
                SelectOption("繼續設定", "continue", "回到模型輸入畫面。"),
                SelectOption("離開", "exit", "結束 LLM Secret Guard。"),
            ], 0)
            if leave.value == "exit" or leave.value == "__cancel__":
                return 0
            continue

        if not confirm_experiment(models or [], scope, plan, skill_profile, custom_rules, output_action, review_level, verification, include_benign, run_count, params, protected_asset):
            print("[已取消] 已取消本次測試設定。")
            wait_key()
            continue

        print("\n[開始測試]")
        print(f"模型：{', '.join(models or [])}")
        print(f"範圍：{_scope_execution_text(scope)} / {scope.styles}")
        print(f"防禦：{plan.name}：{plan.label()}")
        if plan.defense_count > 1:
            print(f"比較展開：{', '.join(_plan_defense_ids(plan))}")
        if skill_profile:
            print(f"Skill：{skill_profile.name} [{skill_profile.profile_id}]")
        if custom_rules.enabled:
            print(f"自訂規則：{custom_rules.total_count} 條")
        print(f"輸出處置：自動；多組比較時依 G 組別指定，單一防禦預設 {output_action.name} [{output_action.action_id}]")
        print(f"審查策略：自動；多組比較時依 G 組別指定，單一防禦預設 {review_level.name} [{review_level.level_id}]")
        print(f"Skill 掛載驗證：{verification.name} [{verification.mode_id}]")
        print(f"敏感資料：{protected_asset.summary()}")
        print(f"正常樣本測試：{'啟用' if include_benign else '未啟用'}")

        problem_models: List[str] = []
        for idx, model in enumerate(models or [], 1):
            print("\n" + "#" * 58)
            print(f"模型進度：{idx}/{len(models)} - {model}")
            print("#" * 58)
            if not run_model(model, installed, run_count, scope, plan, skill_profile, custom_rules, output_action, review_level, verification, include_benign, params, protected_asset):
                problem_models.append(model)

        print("\n" + "═" * 58)
        print("測試完成")
        print(f"總模型數：{len(models or [])}")
        print(f"問題模型數：{len(problem_models)}")
        if problem_models:
            print("問題清單：")
            for m in problem_models:
                print(f"  - {m}")
        print(f"結果資料夾：{ROOT / 'results'}")
        print(f"報告資料夾：{ROOT / 'reports'}")
        print("═" * 58)
        wait_key()


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simple", action="store_true", help="強制使用數字選單")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    global SIMPLE_MODE
    args = parse_args(sys.argv[1:] if argv is None else argv)
    SIMPLE_MODE = args.simple
    print("LLM Secret Guard - OWASP LLM02")
    print(f"Ollama：{OLLAMA_URL}")
    print(f"專案：{ROOT}")
    installed = check_ollama()
    if installed is None:
        print("[FAIL] Ollama 無法連線。請確認 install.bat 已啟動 Ollama，或手動執行 ollama serve。")
        return 1
    return main_menu(installed)


if __name__ == "__main__":
    raise SystemExit(main())
