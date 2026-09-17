---
name: onboard
description: Use when starting work in a new or unfamiliar workspace. Routes to the correct entry point — prototype mode for a raw unvalidated idea, discovery for a cold-start spec, or codebase audit for an existing project. Triggered by /onboard or automatically on first substantive request in an empty or unfamiliar repo.
---

# Onboarding: Route to the Correct Entry Point

## Pre-check: template-repo guard (rule 22)

Before asking anything, check for a `.codestream-template` file at the repo root.

If it exists, **stop immediately**. This is the framework's own source repo, not a project built with it. Running the lifecycle here writes real project runtime state into `.codestream/` files that are tracked by git, and those files then ship inside every future project that copies the template.

Say so plainly, and offer only the two valid next steps:
1. Edit framework files here directly — no lifecycle, no `/discover`, no `/plan`.
2. Validate the change in a throwaway downstream project, then push it back with `/extract-template`.

Proceed anyway only if the user explicitly confirms they intend to dogfood the framework in this repo; treat that as session-scoped and do not carry it forward.

## Routing

Ask (once, single message):
> "How should we start this workspace?
> 1. **Raw idea, want something running fast** → `/prototype`
> 2. **Idea is clear enough to spec directly, no prototype needed** → `/discover`
> 3. **Existing codebase, formalize what's already here** → codebase audit"

## Routing
- **Option 1** → hand off to `/prototype` skill immediately.
- **Option 2** → hand off to `/discover` skill immediately.
- **Option 3** → spawn `codebase-mapper` subagent to audit the existing repo, then hand off to `roadmapper` (vertical-slice roadmap) and present it for the user's direct approval (the STATE 1 halt gate) — not via `/steer`.

## Note
Default to Option 1 whenever the user's framing sounds like an idea rather than a spec ("I want an app that...", "wouldn't it be cool if..."). Only skip straight to `/discover` if the user has already clearly validated the concept elsewhere or explicitly says they don't want a prototype.
