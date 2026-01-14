### Added
- Native transcript generation (replaces external `claude-code-transcripts` binary)
  - Session detection: Automatically finds Claude Code sessions from `~/.claude/projects/`
  - Session tracking: Records file changes during weld commands
  - Transcript rendering: Converts Claude JSONL sessions to markdown with:
    - Secret redaction (API keys, tokens, credentials)
    - Content truncation (tool results, thinking blocks)
    - Size limits (per-message and total)
  - Gist upload: Publishes transcripts to GitHub Gists via `gh` CLI
- Automatic session tracking in `weld implement` command for commit provenance
- Config migration for `[claude.transcripts]` → `[transcripts]` format
- File snapshot timeout protection for large repositories
- Session models: `SessionActivity`, `TrackedSession` in `weld.models`
- Session services: `session_detector`, `session_tracker`, `transcript_renderer`, `gist_uploader`
- `get_sessions_dir()` helper in `weld.core.weld_dir`
- Session-based commit grouping: `weld commit` now groups files by originating Claude session
  - Each session gets its own commit with transcript attached
  - `--no-session-split` flag to disable session-based grouping
- MkDocs documentation site with Material theme
  - Full command reference and configuration docs
  - GitHub Actions workflow for automatic deployment to GitHub Pages
  - Makefile targets: `docs`, `docs-build`, `docs-deploy`, `docs-version`
  - Versioned documentation support via mike
- Codebase exploration guidance in `weld plan` prompts
  - Instructs Claude to explore the codebase structure before planning
  - Requires identification of relevant files and existing patterns
  - Grounds plans in concrete code locations and line numbers
- Documentation clarifying `weld implement` session behavior
  - Each step execution is an independent Claude CLI invocation with fresh context
  - No conversational memory between steps
  - Session tracking is for commit grouping, not conversational context
- `--auto-commit` flag for `weld implement` command
  - Prompts user to commit changes after each step completes successfully
  - Automatically stages all changes (like `weld commit --all`)
  - Creates session-based commits with transcript attachment
  - Non-blocking: commit failures don't stop the implement flow
  - Skips prompt if no changes detected during the step
  - Manual session recording ensures transcripts are included in mid-execution commits

### Changed
- Transcript configuration moved from `[claude.transcripts]` to top-level `[transcripts]`
  - Automatic migration from old config format
  - New `enabled` field to toggle transcript generation
  - Removed `exec` field (no longer needed with native implementation)
- Simplified README.md, moved detailed content to documentation site
- `weld commit` now uses native transcript rendering instead of external binary
- `weld implement` now automatically tracks file changes (no flag required)
- Session-based commits fully functional with implement workflow
- Registry pruning after successful commits to keep registry clean
- Makefile `bump-*` targets now automatically run `uv sync` after version update

### Fixed
- Session tracking gracefully handles missing Claude sessions
- File snapshot performance improved for large repositories (5s timeout)
- Config migration creates backup and safely rolls back on errors

### Removed
- `--edit/-e` flag from `weld commit` (use `git commit --amend` to edit after)
