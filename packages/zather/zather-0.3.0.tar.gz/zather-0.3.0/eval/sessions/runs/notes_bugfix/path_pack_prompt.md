# Path Pack: Discover and Fix Incorrect Unique-Contacts Counts in iMessage Wrapped

## Goal
Guide an agent to explore the iMessage Wrapped repository, understand how contact statistics (unique contacts messaged vs unique contacts received from) are computed and displayed, and apply the correct fix so the two metrics reflect distinct counts.

## Prerequisites
- Repo cloned at the project root (contains README.md, ARCHITECTURE.md, web/, src/, desktop/).
- Python 3.10+ for reading package code.
- Node.js / npm for web app inspection if needed.
- Basic ability to run shell commands to open files (sed/cat/ls).
- Knowledge of where database/web code lives: Python package at src/imessage_wrapped and web app at web/.

## Path Steps

### Step 1: Read high-level docs to understand components

**Action**: read
**Target**: README.md and ARCHITECTURE.md at repo root
**Purpose**: establish the project structure and where CLI/desktop/web components live; get context for how statistics are exported, sanitized, uploaded, and displayed.
**Record**: The project has three distribution modes (CLI, Desktop, Web). The Python package builds exports and statistics; the Web app receives sanitized stats and shows dashboards.

### Step 2: Locate the Python package and list core modules

**Action**: read
**Target**: list directory src/imessage_wrapped
**Purpose**: find modules responsible for reading the iMessage DB, processing messages, analyzing statistics, exporting/loading, and permission checks.
**Record**: Key modules include db_reader.py, service.py (MessageProcessor), analyzer.py (StatisticsAnalyzer / RawStatisticsAnalyzer), models.py, exporter.py, loader.py, permissions.py, utils.py.

### Step 3: Inspect data models to know what a Conversation contains

**Action**: read
**Target**: src/imessage_wrapped/models.py
**Purpose**: learn fields (Conversation.participants, messages, message_count) and Message properties to understand what "unique contacts" might refer to.
**Record**: Conversation.message_count excludes context-only messages; Conversation has participants and messages list.

### Step 4: Find where contact-level statistics are computed

**Action**: search/read
**Target**: src/imessage_wrapped/analyzer.py (search for "contacts" / "top_sent_to" / "top_received_from" / contact-related helpers)
**Purpose**: identify the function(s) building the contacts section and the inputs used (filtered vs full conversations).
**Record**: Analyzer composes many analysis sections (volume, temporal, contacts, content). Contact metrics may be computed from either a filtered conversations set or the full set.

### Step 5: Confirm how conversation filtering is applied

**Action**: read
**Target**: src/imessage_wrapped/ghost/filters.py and ghost/metrics.py and usage in analyzer.py (look for apply_conversation_filters)
**Purpose**: understand which filters (minimum responses, received-to-sent ratio, etc.) the analyzer uses before some analyses and whether contacts are computed pre- or post-filtering.
**Record**: apply_conversation_filters returns a shallow copy with only passing conversations. Filters remove conversations that don't meet thresholds which can exclude one-sided conversations.

### Step 6: Inspect the contacts analysis implementation

**Action**: read
**Target**: the contacts-related functions in src/imessage_wrapped/analyzer.py (look for function names like _analyze_contacts or sections labeled "contacts")
**Purpose**: determine whether the contacts statistics use filtered conversations or the full dataset and how unique contact counts are computed.
**Record**: The bug symptom (identical unique contacts sent and received) often indicates both counts derived from the same filtered set; code may be using filtered conversations for contact counts.

### Step 7: Verify how the exporter/loader serialize contact stats

**Action**: read
**Target**: src/imessage_wrapped/exporter.py and src/imessage_wrapped/loader.py
**Purpose**: ensure the exported JSON contains distinct fields for top_sent_to, top_received_from, unique_contacts_messaged, unique_contacts_received_from and to confirm nothing is renamed or merged during serialization/load.
**Record**: Export includes conversations and statistics; loader reconstructs ExportData from JSONL.

### Step 8: Inspect the web UI consumer of contact stats

**Action**: read
**Target**: web/components/ContactsSection.js and StatCard.js
**Purpose**: check how the UI renders the two unique-contact metrics and whether it incorrectly maps or formats them (e.g., showing the same property twice).
**Record**: ContactsSection displays contacts.* fields; StatCard just prints label + value. If the Python export is correct, the UI should display distinct values.

### Step 9: Trace server-side sanitization and storage

