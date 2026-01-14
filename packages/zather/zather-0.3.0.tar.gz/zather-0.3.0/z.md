# Path Pack: Seeding WBAL Context for Factory Agents

## Goal
Build the mental model and repo-context an agent needs to integrate WBAL into the factory workspace so it can design or implement agents that use WBAL primitives (Agent, Environment, LM) and pick an integration approach (YAML manifests vs. Python classes).

## Prerequisites
- Repository cloned at the workspace root (where pyproject.toml lives).
- A shell with access to the repo (ls, find, sed/cat).
- Python environment available for inspection (not required to run code for this exploration).
- Reasonable file-read permissions in the repo.

## Path Steps

### Step 1: Inspect top-level layout

**Action**: read
**Target**: pyproject.toml (root) and ls -la at repo root
**Purpose**: Confirm workspace members, Python version, and initial guidance about which subpackages are intended for development (e.g., factory is a workspace member).
**Record**: Note workspace members and whether factory is declared; record required Python version and any top-level dependencies that affect factory.

### Step 2: Locate WBAL sources and docs

**Action**: search / read
**Target**: find directories named wbal and list their contents (wbal/, wbal/README.md, wbal/USER.md, wbal/DEVELOPER.md)
**Purpose**: Gather top-level project docs to understand WBAL's goals, quick start, and development notes. These docs explain the core primitives and usage patterns.
**Record**: Keep a short summary of WBAL’s stated primitives (Agent, Environment, LM) and install/quick-start notes (e.g., OPENAI_API_KEY requirement, uv/uv workspace hints).

### Step 3: Read WBAL core design summary

**Action**: read
**Target**: wbal/DEVELOPER.md or wbal/STATE.md
**Purpose**: Learn the architecture (WBALObject hierarchy, intention for sandboxing, async vs. sync design choices). This informs how agents should be wired and whether sandboxing is required.
**Record**: Note the class hierarchy and key design points: WBALObject → {LM, Environment, Agent}; sandbox stub availability; any ACP compatibility notes.

### Step 4: Inspect Agent base and orchestrator behavior

**Action**: read
**Target**: wbal/wbal/agent.py and wbal/wbal/agents/openai_agent.py
**Purpose**: Understand the perceive → invoke → do loop, stop conditions (exit tool, max steps), message handling, and how tool calls are extracted/executed.
**Record**: Summarize: how perceive builds messages, how invoke calls the LM, how do executes function_call outputs, and the agent's options for parallel tool execution and timeouts.

### Step 5: Inspect Environment base and environment flavors

**Action**: read
**Target**: wbal/wbal/environment.py, wbal/wbal/environments/data_env.py, poll_env.py, chat_env.py
**Purpose**: Learn what environments provide (task, env string, observe), the persisted DataEnv state model, PollEnv write tools (store_note/delete_note), and ChatEnv interactive behavior (chat() tool, waiting for input).
**Record**: Note state persistence behavior (working_directory, state file), available helper tools (chat store_note), and how env.observe() contributes to agent input.

### Step 6: Discover tool decorator and tool discovery mechanism

**Action**: read
**Target**: wbal/wbal/helper.py and wbal/wbal/tool_imports.py
**Purpose**: Learn how functions/methods become tools (decorators @tool / @weaveTool), how schemas and descriptions are extracted, and how external modules can be imported to provide tools. This is key to making env/agent capabilities available to the LLM.
**Record**: Note that tools are plain callables with a marker attribute (e.g., _is_tool) and that tool_imports can load bound callables from modules (import spec format module[:attr]).

### Step 7: Inspect LM interface and OpenAI implementation

**Action**: read
**Target**: wbal/wbal/lm.py
**Purpose**: Understand the LM abstraction (invoke signature), OpenAI Responses wrapper, and available test/scripted LMs for offline experiments. This helps choose an LM implementation for local development vs production.
**Record**: Note that OpenAIResponsesLM expects messages+tools and that scripted/test LMs exist for deterministic local testing.

### Step 8: Review helper tools (bash) and examples

