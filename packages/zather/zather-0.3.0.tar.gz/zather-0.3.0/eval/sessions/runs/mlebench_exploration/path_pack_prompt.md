# Path Pack: Building mental context for mlebench_z orchestrator & agents

## Goal
Guide an agent to explore the mlebench_z repository so it gains the same mental model as the original exploration: repository layout, orchestrator runtime contract, agent packaging issues (zagent_v1), Docker/Modal/Daytona backend behaviors, and decisions about "bake vs mount" for images and data.

## Prerequisites
- Repository cloned to a working directory (path like /path/to/mlebench_z).
- Python 3.13 (or the project's declared Python) available with basic shell utilities (bash, docker) where applicable.
- Access to file search tools (rg/grep, sed/cat) and ability to run the repository's CLI (uv run mlebench-run) locally.
- If reproducing Modal-specific behavior: modal SDK installed and Modal credentials configured (but the exploration can be done without Modal access).

## Path Steps

### Step 1: First-pass repo surface scan
**Action**: read  
**Target**: README.md, pyproject.toml, docs/orchestrator_spec.md  
**Purpose**: Establish top-level project intent, CLI entrypoint, and where orchestrator docs/spec live.  
**Record**: Note CLI entrypoint (project.scripts / mlebench-run → orchestrator.run:main), python requirement, and the orchestrator MVP description (YAML config example & expectations about mounts and dataset cache).

### Step 2: Inventory code layout
**Action**: run  
**Target**: list top-level and src paths (e.g., ls -la; find src/mlebench_z -maxdepth 3 -type f -name '*.py')  
**Purpose**: Find package root(s) and where orchestrator and agent code actually live on disk.  
**Record**: Confirm orchestrator lives in src/mlebench_z/orchestrator and agents live under src/mlebench_z/zagent_v1 and zagent_1; note vendor folder mle-bench/ presence.

### Step 3: Read orchestrator config/parsing
**Action**: read  
**Target**: src/mlebench_z/orchestrator/config.py  
**Purpose**: Understand the evaluation YAML schema (agent, tasks, workspace, mounts, env, resources, build).  
**Record**: Record dataclass names (EvaluationConfig, AgentConfig, BuildConfig, RunConfig) and semantics like BuildConfig fields and how env variables are expanded.

### Step 4: Read orchestrator runtime entrypoint
**Action**: read  
**Target**: src/mlebench_z/orchestrator/run.py  
**Purpose**: Learn how evaluations are executed, how per-task env is assembled, where agent code is mounted, and build-hook placement.  
**Record**: Note AGENT_MOUNT_PATH and TASK_MOUNT_PATH semantics, _make_env() keys injected (COMPETITION_ID, WORKSPACE, DATA_DIR, RUN_ID, TASK_DIR), and where build is invoked.

### Step 5: Inspect Docker backend implementation
**Action**: read  
**Target**: src/mlebench_z/orchestrator/backends/docker_backend.py and orchestrator/backends/build.py  
**Purpose**: See how docker run command is constructed, what mounts and env flags are used, and how Docker images are built.  
**Record**: Note build_docker_command() behavior, handling of cpus/memory/gpus, how mounts are formatted, and build_image() CLI (docker build command composition).

### Step 6: Inspect Modal and Daytona backends
**Action**: read  
**Target**: src/mlebench_z/orchestrator/backends/modal_backend.py and daytona_backend.py  
**Purpose**: Understand limitations/assumptions for non-local backends (Modal/Daytona) regarding host mounts and images.  
**Record**: Modal backend uses modal.Image.from_registry / Image.debian_slim with env secrets and requests A100 when resources.wants_gpu(); crucial: Modal backend does not bind-mount host paths—images must contain code/data or use Modal upload APIs. Daytona backend maps numeric resources and creates sandboxes remotely.

### Step 7: Confirm orchestrator tests & examples
**Action**: read  
**Target**: tests/test_docker_backend.py and examples/*.yaml  
**Purpose**: See the expected config patterns in tests and examples to validate what orchestrator expects in practice.  
**Record**: Note example agent blocks (agent_dir, install/run scripts, optional build block) and how tests mock loads/build behavior.

### Step 8: Read zagent_v1 implementation
**Action**: read  
**Target**: src/mlebench_z/zagent_v1/agent.py, src/mlebench_z/zagent_v1/run.sh, src/mlebench_z/zagent_v1/install.sh  
**Purpose**: Determine agent capabilities, expected env vars, install strategy, and import/package expectations.  
**Record**: Record that zagent_v1 is a WBAL-based agent exposing run_command and execute_codex tools (codex usage noted), runtime env var expectations (TASK_DIR, WORKSPACE, DATA_DIR, COMPETITION_ID, RUN_ID, MAX_STEPS), and install.sh uses network installs (wbal/codex) without pinned versions.

### Step 9: Verify packaging/path mismatches
**Action**: search & read  
**Target**: Dockerfile.agent and README references to agent_dir (examples)  
**Purpose**: Identify mismatches between Dockerfile and actual source layout (e.g., Dockerfile expects zagent_v1 at repo root vs actual src path) and how orchestrator mounts agent_dir.  
**Record**: Note the mismatch: examples use src/mlebench_z/zagent_v1 while Dockerfile.agent may expect a top-level zagent_v1; this causes import failures if mount vs package import isn't aligned.

### Step 10: Reproduce agent-import semantics
**Action**: run | read  
**Target**: Try ls of zagent_v1 at repo root and inspect how run.sh imports (attempt fallback imports)  
**Purpose**: Ensure agent run script will import correctly whether the agent directory is mounted as a package (zagent_v1) or as a flat folder (agent.py).  
**Record**: Record needed fix: run.sh should add CWD to PYTHONPATH and attempt both import zagent_v1.agent and import agent as fallback. If only the parent directory is mounted, imports succeed; otherwise, fallback needed.

### Step 11: Create a minimal test config directory
**Action**: run  
**Target**: make a test folder (e.g., ztest_jan5/) and write a YAML that targets Modal with resources.gpus: 1 and agent_dir referencing the package path used by orchestrator examples  
**Purpose**: Validate the orchestrator path expectations and to have a reproducible example for Modal runs.  
**Record**: Note that Modal requires the image to already contain agent code and task files (Modal does not mount host directories). For local Modal testing, you must push image to a registry Modal can access or use Modal's build-from-Dockerfile APIs.

### Step 12: Understand "bake vs mount" tradeoffs
**Action**: read & reason  
**Target**: docs/orchestrator_spec.md, Dockerfile.agent, modal backend, and textadv-aha's env_sandbox_modal.py (if available)  
**Purpose**: Form the design view: Docker mounts provide easy local iteration, but Modal sandboxes prefer baked images or explicit upload/volumes. Decide what the repo's UX should be (the original session concluded a preference for ALWAYS BAKE).  
**Record**: Record implications: baking means build step mandatory; mounts become legacy and should be discouraged; Modal requires either pushed images or Image.from_dockerfile/upload APIs.

### Step 13: Study an external Modal pattern (boss repo)
**Action**: read  
**Target**: provided repo copy (e.g., _tmp_/textadv-aha) focusing on env_sandbox_modal.py, run_eval.py, object_defs/envs_sandbox.yaml, and image-spec patterns  
**Purpose**: Extract useful Modal UX patterns: image spec abstraction, secrets by name, sandbox.create usage, and file open/exec semantics inside sandbox.  
**Record**: Note features to borrow: tag schemes (modal:///debian_slim, dockerfile:///...), modal.Secret.from_name usage, modal.Sandbox.exec/open, and snapshot/image-from-id flow.

### Step 14: Identify pragmatic fixes to implement
**Action**: read & plan  
**Target**: run.py and zagent_v1 run/install scripts, Dockerfile.agent, README  
**Purpose**: Decide minimal code changes required to make end-to-end runs easier (e.g., --build CLI flag, hardened run.sh import, simpler Dockerfile pip installs, documenting env vars).  
**Record**: Key actionable items: add --build flag to orchestrator.run to force image build, modify run.sh to adjust PYTHONPATH and fallback imports, update Dockerfile.agent to pip install wbal from PyPI (avoid broken GitHub subdir), add README for zagent_v1.

### Step 15: Validation checks
**Action**: run | read  
**Target**: git status, tests (optional), try uv run mlebench-run --config ztest_jan5/aerial-cactus-modal-a100.yaml --build (dry-run)  
**Purpose**: Ensure modifications do not break entrypoints and that build flow is invoked when requested.  
**Record**: Note any git changes that need commit and that Modal runs require published image accessible to Modal unless using modal.Image.from_dockerfile.

## Context Checkpoint
After completing all steps, the agent should understand:
- The repository structure: orchestrator code in src/mlebench_z/orchestrator, agents in src/mlebench_z/zagent_v1 and zagent_1, vendored mle-bench/ submodule.
- The orchestrator runtime contract (what env vars are injected, where agent code should live inside the container, how tasks are mounted or expected to be baked).
- Differences between backends:
  - Docker: supports host bind mounts (current default), builds images via docker build, good for local dev iteration.
  - Modal: does not support bind mounts in the current implementation; images must contain code/data or be built via Modal APIs (or pushed to registry). Modal can be used as a sandbox with modal.Sandbox.create and modal.Image builders.
  - Daytona: remote execution with resource wiring; similar constraints to Modal regarding images and mounts.
- The zagent_v1 agent specifics: WBAL-based agent, required env vars, risky codex behaviors, and packaging/import pitfalls.
- UX decision: "Always bake" (no mounts) model recommended for sandboxed backends (Modal/Daytona), with the orchestrator offering a --build flag or agent.build config so YAML is source of truth for builds.
- Short-term fixes to implement: hardened run.sh fallback imports, Dockerfile fixes for wbal install, --build flag to orchestrator.run, and documentation updates for zagent_v1.

## Stop Conditions
Pause and ask the user when any of the following are true:
- You want me to actually apply code patches or create commits (I have only guided discovery and suggested fixes).
- You want me to push built images to a registry or perform operations requiring network credentials/Modal credentials.
- You want to change the policy from "always bake" to a hybrid approach that preserves some mount behavior for development (need confirmation of preferred UX).
- You want me to run integration tests or execute Modal runs that require access to a Modal app or other secrets.

If you want, I can now:
- Produce concrete patch files for the fixes discussed (run.py --build flag, updated Dockerfile.agent, run.sh import fallback, new README for zagent_v1).
- Generate the Dockerfile and steps to build/push a registry image for Modal consumption.
- Implement Modal backend enhancements to support building from Dockerfile or uploading local directories into a modal.Image.