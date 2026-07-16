# Documentation model

## Lifecycle

```text
Idea -> Plan -> ProductFact -> Changelog
             \-> stable intent and choices
```

The arrows describe knowledge handoff, not mandatory file movement.

## Layers

### Ideas

Store work that may be valuable but has not entered development. Keep the problem, expected value, known constraints, and open questions. Avoid detailed implementation logs.

### Plans

Store one feature's complete development history: scope, exclusions, phases, progress, decisions, verification, blockers, and final handoff. Continue updating the same Plan during implementation.

Recommended statuses: `draft`, `active`, `blocked`, `completed`, `superseded`.

Keep unfinished Plans in the configured Plan directory. After a Plan is explicitly marked `completed`, move it to the `archived/` subdirectory under that Plan directory and update references to its old path. Preserve the filename so history stays easy to trace. Do not infer completion when status is missing or ambiguous.

### ProductFact

Store stable, reusable knowledge:

- `00-overview/`: product or system map
- `10-domains/`: current code-backed behavior by domain
- `20-releases/`: optional release-oriented summaries
- `40-intent/`: principles, capability boundaries, and lasting choices
- `50-shared-rules/`: rules shared across domains
- `80-process/`: maintenance and review workflows
- `90-templates/`: project-owned document templates

Only add other sections when the project has a real consumer for them.

Each domain fact should include:

- scope and exclusions
- current behavior
- important constraints and state transitions
- unknowns clearly marked as unverified
- `verified_commit`
- narrow `watch_paths`
- a separate evidence index when multiple source files are involved

### Changelog

Store concise delivery history. Add entries for user-visible features, meaningful behavior changes, and refactors that alter state flow or future development expectations. Skip isolated wording and visual polish without lasting impact.

## Adaptation rules

- Preserve an established directory when its semantics already match a layer; record the custom path in the manifest.
- Use names natural to the repository. The numbered directory layout is a default, not a reason to churn paths.
- Separate product facts from architecture records only when the repository benefits from that distinction.
- For libraries and infrastructure, interpret ProductFact as system behavior and public contracts rather than end-user product flows.
- For small projects, omit Ideas or Changelog if there is no maintenance value, but retain the Plan/ProductFact distinction.

## Source-of-truth hierarchy

1. Executable code, schemas, and live configuration
2. Tests and generated artifacts that prove behavior
3. ProductFact as a reviewed cache of current behavior
4. Plans as historical development context
5. Ideas as uncommitted possibilities

When sources disagree, investigate code and runtime behavior before rewriting documentation.
