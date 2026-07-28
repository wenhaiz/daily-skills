---
name: project-docs-manager
description: Initialize, audit, maintain, and incrementally upgrade a repository documentation system built around Ideas, executable living Plans, ProductFact, and Changelog. Use when Codex needs to establish project documentation, create or implement from a Plan, reorganize an existing docs tree, keep documentation synchronized with implementation, close a feature into stable facts and delivery history, or migrate a project after this skill's documentation contract changes.
---

# Project Docs Manager

Maintain project documentation as a lifecycle instead of a loose collection of files.

## Core rules

- Treat code and live configuration as the final source of truth.
- Preserve useful existing documentation. Do not replace a repository's taxonomy before inspecting it.
- Separate future ideas, active development history, stable current facts, and delivery history.
- Start with the smallest useful structure and the project's one to three highest-value domains.
- Make initialization and upgrades additive by default. Never overwrite project-owned content blindly.
- Follow the repository's `AGENTS.md` and local conventions before this skill's defaults.

Read [references/document-model.md](references/document-model.md) when deciding where content belongs or adapting the model to a repository.
Read [references/migrations.md](references/migrations.md) whenever a project has `Docs/.project-docs.json` or the user asks to upgrade an existing documentation system.
Read [references/exec-plans.md](references/exec-plans.md) whenever creating a Plan, implementing from a Plan, or upgrading a project to the executable Plan contract.

## Select the operation

1. **Audit**: inspect the current documentation structure, rules, scripts, and manifest. Do not write files.
2. **Initialize**: establish the minimum documentation lifecycle in a project that does not have it.
3. **Maintain**: route new or changed knowledge to the correct document and keep links consistent.
4. **Close a delivery**: update stable facts and evidence, add the concise changelog record, complete the Plan, then move it to the Plan archive.
5. **Upgrade**: compare the project's recorded contract version with this skill's migration contract and apply only the missing migrations.

## Audit first

Run:

```bash
python3 <skill-dir>/scripts/project_docs.py inspect --root <repo-root>
```

Also inspect:

- repository instructions such as `AGENTS.md`
- existing documentation entrypoints and naming conventions
- source directories, build/test commands, and major business domains
- current uncommitted changes before editing

Report the existing structure, conflicts with the model, and the smallest useful next action. An audit request does not authorize writes.

## Initialize

Preview the scaffold first:

```bash
python3 <skill-dir>/scripts/project_docs.py init --root <repo-root> --project-name <name>
```

Apply only after the user requested creation or migration:

```bash
python3 <skill-dir>/scripts/project_docs.py init --root <repo-root> --project-name <name> --apply
```

The script creates missing baseline files only. It refuses to overwrite existing files. After scaffolding:

1. Adapt `Docs/README.md` and repository instructions to the real project.
2. Make the Plan contract discoverable and add a repository instruction that requires a full ExecPlan for complex work.
3. Identify one to three core domains from code; do not invent a complete taxonomy.
4. Create domain facts using `Docs/0-ProductFact/90-templates/domain-fact-template.md`.
5. Add concrete `watch_paths`, code evidence, and a real `verified_commit`.
6. Run the generated fact check and resolve broken paths or stale facts.
7. Record the skill contract version in `Docs/.project-docs.json` only after the repository matches it.

## Create and execute Plans

Before creating a Plan, search the configured active and archived Plan directories for the same work. Continue the existing active Plan when one exists. Otherwise, follow the repository's naming convention; when none exists, use `yyyy-MM-dd-<kebab-title>.md`.

Use two levels of Plan:

- **Standard Plan**: use for bounded work that still benefits from written scope and verification. It must remain self-contained, current, and outcome-focused.
- **Full ExecPlan**: use for complex features, significant refactors, cross-module changes, migrations, multi-hour work, meaningful unknowns, or work that needs staged validation or prototypes.

Every Plan must explain the purpose, relevant repository context, scope, implementation approach, current progress, decisions, discoveries, validation, outcomes, and ProductFact handoff. A full ExecPlan must additionally provide novice-oriented repository navigation, independently verifiable milestones, exact commands with working directories and expected observations, interfaces and dependencies, idempotence and recovery guidance, and concise evidence.

When implementing from a Plan:

1. Read the entire Plan and the repository's configured Plan contract before editing.
2. Confirm the Plan still matches the working tree and update stale assumptions before proceeding.
3. Work through milestones within the user's authorized scope without pausing merely to ask for the next step.
4. At every stopping point, update timestamped progress and state what is done and what remains.
5. Record unexpected behavior and evidence in `Surprises & Discoveries`; record changed choices and rationale in `Decision Log`.
6. Keep every section consistent after changing course so the current Plan remains sufficient for a new contributor to resume.
7. Validate observable behavior or a reproducible before/after test, not only compilation or file changes.
8. Complete `Outcomes & Retrospective` and the normal ProductFact and Changelog handoff before marking the Plan `completed`.

Autonomous continuation never overrides the user's instructions, repository rules, approval boundaries, or destructive-action safeguards. Do not require or create commits unless the user or repository workflow authorizes them.

## Maintain and close work

Route documentation by intent:

- Future possibility without active development -> `Docs/2-Ideas/`
- Scoped development and its changing progress -> `Docs/1-Plans/`
- Completed development history -> `Docs/1-Plans/archived/`
- Stable intent, decisions, and current code-backed behavior -> `Docs/0-ProductFact/`
- Concise user-visible or behaviorally meaningful delivery record -> `Docs/3-Changelog/<year>/`

When work starts, create or continue one Plan using the configured Plan contract and template. During implementation, keep that same Plan current. When work finishes:

1. Record implementation and verification results in the Plan.
2. Update stable domain facts from final code, not from the original proposal.
3. Refresh evidence, `watch_paths`, and `verified_commit`.
4. Add a short Changelog entry when the change is meaningful.
5. Remove the source Idea after implementation and fact handoff are complete.
6. Mark the Plan completed only after ProductFact is current.
7. Move the completed Plan to `<plans>/archived/`, preserve its filename, and update repository links that referenced its previous path.

Only archive Plans whose status is explicitly `completed`. Keep `draft`, `active`, `blocked`, and `superseded` Plans in the main Plan directory unless the repository defines another rule. If status is absent or ambiguous, do not infer completion from the filename or implementation state.

## Upgrade projects after this skill changes

Do not assume installing a new skill version automatically changes repositories. Upgrade when this skill is invoked in a project:

1. Inspect `Docs/.project-docs.json`.
2. Read every unapplied entry in [references/migrations.md](references/migrations.md), in version order.
3. Compare migration requirements with real repository state.
4. Preview the proposed file changes and protect project-specific content.
5. Apply semantic edits with the normal file-editing workflow; use scripts only for deterministic checks.
6. Validate links, paths, facts, and repository instructions.
7. Update `contract_version` and `applied_migrations` only after the migration succeeds.

If no manifest exists but the repository already resembles this system, reconstruct the manifest from evidence instead of reinitializing or moving files automatically.

## Validation

Use validation proportional to the change:

- Always inspect changed links and paths.
- Run the repository's ProductFact check script at its configured path when ProductFact domains or watched code changed. Prefer `<product-fact>/check.sh`; continue supporting `scripts/product_fact/check.sh` in projects that still use the legacy location.
- Confirm no project-owned document was unintentionally replaced.
- For a taxonomy migration, search the entire repository for old paths.
- After archiving a Plan, search the entire repository for references to its previous path.
- Keep the Plan active if stable facts, verification, or migration steps remain incomplete.
