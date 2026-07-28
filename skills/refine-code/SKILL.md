---
name: refine-code
description: Refine existing code through evidence-based review or implementation focused on reliability, scalability, and maintainability while preserving intended behavior. Use when reviewing code quality, planning or performing a refactor, simplifying architecture, reducing coupling, improving failure handling or data integrity, preparing code for growing load or requirements, or deciding whether an abstraction is justified across any language or framework.
---

# Refine Code

Improve code in response to concrete risks and change pressure. Preserve intended behavior and public contracts. When fixing a defect requires an observable behavior change, make the change and its impact explicit.

## Establish the boundary

1. Determine whether the user asked for review, diagnosis, a plan, or implementation. Do not edit during review or diagnosis unless explicitly asked.
2. Read repository instructions, the relevant call path, tests, public contracts, configuration, and operational constraints.
3. State the behavior and invariants that must remain true. Include data ownership, failure semantics, compatibility, and performance expectations when relevant.
4. Use current evidence: code paths, tests, logs, measurements, incidents, or known requirement changes. Mark assumptions and unverified risks.

## Evaluate the code

Assess only dimensions relevant to the task.

### Reliability

- Verify that behavior matches the intended contract.
- Contain expected failures without hiding them or crashing unrelated work.
- Protect data correctness and integrity across success, retry, interruption, partial failure, and concurrency.
- Require explicit confirmation for destructive user actions.
- Check whether required latency, throughput, and resource bounds are measured and enforceable.

### Scalability

- Identify the actual load dimension before optimizing: data volume, request rate, concurrency, fan-out, payload size, or another measurable constraint.
- Prefer designs that can grow incrementally instead of requiring an early rewrite.
- Treat requirement growth as a scaling problem too: locate hard-coded policy, unstable boundaries, and changes that spread across unrelated modules.
- Do not introduce distributed systems, caches, queues, generic frameworks, or extension points without present evidence or a credible near-term need.

### Maintainability

- **Operability:** keep important behavior observable; make failures diagnosable; isolate changes in tools, configuration, dependencies, and platforms from domain behavior.
- **Simplicity:** remove accidental complexity; use abstractions that clarify a real concept; reuse behavior without forcing unrelated cases together; reduce coupling and keep responsibilities cohesive.
- **Evolvability:** make common changes local, preserve stable interfaces, cover invariants with tests, and refactor when current structure makes a concrete change unsafe or hard.

## Choose changes

Prioritize by user impact, likelihood, evidence, and cost of recovery. Prefer the smallest coherent change that removes the identified risk.

- Fix correctness and data-integrity risks before structural polish.
- Prefer deleting unnecessary paths or making dependencies explicit over adding layers.
- Keep policy separate from mechanism when they change for different reasons.
- Do not deduplicate code whose similarity is incidental or whose change reasons differ.
- Do not optimize without a workload and measurement.
- Record meaningful trade-offs when improving one quality makes another worse.

## Implement and verify

When implementation is requested:

1. Make changes in small, reviewable steps and avoid unrelated cleanup.
2. Add or update focused tests for preserved behavior, boundaries, and failure cases.
3. Run the narrowest credible checks first, then broader project checks in proportion to risk.
4. Measure performance changes against the stated workload; do not infer them from code shape.
5. Re-read the diff for new coupling, hidden state, compatibility changes, and weakened diagnostics.

## Report the result

For a review, return only actionable findings, ordered by severity. For each finding, state the affected quality, concrete evidence, impact, and smallest suitable action. For an implementation, summarize the preserved contract, changes, verification performed, and residual risks. Do not claim reliability, scalability, maintainability, or performance beyond the evidence collected.
