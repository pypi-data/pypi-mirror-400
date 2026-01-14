# Claude Development Guide for MarkDeck

This comprehensive guide contains everything AI assistants need to know when working on the MarkDeck project.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Development Environment](#development-environment)
4. [Architecture](#architecture)
5. [Core Components](#core-components)
6. [Testing](#testing)
7. [GitHub Actions Workflows](#github-actions-workflows)
8. [Network Restrictions](#network-restrictions)
9. [Git Workflow](#git-workflow)
10. [Common Development Tasks](#common-development-tasks)
11. [Code Style and Conventions](#code-style-and-conventions)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

**MarkDeck** is a lightweight, markdown-based presentation tool that runs locally.

**Key Information:**
- **Language:** Python 3.11+
- **Framework:** FastAPI (backend), Vanilla JS (frontend)
- **Package Manager:** uv (fast Python package manager)
- **License:** MIT
- **Current Version:** 0.3.0
- **Main Branch:** (varies - check git status)

**Core Features:**
- Markdown-based presentations with hot reload
- Grid view for slide navigation (press `O`)
- Theme cycling (dark/light themes, press `T`)
- Speaker notes support
- Syntax highlighting for code blocks
- Mermaid diagram support
- Math equations with KaTeX
- WebSocket-based hot reloading

---

## Repository Structure

```
markdeck/
├── .claude/                         # Claude Code configuration
│   ├── settings.json               # Hooks configuration (SessionStart)
│   └── commands/                   # Custom slash commands
│       └── implement-feature.md    # Feature implementation command
│
├── .github/workflows/               # GitHub Actions CI/CD
│   ├── screenshots.yml             # Automated screenshot generation
│   ├── claude.yml                  # Claude Code integration
│   ├── claude-code-review.yml      # Code review automation
│   └── README.md                   # Workflow documentation
│
├── .venv/                           # Python virtual environment (uv-based)
│   └── bin/                        # Executables (python, markdeck, etc.)
│
├── markdeck/                        # Main Python package
│   ├── __init__.py                 # Package initialization (version info)
│   ├── __main__.py                 # Entry point for `python -m markdeck`
│   ├── cli.py                      # Click-based CLI interface (312 lines)
│   ├── server.py                   # FastAPI server (234 lines)
│   ├── parser.py                   # Markdown slide parser (211 lines)
│   ├── watcher.py                  # File watcher for hot reload (38 lines)
│   └── static/                     # Frontend assets
│       ├── index.html              # Main presentation viewer (107 lines)
│       ├── style.css               # Main styles (467 lines)
│       ├── slides.js               # Presentation controller (593 lines)
│       ├── dark.css                # Dark theme variables (14 lines)
│       └── light.css               # Light theme variables (14 lines)
│
├── tests/                           # Unit tests
│   ├── __init__.py
│   ├── test_parser.py              # Parser tests
│   └── test_server.py              # Server/API tests
│
├── examples/                        # Example presentations
│   ├── features.md                 # Comprehensive feature showcase
│   └── code-examples.md            # Code syntax highlighting demo
│
├── screenshots/                     # Generated screenshots
│   ├── README.md                   # Screenshot documentation
│   └── *.png                       # Grid view and theme screenshots
│
├── scripts/                         # Utility scripts
│   └── install.sh                  # SessionStart hook installation script
│
├── capture_screenshots.py          # Playwright screenshot script (grid view and themes)
├── pyproject.toml                  # Python project configuration
├── package.json                    # Node.js config (for jest, if used)
├── publish.sh                      # PyPI publishing script
├── .gitignore                      # Git ignore patterns
├── .python-version                 # Python version specification
├── LICENSE                         # MIT License
├── README.md                       # User-facing documentation
├── CLAUDE.md                       # This file
├── GRID_VIEW_FEATURE.md            # Grid view feature documentation
├── PLAYWRIGHT_NETWORK_CONFIG.md    # Network restriction details
├── SCREENSHOT_METHODS.md           # Screenshot generation methods
└── ROADMAP_TASKS.md                # Future development tasks
```

---

## Development Environment

### Python Version

**Required:** Python 3.11 or higher

```bash
# Check Python version
python --version
# or
cat .python-version
```

### Virtual Environment

This project uses a **uv-based** virtual environment located at `.venv/`.

**CRITICAL:** The venv does **NOT** have `pip` installed. **Always use `uv` for package management.**

#### Activating the Virtual Environment

```bash
# Method 1: Use full path (recommended)
.venv/bin/python script.py
.venv/bin/markdeck present examples/features.md

# Method 2: Activate environment
source .venv/bin/activate
python script.py
markdeck present examples/features.md
deactivate  # when done
```

### Package Management with uv

**Installation:**
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Check uv version
uv --version
```

**Common uv Commands:**
```bash
# Install package
uv pip install <package> --python .venv/bin/python

# Install from requirements
uv pip install -r requirements.txt --python .venv/bin/python

# Install project in editable mode
uv pip install -e . --python .venv/bin/python

# Install with extras
uv pip install -e ".[dev]" --python .venv/bin/python
uv pip install -e ".[screenshots]" --python .venv/bin/python

# List installed packages
.venv/bin/python -m pip list

# Sync dependencies (in remote environments)
uv sync --extra dev
```

**Project Dependencies** (from `pyproject.toml`):
- **Core:** fastapi, uvicorn, markdown, click, watchfiles
- **Dev:** pytest, pytest-asyncio, ruff, httpx, build, twine
- **Screenshots:** playwright

### SessionStart Hook

The repository includes a SessionStart hook that runs on Claude Code session start (remote environments only).

**File:** `.claude/settings.json`
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "type": "command",
        "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/install.sh"
      }]
    }]
  }
}
```

**Script:** `scripts/install.sh`
- Only runs in remote environments (`CLAUDE_CODE_REMOTE=true`)
- Executes `uv sync --extra dev` to install dependencies

---

## Architecture

### High-Level Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   CLI       │────────▶│  FastAPI     │────────▶│  Parser     │
│  (cli.py)   │         │  (server.py) │         │ (parser.py) │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │                         │
      │                        │                         │
      ▼                        ▼                         ▼
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Watcher    │────────▶│  WebSocket   │────────▶│  Frontend   │
│(watcher.py) │         │  (server.py) │         │  (slides.js)│
└─────────────┘         └──────────────┘         └─────────────┘
```

### Request Flow

1. **User runs:** `markdeck present slides.md --watch`
2. **CLI** (`cli.py`) validates file, configures server
3. **Server** (`server.py`) starts FastAPI app, mounts static files
4. **Browser** opens to `http://127.0.0.1:8000`
5. **Frontend** (`slides.js`) fetches `/api/slides`
6. **Parser** (`parser.py`) parses markdown into slide objects
7. **Server** returns JSON with slides
8. **Frontend** renders slides with marked.js
9. **Watcher** (optional) monitors file for changes
10. **WebSocket** notifies frontend to reload on file change

### File Watching Flow (Hot Reload)

```
File Change ─▶ watchfiles ─▶ watcher.py ─▶ notify_clients_reload() ─▶ WebSocket ─▶ slides.js ─▶ Reload Slides
```

---

## Core Components

### 1. CLI (`markdeck/cli.py`)

**Purpose:** Command-line interface using Click

**Commands:**
- `markdeck present <file>` - Start presentation server
  - `--port, -p` - Port (default: 8000)
  - `--host, -h` - Host (default: 127.0.0.1)
  - `--watch, -w` - Enable hot reload
  - `--no-browser` - Don't open browser automatically
- `markdeck init <file>` - Create new presentation from template
  - `--title, -t` - Custom title
- `markdeck validate <file>` - Validate markdown file
- `markdeck --version` - Show version

**Key Functions:**
- `present()` - Main presentation command
- `init()` - Template creation
- `validate()` - File validation
- `_watch_file_async()` - Async file watcher

### 2. Server (`markdeck/server.py`)

**Purpose:** FastAPI backend serving presentation API

**Endpoints:**
- `GET /` - Main HTML viewer
- `GET /api/slides` - Parse and return slides as JSON
- `GET /api/watch-enabled` - Check if watch mode is on
- `GET /assets/{file_path}` - Serve images/assets from presentation directory
- `GET /health` - Health check
- `POST /api/log-notes` - Log speaker notes to terminal
- `WS /ws` - WebSocket for hot reload

**Global State:**
- `_current_file` - Current presentation file path
- `_watch_enabled` - Whether watch mode is enabled
- `_websocket_clients` - Connected WebSocket clients

**Key Functions:**
- `set_presentation_file()` - Set current file
- `enable_watch_mode()` - Enable/disable watch
- `notify_clients_reload()` - Send reload message to clients

### 3. Parser (`markdeck/parser.py`)

**Purpose:** Parse markdown files into slide objects

**Classes:**
- `Slide` - Represents a single slide
  - `content` - Markdown content (notes and columns removed/transformed)
  - `notes` - Speaker notes
  - `index` - Slide number (0-based)
  - `_extract_notes()` - Extract `<!--NOTES:...-->` comments
  - `_transform_columns()` - Transform `:::columns` syntax into HTML comment markers
  - `to_dict()` - Convert to JSON-serializable dict

- `SlideParser` - Parse markdown into slides
  - `SLIDE_DELIMITER = "---"` - Slide separator
  - `parse()` - Parse file into Slide list
  - `parse_content()` - Parse markdown string (class method)
  - `get_title()` - Extract presentation title (first H1)
  - `to_json()` - Return full JSON with slides and metadata

**Slide Delimiter:** Slides are separated by `---` on its own line

**Two-Column Layout Support:**
- Syntax: `:::columns` ... `|||` ... `:::`
- The `_transform_columns()` method converts this syntax into HTML comment markers
- Markdown content is preserved (not pre-rendered) to allow frontend features like mermaid.js to work
- Code blocks are protected from transformation to prevent transforming example syntax
- Resulting marker structure sent to frontend:
  ```
  <!-- COLUMN:LEFT:START -->
  Left column markdown (raw)
  <!-- COLUMN:LEFT:END -->
  <!-- COLUMN:RIGHT:START -->
  Right column markdown (raw)
  <!-- COLUMN:RIGHT:END -->
  ```
- The frontend (slides.js) processes markers BEFORE marked.parse(), extracts markdown from each column, parses separately, then builds the HTML structure:
  ```html
  <div class="columns-container">
    <div class="column-left">..rendered HTML..</div>
    <div class="column-right">..rendered HTML..</div>
  </div>
  ```
- This approach allows mermaid diagrams, code blocks, KaTeX equations, and other features to work correctly in columns

### 4. Watcher (`markdeck/watcher.py`)

**Purpose:** Watch markdown file for changes and trigger reload

**Dependencies:** `watchfiles` library

**Functions:**
- `watch_file(file_path)` - Async watch loop
  - Uses `awatch()` from watchfiles
  - Calls `notify_clients_reload()` on change
  - Runs indefinitely

### 5. Frontend (`markdeck/static/`)

#### `slides.js` (593 lines)

**Main Class:** `SlideShow`

**Key Methods:**
- `init()` - Initialize marked.js, load slides, setup listeners
- `loadSlides()` - Fetch slides from `/api/slides`
- `processColumnMarkers(markdown)` - Process column markers before parsing (extracts and renders columns)
- `showSlide(index)` - Render specific slide
- `nextSlide()` / `prevSlide()` - Navigation
- `toggleGrid()` - Show/hide grid overview
- `toggleTheme()` - Cycle through themes (dark/light)
- `toggleFullscreen()` - Fullscreen mode
- `setupHotReload()` - Connect to WebSocket for live reload
- `handleKeyPress(e)` - Keyboard navigation

**Keyboard Shortcuts:**
- `→ / Space / PageDown` - Next slide
- `← / PageUp` - Previous slide
- `Home` - First slide
- `End` - Last slide
- `O` - Toggle grid overview
- `T` - Toggle theme
- `F` - Fullscreen
- `?` - Help overlay
- `Esc` - Exit overlay/fullscreen

**External Libraries (CDN):**
- marked.js - Markdown parsing
- highlight.js - Code syntax highlighting
- mermaid.js - Diagram rendering
- KaTeX - Math equations

#### `style.css` (467 lines)

**Features:**
- CSS variables for theming
- Responsive slide layout
- Grid view styling
- Fullscreen support
- Help overlay
- Progress bar
- Mermaid diagram dark theme integration

#### `dark.css` / `light.css` (14 lines each)

**Theme Variables:**
```css
/* dark.css */
--bg-color, --text-color, --accent-color, --border-color, --code-bg, etc.

/* light.css */
/* Same variables, light theme values */
```

---

## Testing

### Test Structure

```
tests/
├── __init__.py
├── test_parser.py          # Parser unit tests
└── test_server.py          # Server/API tests
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests/

# Run with verbose output
python -m unittest discover tests/ -v

# Run specific test file
python -m unittest tests.test_parser

# Run with pytest (if installed)
pytest tests/
pytest tests/ -v
pytest tests/test_parser.py::TestSlide::test_slide_creation
```

### Test Coverage

**Parser Tests** (`test_parser.py`):
- Slide creation
- Speaker notes extraction
- Slide-to-dict conversion
- Empty slide handling
- SlideParser file parsing
- Title extraction

**Server Tests** (`test_server.py`):
- API endpoint testing
- File serving
- WebSocket connections
- Health checks

### Writing Tests

Follow these conventions:
- Use `unittest` framework
- Test classes inherit from `unittest.TestCase`
- Test method names start with `test_`
- Use descriptive docstrings
- Test both success and failure cases
- Use `tempfile` for file-based tests

---

## GitHub Actions Workflows

### 1. Screenshot Generation (`.github/workflows/screenshots.yml`)

**Triggers:**
- Manual: `workflow_dispatch`
- Push: Changes to `markdeck/static/**` or `examples/**`
- Pull Request: Changes to same paths

**Workflow:**
1. Checkout repository (PR branch if applicable)
2. Install Python 3.11 and uv
3. Install MarkDeck with `[screenshots]` extra
4. Install Playwright browsers (chromium)
5. Start MarkDeck server on port 8888
6. Run `capture_screenshots.py` (captures both grid view and theme screenshots)
7. Upload screenshots as artifacts
8. Commit screenshots back to branch (if same repo)

**Important Notes:**
- Fork PRs only get artifacts, not commits (can't push to fork)
- Uses `[skip ci]` in commit message to avoid loops
- Requires `contents: write` and `pull-requests: write` permissions

### 2. Claude Code Integration (`.github/workflows/claude.yml`)

**Triggers:**
- Issue comments containing `@claude`
- PR review comments containing `@claude`
- PR reviews containing `@claude`
- Issues opened/assigned with `@claude` in title/body

**Features:**
- Uses `anthropics/claude-code-action@v1`
- Requires `CLAUDE_CODE_OAUTH_TOKEN` secret
- Has `actions: read` permission for CI results

### 3. Code Review (`.github/workflows/claude-code-review.yml`)

**Purpose:** Automated code review on PRs (details in file)

---

## Network Restrictions

### Blocked Domains

This environment has network restrictions that block:
- `playwright.dev`
- `cdn.playwright.dev`
- `storage.googleapis.com`
- `playwright.download.prss.microsoft.com`

### Impact

**Cannot:**
- Download Playwright browser binaries locally
- Install ChromeDriver
- Access some CDN resources

**Error Message:**
```
Error: Download failed: server returned code 403 body 'Host not allowed'
```

### Workarounds

1. **GitHub Actions** (Recommended)
   - Use `.github/workflows/screenshots.yml`
   - GitHub runners have full network access
   - Automatically generates and commits screenshots

2. **Manual Screenshots**
   - Use browser developer tools
   - Take screenshots manually

3. **Pre-installed Browsers**
   - Check for system Chrome/Chromium
   - Use Selenium with system browsers (if available)

### What Works

- ✅ Installing Playwright Python package: `uv pip install playwright`
- ✅ Running Playwright in GitHub Actions
- ❌ Installing browsers locally: `playwright install chromium`

**Documentation:** See `PLAYWRIGHT_NETWORK_CONFIG.md` for details

---

## Git Workflow

### Branch Naming Convention

**CRITICAL:** When pushing to remote, branch name MUST:
- Start with `claude/`
- End with the session ID (if applicable)
- Example: `claude/add-feature-ABC123`

**Reason:** Push permissions are restricted to branches matching this pattern. Otherwise, you'll get a 403 error.

### Current Branch

Check the current branch context from the system prompt or:
```bash
git branch --show-current
```

### Committing Changes

**Guidelines:**
- Write clear, descriptive commit messages
- Focus on "why" rather than "what"
- Use conventional commit format (optional but recommended)
  - `feat: Add grid view toggle`
  - `fix: Correct slide navigation bug`
  - `docs: Update README with new features`
  - `refactor: Simplify parser logic`
  - `test: Add parser unit tests`

**Commit Workflow:**
```bash
# Stage changes
git add <files>

# Commit with message
git commit -m "Description of changes"

# Check status
git status
```

### Pushing Changes

**IMPORTANT:** Use `-u` flag and retry logic for network errors.

```bash
# Push to branch
git push -u origin <branch-name>

# Example
git push -u origin claude/add-feature-ABC123
```

**Retry Logic:**
- If push fails due to network errors, retry up to 4 times
- Exponential backoff: 2s, 4s, 8s, 16s
- Same applies to `git fetch` and `git pull`

### Pull Requests

**Creating PRs:**
```bash
# Ensure changes are pushed
git push -u origin <branch-name>

# Create PR using gh CLI
gh pr create --title "Title" --body "Description"

# With heredoc for formatting
gh pr create --title "Add feature X" --body "$(cat <<'EOF'
## Summary
- Change 1
- Change 2

## Test plan
- [ ] Test A
- [ ] Test B
EOF
)"
```

### Git Safety

- **NEVER** update git config
- **NEVER** run destructive commands (`push --force`, `reset --hard`) without user confirmation
- **NEVER** skip hooks (`--no-verify`, `--no-gpg-sign`) unless explicitly requested
- **NEVER** force push to `main`/`master`
- **Avoid** `git commit --amend` (only use when explicitly requested or fixing pre-commit hooks)
- **Always** check authorship before amending: `git log -1 --format='%an %ae'`

---

## Common Development Tasks

### Start Development Server

```bash
# Basic
.venv/bin/markdeck present examples/features.md

# With hot reload
.venv/bin/markdeck present examples/features.md --watch

# Custom port, no browser
.venv/bin/markdeck present examples/features.md --port 8888 --no-browser

# Background (for screenshot capture)
.venv/bin/markdeck present examples/features.md --port 8888 --no-browser &

# Verify server is running
curl -f http://127.0.0.1:8888/ -o /dev/null -w "HTTP Status: %{http_code}\n"
# Should return: HTTP Status: 200
```

### Check Server Status

```bash
# Check if server is running
curl http://127.0.0.1:8888/ -I

# Test API endpoint
curl http://127.0.0.1:8888/api/slides

# Check specific static file
curl http://127.0.0.1:8888/static/slides.js | grep "toggleGrid"
```

### Kill Background Processes

```bash
# Kill MarkDeck server
pkill -f "markdeck present"

# Check for running processes
ps aux | grep markdeck
```

### Run Tests

```bash
# All tests
python -m unittest discover tests/

# Verbose
python -m unittest discover tests/ -v

# Specific test
python -m unittest tests.test_parser
```

### Code Quality

```bash
# Run linter
ruff check markdeck/ tests/

# Auto-fix issues
ruff check --fix markdeck/ tests/

# Format code
ruff format markdeck/ tests/

# Check specific file
ruff check markdeck/cli.py
```

### Build and Publish (PyPI)

```bash
# Build distribution
python -m build

# Check distribution
twine check dist/*

# Test upload (TestPyPI)
twine upload --repository testpypi dist/*

# Production upload (use workflow instead)
# See: .github/workflows/publish.yml
```

### Install from Local Clone

```bash
# Editable install
uv pip install -e . --python .venv/bin/python

# With dev dependencies
uv pip install -e ".[dev]" --python .venv/bin/python

# With screenshot dependencies
uv pip install -e ".[screenshots]" --python .venv/bin/python
```

### Clear uv Cache

```bash
# Prune cache
uv cache prune --force

# Clean specific package
uv cache clean markdeck

# Run from local directory
uvx . present examples/features.md --watch
```

---

## Code Style and Conventions

### Python Style

**Configuration:** `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []
```

**Guidelines:**
- **Line length:** 100 characters max
- **Imports:** Sorted alphabetically, grouped (standard, third-party, local)
- **Naming:**
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_CASE`
  - Private: prefix with `_`
- **Type hints:** Use modern Python 3.11+ syntax
  - `str | None` instead of `Optional[str]`
  - `list[Slide]` instead of `List[Slide]`
- **Docstrings:** Google style
  ```python
  def function(arg: str) -> bool:
      """
      Short description.

      Args:
          arg: Argument description

      Returns:
          Return value description
      """
  ```

### JavaScript Style

**Guidelines:**
- Use modern ES6+ syntax
- Class-based components for main logic
- camelCase for variables/functions
- PascalCase for classes
- Clear, descriptive variable names
- Comments for complex logic

### File Naming

- Python: `snake_case.py`
- JavaScript: `kebab-case.js` or `camelCase.js`
- CSS: `kebab-case.css`
- Markdown: `UPPER_CASE.md` for docs, `kebab-case.md` for content

---

## Troubleshooting

### Issue: `playwright` module not found after installation

**Cause:** Installed with system pip instead of venv

**Solution:**
```bash
uv pip install playwright --python .venv/bin/python
.venv/bin/python script.py
```

### Issue: `markdeck: command not found`

**Cause:** Not using venv binary

**Solution:**
```bash
.venv/bin/markdeck present examples/features.md
# or
source .venv/bin/activate
markdeck present examples/features.md
```

### Issue: Playwright browser download fails with 403

**Cause:** Network restrictions block CDN domains

**Solution:** Use GitHub Actions workflow instead:
1. Push changes to branch
2. Trigger `.github/workflows/screenshots.yml` manually or via PR
3. Screenshots are generated and committed automatically

### Issue: Server won't start (port already in use)

**Cause:** Previous server still running

**Solution:**
```bash
# Kill existing server
pkill -f "markdeck present"

# Or use different port
.venv/bin/markdeck present examples/features.md --port 8888
```

### Issue: Hot reload not working

**Cause:** Watch mode not enabled or WebSocket connection failed

**Solution:**
```bash
# Ensure --watch flag is used
.venv/bin/markdeck present examples/features.md --watch

# Check browser console for WebSocket errors
# Check server logs for file watcher messages
```

### Issue: Git push fails with 403

**Cause:** Branch name doesn't match required pattern

**Solution:**
```bash
# Ensure branch starts with 'claude/' and includes session ID
git checkout -b claude/feature-name-SESSION_ID
git push -u origin claude/feature-name-SESSION_ID
```

### Issue: Tests failing after code changes

**Cause:** Code changes broke existing tests or tests need updating

**Solution:**
```bash
# Run tests with verbose output
python -m unittest discover tests/ -v

# Check specific failing test
python -m unittest tests.test_parser::TestSlide::test_slide_creation

# Update tests to match new behavior (if intentional)
```

### Issue: Import errors when running scripts

**Cause:** Not using venv Python or missing dependencies

**Solution:**
```bash
# Use venv Python
.venv/bin/python script.py

# Install missing dependencies
uv pip install <package> --python .venv/bin/python

# Reinstall project
uv pip install -e . --python .venv/bin/python
```

---

## Quick Reference Commands

```bash
# === Environment ===
uv --version                          # Check uv version
.venv/bin/python --version            # Check Python version
.venv/bin/python -m pip list          # List installed packages

# === Development ===
.venv/bin/markdeck present slides.md --watch    # Start with hot reload
.venv/bin/markdeck init new.md                  # Create new presentation
.venv/bin/markdeck validate slides.md           # Validate markdown

# === Testing ===
python -m unittest discover tests/ -v           # Run all tests
ruff check markdeck/ tests/                     # Lint code
ruff format markdeck/ tests/                    # Format code

# === Server Management ===
curl http://127.0.0.1:8888/ -I                  # Check server
pkill -f "markdeck present"                     # Kill server
lsof -ti:8888 | xargs kill -9                   # Kill by port

# === Git ===
git status                                       # Check status
git add . && git commit -m "message"             # Stage and commit
git push -u origin claude/branch-name            # Push to remote
gh pr create --title "Title" --body "Body"       # Create PR

# === Package Management ===
uv pip install <package> --python .venv/bin/python
uv pip install -e ".[dev]" --python .venv/bin/python
uv cache prune --force
```

---

## Additional Resources

### Documentation Files

- **README.md** - User-facing documentation
- **GRID_VIEW_FEATURE.md** - Grid view implementation details
- **PLAYWRIGHT_NETWORK_CONFIG.md** - Network restriction details
- **SCREENSHOT_METHODS.md** - Screenshot generation approaches
- **ROADMAP_TASKS.md** - Future development roadmap
- **LICENSE** - MIT License text

### External Links

- [uv Documentation](https://github.com/astral-sh/uv)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Playwright Python](https://playwright.dev/python/)
- [Click Documentation](https://click.palletsprojects.com/)
- [marked.js](https://marked.js.org/)
- [Mermaid.js](https://mermaid.js.org/)

---

## Tips for AI Assistants

1. **Always use `uv` for package management**, never `pip` directly
2. **Use full path `.venv/bin/python`** for running scripts
3. **Remember network restrictions** - don't try to download browser binaries locally
4. **GitHub Actions is the way** to generate screenshots
5. **Server must be started from venv:** `.venv/bin/markdeck`
6. **Check if background server is running** before starting a new one
7. **Branch naming is critical** for push permissions (`claude/...`)
8. **Read existing code first** before making changes
9. **Run tests after changes** to ensure nothing breaks
10. **Follow the roadmap** in ROADMAP_TASKS.md for future features
11. **Update this file (CLAUDE.md)** when you discover new patterns or solutions
12. **Ask for clarification** if requirements are ambiguous
13. **Keep changes minimal** - avoid over-engineering
14. **Document your changes** in commit messages and code comments

---

**Last Updated:** 2026-01-04
**For Claude Code Sessions**
**Version:** 1.0 (Comprehensive)
