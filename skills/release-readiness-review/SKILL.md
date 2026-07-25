---
name: release-readiness-review
description: Run a structured, risk-focused pre-release review and return a documented GO, NO-GO, or GO-with-waivers decision. Use before production deployment, App Store/TestFlight submission, beta rollout, or any release candidate that needs diff review, validation evidence, and explicit residual-risk tracking.
---

# Release Readiness Review

Review release risk consistently. Adapt project-specific commands and policies; do not assume a particular platform, framework, or documentation layout.

## Applicable scenarios

- Before production, App Store, TestFlight, beta, or internal release.
- When asked for a ship/no-ship decision, final QA gate, release candidate review, or regression-risk scan.
- Not for ordinary code review unless the user explicitly wants release readiness.

## Review workflow

1. Confirm the release range and target. Default to the current branch's staged, unstaged, and committed diff only if no range is supplied.
2. Read changed files and lead with user-visible impact. Identify primary paths, data migration or loss risk, authentication/permission changes, external-service changes, and rollback constraints.
3. Read repository rules, build/test commands, localization policy, and the documentation system. Run feasible relevant checks; never invent results.
4. If the range contains a UI diff, invoke `ui-quality-workflow` and require actual rendered visual evidence. Also invoke `ios-swiftui-ui-quality` when the affected scope is SwiftUI. Mark UI-only checks N/A for logic-only releases.
5. Review the general checklist in [assets/release-checklist.md](assets/release-checklist.md), adapting items that conflict with documented project policy.
6. Return the complete structure in [assets/release-review-report.md](assets/release-review-report.md).

## Decision rules

- `NO-GO`: any unresolved blocker, unbounded data-loss/security/privacy risk, or a broken primary user path.
- `GO with waivers`: material known risks have a named owner, mitigation, and revisit date; the release authority explicitly accepts them.
- `GO`: no unresolved blocker and validation evidence is sufficient for the release scope.

Order findings by Blocker, High, Medium, then Low. Every finding needs impact, concrete evidence, recommended action, and whether it blocks release. Distinguish verified facts from checks not run and residual risk.