**Action**: read
**Target**: wbal/wbal/tools/bash.py and examples (wbal/examples/*.py)
**Purpose**: See real tool examples (bash) and how examples bind env + agent and use tools safely (read-only guidance). Examples show best practices for building agents and environments.
**Record**: Record typical bash tool behavior (executes host commands, read-only recommended) and note example patterns like zagent_v1 orchestrator.

### Step 9: Inspect YAML manifest support and example agents

**Action**: read
**Target**: wbal/wbal/manifests.py and wbal/examples/agents/*.agent.yaml + prompt files
**Purpose**: Learn how YAML manifests define LM, env, tools, delegates, and how YamlAgent constructs agents from these manifests. Useful if you prefer declarative agent configs.
**Record**: Capture manifest fields: env.kind, lm.kind/model, tools lists, delegates mapping, max_steps, parallel_tool_calls — and how delegates point to other agent YAMLs.

### Step 10: Check bundling and WandB swarm runner support

**Action**: read
**Target**: wbal/wbal/bundle.py and wbal/examples/bundles/
**Purpose**: If agents will run in WandB bundles or in a swarm-like deployment, understand the required bundle layout (run.sh, optional install.sh) and validation logic.
**Record**: Note AgentBundleEntry requirements and run/install contract (env vars, run.sh required).

### Step 11: Inspect sandbox helpers and stubs

**Action**: read
**Target**: wbal/wbal/sandboxer.py and wbal/wbal/sandbox_stub.py
**Purpose**: Understand sandbox wiring and default stub behavior. If you plan to use sandboxing (containerized tool execution), know how to set up and how WBAL falls back to a stub when sandbox package is absent.
**Record**: Note setup_objects helper and start_sandbox behavior; sandbox stub defines ExecResult and the interface expected by WBAL objects.

### Step 12: Map relationship between factory and WBAL

**Action**: read
**Target**: factory/pyproject.toml and factory/README.md (if any), and root .pyproject.toml workspace settings
**Purpose**: Decide integration approach: vendor WBAL as a path dependency, add as workspace member, or install from PyPI. Also note factory currently has minimal structure (e.g., factory/f1/f1.py).
**Record**: Record current factory dependencies (none) and the chosen approach to reference wbal (e.g., path = "../wbal" in factory/pyproject or add wbal to workspace members).

### Step 13: Summarize key integration options

**Action**: record (synthesize)
**Target**: your notes from previous steps
**Purpose**: Produce a concise list of recommended starting integrations: (A) add wbal as local path dependency and use YAML manifests (fast), (B) import wbal as package and subclass OpenAIWBAgent/DataEnv in factory code (more flexible), (C) create bundles for WandBSwarm if deploying.
**Record**: For each option, note tradeoffs (YAML: quicker, declarative; Python: full control; Bundles: deployment-ready) and required dependency changes (openai, weave, pydantic, etc).

### Step 14: Locate examples and tests to copy patterns

**Action**: search / read
**Target**: wbal/tests/, wbal/examples/agents/* and zagent_v1.py
**Purpose**: Identify canonical patterns for agents, tools, and manifests to reuse inside factory (e.g., orchestrator + delegate pattern). Tests can also serve as small working snippets.
**Record**: Note example files to reference when implementing (orchestrator.agent.yaml, worker_* agent YAMLs, zagent_v1.py).

### Step 15: Produce next-steps checklist and questions for the user

**Action**: record / ask
**Target**: summarised notes and questions to present to the user
**Purpose**: Before implementing, confirm user's preferred integration approach, whether sandboxing or WandB bundle support is required, and which LM (OpenAI or scripted/test) to use for development.
**Record**: Prepare concise clarifying questions:
- YAML vs Python agents?
- Local path dependency vs PyPI install for wbal?
- Need for sandboxed execution / WandB bundles?
- Which LM and API keys (OpenAI) will be available?

## Context Checkpoint
After completing these steps the agent should understand:
- WBAL's core mental model: three primitives (Agent, Environment, LM) built on a WBALObject base and how they interact.
- How to define and expose tools via @tool / @weaveTool and how tools are discovered and bound from env and agent code or external modules.
- The behavior and lifecycle of the OpenAIWBAgent (perceive → invoke → do loop), including stop conditions (exit), message construction, handling function_call outputs, and optional parallel tool execution.
- Environment flavors (DataEnv, PollEnv, ChatEnv): what state they persist and which tools they expose.
- YAML manifest capabilities (YamlAgent): how to declare env, LM, tools, and delegates; where to find example manifests.
- Sandbox support: how WBAL optionally integrates with a sandbox or uses a stub.
- Integration choices for the factory project (path dependency vs pip, YAML vs subclassing, bundling for deployment) and the practical next steps to wire them together.

## Stop Conditions
Pause and ask the user for clarification when:
- They need a decision on integration approach: (A) use YAML manifests; (B) create Python agent subclasses in factory; or (C) both.
- They want to change project layout (add wbal as workspace member or add a path dependency in factory/pyproject.toml).
- They require production deployment constraints (must run in a sandbox or as WandB bundles).
- They need guidance on credentials (OpenAI API key) or which LM to use for development/testing.