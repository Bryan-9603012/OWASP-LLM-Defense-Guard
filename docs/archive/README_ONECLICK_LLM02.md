# LLM Secret Guard - OWASP LLM02 One-click Edition

## Entry point

Double-click:

```bat
install.bat
```

The launcher will:

1. Check/install Python 3.9.6 for the current Windows user.
2. Create `.venv`.
3. Install packages from `requirements.txt`.
4. Check/install Ollama.
5. Start `ollama serve` if the local API is not reachable.
6. Open the interactive test UI.

## Main menu

First layer:

1. 中型語言模型測試
2. 小型語言模型測試
3. 單一語言模型測試

Controls:

- `↑ / ↓`: select
- `Enter`: confirm
- `Esc`: go back

## Model groups

Model lists are stored in:

```text
model_groups.json
```

The UI supports:

- View list
- Add model
- Remove model
- Start test

If a model is not installed, the tool runs:

```bat
ollama pull <model_name>
```

## Attack set

Default attack catalog:

```text
attacks/attacks.json
```

Current design:

- 8 attack categories
- 1 standard payload per category
- 4 language modes per payload
- Total: 32 payloads

Language modes:

- `ZH_ONLY`: pure Chinese attack
- `EN_ONLY`: pure English attack
- `ZH_EN_MIX`: Chinese-dominant prompt with English terms/instructions
- `EN_ZH_MIX`: English-dominant prompt with Chinese terms/instructions

## Outputs

Per model:

```text
results/*.csv
reports/*.md
reports/*.json
reports/figures/model_radars/radar_<model>.png
```

Overall charts:

```text
reports/figures/model_safety_ranking.png
reports/figures/category_heatmap.png
reports/figures/attack_id_matrix.png
reports/figures/critical_failure_count_by_model.png
reports/figures/critical_failure_count_by_category.png
reports/figures/failed_attack_categories.png
reports/figures/leak_level_distribution.png
reports/figures/model_size_vs_safety.png
reports/figures/radar_top_models.png
reports/figures/weakness_pareto.png
reports/figures/language_mode_summary.csv
```

## Notes

- Official experiment category: `OWASP LLM02 Sensitive Information Disclosure`.
- Prompt injection is treated as the attack method, not the top-level OWASP category.
- Mixed-language attack is stored as `language_mode`, not as a separate attack category.

## 受測模型清單

### 小型模型

```bash
ollama pull llama3.2:1b
ollama pull llama3.2:3b
ollama pull qwen2.5:0.5b
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:3b
ollama pull qwen2.5-coder:0.5b
ollama pull qwen2.5-coder:1.5b
ollama pull qwen2.5-coder:3b
ollama pull gemma3:270m
ollama pull gemma3:1b
ollama pull gemma3:4b
ollama pull phi4-mini:3.8b
```

### 中型模型

```bash
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
ollama pull qwen2.5-coder:7b
ollama pull qwen2.5-coder:14b
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull gemma3:12b
ollama pull phi4:14b
ollama pull phi4-reasoning:14b
ollama pull deepseek-r1:7b
ollama pull deepseek-r1:8b
ollama pull deepseek-r1:14b
```
