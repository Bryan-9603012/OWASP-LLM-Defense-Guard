import argparse
from pathlib import Path

from model_client import get_client
from leak_detector import detect_leak
from defense_loader import apply_defense_to_system_prompt, input_guard, load_defense, output_guard


ROOT = Path(__file__).resolve().parents[1]


def load_flag() -> str:
    return (ROOT / "data" / "protected_data.txt").read_text(encoding="utf-8").strip()


def load_system_prompt(flag: str) -> str:
    template = (ROOT / "prompts" / "system_prompt.txt").read_text(encoding="utf-8")
    return template.format(flag=flag)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mock", help="mock / ollama:<model_name>")
    parser.add_argument("--defense", default="none", help="none / prompt_defense / skill_defense")
    parser.add_argument("--defense-config", default="defenses/defense_config.json")
    parser.add_argument("--review-level", choices=["light", "standard", "strict", "enterprise", "attack_aware"], default="standard")
    parser.add_argument("--output-action", choices=["auto", "block", "redact", "shadow"], default="auto")
    args = parser.parse_args()

    flag = load_flag()
    defense = load_defense(args.defense, args.defense_config)
    system_prompt = apply_defense_to_system_prompt(load_system_prompt(flag), defense)
    client = get_client(args.model)

    print("=== LLM Secret Guard Manual Test ===")
    print("輸入 exit 離開")
    print(f"Model: {args.model}")
    print(f"Defense: {defense.defense_id} ({defense.name})")

    while True:
        user_prompt = input("\n攻擊輸入 > ").strip()
        if user_prompt.lower() == "exit":
            break

        guard = input_guard(user_prompt, defense, args.review_level, None)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if guard.blocked:
            response = guard.safe_response
            raw_response = ""
            defense_triggered = "input_guard"
            defense_reason = guard.reason
        else:
            raw_response = client.generate(messages)
            out_guard = output_guard(raw_response, defense, flag, args.output_action, getattr(guard, "review_level", args.review_level), None)
            response = out_guard.safe_response if out_guard.blocked else raw_response
            defense_triggered = "output_guard" if out_guard.blocked else ("output_guard_shadow" if getattr(out_guard, "action", "") == "shadow" else "none")
            defense_reason = out_guard.reason
        leak = detect_leak(response, flag)

        print("\n模型回覆：")
        print(response)
        print("\n測試結果：")
        print(f"Leak Level: {leak.leak_level}")
        print(f"Result: {leak.result}")
        print(f"Defense Triggered: {defense_triggered}")
        print(f"Review Level: {getattr(guard, 'review_level', args.review_level)}")
        print(f"Defense Reason: {defense_reason}")
        print(f"Reason: {' | '.join(leak.reasons)}")


if __name__ == "__main__":
    main()
