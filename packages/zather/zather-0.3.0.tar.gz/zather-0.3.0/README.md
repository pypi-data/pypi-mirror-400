# zather

`zather` generates **Path Packs**: procedural docs that teach a coding agent how to *recreate the context-building pathway* from an excellent Claude Code / Codex CLI session.

Unlike compaction systems that try to reproduce the final patch, **zather compacts the path**: the ordered set of reads/searches/commands and intermediate "what we learned" checkpoints that got the agent to a useful semantic state.

## Install

```bash
uv pip install -e .
```

## Quick Start

Generate a Path Pack from a Codex CLI session:

```bash
# By session ID
zather build --source codex --session <session-id> --out path-pack.md

# By session file path
zather build --source codex --session-file ~/.codex/sessions/.../rollout-...jsonl --out path-pack.md
```

Generate from a Claude Code session:

```bash
zather build --source claude --project . --session <session-id> --out path-pack.md
```

List available sessions:

```bash
zather list --source codex
zather list --source claude --project .
```

## Options

```bash
zather build --source codex --session <id> --out path-pack.md \
    --model gpt-5-mini \           # Override model (default: from prompt YAML)
    --max-events 250 \             # Max trajectory events to include
    --max-chars 1500 \             # Max chars per tool output
    --prompt custom-prompt.yaml \  # Custom prompt template
    --weave-project wandb/zather \ # Enable weave tracking
    --dry-run                      # Write prompts only, no LLM call
```

### Checkpoints

Target a specific time range within a session:

```bash
zather build ... --since 2026-01-07T20:04:00Z --until 2026-01-07T20:10:00Z
```

## Architecture

zather uses the WBAL agent framework:

- **ZatherEnv**: Loads trajectory data and prompt configuration
- **ZatherAgent**: Generates Path Pack using `submit_path_pack` tool
- **GPT5MiniTester**: Default LM (gpt-5-mini with minimal reasoning)

```python
from zather import ZatherEnv, ZatherAgent, build_path_pack

# Load environment with trajectory
env = ZatherEnv.load(
    source="codex",
    session_id="019b9fa7-...",
    output_path=Path("path-pack.md"),
    prompt_path=Path("zather/prompts/path_pack.yaml"),
)

# Generate path pack
build_path_pack(env=env)
```

## Evaluation

The `eval/` directory contains a weave-based evaluation framework:

```bash
python -m eval.evaluation --sessions-dir eval/sessions --project zather-eval
```

This runs:
1. **ZatherModel**: Generates Path Packs from session files
2. **PathPackQualityScorer**: LLM-as-judge for document quality
3. **PathReconstructionScorer**: Runs Codex with the Path Pack, compares trajectories

### Evaluation Dataset

Place session JSONL files in `eval/sessions/`. Each file should be a Codex CLI session log.

## Prompting

The default prompt template is at `zather/prompts/path_pack.yaml`. It defines:

- `system_prompt`: Instructions for the Path Pack format
- `user_prompt_template`: Template with `{session_meta_yaml}` and `{trajectory_markdown}` placeholders
- `model`: Default model to use
- `reasoning_effort`: Optional reasoning effort level
