# Path Pack: Build Mental Model of the WBAL Agent Framework

## Goal
Guide an agent to explore the WBAL repository so it gains the same working understanding the developer obtained: the core primitives (Agent / Environment / LM), how tools are discovered and formatted, example entry points, where tests exercise behavior, and the main pain points (docs/examples drift, tracked build artifacts, bundle/run contract).

## Prerequisites
- A local clone of the repository (repo root). Example workdir used in the trajectory: /Users/<you>/personal/wbal
- Python virtualenv available if you want to run tests (.venv exists in this repo).
- Read-only access to run shell commands to inspect files.
- Do not assume exact line numbers; search for symbol names and file paths listed below.

## Path Steps

### Step 1: Inventory top-level files and key manifests
**Action**: run
**Target**: ls -la (repo root) and cat pyproject.toml
**Purpose**: establish the package metadata, entrypoints, and high-level file layout so you know where to look for code, examples, and tests.
**Record**: Note package name/version and scripts (wbal-chat / wbal-poll), Python requirement (pyproject.toml 'requires-python'), and presence of dist/, .venv/, tests/, examples/.

### Step 2: Gather the public exports and package overview
**Action**: read
**Target**: wbal/__init__.py
**Purpose**: learn the public API surface the project intends to expose (core classes, helper functions, constants).
**Record**: List the exported core classes (WBALObject, LM, Environment, Agent, OpenAIWBAgent, ExitableAgent) and helper functions/decorators (tool, weaveTool, get_tools, etc.).

### Step 3: Understand the WBALObject base
**Action**: read
**Target**: wbal/object.py
**Purpose**: understand the common base behavior (observe(), setup(sandbox)) used by Agents, LMs, and Environments; note sandbox interface dependency and default behaviors/warnings.
**Record**: WBALObject is a Pydantic BaseModel providing observe() abstract method and an async setup(sandbox) hook. Sandbox interface is imported if available or falls back to sandbox_stub.

### Step 4: Inspect the Agent orchestration loop
**Action**: read
**Target**: wbal/agent.py
**Purpose**: map the perceive → invoke → do loop, how messages and step counts are tracked, how tools are discovered and executed, and stopCondition / maxSteps behavior.
**Record**: Agent implements step/perceive/invoke/do pattern; uses helper functions to get tools and format OpenAI-style tool calls; default maxSteps and stopCondition semantics.

### Step 5: Inspect Environment base and stateful variant
**Action**: read
**Target**: wbal/environment.py and wbal/environments/data_env.py
**Purpose**: learn how environments provide task/context and tools, plus how DataEnv persists notes/observations and manages a working_directory for state.
**Record**: Environment holds task/env strings and output_handler; DataEnv implements persistence helpers, default state schema (notes/observations/metadata) and working_directory behavior.

### Step 6: Review specialized environments
**Action**: read
**Target**: wbal/environments/chat_env.py and wbal/environments/poll_env.py
**Purpose**: see chat and poll behaviors built on DataEnv: chat can wait for user input; PollEnv adds write tools (store_note, delete_note, add_observation).
**Record**: ChatEnv adds chat() weaveTool that can block for input; PollEnv provides persistence-affecting tools.

### Step 7: Learn the LM abstraction and OpenAI wiring
**Action**: read
**Target**: wbal/lm.py and wbal/agents/openai_agent.py
**Purpose**: understand LM.invoke() contract, the GPT5Large/GPT5MiniTester reference implementations, and how OpenAIResponses-style parsing and reasoning extraction are handled by the OpenAIWBAgent.
**Record**: LM is abstract with invoke(messages, tools, mcp_servers). GPT5Large wraps OpenAI client; OpenAIWBAgent contains parsing helpers (extract_message_text, extract_reasoning_summary) and code to format tool calls/results.

### Step 8: Inspect helper utilities for tools and timeouts
**Action**: read
**Target**: wbal/helper.py
**Purpose**: find how methods are converted into tool schemas, how tool decorators (tool, weaveTool) work, constants for OpenAI 'function_call' formats, and tool_timeout context manager.
**Record**: helper defines TOOL_TYPE_FUNCTION / TOOL_CALL_TYPE / TOOL_RESULT_TYPE; extract_tool_schema, to_openai_tool, to_anthropic_tool, format_openai_tool_response; tool_timeout raises ToolTimeoutError.

### Step 9: Explore mixins and additional utilities
**Action**: read
**Target**: wbal/mixins.py and wbal/sandboxer.py
**Purpose**: learn about optional agent mixins (ExitableAgent) and sandbox helpers for starting / wiring objects to sandbox; note sync/async bridging utilities.
**Record**: ExitableAgent adds exit() tool and stop condition handling; sandboxer.setup_objects runs setup which may be async (uses asyncio.run where necessary) and start_sandbox spins an event loop in a thread.

### Step 10: List package modules and example entrypoints
**Action**: run/read
**Target**: find wbal package files (find wbal -maxdepth 2 -type f) and read wbal/scripts/chat.py and wbal/scripts/poll.py
**Purpose**: identify CLI entrypoints and how they instantiate agents/envs (OpenAIWBAgent with ChatEnv/PollEnv) and parse args for project/org/working-dir.
**Record**: CLI scripts create ChatEnv or PollEnv, set env string with org/project, then construct OpenAIWBAgent(env=env) and call agent.run(...).

