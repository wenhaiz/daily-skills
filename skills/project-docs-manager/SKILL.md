---
name: project-docs-manager
description: Initialize, audit, maintain, and incrementally upgrade a repository documentation system built around Ideas, Plans, ProductFact, and Changelog. Use when Codex needs to establish project documentation, reorganize an existing docs tree, keep documentation synchronized with implementation, close a feature into stable facts and delivery history, or migrate a project after this skill's documentation contract changes.
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

## Select the operation

1. **Audit**: inspect the current documentation structure, rules, scripts, and manifest. Do not write files.
2. **Initialize**: establish the minimum documentation lifecycle in a project that does not have it.
3. **Maintain**: route new or changed knowledge to the correct document and keep links consistent.
4. **Close a delivery**: update stable facts and evidence, add the concise changelog record, then complete the Plan.
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
2. Identify one to three core domains from code; do not invent a complete taxonomy.
3. Create domain facts using `Docs/0-ProductFact/90-templates/domain-fact-template.md`.
4. Add concrete `watch_paths`, code evidence, and a real `verified_commit`.
5. Run the generated fact check and resolve broken paths or stale facts.
6. Record the skill contract version in `Docs/.project-docs.json` only after the repository matches it.

## Maintain and close work

Route documentation by intent:

- Future possibility without active development -> `Docs/2-Ideas/`
- Scoped development and its changing progress -> `Docs/1-Plans/`
- Stable intent, decisions, and current code-backed behavior -> `Docs/0-ProductFact/`
- Concise user-visible or behaviorally meaningful delivery record -> `Docs/3-Changelog/<year>/`

When work starts, create or continue one Plan. When work finishes:

1. Record implementation and verification results in the Plan.
2. Update stable domain facts from final code, not from the original proposal.
3. Refresh evidence, `watch_paths`, and `verified_commit`.
4. Add a short Changelog entry when the change is meaningful.
5. Remove the source Idea after implementation and fact handoff are complete.
6. Mark the Plan completed only after ProductFact is current.

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
- Run `scripts/product_fact/check.sh` when ProductFact domains or watched code changed.
- Confirm no project-owned document was unintentionally replaced.
- For a taxonomy migration, search the entire repository for old paths.
- Keep the Plan active if stable facts, verification, or migration steps remain incomplete.
