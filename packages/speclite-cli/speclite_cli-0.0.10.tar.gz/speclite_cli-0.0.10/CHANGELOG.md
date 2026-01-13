# Changelog

All notable changes to the SpecLite CLI and templates are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.10] - 2026-01-05

### Changed

- Rename the CLI executable to `speclite-cli` (package remains `speclite-cli`).
- Docs now recommend running via `uvx speclite-cli ...` for bootstrapping.

## [0.0.9] - 2026-01-04

### Changed

- Rename `speclite init` to `speclite install`; `init` remains as a deprecated alias for compatibility with GitHub SpecKit.
- `speclite install` now always installs/updates SpecLite in the current project (no new project directory creation).

### Fixed

- Show option descriptions in `speclite init --help` so the deprecated alias matches `speclite install`.

## [0.0.8] - 2026-01-04

### Changed

- Combine duplicate `is_update` checks when printing the “Next Steps” and “Enhancement Commands” panels.
- Show a “Slash Commands” section in `speclite --help`, sharing the same command descriptions used by `speclite init` (and formatting for readability).
- Clarify that `/sl.review` is ideally run using a different AI agent than the implementer.

## [0.0.7] - 2026-01-04

### Fixed

- Error if bundled templates include any `*.default*` templates during staging so the live/default sync logic stays authoritative.
- Clean up small docstring/example and implementation nits in the template default path helpers.

## [0.0.6] - 2026-01-04

### Added

- `speclite check` now reports customized templates (live `.md` differs from `.default.md`), with a count and a quick diff hint.
- Update-time guidance for resolving template merges when defaults change while you have customizations, including a suggested `git merge-file` command.

### Changed

- Templates now install as paired files in `.speclite/templates/`: `<name>.default.md` (packaged baseline) and `<name>.md` (user-editable).
- Safe template upgrades: customized live templates are preserved; when defaults change, the previous default is backed up as `*.default.prev.md` and upgrade instructions are shown.
- `speclite init` treats an existing `.speclite/` directory as an update and blocks updates until any pending merges (`*.default.prev.md`) are resolved.
- Scripts now install to `.speclite/scripts/` (flattened; no `bash/`/`powershell/` subdirectories).
- Bundled command templates use explicit `.speclite/...` paths (no internal path rewriting during generation).

## [0.0.5] - 2025-12-20

### Changed

- Preserve existing `memory/constitution.md` when upgrading. The constitution template is now stored in `templates`, not `memory`, to allow this.


## [0.0.4] - 2025-12-19

### Changed

- Bundled `templates/`, `scripts/`, and `memory/` into the CLI wheel and generate agent command files locally during `speclite init` without GitHub downloads.
- Removed unused `--skip-tls` and `--github-token` options from `speclite init`.
- Removed unused GitHub template download helpers from the CLI.
- Simplified `speclite version` to show a single CLI version value.
- Removed unused `httpx` and `truststore` dependencies from the CLI package.
- Removed template package release workflow/scripts now that templates are bundled.
- Removed `docs/local-development.md` in favor of `CONTRIBUTING.md`.

## [0.0.3] - 2025-12-19

### Changed

- Added support for multiple AI agents in a project:
  - `speclite init --ai` accepts comma-separated agents and install templates for each selection.
  - The interactive UI supports multi-select for AI agents (defaults to none).

## [0.0.2] - 2025-12-19

### Changed

- Split template packaging into a core archive plus agent-specific archives, and install both during init.

## [0.0.1] - 2025-12-17

### Changed

- Started SpecLite as a fork of GitHub Spec Kit, taking the latest code as of https://github.com/github/spec-kit/commit/9111699cd27879e3e6301651a03e502ecb6dd65d (Spec Kit version 0.0.22 in `CHANGELOG.md`, released in https://github.com/github/spec-kit/releases/tag/v0.0.90). Will add new updates from Spec Kit from time to time.
