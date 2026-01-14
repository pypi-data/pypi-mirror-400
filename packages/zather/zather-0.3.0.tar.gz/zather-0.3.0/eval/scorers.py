"""
Scorers for evaluating Path Pack quality.

Primary scorer: Runs agent with Path Pack, then LLM-as-judge compares trajectories.
Secondary scorers: Metrics like tool count, token usage, step efficiency.
"""

import json
from pathlib import Path
from typing import Any, ClassVar, Optional

import weave

from .runner import AgentRunner, extract_trajectory_summary, load_session_events

# =============================================================================
# Prompt for LLM-as-judge
# =============================================================================

PATH_RECONSTRUCTION_PROMPT = """You are an expert evaluator assessing how well a "Path Pack" document helped an AI agent reconstruct an exploration pathway.

## Background

A "Path Pack" is a procedural document that teaches an agent how to recreate the context-building steps from an excellent coding session. It captures:
- The ordered sequence of file reads, searches, and commands
- Key insights and "what we learned" checkpoints
- The exploration strategy that led to understanding

## Your Task

Compare the ORIGINAL SESSION TRAJECTORY (ground truth) with the RECONSTRUCTED SESSION TRAJECTORY (produced by an agent following the Path Pack).

Evaluate how well the reconstructed trajectory matches the original in terms of:

1. **Exploration Strategy** (0-10): Did the agent follow a similar exploration pattern?
   - Same types of operations (reads, searches, commands)?
   - Similar order of discovery?
   - Comparable breadth vs depth of exploration?

2. **Key Files Discovered** (0-10): Did the agent find the same important files?
   - Core source files identified?
   - Configuration files found?
   - Documentation accessed?

3. **Tools & Commands Used** (0-10): Similar tool usage patterns?
   - File operations (read, write, search)?
   - Shell commands executed?
   - Search patterns used?

4. **Context Quality** (0-10): Would the agent reach a similar understanding?
   - Key concepts discovered?
   - Architecture understood?
   - Dependencies identified?

5. **Efficiency** (0-10): How efficiently did the reconstructed path achieve similar context?
   - Fewer wasted steps?
   - More direct path to key insights?
   - Reasonable token/step count?

## ORIGINAL SESSION TRAJECTORY
```
{original_trajectory}
```

## RECONSTRUCTED SESSION TRAJECTORY
```
{reconstructed_trajectory}
```

## Instructions

Analyze both trajectories carefully and provide your evaluation.

Respond with a JSON object:
{{
    "exploration_strategy_score": <0-10>,
    "key_files_score": <0-10>,
    "tools_commands_score": <0-10>,
    "context_quality_score": <0-10>,
    "efficiency_score": <0-10>,
    "overall_score": <0-10, weighted average>,
    "reasoning": "<detailed explanation of your assessment>",
    "strengths": ["<list of what the Path Pack did well>"],
    "weaknesses": ["<list of areas for improvement>"]
}}
"""


