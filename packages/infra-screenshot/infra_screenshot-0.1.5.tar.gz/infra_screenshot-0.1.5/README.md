# infra-screenshot

[![PyPI](https://img.shields.io/pypi/v/infra-screenshot.svg)](https://pypi.org/project/infra-screenshot/)
[![Python Versions](https://img.shields.io/pypi/pyversions/infra-screenshot.svg)](https://pypi.org/project/infra-screenshot/)
[![Build Status](https://github.com/pj-ms/infra-screenshot/workflows/Build%20and%20Test/badge.svg)](https://github.com/pj-ms/infra-screenshot/actions)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![License: Commercial](https://img.shields.io/badge/License-Commercial-green.svg)](LICENSE)

`infra-screenshot` provides reusable models, services, and CLI helpers for capturing website screenshots. It exposes the core abstractions.

## Table of Contents

- [infra-screenshot](#infra-screenshot)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
    - [Using uv (Recommended)](#using-uv-recommended)
    - [Using pip](#using-pip)
    - [Quick Verification](#quick-verification)
  - [Usage](#usage)
    - [CLI: Local Screenshot Capture](#cli-local-screenshot-capture)
      - [Basic Examples](#basic-examples)
      - [Input File Format (JSONL)](#input-file-format-jsonl)
      - [Common Options](#common-options)
      - [Real-World Examples](#real-world-examples)
    - [Python API: Programmatic Usage](#python-api-programmatic-usage)
  - [Browser Setup](#browser-setup)
    - [Playwright: Bundled Chromium vs System Chrome](#playwright-bundled-chromium-vs-system-chrome)
    - [Installing System Chrome/Chromium](#installing-system-chromechromium)
      - [For Playwright (Optional - only if using system Chrome)](#for-playwright-optional---only-if-using-system-chrome)
      - [For Selenium (Required)](#for-selenium-required)
  - [Configuration](#configuration)
    - [Environment Variables](#environment-variables)
  - [Logging](#logging)
    - [OpenTelemetry correlation](#opentelemetry-correlation)
  - [Contributing](#contributing)
  - [License](#license)
    - [AGPL-3.0 (Open Source)](#agpl-30-open-source)
    - [Commercial License](#commercial-license)

## Features

- 🎭 **Multiple backends**: Support for both Playwright and Selenium
- 📸 **Flexible capture**: Single screenshots or batch processing
- 🔧 **Configurable viewports**: Desktop, mobile, and custom viewport sizes
- 💾 **Storage abstractions**: Local filesystem or cloud storage backends
- 🚀 **Async/await support**: Modern async architecture for better performance
- 🛠️ **CLI tools**: Ready-to-use command-line interface
- 🔄 **Retry logic**: Built-in retry with exponential backoff for reliability
- 🎨 **Visual cleanup**: Auto-hide overlays, disable animations for cleaner screenshots

## Installation

### Using uv (Recommended)

```bash
# Install with Playwright backend (includes bundled Chromium)
uv pip install "infra-screenshot[playwright]"
uv run playwright install chromium

# OR install with Selenium backend (requires system Chrome)
uv pip install "infra-screenshot[selenium]"
```

### Using pip

```bash
# Install with Playwright backend
pip install "infra-screenshot[playwright]"
playwright install chromium

# OR install with Selenium backend
pip install "infra-screenshot[selenium]"
```

### Quick Verification

```bash
# Check installation
screenshot local -h

# Test capture
screenshot local --urls https://example.com --output-dir ./test-screenshots
```

## Usage

### CLI: Local Screenshot Capture

The CLI provides a `local` subcommand for capturing screenshots locally.

#### Basic Examples

```bash
# Capture a single URL
screenshot local --urls https://example.com --output-dir ./screenshots

# Capture multiple URLs (repeat the --urls flag for each URL)
screenshot local \
  --urls https://example.com \
  --urls https://github.com \
  --output-dir ./screenshots

# For many URLs, use a JSONL input file (recommended)
screenshot local --input urls.jsonl --output-dir ./screenshots

# Capture with custom settings
screenshot local \
  --urls http://localhost:3000 \
  --output-dir ./screenshots \
  --viewports desktop mobile \
  --depth 0 \
  --scroll false \
  --allow-autoplay true
```

#### Input File Format (JSONL)

For batch processing, create a file with one JSON object per line:

```json
{"url": "https://example.com", "job_id": "example"}
{"url": "https://github.com", "job_id": "github"}
{"url": "https://docs.python.org", "job_id": "python-docs"}
```

Then run:
```bash
screenshot local --input urls.jsonl --output-dir ./screenshots
```

#### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--viewports` | Viewport presets (desktop, mobile, tablet) | `desktop` |
| `--depth` | Link depth to follow (0 = single page only) | `1` |
| `--scroll` | Enable scrolling before capture | `true` |
| `--scroll-step-delay-ms` | Delay between scroll steps (ms) | `250` |
| `--max-scroll-steps` | Max scroll iterations | `15` |
| `--full-page` | Capture entire page height (not just viewport) | `true` |
| `--timeout-s` | Page load timeout in seconds | `60` |
| `--post-nav-wait-s` | Wait after navigation (settling time) | `6` |
| `--pre-capture-wait-s` | Wait before screenshot | `2.5` |
| `--hide-overlays` | Auto-hide popups/cookie banners | `true` |
| `--disable-animations` | Disable CSS animations for cleaner shots | `true` |
| `--allow-autoplay` | Allow media autoplay | `true` |
| `--mute-media` | Mute audio/video | `true` |
| `--block-media` | Block video/audio requests | `false` |
| `--site-concurrency` | Number of sites to capture in parallel | `1` |
| `--max-pages` | Max pages per site (when following links) | `5` |

See all options:
```bash
screenshot local -h
```

#### Real-World Examples

**Capture homepage only (no scrolling, viewport-only):**
```bash
screenshot local \
  --urls http://localhost:3000 \
  --output-dir ./tmp \
  --depth 0 \
  --scroll false \
  --full-page false
```

**Full-page screenshot with scrolling:**
```bash
screenshot local \
  --urls http://localhost:3000 \
  --output-dir ./tmp \
  --depth 0 \
  --scroll true \
  --full-page true
```

**Capture multiple viewports:**
```bash
screenshot local \
  --urls https://example.com \
  --output-dir ./screenshots \
  --viewports desktop mobile tablet
```

### Python API: Programmatic Usage

For integration into your own tooling, call the async runner directly with a configured
`ScreenshotOptions` payload:

```python
from pathlib import Path
import asyncio

from screenshot import ScreenshotOptions, capture_screenshots_async
from screenshot.models import CaptureOptions

async def capture_example() -> None:
    options = ScreenshotOptions(
        capture=CaptureOptions(
            enabled=True,
            viewports=("desktop",),
            depth=0,
            scroll=False,
        )
    )

    result = await capture_screenshots_async(
        "demo-job",
        "https://example.com",
        store_dir=Path("screenshots"),
        partition_date=None,
        options=options,
    )

    if result.succeeded:
        print(f"Captured {result.captured} screenshot(s)")
    else:
        for error in result.errors:
            print(f"Capture failed: {error.message}")

asyncio.run(capture_example())
```

## Browser Setup

### Playwright: Bundled Chromium vs System Chrome

**By default**, Playwright uses its own bundled Chromium (installed via `playwright install chromium`). This provides:
- ✅ **Reproducibility**: Known browser version across environments
- ✅ **No system dependencies**: Works in containers/CI without system Chrome
- ✅ **Headless-first design**: Optimized for automation

**When to use system Chrome** (`--playwright-executable-path`):
- 🎯 Testing against real Chrome (not Chromium)
- 🎯 Using Chrome extensions or enterprise policies
- 🎯 Matching end-user browser versions exactly
- 🎯 Debugging with Chrome DevTools locally

**Trade-offs:**

| Aspect | Bundled Chromium | System Chrome |
|--------|-----------------|---------------|
| **Setup** | `playwright install chromium` | Install Chrome + ensure compatibility |
| **Version control** | Pinned to Playwright release | Depends on system updates |
| **Size** | ~300MB download | Already on system |
| **Reproducibility** | ✅ High (version-locked) | ⚠️ Lower (varies by system) |
| **Extensions** | ❌ Not supported | ✅ Supported |
| **DevTools** | Limited | Full local debugging |

**Usage example with system Chrome:**
```bash
screenshot local \
  --urls https://example.com \
  --output-dir ./screenshots \
  --playwright-executable-path /usr/bin/google-chrome-stable
```

> **Need a deeper comparison?**
> Check the repository's `.dev_docs/playwright_vs_selenium_linux.md` for codec/DRM support, driver management, and when to switch to system Chrome.

**Finding Chrome path:**
```bash
# Linux/WSL
which google-chrome-stable    # Usually /usr/bin/google-chrome-stable
which chromium-browser         # Usually /usr/bin/chromium-browser

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome

# Windows (WSL path)
/mnt/c/Program\ Files/Google/Chrome/Application/chrome.exe
```

If the path is invalid, the tool logs a warning and falls back to bundled Chromium automatically.

### Installing System Chrome/Chromium

#### For Playwright (Optional - only if using system Chrome)

```bash
# Google Chrome (stable) - Linux/WSL
wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y /tmp/chrome.deb

# OR Chromium (from distro packages)
sudo apt-get update && sudo apt-get install -y chromium-browser fonts-liberation
```

#### For Selenium (Required)

Selenium **always** requires a system browser + matching `chromedriver`:

```bash
# Install Chrome (as above)
# Then install chromedriver
pip install webdriver-manager  # Auto-downloads matching chromedriver
```

Tools like `webdriver-manager` automatically download the chromedriver matching your installed Chrome version.

## Configuration

### Environment Variables

Runtime behavior can be customized via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SCREENSHOT_SCROLL_STEP_DELAY_MS` | Delay between scroll steps (ms) | `250` |
| `SCREENSHOT_MAX_SCROLL_STEPS` | Maximum scroll iterations | `15` |
| `PLAYWRIGHT_CAPTURE_MAX_ATTEMPTS` | Retry attempts for failed captures | `3` |
| `SCREENSHOT_RETRY_BACKOFF_S` | Initial retry delay (seconds) | `0.5` |
| `SCREENSHOT_RETRY_MAX_BACKOFF_S` | Maximum retry delay (seconds) | `5.0` |
| `SCREENSHOT_ENABLE_TIMING` | Enable additional timing/performance metrics during capture (see `docs/perf-testing.md`) | See `docs/perf-testing.md` |

Example:
```bash
export SCREENSHOT_SCROLL_STEP_DELAY_MS=200
export PLAYWRIGHT_CAPTURE_MAX_ATTEMPTS=5
screenshot local --urls https://example.com --output-dir ./screenshots
```

## Logging

`infra-screenshot` uses Python's standard `logging` module. Enable diagnostics in your application or CLI runs with:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("screenshot.playwright_runner").setLevel(logging.DEBUG)
```

Logger namespaces:

| Logger | Purpose |
|--------|---------|
| `screenshot.playwright_runner` | Playwright capture + upload lifecycle |
| `screenshot.selenium_runner` | Selenium fallback pipeline |
| `screenshot.cli` | CLI orchestration and batch processing |

Log records include structured `extra={...}` fields such as `job_id`, `url`, and `viewport`. URLs are sanitized before logging to prevent leaking SAS tokens or credentials; configure your formatter (JSON/text) to emit those keys for easier filtering.

### OpenTelemetry correlation

When using OpenTelemetry, attach trace/span IDs to screenshot logs so traces and logs stay aligned:

```python
import logging
from pathlib import Path

from opentelemetry import trace

from screenshot import capture_screenshots_async

tracer = trace.get_tracer(__name__)
url = "https://example.com/products"
job_id = "otel-demo"

with tracer.start_as_current_span("screenshot-job") as span:
    logger = logging.getLogger("screenshot.playwright_runner")
    logger.info(
        "Starting screenshot job",
        extra={
            "job_id": job_id,
            "trace_id": span.get_span_context().trace_id,
            "span_id": span.get_span_context().span_id,
        },
    )
    options = ...  # Build ScreenshotOptions as shown above
    await capture_screenshots_async(
        job_id,
        url,
        store_dir=Path("/tmp/screens"),
        partition_date=None,
        options=options,
    )
```

## Contributing

We welcome contributions! To get started with development:

1. **Read the contributing guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Set up your development environment** (covered in CONTRIBUTING.md)
3. **Run tests and linters** before submitting PRs

For bug reports and feature requests, please [open an issue](https://github.com/pj-ms/infra-screenshot/issues).

## License

This project is **dual-licensed**:

### AGPL-3.0 (Open Source)
Free for open-source and non-commercial use under the [GNU Affero General Public License v3.0](LICENSE).

**Key requirement**: If you run this software as a service (SaaS, API, web app), you must make your complete source code available under AGPL-3.0.

### Commercial License
For commercial use without AGPL obligations (proprietary products, SaaS without open-sourcing, etc.).

See [LICENSE](LICENSE) for full details.

---

**Need help?** Check out:
- [Documentation](docs/) - Configuration reference and migration guides
- [Chromium Compatibility Levels](docs/chromium-compatibility-levels.md) - Understanding browser options
- [Architecture](docs/architecture.md) - Internal design and models layer
