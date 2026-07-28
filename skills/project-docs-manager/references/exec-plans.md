# Executable Plan contract

Plans are living execution records, not proposals that become stale after coding starts. A contributor with no prior conversation or memory must be able to use the current working tree and one Plan to understand the goal, continue the work, and prove the result.

## Choose the Plan level

Use a standard Plan for bounded work with a clear approach and a small verification surface. Use a full ExecPlan when the work includes a complex feature, significant refactor, migration, multiple modules or services, several hours of work, important unknowns, prototypes, or staged rollout and validation.

Both levels must be:

- self-contained: repeat every assumption and repository fact needed to continue
- living: update the document as progress, discoveries, and decisions change
- outcome-focused: describe what becomes possible and how a person can observe it
- decision-complete: do not leave important implementation choices to the next contributor
- safe: state retry, recovery, and destructive-operation constraints when relevant

## Required content for every Plan

Every Plan must contain:

- status and a statement that the Plan is a living document
- purpose and observable outcome
- repository context and definitions needed by a new contributor
- scope and exclusions
- implementation approach or work sequence
- timestamped progress that distinguishes completed and remaining work
- surprises and discoveries with concise evidence
- a decision log with rationale and date
- validation and acceptance with commands or observable behavior
- outcomes and retrospective
- ProductFact and Changelog handoff status

Use prose to explain context and milestones. Use checklists only where they improve progress tracking. Name files using repository-relative paths, identify important modules or symbols, and include the working directory for commands.

## Additional content for a full ExecPlan

A full ExecPlan must also contain:

- context and orientation detailed enough for a repository novice
- narrative milestones that each produce an independently verifiable result
- concrete steps with exact commands, expected output, and interpretation
- interfaces and dependencies that name the required modules, services, types, or signatures
- idempotence and recovery instructions for repeatable, partial, risky, or migration steps
- artifacts and notes containing only the evidence needed to prove important results

When feasibility is uncertain, add an independently testable prototype milestone. Define the criteria for keeping or discarding the prototype and how to clean it up.

## Authoring workflow

1. Search active and archived Plans before creating a new document.
2. Continue an existing active Plan for the same work. Do not split history across duplicate Plans.
3. Follow the repository's naming convention. If none exists, use `yyyy-MM-dd-<kebab-title>.md`.
4. Start from the configured template and inspect the real code, tests, configuration, and repository instructions.
5. Resolve important choices in the Plan and explain why. Embed required external knowledge in plain language instead of relying on an unavailable conversation or external page.
6. Set the Plan to `active` when implementation begins.

## Execution workflow

Read the entire Plan and configured Plan contract before editing. Reconcile the Plan with the current working tree, then proceed through the next incomplete milestone within the user's authorized scope.

At every stopping point:

- update Progress with a timestamp
- split partially completed work into explicit completed and remaining parts
- record unexpected behavior and short evidence
- record decisions that changed or clarified the approach
- update affected sections so the document remains internally consistent

Validation must demonstrate useful behavior. For user-facing work, describe how a person exercises the feature and what they should observe. For internal work, provide a reproducible test or scenario that fails before the change and passes after it when practical. Compilation alone is insufficient unless compilation is itself the requested outcome.

Do not pause only to ask what to do next when the next milestone is already authorized and safe. This does not authorize destructive actions, external publication, commits, or work outside the user's scope.

## Completion

At a major milestone and at completion, update `Outcomes & Retrospective` with what was achieved, what remains, and what was learned. Record actual verification results rather than planned commands.

Only mark a Plan `completed` after required validation succeeds and stable final behavior is handed off to ProductFact. Add a Changelog entry when the delivery is meaningful, then move the completed Plan to the configured archive without changing its filename and update references to the old path.