class PathReconstructionScorer(weave.Scorer):
    """
    The main evaluation scorer that:
    1. Runs an agent with the generated Path Pack
    2. Captures the agent's session log
    3. Uses LLM-as-judge to compare original vs reconstructed trajectories

    This is the "full" evaluation that tests if the Path Pack actually works.
    """

    # LLM judge settings
    judge_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    max_trajectory_chars: int = 15000

    # Agent runner settings
    agent: str = "codex"
    agent_model: str = "gpt-4.1"
    agent_timeout: int = 300
    agent_sandbox: str = "read-only"

    def _truncate_trajectory(self, trajectory: str) -> str:
        """Truncate trajectory to max chars while keeping structure."""
        if len(trajectory) <= self.max_trajectory_chars:
            return trajectory

        truncated = trajectory[: self.max_trajectory_chars]
        last_newline = truncated.rfind("\n")
        if last_newline > self.max_trajectory_chars * 0.8:
            truncated = truncated[:last_newline]

        return truncated + "\n\n[... truncated ...]"

    def _format_trajectory_for_judge(self, session_file: str) -> str:
        """Format a session file into a readable trajectory for the judge."""
        events = load_session_events(session_file)

        lines = []
        for i, event in enumerate(events[:200]):  # Limit events
            event_type = event.get("type")
            payload = event.get("payload", {})

            if event_type == "event_msg":
                msg_type = payload.get("type")
                if msg_type == "user_message":
                    msg = payload.get("message", "")[:500]
                    lines.append(f"[{i}] USER: {msg}")
                elif msg_type == "agent_reasoning":
                    text = payload.get("text", "")[:300]
                    lines.append(f"[{i}] REASONING: {text}")

            elif event_type == "response_item":
                item_type = payload.get("type")
                if item_type == "function_call":
                    name = payload.get("name", "unknown")
                    args = str(payload.get("arguments", {}))[:200]
                    lines.append(f"[{i}] TOOL_CALL: {name}({args})")
                elif item_type == "function_call_output":
                    output = str(payload.get("output", ""))[:300]
                    lines.append(f"[{i}] TOOL_OUTPUT: {output[:300]}")
                elif item_type == "message":
                    role = payload.get("role", "")
                    content = ""
                    for c in payload.get("content", []):
                        if isinstance(c, dict) and c.get("type") == "output_text":
                            content = c.get("text", "")[:300]
                            break
                    if content:
                        lines.append(f"[{i}] {role.upper()}: {content}")

        return "\n".join(lines)

    @weave.op
    async def score(
        self,
        output: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Run agent with Path Pack and score the trajectory reconstruction.

        Args:
            output: The ZatherModel output containing:
                - path_pack: The generated Path Pack markdown
                - session_file: Original session file path
                - target_cwd: Working directory for agent
                - session_name: Name for this session

        Returns:
            Dictionary with scores and reasoning.
        """
        import anthropic

        path_pack = output.get("path_pack", "")
        original_session_file = output.get("session_file", "")
        target_cwd = output.get("target_cwd", "")
        session_name = output.get("session_name", "unnamed")

        # Validate inputs
        if not path_pack:
            return {
                "overall_score": 0.0,
                "reasoning": "No path pack generated",
                "agent_error": "No path pack to run",
            }

        if not target_cwd or not Path(target_cwd).exists():
            return {
                "overall_score": 0.0,
                "reasoning": f"Target directory does not exist: {target_cwd}",
                "agent_error": "Invalid target_cwd",
            }

        # Step 1: Run the agent with the Path Pack
        runner = AgentRunner(
            agent=self.agent,
            model=self.agent_model,
            timeout_seconds=self.agent_timeout,
            sandbox=self.agent_sandbox,
        )

        capture_dir = Path(original_session_file).parent / "runs" / session_name

        run_result = runner.run(
            path_pack=path_pack,
            target_cwd=target_cwd,
            capture_dir=str(capture_dir),
        )

        # Check if agent ran successfully
        if run_result.error or not run_result.session_file:
            return {
                "overall_score": 0.0,
                "reasoning": f"Agent failed to run: {run_result.error}",
                "agent_error": run_result.error,
                "agent_exit_code": run_result.exit_code,
                "agent_duration": run_result.duration_seconds,
            }

        # Step 2: Format trajectories for the judge
        original_traj = self._format_trajectory_for_judge(original_session_file)
        reconstructed_traj = self._format_trajectory_for_judge(run_result.session_file)

        original_traj = self._truncate_trajectory(original_traj)
        reconstructed_traj = self._truncate_trajectory(reconstructed_traj)

        # Step 3: LLM judge compares trajectories
        prompt = PATH_RECONSTRUCTION_PROMPT.format(
            original_trajectory=original_traj,
            reconstructed_trajectory=reconstructed_traj,
        )

        client = anthropic.AsyncAnthropic()

        response = await client.messages.create(
            model=self.judge_model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        # Step 4: Compute structural metrics
        try:
            original_summary = extract_trajectory_summary(original_session_file)
            reconstructed_summary = extract_trajectory_summary(run_result.session_file)
            metrics = self._compute_metrics(original_summary, reconstructed_summary)
        except Exception:
            metrics = {}

        try:
            result = self._parse_json_response(response_text)
            return {
                "overall_score": float(result.get("overall_score", 0)) / 10.0,
                "exploration_strategy_score": float(
                    result.get("exploration_strategy_score", 0)
                )
                / 10.0,
                "key_files_score": float(result.get("key_files_score", 0)) / 10.0,
                "tools_commands_score": float(result.get("tools_commands_score", 0))
                / 10.0,
                "context_quality_score": float(result.get("context_quality_score", 0))
                / 10.0,
                "efficiency_score": float(result.get("efficiency_score", 0)) / 10.0,
                "reasoning": result.get("reasoning", ""),
                "strengths": result.get("strengths", []),
                "weaknesses": result.get("weaknesses", []),
                "agent_duration": run_result.duration_seconds,
                "reconstructed_session_file": run_result.session_file,
                **metrics,
            }
        except Exception as e:
            return {
                "overall_score": 0.0,
                "reasoning": f"Failed to parse judge response: {e}\nRaw: {response_text[:500]}",
                "agent_duration": run_result.duration_seconds,
                "reconstructed_session_file": run_result.session_file,
                **metrics,
            }

    def _parse_json_response(self, text: str) -> dict:
        """Extract and parse JSON from the response text."""
        import re

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not parse JSON from response")

    def _compute_metrics(
        self, original_summary: dict[str, Any], reconstructed_summary: dict[str, Any]
    ) -> dict[str, Any]:
        """Compute structural metrics comparing original and reconstructed sessions."""
        # Tool count ratio
        orig_tools = original_summary["num_tool_calls"]
        recon_tools = reconstructed_summary["num_tool_calls"]
        if orig_tools > 0:
            tool_count_ratio = min(recon_tools, orig_tools) / max(
                recon_tools, orig_tools
            )
        else:
            tool_count_ratio = 1.0 if recon_tools == 0 else 0.0

        # Token efficiency
        orig_tokens = original_summary["total_tokens"]
        recon_tokens = reconstructed_summary["total_tokens"]
        if orig_tokens > 0:
            token_efficiency = orig_tokens / max(recon_tokens, 1)
            token_efficiency = min(token_efficiency, 2.0)
        else:
            token_efficiency = 1.0

        # Tool type overlap (Jaccard)
        orig_tool_types = set(original_summary["tool_types"].keys())
        recon_tool_types = set(reconstructed_summary["tool_types"].keys())
        if orig_tool_types or recon_tool_types:
            intersection = orig_tool_types & recon_tool_types
            union = orig_tool_types | recon_tool_types
            tool_type_overlap = len(intersection) / len(union)
        else:
            tool_type_overlap = 1.0

        # Step ratio
        orig_steps = (
            original_summary["user_messages"] + original_summary["assistant_messages"]
        )
        recon_steps = (
            reconstructed_summary["user_messages"]
            + reconstructed_summary["assistant_messages"]
        )
        if orig_steps > 0:
            step_ratio = min(recon_steps, orig_steps) / max(recon_steps, orig_steps)
        else:
            step_ratio = 1.0 if recon_steps == 0 else 0.0

        return {
            "tool_count_ratio": tool_count_ratio,
            "tool_type_overlap": tool_type_overlap,
            "token_efficiency": token_efficiency,
            "step_ratio": step_ratio,
            "original_tool_calls": orig_tools,
            "reconstructed_tool_calls": recon_tools,
            "original_tokens": orig_tokens,
            "reconstructed_tokens": recon_tokens,
        }


class PathPackQualityScorer(weave.Scorer):
    """
    Standalone scorer that evaluates the quality of a Path Pack document
    without running an agent.

    This is the "quick" evaluation - just judges the Path Pack itself.
    Useful for fast iteration on Path Pack generation.
    """

    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 2048

    QUALITY_PROMPT: ClassVar[
        str
    ] = """Evaluate the quality of this Path Pack document for teaching an AI agent how to explore a codebase.

## Path Pack Document
```markdown
{path_pack}
```

## Original Session Trajectory (for reference)
```
{original_trajectory}
```

Rate the Path Pack on:
1. **Clarity** (0-10): Are instructions clear and unambiguous?
2. **Completeness** (0-10): Does it capture the key exploration steps?
3. **Actionability** (0-10): Can an agent directly follow these instructions?
4. **Insight Capture** (0-10): Does it convey the "why" behind steps?
5. **Efficiency** (0-10): Is it concise without losing important details?

Respond with JSON:
{{
    "clarity_score": <0-10>,
    "completeness_score": <0-10>,
    "actionability_score": <0-10>,
    "insight_capture_score": <0-10>,
    "efficiency_score": <0-10>,
    "overall_score": <0-10>,
    "reasoning": "<explanation>"
}}
"""

    @weave.op
    async def score(
        self,
        output: dict[str, Any],
    ) -> dict[str, Any]:
        """Score the quality of a Path Pack document."""
        import anthropic

        path_pack = output.get("path_pack", "")
        session_file = output.get("session_file", "")

        if not path_pack:
            return {
                "overall_score": 0.0,
                "reasoning": "No path pack generated",
            }

        # Get original trajectory for context
        events = load_session_events(session_file)

        # Simple trajectory summary
        traj_lines = []
        for i, event in enumerate(events[:100]):
            event_type = event.get("type")
            payload = event.get("payload", {})
            if event_type == "event_msg" and payload.get("type") == "user_message":
                traj_lines.append(f"USER: {payload.get('message', '')[:200]}")
            elif (
                event_type == "response_item" and payload.get("type") == "function_call"
            ):
                traj_lines.append(f"TOOL: {payload.get('name', '')}(...)")

        original_traj = "\n".join(traj_lines[:50])

        prompt = self.QUALITY_PROMPT.format(
            path_pack=path_pack[:10000],
            original_trajectory=original_traj,
        )

        client = anthropic.AsyncAnthropic()

        response = await client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            import re

            text = response.content[0].text
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "overall_score": float(result.get("overall_score", 0)) / 10.0,
                    "clarity_score": float(result.get("clarity_score", 0)) / 10.0,
                    "completeness_score": float(result.get("completeness_score", 0))
                    / 10.0,
                    "actionability_score": float(result.get("actionability_score", 0))
                    / 10.0,
                    "insight_capture_score": float(
                        result.get("insight_capture_score", 0)
                    )
                    / 10.0,
                    "efficiency_score": float(result.get("efficiency_score", 0)) / 10.0,
                    "reasoning": result.get("reasoning", ""),
                }
        except Exception:
            pass

        return {
            "overall_score": 0.0,
            "reasoning": "Failed to parse response",
        }
