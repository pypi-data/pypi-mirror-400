# Path Pack: Discovering and Extending the MLE-bench Orchestrator

## Goal
Guide an agent through the same discovery process that builds understanding of the newly added orchestrator: its purpose, layout, config schema, Docker run/build semantics, tests, and how to extend it (build support and external backends like Daytona).

## Prerequisites
- A checked-out repository root (the one containing mle-bench and the new orchestrator package).
- A usable Python environment (project uses a workspace tool `uv`; tests are run with `uv run pytest`).
- Docker installed and accessible from the host (for building/running images).
- Host dataset cache present (macOS users: `~/Library/Caches/mle-bench/data/`; Linux: `~/.cache/mlebench`).
- (Optional) Daytona API access if you plan to implement Daytona backend functionality.

## Path Steps

### Step 1: Read the orchestrator specification

**Action**: read
**Target**: docs/orchestrator_spec.md
**Purpose**: Understand MVP goals, scope (Docker implemented, Modal/Daytona stubbed), non-goals, expected CLI and config features. This sets the design constraints and what the orchestrator should/shouldn't do.
**Record**: The orchestrator CLI is a single-run tool (python orchestrator/run.py --config <yaml>); image build automation is out of scope for the initial spec (later extended as optional).

### Step 2: Inspect repo root to locate new/changed files

**Action**: read | search
**Target**: repository root (ls), pyproject.toml, main.py
**Purpose**: Confirm workspace layout, check packaging tool usage (uv), and whether orchestrator already exists under repo root. Ensures you run commands in the right workspace.
**Record**: Workspace uses `uv` workspace; top-level pyproject references subpackages. main.py is simple. Orchestrator package may not be present initially.

### Step 3: Locate orchestrator package and examples

