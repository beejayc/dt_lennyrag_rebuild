---
name: repo-pdt-explainer
description: analyze a github repository from a product owner perspective. reverse engineer the product objective, target audience, user journey, and value proposition from the codebase. use when asked for a product breakdown, PO analysis, or to understand what a repo does as a product — not just technically.
---

Read the repository to understand the product intent, not just the implementation.

## Workflow

1. **Start with surface signals**
   - README, package name, folder names, route/endpoint names, UI copy, and config defaults.
   - These reveal intended users and product positioning before reading a single line of logic.

2. **Follow the user's journey**
   - Identify where a user enters the product (UI, CLI, API call, file input).
   - Trace the path from that entry point to the value delivered.
   - This is the core product loop.

3. **Infer the product goal from code, not marketing**
   - What problem does the main execution path actually solve?
   - What would a user be trying to accomplish when they open this?

4. **Identify the target user from evidence**
   - Look at: naming conventions, example data, documentation tone, input/output formats, required setup complexity.
   - Distinguish between the intended user and the likely actual user.

5. **Extract tech stack as supporting evidence**
   - List only the technologies that explain product decisions (e.g., "uses streaming because responses are long").
   - Skip dependencies that are implementation detail only.

## Required Output (Markdown)

### What This Product Does
2–3 sentences. Plain English. No code, no jargon.

### The Problem It Solves
1 paragraph. What pain or friction would cause someone to build and use this?

### Target Audience
1 paragraph. Who is this for? What's their workflow? Why does this tool fit them specifically?

### Core User Journey
Ordered steps showing how a user gets value from the product. Focus on actions and outcomes, not implementation.

### Value Proposition
1–2 sentences. What makes this worth using over an alternative?

### Tech Stack (Brief)
4–6 bullets. Each one: technology → why it was chosen for this product.

### Product Gaps & Open Questions
What's unfinished, unclear, or likely to frustrate the target user based on what's visible in the repo?

### One-Line Summary
One sentence. What is this product?

## Quality Bar
- Ground all claims in the repository. Mark inferences with "likely" or "appears to".
- Write for a product manager who will never read the code.
- Avoid architecture diagrams and developer setup steps — those belong in a separate technical writeup.