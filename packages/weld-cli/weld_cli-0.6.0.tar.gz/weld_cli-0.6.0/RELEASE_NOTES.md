### Added
- Interactive review prompt after step completion in `weld implement` command
  - Prompts user to review changes with optional auto-fixing via `weld review --diff [--apply]`
  - Non-blocking: review failures don't stop implement flow
  - Always available (independent of --auto-commit flag)

### Fixed
- Interactive menu cursor position in `weld implement` - now automatically positions on first incomplete step
- Makefile `bin-install` target now forces package rebuild with `--force` flag to pick up source changes
- **Critical**: EOFError handling in auto-commit prompt (now handles non-interactive environments)
- **Critical**: File I/O error handling in review prompt (disk full/permission errors no longer crash)
- **Critical**: Exception handling for review prompt generation
- Directory naming for review artifacts (sanitize step numbers with dots, e.g., "1.2" → "1-2")
- Added model parameter to review Claude invocations (respects configured model)
- Removed redundant git status check in review prompt (performance improvement)
- Config validation with safe defaults for review feature (graceful handling of malformed configs)
- Result validation for empty Claude output in reviews
- Consistent error messages across all non-blocking failures
- Security documentation for `skip_permissions` behavior in review auto-fix mode
