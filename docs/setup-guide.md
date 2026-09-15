# Setup Guide

Tested on a clean Ubuntu 24.04 environment with Python 3.12.

## Prerequisites

- Python 3.10+
- pip
- IBM Bob installed and signed in (see `bob.ibm.com/download`) — only
  required for the live Bob integration; the analysis engine and
  dashboard run standalone without it.

## Environment variables

None required for the base analysis engine or dashboard. If you extend
the MCP server to call a real sensor API, add credentials to
`src/.env` (see `src/.env.example`).

## Install

```bash
git clone https://github.com/[your-username]/bob-ai-hackathon-[team-name].git
cd bob-ai-hackathon-[team-name]
pip install pandas numpy "mcp<2"
```

## Run the analysis engine

```bash
cd src
python3 analyze.py
```

(Reads CSVs from `src/data/`, writes `src/readiness_report.csv`.)

Expected output: a ranked table printed to stdout, plus
`readiness_report.csv` written to the same directory.

## Run the dashboard

No build step needed — it's a static file with embedded data.

```bash
# just open it
open src/dashboard.html      # macOS
xdg-open src/dashboard.html  # Linux
```

Or double-click the file in a file browser. To refresh the dashboard
after changing the data, re-run `analyze.py`, then re-embed the updated
`readiness_report.csv` into `dashboard.html` (see `build_dashboard.py`
if included, or manually update the `DATA` constant in the file).

## Run the MCP server (for Bob integration)

```bash
cd src/mcp_server
python3 readiness_mcp_server.py
```

This starts the server on stdio transport, waiting for a client (Bob)
to connect — it will appear to hang, which is expected.

## Connect Bob to the MCP server

1. Open Bob → Settings → MCP integrations.
2. Add a new server using the config in
   `src/mcp_server/bob_mcp_config.json` (adjust the path to match
   where you cloned the repo).
3. Restart Bob.
4. Ask Bob: *"List your available tools"* — confirm the 4
   `mission-readiness-copilot` tools appear.
5. Try: *"Give me today's mission readiness briefing."*

## Verify it's working

- `analyze.py` should print 20 rows (or however many assets are in
  `assets.csv`), sorted by risk score descending.
- `dashboard.html` should open in any modern browser and show a fleet
  summary strip with non-zero counts.
- Bob should be able to call `get_fleet_summary` and return real
  numbers matching the dashboard.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'mcp'` | `pip install "mcp<2"` — the v2 API renamed `FastMCP`, this project targets v1 |
| `FileNotFoundError` for CSVs in `analyze.py` | Run the script from inside `src/`, or adjust the paths at the top of the script |
| Bob doesn't see the MCP server | Confirm the path in `bob_mcp_config.json` is absolute and correct for your machine, then restart Bob fully |
| Dashboard shows no data | Data is embedded at build time — if you regenerate `readiness_report.csv`, you must rebuild `dashboard.html` (see `build_dashboard.py`) |
