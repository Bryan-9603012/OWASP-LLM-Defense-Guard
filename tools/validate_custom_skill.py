from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment_qa import validate_custom_skill_file  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a custom enterprise Skill markdown file.")
    parser.add_argument("skill_file", help="Path to custom Skill .md file")
    parser.add_argument("--json", action="store_true", help="Print full JSON validation result")
    args = parser.parse_args()

    result = validate_custom_skill_file(args.skill_file, ROOT)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=== Custom Skill Validation ===")
        print(f"File          : {result.get('resolved_file') or result.get('file')}")
        print(f"Status        : {result.get('status')}")
        print(f"SHA256        : {result.get('sha256') or 'none'}")
        print(f"Chars/Tokens  : {result.get('chars')} chars / {result.get('est_tokens')} est. tokens")
        print(f"First heading : {result.get('first_heading') or 'none'}")
        if result.get("warnings"):
            print("Warnings:")
            for w in result["warnings"]:
                print(f"  - {w}")
        if result.get("errors"):
            print("Errors:")
            for e in result["errors"]:
                print(f"  - {e}")
    return 1 if result.get("status") == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
