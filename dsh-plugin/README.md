# dsh-idc

Native DeepSeek Harness plugin for [Intent-Driven Coding](../README.md). It writes and
reads IDC task records without a Python runtime, while staying byte-compatible with the
reference implementation (`idc_core`).

## What you get

- Ten tools: `idc_status`, `idc_init`, `idc_start`, `idc_promote`, `idc_shape`,
  `idc_record`, `idc_transition`, `idc_close`, `idc_learning`, `idc_discard`.
- Eight IDC skills registered as runtime skills (`team`, `architecture`, `debug`,
  `code-review`, `verify`, `meta-skill-designer`, `skill-creator`,
  `learning-curator`).
- A resident prompt section: when the session workspace contains `.idc/`, the model is
  told the current record state and the IDC rules; it is not injected into projects
  without `.idc/`.

## Install (once per profile)

```powershell
# from a profile directory, or with the plugin manager UI
pnpm add link:D:/intent-driven-coding/dsh-plugin
```

Add `dsh-idc` to `dsh.profile.bundles` in the profile `package.json`, then restart the
DSH session. Remove the entry (and run `pnpm remove dsh-idc`) to uninstall. The bundle
runs in any workspace; it only writes when that workspace has `.idc/config.json` with
`schema_version: 2` and `idc_version: "1.2.0"`.

## Project setup

```powershell
python scripts/bootstrap.py --target <project> --project-name "<name>" --platform dsh --apply
```

This adds the IDC entry to `AGENTS.md` and eight Skills under `.dsh/skills/`. The plugin
can also initialize a repository itself: call `idc_init` (it writes
`.idc/config.json` with adapter `dsh`).

## Safety limits

- One writer at a time: the reference CLI and the plugin must not append concurrently.
- Records containing schema 1 events stay read-only; appends are refused.
- A protocol mismatch (`schema_version` or `idc_version`) refuses writes with the same
  message as the reference implementation.
- Evidence graded `human-confirmed` requires an explicit user confirmation in the
  current conversation (`human_confirmation: true`), otherwise the tool refuses.
- No custom session events and no second domain model: `.idc/events.jsonl` remains the
  single source of truth.

## Verification

```powershell
npm test
```

The suite compares this implementation with the Python reference over this repository
and the LAS corpus (event folding, rendered cards, six gate targets, rebuilt index),
replays the same write scenario in both implementations, and exercises the tools,
gate refusals, protocol mismatch and skill parsing.
