### High Priority

- [x] Fix installed-status detection in `src/brewse/cli.py`
  - Decide cask vs formula reliably (presence of `token` vs `name`, or pass category).
  - Prefer `brew list --formula <pkg>` / `--cask <pkg>` and check exit code.
  - Optionally cache one-time results of `brew list --formula` and `--cask` per session.

- [x] Remove recursive calls to `main()` from input handlers
  - Replace `self.main(stdscr, ...)` re-entries with view/state flags and loop control.

- [x] Implement a real Help view or remove the `h` binding
  - If implemented, add a `draw_help` branch and footer hints.

- [x] Resolve version mismatch
  - `pyproject.toml` has `0.1.1`, `src/brewse/__init__.py` has `0.1.0`.
  - Choose single source of truth (e.g., hatch version or `importlib.metadata`).

- [x] Align README Python version with project requirement
  - ✓ README updated to Python 3.7+, matching `pyproject.toml` requirement.

### Medium Priority

- [ ] Keep TUI running after install/uninstall
  - End curses for the command, then resume UI, refresh install status, show a notice.

- [x] Add proper CLI argument parsing with `argparse`
  - ✓ Implemented `--version`, `--refresh`, `--clear-cache`, `--help`
  - ✓ Supports optional positional search_term argument
  - Note: `--debug` and `--no-cache` can be added later if needed.

- [x] Improve loading/preload UX
  - ✓ Added real-time progress indicator with download progress bar on search prompt screen.
  - ✓ Uses HEAD request to get file sizes before download (formula: ~28MB, cask: ~13MB).
  - ✓ Shows "Preparing download..." → progress bar with MB/percentage → "✓ Ready to search".
  - ✓ Only downloads when cache is missing or stale (>24 hours).
  - Note: Full preload is necessary - Homebrew API doesn't provide a search endpoint.

- [ ] Handle small terminals and resizes defensively
  - Clamp all `addstr` widths, reflow on `KEY_RESIZE` for all views.

### Low Priority

- [x] Debounce installed checks
  - ✓ Implemented caching of `brew list --formula` and `--cask` results per session.
  - ✓ Cache invalidates after successful install/uninstall operations.
  - ✓ Dramatically improved search performance by avoiding N subprocess calls.

- [ ] Network robustness
  - Add retries with backoff; clearer offline messages; allow using cached data offline.

- [ ] Cache management improvements
  - ✓ Added `--clear-cache` option
  - TODO: Add `--max-age` option; guard JSON decode errors; stable cache filenames.

- [ ] Enrich project metadata in `pyproject.toml`
  - Add authors, keywords, classifiers, and `urls` (Homepage, Repository, Issues).
  - Prefer `license = { file = "LICENSE" }`; add `project.optional-dependencies.dev`.

- [ ] Automate versioning
  - Use hatch VCS versioning or a single source to prevent drift.

- [ ] CI and quality tooling
  - Add `ruff`/`black` with pre-commit; GitHub Actions to lint, test, and build wheels.

- [ ] Documentation upgrades
  - README: keybindings table, screenshot/GIF, known limitations, troubleshooting.


