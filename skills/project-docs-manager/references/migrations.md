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

## Adding future migrations

When updating this skill:

1. Increment `CURRENT_CONTRACT_VERSION` in `scripts/project_docs.py`.
2. Add a new section here with a unique migration id, required semantic changes, and validation steps.
3. Keep earlier migrations unchanged so older projects can upgrade sequentially.
4. Prefer additive migrations. For renames or removals, require repository-wide reference search and explicit preservation of project-owned content.
5. Update scaffold assets only for newly initialized projects; do not treat template replacement as an upgrade strategy.
