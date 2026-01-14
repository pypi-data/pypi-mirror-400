# Playwright Browser Download Blocked in Claude Code on the Web

## Issue Summary

Playwright browser binaries cannot be downloaded in Claude Code on the web sessions due to missing domains in the egress proxy allowlist.

**Status:** Blocked
**Date Reported:** 2025-12-28
**Affects:** Claude Code on the web sessions
**Does NOT affect:** Regular Claude.ai chat sessions (confirmed to have access)

## Status Tracking

- [x] Issue documented
- [x] Infrastructure team notified (https://github.com/anthropics/claude-code/issues/15583)
- [ ] Domains added to allowlist
- [ ] Verified in Claude Code on the web

## The Problem

When attempting to install Playwright browsers in Claude Code on the web:

```bash
.venv/bin/python -m playwright install chromium
```

**Error received:**
```
Error: Download failed: server returned code 403 body 'Host not allowed'
URL: https://cdn.playwright.dev/dbazure/download/playwright/builds/chromium/1200/chromium-linux.zip
URL: https://playwright.download.prss.microsoft.com/dbazure/download/playwright/builds/chromium/1200/chromium-linux.zip
```

## Root Cause

Claude Code on the web uses an **Envoy proxy** with JWT-based allowlist for egress traffic. The proxy configuration is controlled by:

- **Service:** `anthropic-egress-control`
- **Proxy server:** `21.0.0.89:15004` (container-specific)
- **Authentication:** JWT token embedded in environment variables
- **Blocking mechanism:** `x-deny-reason: host_not_allowed`

### Why WebFetch Permissions Don't Solve This

**Critical architectural limitation discovered:** WebFetch permissions in `settings.json` and `ALLOWED_FETCH_DOMAINS` hooks **only control Claude's WebFetch tool**, not subprocess HTTP requests.

```
Claude Code Container Architecture:
├── Claude's Tools (WebFetch, WebSearch)
│   └── Controlled by: settings.json permissions + hooks ✅
├── Subprocess Tools (Node.js, Python child processes)
│   ├── Playwright's Node.js installer
│   ├── npm install, pip install
│   └── Controlled by: Container-level JWT proxy ❌ (BLOCKED)
└── JWT-based egress proxy
    └── Controls: ALL outbound HTTP/HTTPS traffic
```

**What we tried:**
1. ✅ Added Playwright domains to `.claude/settings.json` WebFetch permissions
2. ✅ Investigated `ALLOWED_FETCH_DOMAINS` hook approach
3. ❌ **Result:** Playwright still blocked because it makes direct HTTP requests via Node.js subprocess

**Node.js specific limitation:** Node.js built-in `https` module [ignores `HTTP_PROXY`/`HTTPS_PROXY` environment variables](https://www.wunsch.dk/blog/claude-code-web-connectivity/) - a documented historical limitation.

**Conclusion:** This requires **infrastructure-level changes** to the JWT proxy's `allowed_hosts` field. WebFetch permissions and hooks cannot override container-level network restrictions.

### Current Allowlist Status

The JWT's `allowed_hosts` field includes hundreds of development-related domains:
- ✅ `storage.googleapis.com`
- ✅ `github.com`, `raw.githubusercontent.com`
- ✅ `npmjs.com`, `registry.npmjs.org`
- ✅ `pypi.org`, `pypi.python.org`
- ✅ `microsoft.com`, `packages.microsoft.com`
- ✅ Many others (npm, maven, docker, gradle, rust, ruby, etc.)

**But missing:**
- ❌ `cdn.playwright.dev`
- ❌ `playwright.download.prss.microsoft.com`
- ❌ `*.playwright.dev` (wildcard)

## Key Discovery: Different Proxies for Different Services

**Regular Claude sessions (claude.ai):**
- Confirmed to have Playwright domains in allowlist
- Different proxy infrastructure

**Claude Code on the web:**
- Separate proxy configuration
- More restrictive allowlist (security for code execution)
- **Playwright domains NOT YET added to this specific allowlist**

## Evidence

### 1. Fresh JWT Token Analysis
After forcing environment refresh (exec bash):
- New JWT issued: `iat: 1766917369`
- Container changed: `sad-drab-flaky-comb`
- Proxy changed: `21.0.0.89:15004`
- **Playwright domains still missing from `allowed_hosts`**

### 2. Direct Network Tests
```bash
curl -I https://cdn.playwright.dev
# Result: HTTP/1.1 403 Forbidden
# Header: x-deny-reason: host_not_allowed
```

### 3. Playwright Installation Attempts
Multiple attempts across different containers and JWT tokens - all failed with identical 403 errors.

## Requested Domains to Add

Please add the following domains to the **Claude Code on the web** egress proxy allowlist:

1. `cdn.playwright.dev` - Primary CDN for Playwright browsers
2. `playwright.download.prss.microsoft.com` - Microsoft CDN mirror
3. `*.playwright.dev` (optional wildcard) - Future-proofing for any new subdomains

## Impact

**Users affected:**
- Anyone trying to use Playwright for browser automation in Claude Code on the web
- Screenshot generation workflows
- E2E testing scenarios
- Web scraping projects

**Current workarounds:**
1. ✅ GitHub Actions workflow (has full network access)
2. ❌ Local browser installation (no Chrome/Chromium in container)
3. ❌ Alternative CDNs (none available for Playwright)

## Reproduction Steps

1. Start Claude Code on the web session
2. Install Playwright: `uv pip install playwright --python .venv/bin/python`
3. Attempt browser download: `.venv/bin/python -m playwright install chromium`
4. Observe 403 errors from both CDN URLs

## Environment Details

- **Platform:** Claude Code on the web
- **Container OS:** Linux 4.4.0
- **Python:** 3.11
- **Playwright version:** 1.57.0
- **Chromium build:** 1200 (143.0.7499.4)

## Technical Details

### JWT Token Structure
```json
{
  "iss": "anthropic-egress-control",
  "organization_uuid": "[redacted]",
  "iat": 1766917369,
  "exp": 1766931769,
  "allowed_hosts": "[comma-separated list - missing playwright domains]",
  "is_hipaa_regulated": "false",
  "use_egress_gateway": "false",
  "session_id": "[session_id]",
  "container_id": "[container_id]"
}
```

### Environment Variables Affected
- `HTTPS_PROXY`
- `HTTP_PROXY`
- `GLOBAL_AGENT_HTTP_PROXY`
- `YARN_HTTPS_PROXY`
- `YARN_HTTP_PROXY`

All contain the JWT-authenticated proxy URL with the restricted allowlist.

## Infrastructure Change Request

### Required Action

**Add the following domains to the JWT-based egress proxy allowlist** for Claude Code on the web containers.

This is an **infrastructure-level configuration change** to the `allowed_hosts` field in JWT tokens issued by `anthropic-egress-control`.

### Domains to Add

| Domain | Purpose | Similar Existing Domains |
|--------|---------|-------------------------|
| `cdn.playwright.dev` | Primary CDN for Playwright browser binaries | Similar to: `cdn.cocoapods.org`, `static.crates.io` |
| `playwright.download.prss.microsoft.com` | Microsoft CDN mirror for Playwright | Similar to: `packages.microsoft.com`, `dotnet.microsoft.com` |
| `playwright.dev` | Playwright documentation and resources | Similar to: `docs.claude.com`, `nodejs.org` |

### Justification

**Playwright is a standard development tool** comparable to other package managers and build tools already in the allowlist:

| Tool Category | Already Allowed | Requesting |
|---------------|----------------|------------|
| **Package CDNs** | npmjs.com, pypi.org, rubygems.org | cdn.playwright.dev |
| **Microsoft CDNs** | packages.microsoft.com, mcr.microsoft.com | playwright.download.prss.microsoft.com |
| **Browser automation** | *(none)* | playwright.dev |

**Use cases:**
- End-to-end testing (E2E tests)
- Screenshot generation for documentation
- Web scraping and automation
- UI testing workflows

**Security:** Playwright is developed by Microsoft, same trust level as other Microsoft domains already in allowlist.

### Technical Implementation

The JWT signing service (`anthropic-egress-control`) needs to update the `allowed_hosts` field in the token payload template for Claude Code on the web sessions.

**Example JWT field update:**
```json
{
  "allowed_hosts": "existing,domains,here,cdn.playwright.dev,playwright.download.prss.microsoft.com,playwright.dev"
}
```

### Testing Verification

After deployment, verify with:
```bash
# In Claude Code on the web session:
curl -I https://cdn.playwright.dev
# Expected: HTTP/1.1 200 OK (not 403 Forbidden)

.venv/bin/python -m playwright install chromium
# Expected: Successful browser download
```

## Recommendation

This change enables browser automation workflows in Claude Code on the web, bringing parity with regular Claude.ai sessions which already have access to these domains.

## Related Files in This Repository

- `/home/user/markdeck/CLAUDE.md` - Documents the network restrictions
- `/home/user/markdeck/.github/workflows/screenshots.yml` - Working GitHub Actions workaround
- `/home/user/markdeck/capture_screenshots.py` - Playwright screenshot script

## Contact

Repository: orangewise/markdeck
Branch: claude/fix-screenshot-generation-N9Uhn
Session: Claude Code on the web

---

## References and Sources

### Documentation Consulted

1. **Claude Code Settings:** https://code.claude.com/docs/en/settings
2. **Claude Code Hooks:** https://code.claude.com/docs/en/hooks
3. **Enterprise Network Configuration:** https://code.claude.com/docs/en/network-config

### Related Issues and Discussions

4. **WebFetch Domain Bug:** [GitHub Issue #1217](https://github.com/anthropics/claude-code/issues/1217) - Domain is not allowed even though explicitly allowed
5. **Node.js Connectivity in Claude Code Web:** https://www.wunsch.dk/blog/claude-code-web-connectivity/
6. **WebFetch Auto-Approval Hooks:** https://dev.to/alexisfranorge/auto-approve-webfetch-and-websearch-in-claude-code-with-hooks-4kpg

### Technical References

7. **Claude Code Permissions Guide:** https://www.petefreitag.com/blog/claude-code-permissions/
8. **Complete Permissions Reference:** https://www.eesel.ai/blog/claude-code-permissions
9. **Environment Variables Guide:** https://medium.com/@dan.avila7/claude-code-environment-variables-a-complete-reference-guide-41229ef18120
10. **Playwright MCP Installation:** https://testdino.com/blog/playwright-mcp-installation/

### Key Findings Summary

- **WebFetch permissions scope:** Only controls Claude's WebFetch tool, not subprocess HTTP requests
- **Node.js proxy limitation:** Node.js ignores `HTTP_PROXY`/`HTTPS_PROXY` environment variables
- **Architecture gap:** No user-level mechanism to override container-level proxy restrictions
- **Recommended solution:** Infrastructure-level JWT allowlist update

---

**Note:** This issue is specific to Claude Code on the web infrastructure and does not affect regular Claude.ai chat sessions, which reportedly have access to these domains.
