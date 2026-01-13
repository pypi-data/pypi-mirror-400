# SERP MCP Server

[![PyPI version](https://img.shields.io/pypi/v/serp-mcp?style=flat)](https://pypi.org/project/serp-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/serp-mcp?style=flat)](https://pypi.org/project/serp-mcp/)
[![CI](https://github.com/LiranYoffe/serp-mcp/actions/workflows/publish.yml/badge.svg)](https://github.com/LiranYoffe/serp-mcp/actions)

Google SERP scraper as a Model Context Protocol (MCP) server with fingerprint rotation.

---

## Sponsored by

<p align="center">
  <a href="https://quercle.dev">
    <img src="https://quercle.dev/opengraph-image" alt="Quercle" width="100%">
  </a>
</p>

<p align="center">
  <strong><a href="https://quercle.dev">Quercle</a></strong> - Stop wasting tokens on junk. Get exactly what your LLM needs.<br>
  <em>Web Fetch & Search API that strips navigation, ads, and footers. Handles JS sites. Returns clean, cited content.</em>
</p>

## Features

- Automatic fingerprint rotation per request
- Request blocking (only www.google.com/search allowed)
- Lite mode for 50% less traffic (organic results only, DEFAULT)
- Full mode extracts: organic results, sitelinks, PAA, related searches, knowledge graph
- Location encoding via protobuf (UULE format)
- Validated country/language codes

## Installation

### Claude Code

```bash
claude mcp add serp-mcp -- uvx serp-mcp
```

### opencode

Add to your `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "serp-mcp": {
      "type": "local",
      "command": ["uvx", "serp-mcp"],
      "enabled": true
    }
  }
}
```

### Manual Usage

```bash
# Run with uvx (automatically installs and runs the latest version)
uvx serp-mcp
```

### Development

```bash
git clone https://github.com/LiranYoffe/serp-mcp
cd serp-mcp
uv sync
uv run serp-mcp
```

## Tools

### search

Search Google and extract SERP data.

**Parameters:**
- `query` (required): Search query
- `country` (default: "us"): Country code (us, uk, fr, de, etc.)
- `language` (default: "en"): Language code (en, fr, de, es, etc.)
- `location` (optional): Location for local results (e.g., "New York, NY")
- `time_range` (optional): Time filter (hour, day, week, month, year)
- `autocorrect` (default: true): Enable query autocorrection
- `page` (default: 1): Page number
- `lite` (default: true): Lite mode (organic results only, 50% less traffic)

**Example Usage:**

```
Search for "python tutorial" with default settings
Search for "python tutorial" in France with lite mode
Search for "restaurants" in New York with 7-day time filter
```

## Country Codes

Valid ISO 3166-1 alpha-2 codes: us, uk, fr, de, es, it, jp, kr, cn, in, br, etc. (243 codes)

### Language Codes

Valid Google language codes: en, fr, de, es, it, pt, ru, ja, ko, zh-cn, zh-tw, ar, hi, etc. (78 codes)

### Time Ranges

- `hour`: Past hour
- `day`: Past 24 hours
- `week`: Past week
- `month`: Past month
- `year`: Past year

## Architecture

- **Fingerprint Rotation**: Automatic browser fingerprint rotation for each request
- **MCP Protocol**: Model Context Protocol server with stdio transport
- **Blocking**: All non-Google requests blocked for efficiency

## Development

### Run Tests

```bash
uv run pytest
```

### Regenerate Protobuf

```bash
uv run python -m grpc_tools.protoc \
  --python_out=serp_mcp \
  -Iserp_mcp \
  serp_mcp/uule.proto
```

## License

MIT