### Step 11: Read README and developer/user docs
**Action**: read
**Target**: README.md, DEVELOPER.md, USER.md, Agent_Instructions.md, STATE.md
**Purpose**: capture the intended quickstart, design notes, testing commands, and documented primitives—compare with actual code to spot drift.
**Record**: README shows quickstart using weave.init and a sample Agent; DEVELOPER.md lists architecture and test commands (uv run pytest); USER.md documents method-level expectations (observe(), perceive(), invoke(), do()).

### Step 12: Inventory examples and tests
**Action**: run/read
**Target**: find examples/* and tests/*; open examples/simple_example.py and examples/story_summarizer.py; open tests/test_*.py
**Purpose**: learn how examples illustrate usage and what tests assert about behavior; confirm which tests pass/fail in a controlled environment.
**Record**: Examples use weaveTool and sandbox usage; story_summarizer calls weave.init at import time (note side effect). Tests mostly pass locally with .venv pytest, but tests for story_summarizer may fail due to drift (missing methods or import-time side effects).

### Step 13: Run tests (optional, if env available)
**Action**: run
**Target**: .venv/bin/pytest -q (or pytest -q if in active venv)
**Purpose**: validate current library behavior and capture failing tests to prioritize fixes.
**Record**: Running tests in the referenced environment showed most tests pass; tests under tests/test_story_summarizer.py failed (get_memory and other story-agent specifics). Note: pytest must be invoked from repo venv to match dependencies.

### Step 14: Check packaging / dist artifacts and tracked files
**Action**: read/run
**Target**: ls -la dist/ and git ls-files | rg patterns (pyc, __pycache__, .venv, dist)
**Purpose**: understand if build artifacts or envs are committed and whether repository hygiene is needed.
**Record**: dist contains built wheels (wbal-0.2.0, wbal-0.3.0). Repository tracks some __pycache__/.pyc files and lacks a root .gitignore — these are hygiene issues to propose cleaning.

### Step 15: Inspect WandBSwarm symlink (optional contextual integration)
**Action**: read
**Target**: ls -la WandBSwarm (in repo root if present) and open WandBSwarm/examples/hello_agent/run.sh and install.sh; read WandBSwarm/README.md
**Purpose**: learn the external launch contract used in the environment for agent bundles (install.sh/run.sh contract, layout expectations).
**Record**: WandBSwarm enforces run.sh (required) and install.sh (optional); workspace/task layout and env vars are used to stage agent bundles; this is a good model for an AgentBundle contract.

### Step 16: Note mismatches and pain points
**Action**: search/read
**Target**: examples/simple_example.py, examples/story_summarizer.py, README references to missing files (e.g., GRIFFIN_AGENT_INSTRUCTIONS.md)
**Purpose**: locate drift between docs/examples and code that will affect new contributors.
**Record**: simple_example imports outdated symbols (Env, OpenAIResponsesLM) not present in current exports; story_summarizer triggers weave.init at import time, causing noisy network/telemetry calls; missing GRIFFIN_AGENT_INSTRUCTIONS.md referenced in README.

### Step 17: Produce a short checklist for fixes / next steps
**Action**: synthesize (no file action)
**Target**: your notes
**Purpose**: produce a prioritized set of small changes to stabilize the repo for work: tests, docs, hygiene, bundle runner.
**Record**: Propose: add root .gitignore and remove tracked pyc files; update examples to match current API; avoid weave.init() at import-time in examples; fix failing story_summarizer tests (get_memory, message counts); consider adding wbal.bundle runner & simple CLI.

## Context Checkpoint
After completing all steps the agent should be able to:
- Explain WBAL's core primitives: WBALObject (base), Agent (perceive→invoke→do), Environment (tools/context), LM (invoke contract).
- Locate code implementing: tool discovery & schema (wbal/helper.py), agent loop (wbal/agent.py), OpenAI-specific parsing (wbal/agents/openai_agent.py), environment state (wbal/environments/*).
- Run the test-suite in the repository virtualenv and reason about failing tests (notably story_summarizer).
- Identify actionable hygiene issues: tracked __pycache__/.pyc files, missing .gitignore, examples/docs drift, and import-time side effects (weave.init).
- Describe a plausible next step plan: minimal fixes (tests/docs/examples), introduce an AgentBundle contract (require run.sh, optional install.sh), and add a single unified CLI (wbal run / wbal bundle-run) while keeping OpenAIWBAgent as the "batteries-included" reference.

## Stop Conditions
Pause and ask the user if any of these are true:
- You want me to modify files in the repo (e.g., add .gitignore, remove tracked pyc files, update examples). (Approve before writing.)
- You want me to implement a new CLI or bundle runner (this changes repo code and must be approved).
- You want me to run tests in an environment that requires network/API keys (OPENAI_API_KEY) — confirm credentials and permission.
- You prefer a different priority than: (1) repo hygiene & tests, (2) docs/examples sync, (3) bundle runner/CLI—ask which milestone to start with.