**Action**: read | search
**Target**: orchestrator/ (ls, open files), orchestrator/examples/*.yaml
**Purpose**: Find orchestrator modules (config, run CLI, backends, utils) and example YAMLs that show how to run builds or runs. This builds familiarity with file-level organization and entrypoints.
**Record**: Key modules: orchestrator/run.py (CLI entry), orchestrator/config.py (dataclasses and normalization), orchestrator/backends/docker_backend.py (implemented), orchestrator/backends/{modal_backend.py, daytona_backend.py} (stubs).

### Step 4: Open CLI entry to see top-level flow

**Action**: read
**Target**: orchestrator/run.py
**Purpose**: Learn the runtime sequence: load config, normalize/validate, optionally build image, dispatch to chosen backend, ensure workspace existence, and stream logs. This tells you how config informs execution.
**Record**: run.py reads RunConfig; if config.build present, it triggers build backend; backend dispatch based on config.backend (docker|modal|daytona).

### Step 5: Inspect config parsing and normalization

**Action**: read
**Target**: orchestrator/config.py
**Purpose**: Understand config schema, allowed fields, expansion/variable interpolation, default paths, mount/env format, and how resources/timeouts are represented. This is crucial for producing valid YAML and for tests.
**Record**: Config defines BuildConfig (context/dockerfile/platform/build_args/etc) and RunConfig (agent_image, command, workspace, mounts, env, resources, backend, build). Values are normalized and expanded (tilde/vars to absolute paths).

### Step 6: Review Docker backend implementation

**Action**: read
**Target**: orchestrator/backends/docker_backend.py
**Purpose**: Determine how docker run command and mounts/envs/resources are constructed, and how logs/submission artifacts are handled. Also inspect helpers for streaming subprocess outputs. This tells you exactly what Docker invocation the orchestrator will perform.
**Record**: Docker backend builds a docker run command with workspace host→container bind, cache/Kaggle mounts, environment variables, resources (gpus/cpus/memory) and then runs via a streaming subprocess helper.

### Step 7: Inspect build backend (new build support)

**Action**: read
**Target**: orchestrator/backends/build.py (or build logic in run.py)
**Purpose**: Learn the optional build step semantics: which docker build flags are supported (context, dockerfile, platform, build_args), whether pull/caching is allowed, and how the orchestrator marks failure/stop. This explains how the orchestrator can produce an agent image before running.
**Record**: If build block exists in YAML, run executes `docker build --platform ... --file ... --tag <agent_image> ...` before docker run. No registry push in MVP.

### Step 8: Check Modal/Daytona stubs and their contract

**Action**: read
**Target**: orchestrator/backends/modal_backend.py and orchestrator/backends/daytona_backend.py
**Purpose**: Understand the expected interface for alternative backends: function signature (takes RunConfig and logger), expected responsibilities (image reference resolution, mounts, resource mapping, log streaming). This informs how to implement a real backend later.
**Record**: Stubs log "not implemented" and include docstrings describing required integration points: create job/sandbox, map mounts/env/resources, stream logs to workspace.

### Step 9: Find tests relevant to the orchestrator

**Action**: list / read
**Target**: tests/test_docker_backend.py and tests/conftest.py (if present)
**Purpose**: See which parts of orchestrator are unit-tested (command construction, env/mount resolution, build invocation mocks). Tests show expected behavior and help you validate local changes.
**Record**: Tests mock subprocess or runners to verify command assembly and that config expansion/normalization works. Running only these focused tests avoids unrelated heavy dataset tests.

### Step 10: Run focused tests locally

**Action**: run
**Target**: uv run pytest tests/test_docker_backend.py -q
**Purpose**: Execute only orchestrator-specific tests to quickly verify behavior without triggering the larger mle-bench suite (which downloads datasets). Ensures orchestrator code is importable and functions as expected.
**Record**: Tests pass (e.g., 3-4 passed). If pytest package isn't available directly, use `.venv/bin/python -m pytest` or `uv run pytest`.

### Step 11: Validate Python import path for tests

**Action**: run | read
**Target**: uv run python -c "import sys; print(sys.path)" and tests/conftest.py
**Purpose**: If tests fail with ModuleNotFoundError for orchestrator, confirm test runner rootdir and sys.path; ensure top-level tests add repo root to sys.path (conftest.py). This resolves import resolution issues when pytest changes working directory.
**Record**: Add a top-level tests/conftest.py that prepends repo root to sys.path if needed.

### Step 12: Inspect mle-bench expectations (data & outputs)

**Action**: read
**Target**: mle-bench/README.md and mle-bench/agents/README.md and run_agent.py
**Purpose**: Learn where datasets live, how agents are expected to produce outputs (submission CSVs), the grader flow, and the paths conventions so agent images can be written accordingly. This shows how agent code should read data and where to write outputs.
**Record**: Data cache: host `~/.cache/mlebench` (or macOS `~/Library/Caches/mle-bench/data/`) mounted into container at `/root/.cache/mlebench`. Agents output CSVs into workspace mount (e.g., `/home/workspace/output`), then `mlebench grade` or sample grader inspects those files.

### Step 13: Explore the WBAL agent pattern (for agent authoring)

**Action**: read
**Target**: CodeCurious/lib/wbal examples and Agent/Environment classes (e.g., lib/wbal/examples/simple_example.py, lib/wbal/wbal/agent.py, lib/wbal/USER.md)
**Purpose**: Understand how an agent is structured in the WBAL framework (Agent/Environment classes, @weaveTool tools, LM classes GPT5Large/GPT5MiniTester, perceive-invoke-do loop). Use this pattern when authoring agent code for images to be run by the orchestrator.
**Record**: Typical agent defines Environment (task/env), Agent subclass with LM (GPT5Large), override perceive to seed messages and run() invokes the LLM; no tools is a minimal pattern.

### Step 14: Inspect or create an example minimal agent

**Action**: read / create
**Target**: zagent_1/agent.py and Dockerfile.agent (in repo root)
**Purpose**: Verify how to package an agent into an image that the orchestrator can run. The Dockerfile should base on mlebench-env, install any dependencies (e.g., wbal via pip), copy minimal agent code, and set a default CMD. This provides a template for users.
**Record**: Dockerfile.agent example includes optional GITHUB_TOKEN build-arg to install private wbal via HTTPS; zagent_1/agent.py provides a MinimalMLEBenchAgent that uses GPT5Large and writes outputs into workspace path.

### Step 15: Create an orchestrator run YAML for a concrete competition

**Action**: read / create
**Target**: orchestrator/examples/aerial-cactus.yaml (or new file)
**Purpose**: Provide a concrete example config for running the orchestrator on a host cache layout (macOS or Linux). Include agent_image, optional build block, workspace paths, mounts for cache and Kaggle creds, env, resources, timeout, backend. This is the actual input the CLI consumes.
**Record**: Example YAML mounts `~/Library/Caches/mle-bench` → `/root/.cache/mlebench` (macOS), `~/.kaggle` → `/root/.kaggle`, workspace `./runs/${run_id}` → `/home/workspace`, agent_image `my-agent:latest`. Build block optional.

### Step 16: Build and test an agent image locally

**Action**: run
**Target**: docker build --platform=linux/amd64 --pull=false -f Dockerfile.agent -t my-agent:latest .
**Purpose**: Ensure image builds successfully in your local environment; be mindful of platform mismatches on macOS (use --platform=linux/amd64 and --pull=false to prefer local images). This step ensures the orchestrator can run your agent_image locally.
**Record**: If base image `mlebench-env:latest` exists locally but is amd64, forcing platform and disabling pull avoids Docker trying to fetch an arm64 manifest.

### Step 17: Run the orchestrator with the example YAML

**Action**: run
**Target**: uv run python orchestrator/run.py --config orchestrator/examples/aerial-cactus.yaml
**Purpose**: Execute the full flow: optional build (if present), then the backend run (docker), streaming logs and writing outputs to workspace. This validates end-to-end behavior for a single run.
**Record**: After run, check workspace dir for stdout.log, stderr.log, and submission CSV; use `mlebench grade` to score if desired.

### Step 18: Investigate Daytona docs for backend implementation

**Action**: run | read
**Target**: Daytona docs pages (https://www.daytona.io/docs/en/python-sdk/sync/daytona/) and process docs (`process.md`)
**Purpose**: Learn how the Daytona Python SDK creates sandboxes, maps volumes, runs commands via Process.exec, and returns execution results. This guides implementing an actual daytona_backend implementation rather than a stub.
**Record**: Key constructs: Daytona() client that reads API key from env or config, Daytona.create() for sandboxes, Process.exec(command, cwd, env, timeout) to run commands, and methods to manage volumes/snapshots.

### Step 19: Plan extension for Daytona backend

**Action**: read / plan
**Target**: orchestrator/backends/daytona_backend.py and Daytona SDK docs
**Purpose**: Define a minimal implementation strategy: create sandbox from agent image, translate mounts to Daytona volumes, set environment variables, run command via Process.exec, poll/stream logs to workspace, and cleanup. Note dependency and credential handling (DAYTONA_API_KEY, DAYTONA_API_URL).
**Record**: Daytona backend will be optional and require installing the Daytona SDK; initial MVP can return NotImplemented but include clear hooks and docstrings.

### Step 20: Stop and validate context before major changes

**Action**: read / ask
**Target**: Current repo state and tests
**Purpose**: Before making further changes (e.g., implementing Daytona backend or adding packaging/CI), ensure the agent has validated requirements (Docker, uv environment), that tests pass locally for orchestrator, and confirm desired build semantics (local-only build, push support later).
**Record**: Focused orchestrator tests pass; full mle-bench test suite downloads datasets and will fail without Kaggle credentials. Decide on next priorities (Daytona, Modal, build caching or registry push).

## Context Checkpoint
After completing all steps, the agent should understand:
- The orchestrator's purpose: run a single agent run from a YAML config, for Docker (implemented) and stubs for Modal/Daytona.
- Where to find and edit code: orchestrator/run.py (entrypoint), orchestrator/config.py (schema/validation), orchestrator/backends/docker_backend.py (run semantics), and orchestrator/backends/build.py (optional build step).
- How to author an agent: package code into a Docker image (FROM mlebench-env or custom), ensure it reads competition data from the mounted cache (/root/.cache/mlebench) and writes outputs/submission CSVs to the mounted workspace path (/home/workspace), or mount code into the container for iteration.
- How to write a config YAML that optionally builds an image (build block) and then runs it with correct mounts/envs/resources.
- Practical debugging tips: run focused tests (uv run pytest tests/test_docker_backend.py), and when building images on macOS, prefer `--platform=linux/amd64 --pull=false` to reuse local amd64 images.
- Daytona integration is feasible via their Python SDK (Daytona.create, Process.exec) but requires adding the SDK and handling credentials.

## Stop Conditions
Pause and ask the user when any of the following apply:
- You want the orchestrator to push built images to a registry (the current build implementation is local-only).
- You want full Modal or Daytona backends implemented now (requires external dependencies and credentials).
- You want multi-run scheduling, retries, or leaderboard aggregation added (out of MVP scope).
- You want CI/packaging rules changed (pyproject or workspace packaging adjustments).
- You need the orchestrator to run under containerized CI (i.e., make orchestrator itself an image) rather than as a host-side CLI.

If any of the above are desired, ask for explicit confirmation, credentials (e.g., Daytona API key, registry credentials), and exact UX expectations (push policy, caching behavior, platform targets).