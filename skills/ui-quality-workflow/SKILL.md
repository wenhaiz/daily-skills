---
name: ui-quality-workflow
description: Plan, implement, and independently verify non-trivial UI changes with a clear design contract, state coverage, accessibility checks, and visual evidence. Use when creating a screen, materially changing layout or a shared UI component, reviewing UI quality, or preparing a UI-heavy release in any app or web project.
---

# UI Quality Workflow

Use this workflow to turn a UI change into a verifiable user experience, rather than treating a code diff as visual proof.

## Applicable scenarios

- A new page, flow, or reusable component.
- A material layout, information-hierarchy, navigation, gesture, or motion change.
- A UI review, design QA pass, or UI-heavy release review.
- Not needed for isolated copy corrections, token-only changes with no visible delta, or pure logic changes.

## Establish the project contract

1. Read repository instructions, the product's design entrypoint, and the active plan or feature brief.
2. Inspect the closest production screen, shared components, design tokens, navigation patterns, and localization approach before adding abstractions.
3. State the user scenario, one primary action, secondary actions, information hierarchy, and intentional omissions. Preserve project conventions unless the task explicitly changes them.
4. Record the contract in the project's plan system. When no plan exists, include it in the implementation handoff.

## Build the smallest coherent change

- Reuse semantic tokens and components whose behavior fits; do not copy a component solely for its appearance.
- Keep presentation separate from business behavior, and avoid unrelated redesign.
- Localize user-facing strings using the project's established mechanism.
- Design loading, empty, error, disabled, long-content, and extreme-data states that the change can reach.
- For motion or gestures, provide immediate feedback, make movement interruptible when direct manipulation is involved, and include a reduced-motion alternative.

## Verify with evidence

Use the platform's preview, Storybook, simulator, device, or browser—choose the fastest credible path.

- Check representative content plus the relevant boundary states.
- Check supported languages, larger text/content scaling, target viewport sizes, contrast, focus/VoiceOver semantics, and touch/click targets.
- Inspect gestures and meaningful motion on a real rendering surface; code review alone cannot establish spatial or interaction quality.
- Add or update a stable preview and focused UI test when practical. If unavailable, record why and the replacement verification path.

## Review output

For non-trivial work, report separately:

- **Design contract and primary action**
- **Code evidence**: components, tokens, states, and accessibility implementation
- **Visual evidence**: where and under which states the UI was actually inspected
- **Unverified risk**: languages, devices, states, gestures, or motion not checked

Give only actionable findings. Cite exact files and lines for code findings; never claim visual quality without visual evidence.
