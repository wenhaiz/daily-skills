# Migration contract

Apply migrations in order. Never mark a migration complete before repository-specific validation succeeds.

## Version 1

Migration id: `v1-baseline-lifecycle`

Required contract:

- A discoverable documentation entrypoint exists.
- Future ideas, development process, stable facts, and delivery history have distinct destinations, even if the repository uses custom paths.
- Stable domain facts identify the code revision and source paths used for verification.
- Repository instructions explain the documentation handoff and completion gate.
- A lightweight freshness check exists when ProductFact is enabled.
- `Docs/.project-docs.json` records the mapped paths and applied migration id.

Validation:

- Inspect every configured path.
- Confirm at least one real core domain is documented if ProductFact is enabled.
- Confirm watched paths exist at the recorded commit.
- Run the project's freshness check.
- Search repository instructions for obsolete documentation paths.

## Version 2

Migration id: `v2-archive-completed-plans`

Required contract:

- The configured Plan directory has an `archived/` subdirectory.
- Plans explicitly marked `completed` live in `archived/`; unfinished and ambiguous Plans remain in the main Plan directory.
- Repository instructions and Plan navigation explain the completion and archive rule.
- The manifest records the archive path separately from the active Plan path.
- References to moved Plans use their archived paths.

Validation:

- Inspect Plan status from document content; do not classify completion from filenames.
- Confirm every moved Plan is explicitly `completed` and ProductFact handoff is recorded.
- Search the entire repository for references to each moved Plan's previous path.
- Confirm `paths.plans_archive` resolves to the configured Plan directory's `archived/` subdirectory.

## Version 3

Migration id: `v3-executable-living-plans`

Required contract:

- Every Plan is treated as a self-contained, living, outcome-focused document that a contributor without prior conversation can use to continue work.
- The repository distinguishes standard Plans from full ExecPlans. Full ExecPlans are required for complex features, significant refactors, cross-module changes, migrations, multi-hour work, meaningful unknowns, prototypes, or staged validation.
- The configured Plan directory has a discoverable Plan contract that defines authoring, implementation, validation, completion, and archive behavior.
- A project-owned Plan template exists and contains the standard living sections plus the additional full ExecPlan sections.
- Repository instructions or the configured Plan navigation explain when to use a full ExecPlan and link to the Plan contract.
- `Docs/.project-docs.json` records `paths.plan_contract` and `paths.plan_template`.
- Active Plans are upgraded when work resumes and the missing sections are material to safe continuation. Archived Plans are preserved and are not rewritten in bulk.

Validation:

- Confirm the configured Plan contract and Plan template paths exist.
- Confirm the Plan contract requires timestamped progress, discoveries with evidence, decision rationale, observable validation, outcomes, and ProductFact handoff.
- Confirm the full ExecPlan rules include repository orientation, independently verifiable milestones, exact commands and expected observations, interfaces and dependencies, idempotence and recovery, and concise evidence.
- Confirm Plan generation searches active and archived Plans before creating a new document and follows repository naming rules, with `yyyy-MM-dd-<kebab-title>.md` as the fallback.
- Confirm implementation guidance keeps all Plan sections current at stopping points without overriding user authorization, repository rules, approvals, or commit policy.
- Confirm existing archived Plans were not modified merely to satisfy the new template.
- Confirm `paths.plan_contract` and `paths.plan_template` resolve from the manifest rather than fixed default directories.

## Adding future migrations

When updating this skill:

1. Increment `CURRENT_CONTRACT_VERSION` in `scripts/project_docs.py`.
2. Add a new section here with a unique migration id, required semantic changes, and validation steps.
3. Keep earlier migrations unchanged so older projects can upgrade sequentially.
4. Prefer additive migrations. For renames or removals, require repository-wide reference search and explicit preservation of project-owned content.
5. Update scaffold assets only for newly initialized projects; do not treat template replacement as an upgrade strategy.
