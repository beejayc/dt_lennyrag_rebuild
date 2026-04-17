---
name: repo-tech-explainer
description: reverse engineer a github repository from a technical lead perspective. extract tech stack, system design decisions, data flow, dependencies, and rebuild instructions. use when asked for a technical breakdown, engineering deep-dive, how to rebuild this, or how it was built — not a product summary.
---

Analyze the repository as a technical lead preparing to rebuild or onboard an engineering team.
Read actual code, configs, manifests, and scripts — do not rely on marketing docs.

## Workflow

1. **Read the manifests first**
   - `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml` — whichever applies.
   - These reveal the canonical dependency list, runtime version, and build toolchain.

2. **Map the entrypoints and execution paths**
   - Find `main`, `app`, `index`, `server`, `cli`, or equivalent entrypoints.
   - Trace the primary execution path end to end: input → processing → output/storage.
   - Identify any background jobs, workers, scheduled tasks, or event-driven flows separately.

3. **Identify system boundaries**
   - What external services, APIs, databases, queues, or file systems does this touch?
   - Where are credentials or config injected (env vars, config files, secrets managers)?

4. **Extract design decisions from code evidence**
   - Look for patterns: how is state managed, how are errors handled, how is auth done?
   - Note any non-obvious choices: custom implementations where libraries exist, deliberate simplifications, performance-sensitive paths.
   - Flag technical debt, workarounds, TODOs, and known rough edges.

5. **Assess testability and observability**
   - Is there a test suite? What kind (unit, integration, e2e)? How complete does it appear?
   - Is there logging, tracing, metrics instrumentation?

6. **Extract rebuild instructions from evidence**
   - Prefer explicit steps from README, Makefile, docker-compose, scripts.
   - For anything undocumented, infer the most likely setup and label it as inferred.

## Required Output (Markdown)

### System Summary
2–3 sentences. What this system does technically — runtime, primary language, execution model (server, CLI, pipeline, etc.).

### Tech Stack Breakdown
Table or structured list covering:
- **Language & Runtime** — version and why it matters
- **Frameworks** — web, CLI, data, ML, etc.
- **Data stores** — databases, caches, vector stores, file storage
- **Third-party APIs / services** — external dependencies the system calls
- **Dev & build tooling** — package manager, bundler, test runner, linter, formatter
- **Infrastructure / deployment** — Docker, cloud services, CI/CD if visible

### Data Flow
Ordered steps tracing how data moves through the system from entry to output.
Focus on transformations, storage writes, and side effects — not implementation detail.

### Key Technical Decisions
List 4–8 concrete decisions visible in the codebase. For each one:
- **What was decided** — the choice made
- **Evidence** — where this is visible in the repo
- **Tradeoff** — what was gained and what was given up

### Dependency Map
List direct runtime dependencies that carry architectural weight (not utilities).
For each: name → role in the system → why it's non-trivial to replace.

### Configuration & Environment
What environment variables, config files, or secrets must be present for the system to run?
List required vs. optional, and note any undocumented assumptions.

### Test Coverage Assessment
What tests exist, what they cover, and what is clearly untested. Be honest.

### How to Rebuild This
Ordered steps a new engineer would follow to go from zero to a running local instance.
Label inferred steps clearly. Include:
1. Prerequisites (language runtime, tools)
2. Dependency install
3. Environment setup
4. Database / service setup if needed
5. Run command
6. Verify it works

### Technical Debt & Known Gaps
List TODOs, FIXMEs, commented-out code, stub implementations, shallow error handling,
missing validation, or anything that signals incomplete or deferred work.

### One-Line Technical Summary
One sentence: what is this system, built with what, doing what.

## Quality Bar
- Every claim must be traceable to a file, config, or code pattern in the repo.
- Mark inferences with "likely", "appears to", or "inferred from [filename]".
- Write for a senior engineer who needs to rebuild or extend this system — not a manager.
- Skip marketing language. Be direct about limitations and rough edges.
- If the repo is thin, incomplete, or poorly structured, say so and explain what evidence supports that conclusion.