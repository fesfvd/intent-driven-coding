---
status: "hypothesis"
name: intent-driven-coding-design-system
description: "A calm blue control room with an orange human decision layer for observing and evolving project-specific AI engineering systems."
---

# Proposed Observatory Design Hypothesis

## Overview

> **This product does not exist today.** This document is a Phase 5 hypothesis, not a roadmap commitment, product specification, or implementation mandate. It must not be used to imply that a Web Observatory is planned before host acceptance, provenance, CLI, and local-report evidence justify it.

If built, Intent-Driven Coding could offer a local-first web observatory for project-specific AI engineering systems. It would help one person or a small team understand how Skills, Squads, contracts, evidence, and host adapters evolve across multiple projects.

The hypothetical product would be an observation surface for methodology. It would not be an Agent chat client, task inbox, prompt composer, or command dispatcher. The visual system would need to make the current state, evidence quality, and human decisions easy to inspect without pretending that configuration is proof of execution.

The first screen is the usable portfolio workspace: projects, current health, recent evolution, and evidence. Do not lead with a marketing hero, an abstract AI illustration, or a wall of feature cards.

## Design Personality

The interface is **a calm blue control room with an orange human decision layer**.

- **Blue** means structure, repository facts, stable methods, verified state, and calm orientation.
- **Orange** means human judgment, change, creative evolution, open decisions, and attention that deserves review.
- **Neutral surfaces** keep the interface quiet enough for evidence, history, and relationships to remain readable.
- **Semantic colors** are independent from the brand pair. Success, error, warning, and unavailable states must never be inferred from blue or orange alone.

The experience should feel precise, trustworthy, inspectable, and alive without becoming theatrical. It is a professional tool for repeated review, not a futuristic control-room imitation.

### Non-goals

- Do not make the visual product a second Solo-style collaboration workspace.
- Do not put task creation, Agent chat, prompt submission, or deployment commands in the observatory.
- Do not present inferred Agent activity as verified execution.
- Do not make every project look identical. The system shell is shared; each project's methods and evidence remain distinct.

## Source Influences

### Base: Linear

Use Linear as the structural base for:

- dense but calm operational surfaces;
- a deliberate surface ladder instead of heavy shadows;
- hairline borders and compact controls;
- clear state, status, and navigation hierarchy;
- fast scanning across lists, timelines, and project views.

We do not copy Linear's near-black marketing canvas, lavender-only accent, negative tracking, or issue-tracker identity. IDC uses a readable light default, a blue/orange semantic brand pair, and evidence-oriented project views.

### Figma

Borrow precision in graph interaction, selection feedback, spatial grouping, and small tool controls. Translate Figma's expressive color blocks into restrained topology accents and selection states. Do not use pastel poster panels or oversized pill buttons.

### Notion

Borrow the idea that durable knowledge is part of the product surface: methodology notes, decision rationale, and historical context should be readable in place. Translate its document-first calm into evidence drawers and evolution records. Do not copy its database-property rainbow or card-heavy marketing layout.

### Stripe

Borrow technical trust: strong numeric hierarchy, tabular figures, explicit states, and restrained surfaces for complex operational information. Translate the dashboard discipline into evidence quality and provenance labels. Do not use atmospheric gradients or finance-specific visual motifs.

### Sentry

Borrow observability semantics: current versus stale, issue severity, traceability, and a clear distinction between signal and noise. Translate this into project health and verification freshness. Do not use mascots, decorative starfields, or a dark-purple developer-console personality.

## Translation Rules

Every visual decision must answer one of these questions:

1. Does it make project state easier to compare?
2. Does it reveal why a Skill or Squad changed?
3. Does it distinguish configuration from observed evidence?
4. Does it expose a human decision or an unresolved boundary?
5. Does it make a cross-project relationship safer to understand?

If the answer is no, remove the decoration or move it out of the primary workflow.

## Color Tokens

All application colors must use semantic tokens. Raw color values are permitted only in the token definition layer.

### Brand axes

| Token | Value | Use |
|---|---|---|
| `--color-blue-950` | `#102A43` | Deep navigation, high-contrast headings, dark theme anchor |
| `--color-blue-800` | `#174A75` | Strong structure, selected navigation, dark theme surfaces |
| `--color-blue-700` | `#1D6FB8` | Primary action, verified route, active links |
| `--color-blue-600` | `#2C83C9` | Hover and interactive emphasis |
| `--color-blue-100` | `#DCEEFF` | Selected surface, verified state background |
| `--color-blue-050` | `#F1F7FC` | Blue-tinted project context surface |
| `--color-orange-800` | `#9A431D` | Dark orange text and selected emphasis on light surfaces |
| `--color-orange-700` | `#C95B22` | Pressed orange action |
| `--color-orange-600` | `#E8782F` | Human decision, evolution, creative action |
| `--color-orange-100` | `#FFE8D5` | Decision-needed and change surfaces |
| `--color-orange-050` | `#FFF6EE` | Subtle evolution background |

