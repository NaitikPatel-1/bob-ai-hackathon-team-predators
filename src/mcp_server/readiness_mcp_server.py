"""
D1 - Mission Readiness & Predictive Maintenance Copilot
MCP Server exposing the readiness analysis engine as tools for IBM Bob.

This is the REAL integration point: Bob (as an MCP client) calls these
tools directly against live data, then reasons over the results in
natural language. Nothing here is hardcoded output for the demo --
Bob is calling actual analysis code every time.

Run:  python readiness_mcp_server.py
Then register this server with Bob (stdio transport) via Bob's MCP config.
"""
import sys
import os
import json
import importlib.util
import time
import pandas as pd
from mcp.server.fastmcp import FastMCP

# Make sure we resolve paths relative to this file, regardless of cwd.
# analyze.py and readiness_report.csv live one level up, in src/.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..")

mcp = FastMCP("mission-readiness-copilot")

# ---------------------------------------------------------------------------
# In-process analysis cache
# ---------------------------------------------------------------------------
# Instead of spawning a new Python subprocess on every tool call (which
# cold-starts the interpreter + re-imports pandas/numpy each time and reliably
# exceeds Bob's MCP timeout), we:
#   1. Run analyze.py directly in this process via importlib.
#   2. Cache the resulting DataFrame for CACHE_TTL_SECONDS.
#   3. Only re-run when the cache is stale OR a source CSV has been modified.
# ---------------------------------------------------------------------------
CACHE_TTL_SECONDS = 60  # refresh at most once per minute

_cache: pd.DataFrame | None = None
_cache_time: float = 0.0
_cache_mtime: float = 0.0  # mtime of sensor_logs.csv at last analysis run


def _source_mtime() -> float:
    """Return the most-recent modification time across all three source CSVs."""
    data_dir = os.path.join(DATA_DIR, "data")
    files = ["assets.csv", "sensor_logs.csv", "service_records.csv"]
    mtimes = []
    for f in files:
        p = os.path.join(data_dir, f)
        try:
            mtimes.append(os.path.getmtime(p))
        except OSError:
            pass
    return max(mtimes) if mtimes else 0.0


def _run_analysis() -> pd.DataFrame:
    """
    Run the core analysis in-process and return the resulting DataFrame.
    Results are cached for CACHE_TTL_SECONDS; the cache is also invalidated
    whenever a source CSV is newer than the last run.
    """
    global _cache, _cache_time, _cache_mtime

    now = time.monotonic()
    current_mtime = _source_mtime()

    # Return cached result if still fresh and source files unchanged.
    if (
        _cache is not None
        and (now - _cache_time) < CACHE_TTL_SECONDS
        and current_mtime <= _cache_mtime
    ):
        return _cache

    # Run analyze.py directly inside this process.
    script_path = os.path.join(DATA_DIR, "analyze.py")
    spec = importlib.util.spec_from_file_location("analyze", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load analysis script: {script_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    # analyze.py writes readiness_report.csv and keeps `report` as a module attribute.
    if hasattr(mod, "report"):
        df: pd.DataFrame = mod.report.copy()
    else:
        report_path = os.path.join(DATA_DIR, "readiness_report.csv")
        df = pd.read_csv(report_path)

    _cache = df
    _cache_time = now
    _cache_mtime = current_mtime
    return _cache


@mcp.tool()
def get_prioritized_maintenance_plan(top_n: int = 10) -> str:
    """
    Returns the current prioritized maintenance plan for all fleet assets,
    ranked by risk score (highest risk first). Use this as the primary
    entry point for a fleet-wide readiness briefing.

    Args:
        top_n: number of highest-priority assets to return (default 10)
    """
    df = _run_analysis()
    top = df.sort_values("risk_score", ascending=False).head(top_n)
    return str(top.to_json(orient="records", indent=2))


@mcp.tool()
def get_asset_detail(asset_id: str) -> str:
    """
    Returns full readiness detail for a single asset: risk score, readiness
    status, predicted failure component/timeline, reasons, and recommended
    maintenance action. Use this when a commander asks about one specific
    asset by ID.

    Args:
        asset_id: the asset identifier, e.g. "AST-003"
    """
    df = _run_analysis()
    row = df[df["asset_id"] == asset_id]
    if row.empty:
        return json.dumps({"error": f"No asset found with id {asset_id}"})
    return str(row.to_json(orient="records", indent=2))


@mcp.tool()
def get_fleet_summary() -> str:
    """
    Returns a fleet-wide readiness summary: counts of READY / DEGRADED /
    NOT MISSION READY assets, and the single highest-risk asset. Use this
    for a quick top-line status check before drilling into details.
    """
    df = _run_analysis()
    counts = df["readiness_status"].value_counts().to_dict()
    highest_risk = df.sort_values("risk_score", ascending=False).iloc[0].to_dict()
    summary = {
        "total_assets": int(len(df)),
        "status_counts": counts,
        "highest_risk_asset": highest_risk,
    }
    return json.dumps(summary, indent=2, default=str)


@mcp.tool()
def get_assets_at_risk_before_mission(days_threshold: int = 10) -> str:
    """
    Returns assets whose predicted failure window falls BEFORE their next
    scheduled mission -- i.e. assets that will fail during or before the
    mission if not serviced. This is the highest-value output for
    commanders: it directly answers "what will break before we fly/deploy?"

    Args:
        days_threshold: only flag assets predicted to fail within this many days (default 10)
    """
    df = _run_analysis()
    at_risk = df[
        df["predicted_failure_days"].notna()
        & (df["predicted_failure_days"] <= df["days_to_next_mission"])
        & (df["predicted_failure_days"] <= days_threshold)
    ].sort_values("predicted_failure_days")  # type: ignore[call-overload]
    return str(at_risk.to_json(orient="records", indent=2))


if __name__ == "__main__":
    mcp.run(transport="stdio")