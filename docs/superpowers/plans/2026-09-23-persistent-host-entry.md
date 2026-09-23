# Persistent Host Entry Integration

## Overview

Make IDC's always-loaded host entry a short managed pointer to `IDC.md`, preserving existing project instructions. Clarify installation commands and distinguish file generation from host acceptance.

## File Structure

- `templates/IDC_ENTRY.md` — managed, minimal IDC instruction block for host-recognized entry files.
- `scripts/bootstrap.py` — choose the host entry, preview an insertion/update, and apply it idempotently without replacing surrounding content.
- `tests/test_progressive_distribution.py` and `tests/test_repository.py` — cover first install, existing-file preservation, reruns, dry-run, and host mapping.
- `AI_START_HERE.md`, `docs/INSTALLATION.md`, `docs/PLATFORM_ADAPTERS.md`, `docs/CLAUDE_CODE_ADAPTER.md`, `docs/OPENCODE_ADAPTER.md`, `QUICKSTART.md`, and relevant README sections — state the actual support boundary and reproducible commands.

## Tasks

### Task 1: Define and test the managed entry behavior
- [ ] Add failing tests for Codex/OpenCode `AGENTS.md` and Claude Code `CLAUDE.md` hook insertion.
- [ ] Cover existing user text, idempotent rerun, and dry-run non-mutation.
- [ ] Run the focused tests and confirm the expected failures.

### Task 2: Implement safe, idempotent integration
- [ ] Add one short entry template that points to the full IDC rules in `IDC.md`.
- [ ] Extend bootstrap planning to preview insertion into the correct host entry and preserve all text outside IDC markers.
- [ ] Apply changes only with `--apply`; do not overwrite existing entry files or require `--force` for managed insertion.
- [ ] Run focused tests and confirm they pass.

### Task 3: Make installation instructions executable
- [ ] Document editable package installation for the `idc` CLI.
- [ ] Document plugin/config/scaffold commands per supported host and safe behavior when entry files already exist.
- [ ] State that structural installation is not host acceptance; list what is community-only or unverified.
- [ ] Run repository validation, focused tests, and the full test suite where practical.

## Testing Strategy

- Verify existing `AGENTS.md`/`CLAUDE.md` bytes outside the managed block remain unchanged.
- Verify a second apply does not duplicate the IDC block and updates only that block if its template changes.
- Verify dry-run reports the proposed integration while leaving the target unchanged.
- Verify a clean Codex scaffold puts the IDC block before the architecture template and a Claude Code scaffold creates the root entry.
- Run `python -m unittest discover -s tests -v` and the repository validation scripts.

## Completion Criteria

- [ ] Host entries include a concise IDC hook and point to full rules kept in separate files.
- [ ] Existing host instructions are preserved and the integration is repeatable.
- [ ] Installation docs contain the commands needed to install the CLI and connect each documented host.
- [ ] Documentation makes no compatibility claim beyond recorded host acceptance.
- [ ] Tests and validators pass, or any environment-specific failures are recorded precisely.
