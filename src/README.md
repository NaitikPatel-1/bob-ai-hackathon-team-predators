# src/ layout

- `analyze.py` — core readiness classifier + failure prediction engine. Reads CSVs from `data/`, writes `readiness_report.csv`.
- `data/` — assets, sensor logs, service records (synthetic, with injected failure signatures for 5 assets).
- `dashboard.html` — self-contained interactive dashboard, embeds a snapshot of `readiness_report.csv`.
- `mcp_server/` — MCP server exposing the analysis engine as live tools for IBM Bob. See `mcp_server/README_bob_integration.md` for setup.
