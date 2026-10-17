---
name: project-docs-manager
description: Manage a repository-wide documentation lifecycle built around Ideas, executable Plans, ProductFact, and Changelog. Use for initializing, auditing, reorganizing, or upgrading that system; implementing work from its Plan contract; or closing a delivery across Plan, facts, and history. Do not use for routine single-document edits or ordinary code-aligned ProductFact updates unless the user requests the lifecycle handoff.
---

# Project Docs Manager

Maintain the documentation system without replacing project-owned structure or content. Code and live configuration remain the final source of truth; repository instructions override this skill's defaults.

## Choose the operation

- **Audit or initialize:** inspect the current structure and add only missing foundations.
- **Plan work:** create, continue, or execute a living Plan under the repository's contract.
- **Close delivery:** synchronize the completed Plan, stable facts, Changelog, and archive.
- **Upgrade:** apply only migrations not recorded by the repository manifest.

For an ordinary edit to one existing document, follow the repository's own instructions directly and do not load this workflow.

## Load only what the operation needs

- Read [references/document-model.md](references/document-model.md) when choosing or adapting the Ideas / Plans / ProductFact / Changelog structure.
- Read [references/exec-plans.md](references/exec-plans.md) when creating or implementing a Plan.
- Read [references/migrations.md](references/migrations.md) only when initializing, reconstructing, or upgrading a versioned documentation system.

Do not load all references by default.

## Audit and initialize

Inspect before proposing changes:

```bash
python3 <skill-dir>/scripts/project_docs.py inspect --root <repo-root>
```

For initialization, preview first and apply only when creation or migration is authorized:

```bash
python3 <skill-dir>/scripts/project_docs.py init --root <repo-root> --project-name <name>
python3 <skill-dir>/scripts/project_docs.py init --root <repo-root> --project-name <name> --apply
```

Preserve the existing taxonomy and project content. Add the smallest useful structure, concrete code evidence, and real watched paths; never fabricate a complete domain catalog.

## Plan work

Search active and archived Plan directories before creating a new Plan. Continue an existing active Plan for the same work; otherwise follow the repository's naming and template rules.

Before editing code, read the complete Plan and repository Plan contract, check them against the current worktree, and keep the Plan current as decisions or scope change. Validate observable behavior, not only file changes or compilation. A complex or multi-stage effort uses the full ExecPlan requirements in `references/exec-plans.md`.

## Close delivery

When implementation and required validation are complete:

1. Record final implementation and verification in the Plan.
2. Update stable ProductFact from final code and refresh its evidence.
3. Add a concise Changelog entry when the delivery is meaningful.
4. Remove a source Idea only after its fact handoff is complete.
5. Mark the Plan `completed`, move it to the configured archive without renaming it, and update old links.

Never archive a Plan whose status is absent, ambiguous, or not `completed`.

## Upgrade

Inspect the manifest and read every unapplied migration in version order. Compare each requirement with the real repository, preview semantic edits, protect project-specific content, and update the recorded contract version only after validation succeeds. If no manifest exists, reconstruct it from evidence rather than reinitializing an established system.

## Validation

Use checks proportional to the change:

- inspect changed links and paths;
- run the configured ProductFact check when facts or watched code changed;
- search for old paths after taxonomy changes or Plan archival;
- confirm no project-owned document was replaced;
- keep the Plan active while required facts, evidence, or validation remain incomplete.
