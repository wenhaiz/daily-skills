---
name: ios-swiftui-ui-quality
description: Design, implement, and visually verify polished, accessible SwiftUI screens and reusable components for iPhone, iPad, or Apple-platform apps. Use when creating or materially changing a SwiftUI page, navigation flow, layout, interaction, animation, shared component, Preview, or SwiftUI UI test.
---

# iOS SwiftUI UI Quality

Use this iOS-specific workflow alongside the project's design rules. For platform-neutral UI work, use `ui-quality-workflow` instead.

## Applicable scenarios

- A new SwiftUI screen, sheet, navigation path, or shared component.
- A meaningful change to layout, Dynamic Type behavior, touch interaction, motion, or SwiftUI state presentation.
- A SwiftUI UI review, Preview improvement, simulator QA pass, or UI-test addition.
- Not needed for pure view-model or persistence changes with no visual result, or an isolated localized-string correction.

## Start from the app's own language

1. Read `AGENTS.md`, the app's design entrypoint, active plan, localization policy, and nearest production views.
2. Identify the user scenario, one primary action, important secondary actions, state ownership, and which states must be rendered.
3. Reuse the app's semantic colors, typography, component styles, navigation, presentation, and observation conventions. Do not introduce a competing design system.
4. Keep domain/business logic in its model or view model; make the view's data flow and ownership explicit.

## Implement for the platform

- Prefer semantic `Font` styles and scalable layouts. Avoid fixed dimensions that clip labels, values, or primary actions at larger Dynamic Type sizes.
- Provide VoiceOver labels, values, traits, and hints for non-text controls where needed. Keep interactive targets at least 44 by 44 points.
- Use accessibility-safe color contrast and do not convey required state by color alone.
- Localize all user-visible text through the project mechanism; inspect every supported language affected by layout.
- Use `@Environment(\.accessibilityReduceMotion)` for meaningful movement. Replace large motion with a subtle opacity or direct-state alternative when enabled.
- Animate the specific value that changes; avoid broad implicit animations across a large view tree. Use continuous, interruptible behavior for direct-manipulation gestures.

## Preview and render actual states

Add useful `#Preview` coverage whenever it can be isolated safely. Use deterministic fixtures or in-memory stores; do not depend on production accounts, iCloud, network, or user data.

Cover the changed surface's relevant cases:

- representative populated content and the most failure-prone boundary state;
- empty, loading, error, and disabled states when reachable;
- long localized text, large Dynamic Type, and compact iPhone width;
- iPad or regular width when the layout changes materially;
- dark/light appearance only when the project supports each appearance.

Build and inspect the Preview, simulator, or device. For user-critical or regression-prone flows, add focused UI tests with deterministic launch configuration and stable assertions; do not rely on pixel-perfect assertions for system typography or continuous animations.

## Review handoff

State separately:

- **Code evidence**: view structure, state ownership, reuse, localization, accessibility, and motion fallback.
- **Visual evidence**: Preview/simulator/device, devices, languages, content sizes, and states actually inspected.
- **Unverified interaction risk**: gestures, VoiceOver order, system sheets, hardware behavior, or device states not tested.

Report actionable findings with exact file and line references. Do not claim visual polish or interaction quality from source inspection alone.
