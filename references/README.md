# References

This directory stores external research, independent reviews, host acceptance records, and other supporting material that informs Intent-Driven Coding decisions.

Reference material is evidence or input, not normative project behavior. Current requirements and implementation commitments live in `plans/`, the root documentation, contracts, and executable checks.

## Files

- `external-review-2026-07-25.md`: Raw independent review produced from a cold-start clone. It is preserved as received, including duplicated sections and conclusions that require later validation.
- `host-acceptance/README.md`: Manual record template and interpretation rules for real host acceptance runs.
- `host-acceptance/opencode-1.18.5-2026-07-26.md`: Partial OpenCode pilot using a disposable fixture. It records observed route gaps and does not establish compatibility.
- `host-acceptance/opencode-1.18.5-controller-2026-07-26.md`: Mismatched experimental-controller acceptance. Project Agents were listed, but the exported OpenCode session recorded generic `build` instead of requested `debug` and did not reach a handoff or command result.
- `host-acceptance/claude-code-2.1.154-2026-07-26.md`: Partial Claude Code pilot using the non-leaking fixture. It records model, budget, route, handoff, and permission gaps without establishing compatibility.

## Rules

- Preserve raw external reports when possible; add a separate decision or plan instead of silently rewriting a source.
- Record source, date, scope, and any commands actually run.
- Mark claims from external material as unverified until repository evidence, host acceptance, or user research confirms them.
- Do not store credentials, private repositories, personal paths, or production logs here.
