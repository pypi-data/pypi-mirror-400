# MarkDeck Roadmap Tasks

This file contains planned tasks and issues for MarkDeck development. Once Beads is installed, these can be converted to Beads tasks.

## High Priority Tasks

### Feature: Multiple Themes
**Priority:** High
**Status:** Ready
**Description:** Add support for multiple presentation themes beyond the current dark theme.

**Sub-tasks:**
- Design light theme color scheme
- Implement theme switcher UI component
- Add theme persistence (localStorage)
- Create theme CSS variables system
- Add keyboard shortcut for theme toggle (e.g., 'T')
- Update documentation with theme information

**Dependencies:** None

---

### Feature: Slide Overview/Grid View
**Priority:** High
**Status:** Ready
**Description:** Implement a grid view showing thumbnails of all slides for quick navigation.

**Sub-tasks:**
- Design grid layout UI
- Implement thumbnail generation for each slide
- Add keyboard shortcut to toggle grid view (e.g., 'G' or 'Esc')
- Add click-to-navigate functionality
- Ensure responsive design for grid view
- Add visual indicator for current slide in grid

**Dependencies:** None

---

### Feature: Export to PDF
**Priority:** High
**Status:** Ready
**Description:** Add ability to export presentations to PDF format.

**Sub-tasks:**
- Research PDF generation libraries (puppeteer, playwright, weasyprint)
- Implement PDF export command in CLI
- Ensure proper page breaks between slides
- Handle code blocks and mermaid diagrams in PDF
- Add option for different page sizes (16:9, 4:3, A4)
- Update documentation with export instructions

**Dependencies:** None

---

## Medium Priority Tasks

### Feature: Slide Transitions
**Priority:** Medium
**Status:** Ready
**Description:** Add configurable slide transition animations.

**Sub-tasks:**
- Design transition effect options (fade, slide, none)
- Implement CSS transitions
- Add configuration option to markdown frontmatter
- Make transitions accessible (respects prefers-reduced-motion)
- Test performance on large presentations

**Dependencies:** None

---

### Feature: Two-Column Layouts
**Priority:** Medium
**Status:** Completed
**Description:** Support two-column slide layouts for side-by-side content.

**Sub-tasks:**
- ✅ Design markdown syntax for two-column layout (`:::columns` ... `|||` ... `:::`)
- ✅ Implement CSS flexbox/grid layout
- ✅ Support nested markdown in columns (via Python markdown library)
- ✅ Ensure responsive behavior on smaller screens (columns stack on mobile)
- ✅ Add example slides to documentation (`examples/two-column-examples.md`)

**Dependencies:** None

**Implementation Notes:**
- Parser transforms `:::columns` syntax into HTML divs
- Each column's markdown is rendered server-side using Python's `markdown` library
- CSS uses flexbox with responsive breakpoint at 768px
- Supports all markdown features within columns (code, lists, images, etc.)

---

### Feature: Export to Standalone HTML
**Priority:** Medium
**Status:** Ready
**Description:** Export presentation as a single HTML file with embedded assets.

**Sub-tasks:**
- Implement HTML export command in CLI
- Inline all CSS and JavaScript
- Embed images as base64 data URLs
- Bundle external dependencies (highlight.js, mermaid, etc.)
- Test cross-browser compatibility
- Add documentation for HTML export

**Dependencies:** None

---

### Enhancement: Configuration File Support
**Priority:** Medium
**Status:** Ready
**Description:** Add support for `.markdeck.yml` configuration files for project-level settings.

**Sub-tasks:**
- Define configuration schema (theme, transitions, defaults)
- Implement YAML parsing
- Add CLI option to specify config file
- Support per-presentation overrides
- Document all configuration options
- Add example configuration files

**Dependencies:** None

---

## Low Priority Tasks

### Enhancement: Custom Themes
**Priority:** Low
**Status:** Ready
**Description:** Allow users to create and use custom CSS themes.

**Sub-tasks:**
- Define theme structure and required CSS variables
- Add --theme CLI option to specify custom theme file
- Create theme template/boilerplate
- Document theme creation guide
- Create gallery of community themes

**Dependencies:** Feature: Multiple Themes

---

### Enhancement: Media Embedding Improvements
**Priority:** Low
**Status:** Ready
**Description:** Improve support for embedded media (videos, iframes, etc.).

**Sub-tasks:**
- Add support for video embedding (YouTube, Vimeo)
- Implement responsive iframe containers
- Add audio file support
- Test autoplay and controls behavior
- Document media embedding syntax

**Dependencies:** None

---

### Feature: Plugin System
**Priority:** Low
**Status:** Ready
**Description:** Create a plugin architecture for extending MarkDeck functionality.

**Sub-tasks:**
- Design plugin API and hooks system
- Implement plugin discovery and loading
- Create example plugins (analytics, custom renderers)
- Document plugin development guide
- Set up plugin registry/marketplace

**Dependencies:** Configuration File Support

---

### Enhancement: Speaker Timer
**Priority:** Low
**Status:** Ready
**Description:** Add a configurable timer for presentations with time warnings.

**Sub-tasks:**
- Design timer UI (minimal, non-intrusive)
- Add keyboard shortcut to start/stop timer
- Implement time warnings at intervals
- Add per-slide time allocation support
- Persist timer state across slide navigation

**Dependencies:** None

---

### Testing: E2E Test Suite
**Priority:** Medium
**Status:** Ready
**Description:** Add end-to-end testing for the presentation interface.

**Sub-tasks:**
- Set up Playwright or Cypress
- Write tests for keyboard navigation
- Test hot reload functionality
- Test markdown rendering edge cases
- Add CI integration for E2E tests

**Dependencies:** None

---

### Documentation: Video Tutorials
**Priority:** Low
**Status:** Ready
**Description:** Create video tutorials for getting started with MarkDeck.

**Sub-tasks:**
- Plan tutorial content (basics, advanced features)
- Record screen capture videos
- Edit and publish to YouTube
- Add links to README and docs
- Create accompanying blog posts

**Dependencies:** None

---

## Bugs / Technical Debt

### Bug: Slide Scroll Issue
**Priority:** High
**Status:** Completed
**Description:** ~~Fix scrolling behavior on slides with overflow content~~

**Note:** This was already fixed in a previous PR.

---

## Future Ideas (Not Prioritized)

- **Remote Control Support:** Control presentations from phone/tablet
- **Presenter Notes View:** Separate window with notes and preview
- **Live Collaboration:** Multiple users editing same presentation
- **Slide Templates:** Pre-built slide layouts and designs
- **Analytics Integration:** Track presentation engagement
- **Accessibility Audit:** WCAG compliance improvements
- **Progressive Web App:** Offline presentation support
- **Internationalization:** Multi-language support
- **Math Equation Editor:** Visual editor for KaTeX equations
- **Diagram Templates:** Pre-built mermaid diagram templates

---

## How to Use This File

### With Beads (Recommended)

Once Beads is installed, you can create these tasks:

```bash
# Initialize Beads
bd init

# Create tasks (example)
bd create "Multiple Themes" -p 0 --description "Add support for multiple presentation themes"
bd create "Slide Overview/Grid View" -p 0
bd create "Export to PDF" -p 0
# ... etc
```

### Manual Tracking

Update the **Status** field as you work:
- `Ready` - Ready to be worked on
- `In Progress` - Currently being worked on
- `Blocked` - Waiting on dependencies or decisions
- `Completed` - Task is done
- `Cancelled` - Task no longer needed

---

**Last Updated:** 2025-12-21
