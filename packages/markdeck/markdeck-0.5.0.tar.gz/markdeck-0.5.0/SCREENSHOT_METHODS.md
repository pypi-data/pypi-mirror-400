# Alternative Screenshot Methods

## MCP Server Approach (For Unrestricted Environments)

If you have network access, you can use MCP servers to take screenshots.

### Option 1: Chrome DevTools MCP Server

**Setup:**

1. Create/edit `~/.claude.json`:
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-chrome-devtools"]
    }
  }
}
```

2. Launch Chrome with remote debugging:
```bash
# Linux
google-chrome --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

3. Restart Claude Code

4. Use MCP tools to take screenshots:
```
Take a screenshot of http://localhost:8000
```

### Option 2: Playwright MCP Server (Microsoft Official)

**Setup:**

1. Add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

2. Install Playwright browsers:
```bash
npx playwright install chromium
```

3. Restart Claude Code

4. The Playwright MCP provides browser automation tools

### Why This Doesn't Work in Current Environment

This sandboxed environment blocks:
- ✗ npm package downloads from registry.npmjs.org
- ✗ Browser binary downloads (playwright.dev, storage.googleapis.com)
- ✗ MCP server installations

These would all work fine on your local machine with normal network access.

## Working Alternatives (No Network Required)

### Manual Screenshots

The simplest approach that always works:

1. Start the server:
```bash
markdeck present examples/features.md
```

2. Open browser to http://localhost:8000

3. Take screenshots using:
   - **macOS**: Cmd+Shift+4
   - **Windows**: Win+Shift+S
   - **Linux**: Print Screen or Spectacle

4. Press `O` to show grid view and take more screenshots

### Browser DevTools Screenshots

Most browsers have built-in screenshot tools:

**Chrome/Edge DevTools:**
1. Open DevTools (F12)
2. Ctrl+Shift+P (Cmd+Shift+P on Mac)
3. Type "screenshot"
4. Choose "Capture full size screenshot" or "Capture screenshot"

**Firefox:**
1. Right-click → "Take a Screenshot"
2. Choose "Save full page" or "Save visible"

## Summary

| Method | Network Required | Works Here | Best For |
|--------|------------------|------------|----------|
| Manual screenshots | ✗ No | ✓ Yes | Quick, simple |
| Browser DevTools | ✗ No | ✓ Yes | Full-page captures |
| Python Selenium | ✓ Yes (drivers) | ✗ No | Automation |
| Playwright Python | ✓ Yes (binaries) | ✗ No | Automation |
| MCP Servers | ✓ Yes (npm) | ✗ No | Claude integration |
| Puppeteer | ✓ Yes (binaries) | ✗ No | Node.js automation |

**For this demo:** Manual screenshots or browser DevTools are the most practical options.

**For production:** MCP servers or Playwright are recommended for automated testing.
