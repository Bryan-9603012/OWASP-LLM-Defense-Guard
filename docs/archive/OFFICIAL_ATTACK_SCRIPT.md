# Official Attack Script

This package keeps only one formal attack dataset:

```text
attacks/attacks.json
```

It contains the final 20 × 4 benchmark design:

```text
20 attack categories × 4 prompt language styles = 80 prompts per run
```

A19 has been finalized as:

```text
A19: translation_based_leakage
中文：翻譯型洩漏攻擊
```

For the formal experiment, use this file only. Other draft attack datasets were removed to avoid accidentally mixing old and new attack definitions.

Recommended full formal run:

```bash
python src/run_benchmark.py --model ollama:<model_name> --attacks attacks/attacks.json --styles all --runs 3 --limit-base-attacks 20 --temperature 0 --top-p 1 --top-k 40 --num-ctx 4096 --max-tokens 300 --seed 42
```
