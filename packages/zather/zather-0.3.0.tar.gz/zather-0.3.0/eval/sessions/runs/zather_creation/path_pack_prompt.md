# Path Pack: Zather — Reconstructing an Agent's Context-Building Path

## Goal
Guide an agent to reconstruct the ordered, semantic context-acquisition steps (the "path") from a successful Claude Code / Codex session so the agent can reliably re-create the same mental model before doing unsupervised edits. This Path Pack teaches an agent what to read, search, and run (safely) and why each step matters.

## Prerequisites
- Repository cloned and available (root path used in examples: project root).
- Access to session logs:
  - Codex CLI sessions: ~/.codex/sessions/*.jsonl and ~/.codex/history.jsonl
  - Claude Code sessions: ~/.claude/projects/<project>/*.jsonl
- Python 3.11+ environment (or the project's configured Python).
- zather package (or run from source: cd zather; python3 -m zather.cli ...)
- Optional LLM client configured (OpenAI/GPT5Mini or other) if you want zather to generate final narrative; dry-run mode produces the Path Pack without calling an LLM.
- Read-only Git access to repo; ability to run safe read/search commands (no destructive commands by default).

## Path Steps

### Step 1: Identify the session to replay

**Action**: search  
**Target**: ~/.codex/sessions/ (or ~/.claude/projects/<project>/ for Claude) — list session files or read session meta lines  
**Purpose**: select the specific recorded session (session_id + cwd + timestamp) that defines the desired path.  
**Record**: Note session_id, session file path, session start time, and working directory (cwd). This determines base context and where to re-run reads.

### Step 2: Parse session metadata and event timeline

**Action**: read  
**Target**: first line / session_meta block of the session JSONL file (or session header in Claude JSONL)  
**Purpose**: extract session-level metadata: session_id, cli_version, originator, initial instructions, and declared cwd. This orients the replay.  
**Record**: session meta (session_id, cwd, git_branch/base_hash if present, model/provider, instructions). Use these to bind subsequent file reads to the right repo location.

### Step 3: Extract ordered trajectory events (user messages, assistant messages, tool calls, tool results)

**Action**: read  
**Target**: full session JSONL; filter for events of type message / response_item / tool_call / tool_result (or equivalent) and preserve chronological order  
**Purpose**: build an ordered, timestamped event stream (TrajectoryEvent) representing context acquisition: reads, searches, commands, and assistant observations.  
**Record**: For each event record: timestamp, actor (user/assistant/tool), brief text summary, referenced file paths, and any explicit command/tool outputs. Trim long outputs to a safe max (e.g., 200–500 chars) for notes.

### Step 4: Canonicalize "path events" into symbolic steps

**Action**: read + run (local safe commands like grep or git show)  
**Target**: transform events into normalized step types: READ(path | symbol), SEARCH(pattern), RUN(cmd) [safe only], EXTRACT(symbols/contract), NOTE(observation)  
**Purpose**: create an compact, reproducible recipe that describes the kind of action and conceptual goal of each step (not brittle line ranges).  
**Record**: produce a list of PathRecipe steps like:
- READ file X to find entrypoint or config (why: establishes runtime contract)
- SEARCH for symbol Y across repo (why: finds authoritative implementation)
- RUN safe command e.g., git rev-parse HEAD or git show <hash>:<file> (why: lock down state)
- EXTRACT function signatures / env vars (why: required invariants)

Note: prefer safe-run (git show, git ls-files, head, sed to show small snippet). DO NOT run arbitrary shell commands from logs without explicit human approval.

### Step 5: Resolve repository state targets (optional: base hash / commit)

**Action**: read + run (git)  
**Target**: git history in project root, git diff range referenced by session (get_first_commit_hash/get_git_diff style)  
**Purpose**: record the commit(s) or commit time range that the original session used. This helps the agent find the same file contents or at least detect drift.  
**Record**: base commit hash (or commit at session start). If present, include guidance to use a git worktree or `git show <hash>:<path>` to read the exact historical file snapshot.

### Step 6: For each READ step — create robust selectors

**Action**: read + search  
**Target**: file paths referred in events or discovered via search (README.md, module file, config files)  
**Purpose**: convert brittle references into robust selectors: "open module X (file path) and look for symbol/class/function named Y" or "open Dockerfile in directory Z and check entrypoint".  
**Record**: canonical selector: (file path, fallback search pattern). Example: README -> "search for 'Compaction Pipeline' or class Compactor in ccoy/ccoy/pipeline.py".

### Step 7: Build the Context Pack gate

**Action**: run (small checks) + generate artifact  
**Target**: create AgentArtifacts/context-pack.yaml or a small JSON/MD artifact containing: version, created_at, goal, route, entrypoints, discovered key facts (symbols, base_hash, runtime hints), and open questions  
**Purpose**: force the future agent to confirm it has assembled the same context before proceeding. This is a zethis convention and a required gate.  
**Record**: a minimal context-pack skeleton with fields:
- goal: one-sentence objective of session
- route: selected subsystem (e.g., "compaction/pipeline")
- entrypoints: commands or files to open first
- facts: files touched, symbols found, base_hash
- checks: small commands to verify (e.g., "git rev-parse --verify <hash>" or "python -c 'import modulename; print(modulename.__version__)'")

### Step 8: Encode stop/ask conditions and safety rules

**Action**: read + write (document)  
**Target**: produce explicit stop/ask rules to include in the Path Pack (e.g., ambiguities, missing files, divergent base hash)  
**Purpose**: ensure the agent pauses when key assumptions are missing, preventing destructive or misdirected edits.  
**Record**: rules such as:
- If a required file is missing, stop and ask.
- If git HEAD differs from recorded base hash by more than N commits in touched paths, stop and ask.
- Disallow running commands not in allowed list; if tool calls in transcript were destructive, require human approval.

### Step 9: Generate the Path Pack narrative (dry-run + LLM if desired)

**Action**: run (zather generator)  
**Target**: use the consolidated TrajectoryEvent list + Context Pack to generate the final Path Pack Markdown. Optionally call configured LLM with a prompt template (prompts/path_pack.yaml) to produce a zethis-style INTRO + ordered steps. Use dry-run mode if LLM not available.  
**Purpose**: convert structured, symbolic steps into a human- and agent-readable document that enforces the Context Pack gate and lists step-by-step reconstruction instructions with rationale.  
**Record**: the markdown file (e.g., AgentArtifacts/path-pack-<session_id>.md) containing Goal, Prereqs, Router, Context Pack gate, Path Steps (ordered, each with action/target/purpose/record), Stop Conditions, and Validation.

### Step 10: Validation checklist and smoke-run (no destructive changes)

**Action**: run (safety-first checks)  
**Target**: run the documented validation commands from the Context Pack and make sure all checks pass (e.g., git show works, files exist, key symbols present). Avoid any modifying commands.  
**Purpose**: give a concrete acceptance criterion so the agent (or human) can confirm the Path Pack maps to the current repo state.  
**Record**: a short Validation block with commands and expected outputs (e.g., "git show <hash>:path/to/file contains function foo()").

## Context Checkpoint
After completing all steps the agent should be able to:
- Name the exact session (session_id) and its cwd + start time.
- Describe the high-level goal and subsystem route the session targeted (e.g., compaction pipeline).
- Produce a Context Pack artifact listing entrypoints, key files, base_hash (if available), and a short list of extracted facts (symbols, commands, observed assumptions).
- Follow an ordered PathRecipe of safe actions (READ, SEARCH, RUN-safe, EXTRACT) that reconstructs the same conceptual context the original session used.
- Know explicit stop/ask conditions and validation commands to confirm correctness.

## Stop Conditions
Pause and ask the human if:
- A required file or path referenced by the Path Pack is missing in the repo.
- The recorded base_hash is not present locally or HEAD differs significantly in the touched files.
- The session contains tool calls that would execute arbitrary or privileged shell commands — require explicit human approval before replaying any RUN step beyond safe git/file reads.
- The agent cannot unambiguously identify an entrypoint symbol or module to start the reconstruction.
- The Context Pack Gate checks fail (any required verification command returns unexpected results).
- There is uncertainty about whether to aim to recreate the final patch (not required by Zather) vs. recreate the same mental model — clarify goal before proceeding.

---

Notes on best practices and why each step matters:
- Prefer symbolic selectors (symbols, filenames, command intent) over brittle line ranges to tolerate repo drift.
- Use git-based snapshots (git show <hash>:<path>) to anchor contents when available; otherwise include search patterns and acceptance checks.
- Keep the Context Pack small and verifiable: it is the “gate” that prevents wandering and hidden assumptions.
- Default to read/search/list operations. Only run commands that are read-only or explicitly safe (git, head, sed for small snippets). Any destructive or environment-changing command must be explicitly approved.
- Include acceptance criteria and concrete validation commands to make the Path Pack actionable and testable.

If you want, I can:
- Generate a Path Pack for a specific session from your codex/claude logs (give me the session_id or point at the session file).
- Scaffold the zather CLI command to produce AgentArtifacts/context-pack.yaml + path-pack.md for a selected session.
- Produce a sample Path Pack MD for the session we inspected (session_id: 019b9a7e-903f-7603-85b3-6f3499851312) in dry-run mode.