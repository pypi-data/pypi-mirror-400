"""
Main evaluation orchestrator for zather Path Pack evaluation.

Evaluation flow:
1. Dataset: session files with their original cwds
2. Model (ZatherModel): generates Path Pack from session
3. Scorers:
   - PathPackQualityScorer: judges the Path Pack document quality
   - PathReconstructionScorer: runs agent with Path Pack, compares trajectories
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import weave

from .model import ZatherModel
from .scorers import (
    PathPackQualityScorer,
    PathReconstructionScorer,
)


def load_eval_dataset(sessions_dir: str) -> list[dict[str, Any]]:
    """
    Load the evaluation dataset from the sessions directory.

    Each session JSONL file becomes one eval example with:
    - session_file: path to the JSONL
    - session_name: human-readable name
    - target_cwd: original working directory (for agent execution)
    """
    sessions_path = Path(sessions_dir)
    examples = []

    for session_file in sorted(sessions_path.glob("*.jsonl")):
        # Extract metadata from the session
        with open(session_file) as f:
            first_line = f.readline()
            meta = json.loads(first_line)

        # Get the original working directory
        payload = meta.get("payload", {})
        cwd = payload.get("cwd", str(Path.cwd()))

        examples.append(
            {
                "session_file": str(session_file),
                "session_name": session_file.stem,
                "target_cwd": cwd,
            }
        )

    return examples


async def run_evaluation(
    sessions_dir: str = "eval/sessions",
    weave_project: str = "zather-eval",
    zather_model: str = "gpt-4.1-mini",
) -> None:
    """
    Run the zather evaluation.

    Args:
        sessions_dir: Directory containing session JSONL files.
        weave_project: Weave project name for logging.
        zather_model: Model for Path Pack generation.
    """
    # Initialize Weave
    weave.init(weave_project)

    # Load dataset
    dataset = load_eval_dataset(sessions_dir)
    print(f"Loaded {len(dataset)} eval examples")

    # Validate target_cwds exist
    for example in dataset:
        cwd = example["target_cwd"]
        if not Path(cwd).exists():
            print(f"WARNING: target_cwd does not exist: {cwd}")
            print(f"  Session: {example['session_name']}")
            print(f"  Agent execution will fail for this example.")

    # Create the model
    model = ZatherModel(
        model=zather_model,
    )

    # Run all scorers
    scorers = [
        PathPackQualityScorer(),  # Judges the Path Pack document quality
        PathReconstructionScorer(),  # Runs agent, compares trajectories, includes metrics
    ]

    # Run evaluation
    evaluation = weave.Evaluation(
        name="zather-path-pack-eval",
        dataset=dataset,
        scorers=scorers,
    )

    results = await evaluation.evaluate(model)

    print("\n=== Evaluation Complete ===")
    print(f"Results logged to Weave project: {weave_project}")

    return results


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run zather evaluation")
    parser.add_argument(
        "--sessions-dir",
        type=str,
        default="eval/sessions",
        help="Directory containing session JSONL files",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="zather-eval",
        help="Weave project name",
    )
    parser.add_argument(
        "--zather-model",
        type=str,
        default="gpt-4.1-mini",
        help="Model for Path Pack generation",
    )

    args = parser.parse_args()

    asyncio.run(
        run_evaluation(
            sessions_dir=args.sessions_dir,
            weave_project=args.project,
            zather_model=args.zather_model,
        )
    )


if __name__ == "__main__":
    main()
