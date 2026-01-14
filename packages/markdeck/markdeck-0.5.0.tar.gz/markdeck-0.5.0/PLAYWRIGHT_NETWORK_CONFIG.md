# Playwright Installation - Network Configuration

## Issue

Playwright browser installation fails with:
```
Error: Download failed: server returned code 403 body 'Host not allowed'
```

## Required Network Allowlist

Add these domains to Claude Code network settings:

### Required Domains

```
cdn.playwright.dev
playwright.download.prss.microsoft.com
```

### Download URLs Being Blocked

Playwright tries these URLs in order:
1. `https://cdn.playwright.dev/dbazure/download/playwright/builds/chromium/1200/chromium-linux.zip`
2. `https://playwright.download.prss.microsoft.com/dbazure/download/playwright/builds/chromium/1200/chromium-linux.zip`
3. `https://cdn.playwright.dev/builds/chromium/1200/chromium-linux.zip`

All return: **403 Forbidden**

## How to Configure

### Option 1: Update Claude Code Settings

If there's a network allowlist configuration, add:

```json
{
  "sandbox": {
    "network": {
      "allowedHosts": [
        "cdn.playwright.dev",
        "playwright.download.prss.microsoft.com"
      ]
    }
  }
}
```

### Option 2: Check Proxy Settings

If using a proxy, ensure these hosts are allowed through.

### Option 3: Use Pre-Downloaded Browser

Alternatively, we can use the **existing Chromium** that's already installed:

```bash
# Existing browser location
/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome
```

This browser works! We can use it directly without downloading.

## Verification

Test if hosts are accessible:

```bash
# Test CDN access
curl -I https://cdn.playwright.dev/builds/chromium/1200/chromium-linux.zip

# Should return 200 OK or 302 redirect, NOT 403
```

## Current Status

- ❌ cdn.playwright.dev - **BLOCKED** (403)
- ❌ playwright.download.prss.microsoft.com - **BLOCKED** (403)
- ✅ Existing Chromium browser - **AVAILABLE** at /root/.cache/ms-playwright/chromium-1194/

## Workaround

Since we have an existing browser, we can generate screenshots **right now** using:

```python
# Use existing browser directly
browser = await p.chromium.launch(
    executable_path='/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome',
    headless=True
)
```

This bypasses the download entirely!