**Action**: read
**Target**: web/app/api/upload/route.js and web/lib/privacy.js and web/lib/db.js
**Purpose**: verify that sanitization removes PII but keeps counts intact and that the saved JSON is not altering numeric fields. Also check DB schema expectations (wrapped_stats).
**Record**: sanitizeStatistics removes PII (sample_messages etc.) but should preserve counts; createWrapped stores JSON in wrapped_stats.data.

### Step 10: Reproduce the bug hypothesis by comparing filtered vs unfiltered counts

**Action**: run | read
**Target**: In analyzer.py locate the call sites that compute contacts stats. If convenient, run a small script (or run analyzer with a small export) to print both filtered and unfiltered unique-contact counts; otherwise reason from code paths.
**Purpose**: confirm whether contact stats were computed on filtered conversations and that filtering removes one-sided conversations causing both unique counts to match.
**Record**: If contacts were computed from filtered conversations, one-sided received contacts could be excluded, making sent and received unique counts match.

### Step 11: Prepare the fix: use full conversation set for contact counts

**Action**: edit (code change)
**Target**: src/imessage_wrapped/analyzer.py — change the contacts computation to use the full conversations mapping (not the filtered subset used for other analyses) when computing unique_contacts_messaged and unique_contacts_received_from and distribution/top lists.
**Purpose**: ensure unique-contact metrics reflect all conversations (including one-sided ones) while preserving filtering for analyses that need it (e.g., ghost detection).
**Record**: The fix is to pass the original conversations (or build contacts using unfiltered conversations) when computing contact aggregates.

### Step 12: Update any unused/incorrect parameters noticed

**Action**: edit
**Target**: analyzer.py functions that accept sent_messages/received_messages or similar but do not use them; remove or correctly use these parameters to avoid confusion.
**Purpose**: clean up dead parameters and ensure calls pass intended data (full conversations) explicitly.
**Record**: After change, calls to contact analysis must provide the full conversations mapping.

### Step 13: Verify serialization and UI mapping still line up

**Action**: read/run
**Target**: exporter.py to confirm exported field names and web/components/ContactsSection.js to confirm UI reads the same keys. Optionally produce a sample export file and load it in the web loader to ensure keys map.
**Purpose**: ensure no mismatch between exported field names and web UI expectations (e.g., unique_contacts_messaged vs unique_contacts_received_from).
**Record**: Exporter outputs top_sent_to, top_received_from, unique_contacts_messaged, unique_contacts_received_from; UI reads contacts.unique_contacts_messaged and contacts.unique_contacts_received_from (or value passed into components).

### Step 14: (Optional) Run a local smoke/packaging test if you changed packaging files

**Action**: run
**Target**: scripts/smoke-test.py or make test-install (optional)
**Purpose**: confirm pack builds and core functionality not broken by edits.
**Record**: Tests not required but recommended in CI.

### Step 15: Run quick local verification (web dev server + DB) — optional for end-to-end check

**Action**: run
**Target**: Start Postgres in Docker and set env, then run the dev server:
- Docker: docker run -d --name imessage-wrapped-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=imessage_wrapped -p 5432:5432 postgres:14
- Start web dev with DATABASE_URL:
DATABASE_URL="postgres://postgres:postgres@localhost:5432/imessage_wrapped" npm run dev --workspace web
**Purpose**: verify web app can initialize DB and show uploaded/saved wrapped pages.
**Record**: If server errors about missing password, ensure DATABASE_URL is set and .env.local exists with DATABASE_URL and BASE_URL.

## Context Checkpoint
After completing these steps the agent should understand:
- The architecture flow: Python package exports/analyzes messages, sanitizer/uploader sends anonymized stats to the web backend, web UI presents metrics.
- Where unique contact metrics are computed (analyzer.py contact analysis) and how conversation filtering can unintentionally exclude one-sided conversations.
- The root cause: contact stats were being computed from a filtered subset of conversations (used elsewhere for other analyses), causing symmetric counts.
- The correct fix: compute unique_contacts_messaged and unique_contacts_received_from from the full conversation set (unfiltered), while keeping filters for other analyses (ghosts, streaks).
- How data is serialized (exporter.py), sanitized (web/lib/privacy.js), and displayed (web/components/ContactsSection.js), so the full pipeline respects field names and values.

## Stop Conditions
Pause and ask the user when:
- You are unsure whether to change analyzer behavior globally (i.e., should contact metrics always use unfiltered conversations for all analyses?) — ask for desired product behavior.
- The repository structure differs (files moved or renamed) from paths listed above — ask for updated paths or a directory listing.
- You need permission to run or modify code in a protected environment (CI or production).
- You want me to implement the patch now (create PR/diff) versus only describing the change.