### Light surfaces and ink

| Token | Value | Use |
|---|---|---|
| `--color-canvas` | `#F5F8FC` | Application background |
| `--color-surface-0` | `#FFFFFF` | Main content and standard panels |
| `--color-surface-1` | `#F0F5FA` | Raised toolbar, table header, secondary panel |
| `--color-surface-2` | `#E7EFF7` | Hovered panel, selected neutral surface |
| `--color-surface-3` | `#D9E5F0` | Dropdown, popover, focused context surface |
| `--color-ink` | `#132238` | Primary text |
| `--color-ink-secondary` | `#3E5268` | Secondary text, descriptions |
| `--color-ink-muted` | `#66798D` | Metadata and helper text |
| `--color-ink-disabled` | `#9AAABA` | Disabled text |
| `--color-border` | `#CFDAE5` | Standard border and table rule |
| `--color-border-strong` | `#AEBECE` | Input, selected outline, emphasized divider |

### Dark theme surfaces

| Token | Value | Use |
|---|---|---|
| `--color-night-canvas` | `#0B1724` | Dark theme background |
| `--color-night-surface-0` | `#122334` | Dark theme main panel |
| `--color-night-surface-1` | `#183047` | Dark theme raised panel |
| `--color-night-surface-2` | `#20415F` | Dark theme hover and selected panel |
| `--color-night-ink` | `#F3F8FC` | Dark theme primary text |
| `--color-night-ink-secondary` | `#B7C8D8` | Dark theme secondary text |
| `--color-night-border` | `#2C4962` | Dark theme border |

Dark mode is a complete theme, not a black background with light-mode tokens inverted. It must remain readable for long sessions and must not become the default visual identity of every view.

### Semantic tokens

| Token | Value | Meaning |
|---|---|---|
| `--color-success` | `#2E7D5B` | Verified, healthy, or completed with evidence |
| `--color-success-soft` | `#DDF3E9` | Success background |
| `--color-warning` | `#B9681E` | Risk, aging evidence, or attention required |
| `--color-warning-soft` | `#FFF0D8` | Warning background |
| `--color-danger` | `#C54855` | Invalid, blocked, rejected, or unsafe |
| `--color-danger-soft` | `#FCE3E6` | Danger background |
| `--color-info` | `#2F78B7` | Informational state |
| `--color-neutral` | `#66798D` | Unknown, unverified, or not yet observed |

Orange brand tokens represent change and human attention. Use `--color-warning` for risk; do not make every orange element look like a warning.

### Chart palette

Charts must use more than hue alone: pair color with labels, patterns, position, or icons.

```css
--chart-blue: #1D6FB8;
--chart-orange: #E8782F;
--chart-green: #2E7D5B;
--chart-red: #C54855;
--chart-violet: #6A5FC1;
--chart-slate: #66798D;
```

Blue and orange are the first two series only when the comparison is meaningful. Do not assign colors randomly to Skill names.

## Typography

The type system is quiet, technical, and readable in dense tables. Do not use display-scale type inside the dashboard shell.

```css
--font-sans: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
--font-mono: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
```

| Token | Size / line height | Weight | Use |
|---|---:|---:|---|
| `--type-page-title` | 28px / 1.2 | 650 | Page title, one per view |
| `--type-section-title` | 20px / 1.3 | 600 | Major panel heading |
| `--type-card-title` | 16px / 1.35 | 600 | Project, Skill, Squad title |
| `--type-body` | 14px / 1.5 | 400 | Default UI text |
| `--type-body-medium` | 14px / 1.5 | 550 | Labels, selected values |
| `--type-small` | 13px / 1.45 | 400 | Secondary descriptions |
| `--type-caption` | 12px / 1.4 | 500 | Metadata, status labels |
| `--type-code` | 12px / 1.5 | 400 | IDs, paths, commands, event keys |
| `--type-metric` | 24px / 1.1 | 650 | Numeric summary only |

Letter spacing is `0`. Use weight, size, and surface contrast for hierarchy. Never use negative tracking to imitate a brand font.

Numbers, timestamps, counts, and identifiers use tabular figures where comparison matters:

