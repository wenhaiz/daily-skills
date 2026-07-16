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

## Adding future migrations

When updating this skill:

1. Increment `CURRENT_CONTRACT_VERSION` in `scripts/project_docs.py`.
2. Add a new section here with a unique migration id, required semantic changes, and validation steps.
3. Keep earlier migrations unchanged so older projects can upgrade sequentially.
4. Prefer additive migrations. For renames or removals, require repository-wide reference search and explicit preservation of project-owned content.
5. Update scaffold assets only for newly initialized projects; do not treat template replacement as an upgrade strategy.
