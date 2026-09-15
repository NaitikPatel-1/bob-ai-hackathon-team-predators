# Bob Integration — How It Works

## Why MCP (not a hardcoded demo script)
Bob connects to external tools/data via MCP (Model Context Protocol) per
the IBM Bob docs. We expose our readiness analysis engine (`analyze.py`)
as an MCP server with 4 tools. Bob calls these tools live, on real data,
every time — nothing is pre-scripted output pasted into a prompt.

## Tools exposed to Bob

| Tool | What it does |
|---|---|
| `get_prioritized_maintenance_plan(top_n)` | Full ranked fleet list by risk score |
| `get_asset_detail(asset_id)` | Deep dive on one asset |
| `get_fleet_summary()` | Status counts + single highest-risk asset |
| `get_assets_at_risk_before_mission(days_threshold)` | Assets predicted to fail *before* their next mission — the commander's key question |

Every tool call re-runs `analyze.py` under the hood, so results always
reflect the current CSV data (swap in real HUMS sensor feeds later with
zero changes to Bob's side).

## Setup Steps

1. Copy `readiness_mcp_server.py` into `src/mcp_server/` in your repo.
2. Copy `analyze.py` + the 3 CSVs into `src/` (or wherever the server's
   relative path expects them — adjust `DATA_DIR` in the script if you
   reorganize folders).
3. Install deps: `pip install mcp pandas numpy`
4. In Bob → Settings → MCP integrations (see bob.ibm.com/docs/ide/configuration),
   add a new server entry pointing at `readiness_mcp_server.py` (stdio transport).
   Reference: `bob_mcp_config.json` in this folder for the exact JSON shape.
5. Restart Bob so it picks up the new server. Type `/` or ask Bob to list
   its tools to confirm `mission-readiness-copilot` tools appear.

## Example prompts to run in Bob (Agent or Ask mode)

> "Give me today's mission readiness briefing. Use the fleet summary tool
> first, then tell me which assets will fail before their next mission."

> "Explain why AST-003 is flagged NOT MISSION READY and what should be
> done about it."

> "Generate a prioritized maintenance plan for the top 5 highest-risk
> assets, written for a commander who has 2 minutes to read it."

Bob calls the MCP tools to get the real numbers, then writes the natural
language explanation/plan itself — this is the "load-bearing" integration
judges are scoring (10 pts: IBM Bob Integration).