```css
font-variant-numeric: tabular-nums;
```

## Spacing, Layout, and Shape

### Spacing

Use a 4px base unit:

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
```

Use 8px or 12px gaps inside dense controls, 16px between related controls, 24px between content groups, and 32px between major page sections.

### Application shell

- Desktop shell: 240px left navigation, 64px top bar, fluid main content.
- Main content max width: 1440px; use a 12-column grid at wide desktop.
- Default dashboard padding: 24px desktop, 16px tablet, 12px mobile.
- A full-width page section is not a card. Use cards only for individual repeated entities, framed tools, or modal content.
- Do not put cards inside cards. Use spacing, dividers, and surface changes for hierarchy.
- The portfolio overview should show a visible slice of recent evolution below the current-state summary.

### Radius

| Token | Value | Use |
|---|---:|---|
| `--radius-xs` | 2px | Status tags, compact code labels |
| `--radius-sm` | 4px | Inputs, table rows, compact controls |
| `--radius-md` | 6px | Buttons and standard cards |
| `--radius-lg` | 8px | Panels, large framed visualization, evidence drawer |
| `--radius-full` | 9999px | Avatars and status dots only |

Buttons and cards use rectangular geometry with restrained corners. Pills are reserved for compact status or filter tokens, never for every action.

### Elevation

Use borders and surface lifts before shadows:

```css
--shadow-floating: 0 8px 24px rgba(19, 34, 56, 0.12);
```

| Level | Treatment | Use |
|---|---|---|
| 0 | Canvas, no border | Page sections and background |
| 1 | Surface 0 + `--color-border` | Standard repeated item or panel |
| 2 | Surface 1 + strong border | Toolbar, selected panel, sticky summary |
| 3 | Surface 3 + `--shadow-floating` | Popover, menu, modal |

No glassmorphism, blur panels, glow borders, or decorative elevation stacks.

## Navigation and Information Architecture

The primary navigation is about inspection, not execution:

1. **Portfolio** - all projects and cross-project signals.
2. **Projects** - project-level team systems.
3. **Evolution** - changes to Skills, Squads, contracts, and evidence.
4. **Evidence** - evaluations, verification freshness, provenance, and unresolved boundaries.
5. **Settings** - adapters, local index paths, privacy, and display preferences.

Every project view must expose its project name, source path, host adapters, last indexed time, and evidence freshness near the top.

Use breadcrumbs for project and historical detail. Use tabs for sibling views of the same entity. Do not use tabs as a substitute for navigation.

## Core Visual Objects

### Project

A project is a repeated item with:

- name and repository path;
- supported host adapters;
- active Skill and Squad count;
- current evidence freshness;
- latest evolution event;
- one primary status: `healthy`, `attention`, `stale`, `blocked`, or `unverified`.

The project card is not a marketing tile. It is a compact scan row with a clear route to details.

### Skill node

Skill nodes use a blue outline for stable method ownership. A node label includes the Skill name, owned judgment, current lifecycle state, and last observed use. Do not encode the whole Skill body inside a graph node.

### Squad chain

Squads are shown as ordered chains, not org-chart boxes. Use solid blue connectors for declared handoffs and orange markers for human decision gates. A third member must be visibly justified by a distinct risk boundary.

### Evolution event

An evolution event is a timeline row with:

- timestamp;
- project;
- changed entity;
- event type: `observed`, `proposed`, `adopted`, `revised`, `deprecated`, or `rejected`;
- evidence link or explicit `unverified` label;
- human decision state.

Orange marks change and decision. Blue marks confirmed structure. Grey marks imported or unverified history.

### Evidence record

Evidence views must show the difference between:

- configured contract;
- Agent-declared record;
- executed command result;
- persisted artifact or runtime trace;
- human review decision.

Never use a single green "success" badge for all five categories.

## Component Constitution

### Buttons

Use Lucide icons inside buttons when a familiar icon exists. Icon-only buttons require a tooltip and accessible name.

Variants:

- **Primary blue**: inspect, open, compare, or confirm a local reversible view action.
- **Secondary**: neutral navigation or filter action.
- **Orange decision**: approve, adopt, revise, or record a human choice. It must never silently change a project's source files.
- **Danger**: reject, remove, or archive. Use danger red, not orange.
- **Ghost**: low-priority toolbar action.
- **Icon-only**: compact tools such as close, expand, copy, or open external source.

States required for interactive buttons: default, hover, active, focus-visible, disabled, and loading. Loading preserves width and uses a compact spinner or progress indicator.

### Status badges

Badges are compact state labels, not decoration. Pair every state color with text or an icon. Recommended labels:

- `Verified` - success;
- `Current` - blue;
- `Needs review` - orange/warning;
- `Stale` - warning;
- `Blocked` - danger;
- `Unverified` - neutral;
- `Not observed` - neutral.

### Panels and cards

Use a panel for one coherent view such as current state, evidence, or a timeline. Use a card for repeated projects, Skills, events, or Squad members. Do not nest panels inside cards.

Every panel defines its empty, loading, error, stale, and populated states. Empty state copy tells the user what evidence is missing; it does not advertise features.

### Tables and lists

Use tables for comparison and lists for chronological or navigational scanning. Align numeric columns on the decimal edge when practical. Keep row actions visible on hover and keyboard focus; never hide the only route to a record in a hover-only control.

### Timeline

The evolution timeline uses a vertical rule, date group, event marker, and evidence link. Avoid a series of floating cards. Important transitions may use an orange marker; ordinary imported events use neutral markers.

### Graphs

- Graphs must have a legend and a text alternative.
- Node positions remain stable when data has not changed.
- Edges represent real relationships: declared route, handoff, dependency, or evidence link.
- Blue edges mean declared structure; orange edges mean a decision or proposed change; dashed edges mean unverified or inferred.
- Do not animate graph layout on every render.
- Provide list and table views for users who do not use spatial diagrams.

### Search and status query

The global search bar is for finding projects, Skills, Squads, contracts, and evidence. A status query surface may answer read-only questions such as "What is the current team state?" It does not send coding instructions or start an Agent run.

## Interaction Rules

1. The current project and evidence freshness are always visible.
2. Every status claim links to its source record, command result, or explicit reason for being unverified.
3. Blue is for orientation and confirmed structure; orange is for change and human decisions.
4. A user can reach the same record through graph, list, and search views.
5. A visual change must not imply a source-file change unless an explicit local action is confirmed.
6. Archive and delete actions require a clear confirmation naming the exact project or capability.
7. Compare views align the same concepts across projects before showing differences.
8. Stale data is visible, not silently refreshed into apparent truth.
9. Long content opens in a readable detail surface; do not truncate evidence into tooltips.
10. Use optimistic UI only for reversible local view state, never for adoption, deprecation, authorization, or evidence claims.
11. Do not make the user remember internal Skill names to navigate normal project status.
12. Keyboard navigation and visible focus are first-class, not an afterthought.

## Data State Matrix

Every data-driven view must cover these states:

| State | Visual treatment | Required copy |
|---|---|---|
| Loading | Stable skeleton with preserved geometry | None or short loading label |
| Empty | Neutral surface, no fake metrics | What is missing and how it becomes available |
| Populated | Normal tokens | Source and freshness where relevant |
| Stale | Warning marker and timestamp | Last known time and refresh/index action |
| Partial | Neutral/orange boundary | Which projects or records are unavailable |
| Error | Danger surface with recovery action | What failed, scope, and retry path |
| Unverified | Neutral dashed marker | Explicitly state that the record is declarative |
| Success | Success token plus evidence link | What was verified and by which check |

## Motion

Motion communicates state, hierarchy, and continuity:

```css
--motion-fast: 120ms;
--motion-standard: 180ms;
--motion-slow: 280ms;
--motion-ease: cubic-bezier(.2, .8, .2, 1);
```

- Use 120ms for hover, focus, and icon feedback.
- Use 180ms for panels, tabs, and status transitions.
- Use 280ms for opening a detail surface or changing a view.
- Do not animate numbers unless the change itself is the subject of the view.
- Do not use bounce, shimmer, parallax, floating particles, or decorative loops.
- Graph transitions may interpolate only when topology changed and the destination remains understandable.
- Respect `prefers-reduced-motion: reduce`; remove transforms and non-essential transitions.

## Responsive Rules

Breakpoints are behavior boundaries, not device labels:

| Range | Behavior |
|---|---|
| `>= 1440px` | Full sidebar, 12-column portfolio, graph and evidence visible together |
| `1024-1439px` | Narrow sidebar, 8-column layout, evidence opens as a drawer |
| `768-1023px` | Collapsible navigation, stacked project summary, graph has explicit focus mode |
| `< 768px` | Bottom or drawer navigation, one primary column, graph becomes list-first |
| `< 480px` | Compact metadata, horizontal comparison scroll, no clipped labels |

Rules:

- Minimum touch target is 44x44px on touch devices.
- Do not shrink body text below 14px for the main application.
- Do not scale type directly with viewport width.
- Preserve stable geometry for cards, graph nodes, badges, and toolbar controls.
- On mobile, show project status and evolution before detailed topology.
- Tables may scroll horizontally; they must not compress into unreadable columns.

## Accessibility

- Meet WCAG AA contrast for body text and controls.
- Never use color as the only indicator of project state, evidence freshness, or graph relationship.
- Every graph has a list/table alternative and an accessible relationship description.
- Every icon-only control has a visible tooltip on hover and an accessible name.
- Use `:focus-visible` with a 2px blue outline and sufficient offset.
- Dialogs trap focus, restore focus on close, and expose an appropriate title.
- Status changes are announced without interrupting the user's current reading position.
- Support keyboard navigation for sidebar, tabs, timeline, tables, graph selection, and drawers.
- Support reduced motion and high-contrast browser settings.

## Target Cross-Tool Compatibility

The web observatory must be designed to ingest data from Claude Code, Codex CLI, OpenCode, Hermes, Cursor, GitHub Copilot, and other hosts through adapters. The visual language never assumes one host is the source of truth.

Adapters should normalize only these concepts:

- project identity and repository path;
- host and adapter version;
- Skill and Squad identifiers;
- contract and handoff references;
- evidence and verification records;
- execution provenance when the host exposes it;
- human decision events.

Host logos are small metadata markers, never the primary page decoration. Unsupported or partially connected hosts use the `Unverified` state instead of a guessed compatibility badge.

## Anti-Patterns

- No purple-dominated palette or purple-blue gradient default.
- No blue/orange gradient, mesh, glow, orb, bokeh, or glassmorphism.
- No oversized hero as the first application screen.
- No fake AI faces, robot illustrations, emoji as functional icons, or mascot teams.
- No task-chat composer or deployment button in the observatory.
- No card nested inside another card.
- No color-coded graph nodes without a legend and text labels.
- No unbounded rainbow palette for Skills.
- No orange for every notification, selected row, and primary action.
- No green badge that means only "the JSON parsed" while execution is unknown.
- No claims such as "healthy" or "optimized" without a visible basis.
- No hover-only actions, hidden critical information, or clipped long labels.
- No `z-index: 9999`; use a documented layer scale.
- No raw hex, `rgba`, or arbitrary shadow values outside token definitions.

## Layer and Z-Index Tokens

```css
--z-base: 0;
--z-raised: 10;
--z-sticky: 20;
--z-dropdown: 30;
--z-drawer: 40;
--z-modal: 50;
--z-toast: 60;
```

## Implementation Rules

- Prefer CSS custom properties with the token names in this document.
- Add new tokens only when an existing semantic token cannot express the intended meaning.
- Use Lucide or the host project's established icon library; do not hand-draw familiar UI icons.
- Keep page sections unframed; reserve cards for repeated items, dialogs, and genuinely framed tools.
- Keep data and method semantics in the domain model, not encoded only in CSS classes.
- Expose an event source and freshness timestamp for every visualized status.
- Build list and detail views before graph polish.
- Preserve stable dimensions for visualization nodes and repeated rows.
- Add visual regression coverage for light and dark themes at desktop and mobile widths.
- Test empty, stale, partial, unavailable, and unverified data before calling a view complete.

## Review Checklist

### Product meaning

- Does the screen help inspect or evolve a project AI engineering system?
- Is it clear whether a statement is configured, observed, verified, or unverified?
- Does the screen avoid becoming a task dispatcher or chat client?
- Are human decisions visible without implying that the UI executed them?

### Visual system

- Are all colors semantic tokens?
- Is blue used for structure and orange for change or human judgment?
- Is the palette balanced with neutral surfaces and semantic colors?
- Are there no gradients, orbs, glass panels, nested cards, or generic SaaS decorations?
- Are typography, radius, spacing, and elevation consistent with this document?

### Interaction and states

- Do controls cover default, hover, active, focus-visible, disabled, and loading?
- Does every data surface cover loading, empty, populated, stale, partial, error, and unverified?
- Can every graph relationship be understood in a list or table view?
- Are critical actions visible without hover and safe to cancel?

### Accessibility and responsive behavior

- Are contrast, focus, keyboard navigation, reduced motion, and touch targets covered?
- Does the mobile view prioritize project state and evolution over topology detail?
- Can long evidence, identifiers, and labels be read without overlap or clipping?

### Evidence integrity

- Does every health, evolution, and verification claim point to a source or explicitly say unverified?
- Does the UI distinguish an Agent-declared record from actual command or runtime evidence?
- Does the view show freshness and partial coverage instead of manufacturing completeness?
