# BCCI.tv API & MCP Server

An unofficial Model Context Protocol (MCP) server and Python library for interacting with `bcci.tv` data. This package allows you to retrieve cricket tournament schedules, standings, and match summaries for Indian cricket.

> **Disclaimer:** This is an **unofficial** package. It is not affiliated with, maintained by, or endorsed by the Board of Control for Cricket in India (BCCI). This tool is intended for personal and educational use only and is **not meant for commercial use**.

---

## 🚀 Features

- **Dual Circuit Support**: Seamlessly fetch data for both **Domestic** and **International** matches.
- **Comprehensive Match Data**: Retrieve overall summaries, or detailed scorecards.
- **Pretty Formatting**: Optimized tool outputs designed for LLMs to render perfect Markdown tables.
- **Smart Discovery**: Catalog resources and search tools to find tournament IDs without wasting tokens. Maintain local cache for 24 hours for tournament IDs.

---

## 🛠 Configuration

To use this as an MCP server in clients like Claude Desktop, Cursor, Windsurf, Gemini, etc., add the following to your `settings.json`.

### Option 1: Run via GitHub (Recommended)
Use `uvx` to run the server directly from GitHub without cloning the repository.

```json
{
  "mcpServers": {
    "bcci-tv": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/importhuman/bcci-tv",
        "bcci-tv-mcp"
      ]
    }
  }
}
```

### Option 2: Run via Local Path
If you have cloned the repository locally:

```json
{
  "mcpServers": {
    "bcci-tv": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/cloned/bcci-tv",
        "run",
        "bcci-tv-mcp"
      ]
    }
  }
}
```

---

## 🧰 Available Tools

| Tool | Description |
|------|-------------|
| `search_competitions` | Find tournament IDs by name (e.g., "Vijay Hazare", "Ranji"). Returns circuit context (domestic/international). |
| `get_live_tournaments` | Get a list of currently active tournaments (based on how the BCCI website lists them). |
| `get_tournament_details` | Retrieve full metadata (dates, category) for a specific `CompetitionID`. |
| `get_tournament_schedule` | Fetch match schedules with optional filtering by status (`upcoming`, `live`, `post`). |
| `get_tournament_standings` | Retrieve points tables grouped by category and sorted by rank. |
| `get_domestic_match_summary` | Fetch comprehensive data for domestic matches (Overall/all innings/specific innings). |
| `get_intl_match_summary` | Fetch comprehensive data for international matches (Overall/all innings/specific innings). |

### Resources
- `tournaments://domestic/catalog`: A lightweight index of all domestic tournaments.
- `tournaments://international/catalog`: A lightweight index of all international tournaments.

---

## 📦 Usage as a Library

The core `BCCIApiClient` is fully namespaced and can be imported directly into a Python project.

```python
from bcci_tv import BCCIApiClient

async with BCCIApiClient() as client:
    # Search for a tournament
    results = await client.get_domestic_competitions()
    
    # Get standings
    standings = await client.get_tournament_standings(competition_id=318)
```

---

## 👨‍💻 Development

This project uses `uv` for dependency management. A `Makefile` is provided for common tasks:

- `make test`: Run the full test suite.
- `make lint`: Check for linting issues using Ruff.
- `make format`: Auto-format code.
- `make clean`: Clear local caches and temporary files.
