# Release checklist

Mark every relevant item `Pass`, `Fail`, `N/A`, or `Not Run`.

## Scope

- Release range and target are explicit.
- Changed files match intended scope; no debug artifacts or temporary work remain.

## Primary risks

- Changed primary paths have no obvious crash, invalid state, or broken navigation path.
- Data schema, migration, sync, import/export, and destructive operations have an appropriate safety path.
- Permissions, secrets, privacy disclosures, and network/service configuration match behavior.
- Required assets, configuration, localization resources, and feature flags resolve correctly.

## Quality and validation

- Code is readable; error handling and state transitions are explicit where user-impacting.
- Relevant build, unit, integration, UI, and manual tests were run, or their absence is recorded with risk.
- UI diff: actual visual evidence, relevant states, accessibility, supported languages, viewport/device coverage, and reduced motion are checked.

## Delivery hygiene

- Release notes, stable behavior documentation, and operational runbooks are current when the project requires them.
- Rollback, monitoring, and post-release ownership are understood for material changes.
- No unresolved Blocker remains; High findings are fixed or explicitly waived.
