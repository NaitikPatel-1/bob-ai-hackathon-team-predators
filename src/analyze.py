"""
D1 - Mission Readiness & Predictive Maintenance Copilot
Core Logic: Readiness Classifier + Failure Prediction + Prioritized Plan

Run from anywhere:
    python analyze.py
(paths are resolved relative to this file, not your current directory)
"""
import os
import sys
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

REQUIRED_FILES = ["assets.csv", "sensor_logs.csv", "service_records.csv"]

# ---------- Load Data (with a clear error instead of a raw traceback) ----------
missing = [f for f in REQUIRED_FILES if not os.path.isfile(os.path.join(DATA_DIR, f))]
if missing:
    print(f"ERROR: missing data file(s) in {DATA_DIR}: {', '.join(missing)}")
    print("Expected assets.csv, sensor_logs.csv, service_records.csv in src/data/")
    sys.exit(1)

try:
    assets = pd.read_csv(
        os.path.join(DATA_DIR, "assets.csv"),
        parse_dates=["last_maintenance_date", "next_mission_window"],
    )
    sensors = pd.read_csv(os.path.join(DATA_DIR, "sensor_logs.csv"), parse_dates=["timestamp"])
    service = pd.read_csv(os.path.join(DATA_DIR, "service_records.csv"), parse_dates=["service_date"])
except Exception as e:
    print(f"ERROR: failed to read data files - {e}")
    sys.exit(1)

# Normalize fault_code to plain empty-string-or-code, regardless of how this
# pandas version round-trips empty CSV cells (NaN vs "" vs <NA> all handled).
sensors["fault_code"] = sensors["fault_code"].fillna("").astype(str)
sensors.loc[sensors["fault_code"].str.lower() == "nan", "fault_code"] = ""

# Use the real current date rather than a fixed one, so "days to mission" /
# "predicted failure in X days" stay accurate no matter when this is run.
TODAY = pd.Timestamp(datetime.now().date())

# ---------- Thresholds (rule-based classifier) ----------
THRESH = {
    "vibration_critical": 7.0,      # mm/s - ISO 10816-ish danger zone
    "temp_critical": 90.0,          # deg C
    "pressure_critical_low": 80.0,  # psi
    "slope_vibration_warn": 0.10,   # mm/s per day drift
    "slope_temp_warn": 0.5,         # deg C per day drift
    "slope_pressure_warn": -0.5,    # psi per day (dropping)
}


def trend_slope(series_vals: Any) -> float:
    """Linear regression slope over time index (per day)."""
    x = np.arange(len(series_vals))
    if len(x) < 2:
        return 0.0
    coeffs: np.ndarray = np.polyfit(x, np.asarray(series_vals, dtype=float), 1)
    return float(coeffs[0])


def days_to_threshold(
    current_val: float,
    slope: float,
    threshold: float,
    rising: bool = True,
) -> float | None:
    """Extrapolate days until value crosses threshold. Returns None if it
    isn't heading toward the threshold at all (flat or moving away)."""
    if slope == 0:
        return None
    days = (threshold - current_val) / slope
    if rising and slope > 0 and days > 0:
        return round(days, 1)
    if not rising and slope < 0 and days > 0:
        return round(days, 1)
    return None


results = []

for _, asset in assets.iterrows():
    aid = asset["asset_id"]
    a_sensors: pd.DataFrame = sensors[sensors["asset_id"] == aid].sort_values(by=["timestamp"]).reset_index(drop=True)  # type: ignore[assignment]

    if a_sensors.empty:
        # No sensor history for this asset - flag it rather than silently skip.
        results.append({
            "asset_id": aid,
            "asset_type": asset["asset_type"],
            "readiness_status": "UNKNOWN",
            "risk_score": 0,
            "predicted_failure_days": None,
            "predicted_failure_component": None,
            "days_to_next_mission": (asset["next_mission_window"] - TODAY).days,
            "reasons": "No sensor data available for this asset",
        })
        continue

    temp_vals = np.asarray(a_sensors["temperature_c"].values, dtype=float)
    vib_vals = np.asarray(a_sensors["vibration_mm_s"].values, dtype=float)
    pres_vals = np.asarray(a_sensors["pressure_psi"].values, dtype=float)

    latest_temp = temp_vals[-1]
    latest_vib = vib_vals[-1]
    latest_pres = pres_vals[-1]

    temp_slope = trend_slope(temp_vals)
    vib_slope = trend_slope(vib_vals)
    pres_slope = trend_slope(pres_vals)

    fault_count = int((a_sensors["fault_code"].str.len() > 0).sum())

    # ---------- Rule-based Readiness Classification ----------
    reasons = []
    risk_score = 0

    if latest_vib >= THRESH["vibration_critical"]:
        risk_score += 40
        reasons.append(f"Vibration at critical level ({latest_vib:.1f} mm/s)")
    elif vib_slope >= THRESH["slope_vibration_warn"]:
        risk_score += 20
        reasons.append(f"Vibration trending up ({vib_slope:+.2f} mm/s/day)")

    if latest_temp >= THRESH["temp_critical"]:
        risk_score += 30
        reasons.append(f"Temperature at critical level ({latest_temp:.1f}°C)")
    elif temp_slope >= THRESH["slope_temp_warn"]:
        risk_score += 15
        reasons.append(f"Temperature trending up ({temp_slope:+.2f}°C/day)")

    if latest_pres <= THRESH["pressure_critical_low"]:
        risk_score += 20
        reasons.append(f"Pressure critically low ({latest_pres:.1f} psi)")
    elif pres_slope <= THRESH["slope_pressure_warn"]:
        risk_score += 10
        reasons.append(f"Pressure trending down ({pres_slope:+.2f} psi/day)")

    if fault_count > 0:
        risk_score += 10 * min(fault_count, 3)
        reasons.append(f"{fault_count} fault code(s) logged in last 30 days")

    # Overdue maintenance check
    overdue = service[
        (service["asset_id"] == aid)
        & (service["notes"].str.contains("overdue", case=False, na=False))
    ]
    if not overdue.empty:
        risk_score += 15
        reasons.append("Scheduled inspection overdue per service records")

    # ---------- Failure Prediction (extrapolation) ----------
    d_vib = days_to_threshold(latest_vib, vib_slope, THRESH["vibration_critical"], rising=True)
    d_temp = days_to_threshold(latest_temp, temp_slope, THRESH["temp_critical"], rising=True)
    d_pres = days_to_threshold(latest_pres, pres_slope, THRESH["pressure_critical_low"], rising=False)

    candidates: list[tuple[float, str]] = [
        (d, c)
        for d, c in [(d_vib, "Vibration"), (d_temp, "Temperature"), (d_pres, "Pressure")]
        if d is not None
    ]
    predicted_days: float | None
    pred_component: str | None
    if candidates:
        predicted_days, pred_component = min(candidates, key=lambda x: x[0])
    else:
        predicted_days, pred_component = None, None

    # ---------- Readiness Status ----------
    if risk_score >= 60:
        status = "NOT MISSION READY"
    elif risk_score >= 30:
        status = "DEGRADED"
    else:
        status = "READY"

    mission_days_away = (asset["next_mission_window"] - TODAY).days

    results.append({
        "asset_id": aid,
        "asset_type": asset["asset_type"],
        "readiness_status": status,
        "risk_score": risk_score,
        "predicted_failure_days": predicted_days,
        "predicted_failure_component": pred_component,
        "days_to_next_mission": mission_days_away,
        "reasons": "; ".join(reasons) if reasons else "No anomalies detected",
    })

report = pd.DataFrame(results).sort_values(
    by=["risk_score", "predicted_failure_days"],
    ascending=[False, True],
    na_position="last",
).reset_index(drop=True)
report.insert(0, "priority_rank", report.index + 1)


# ---------- Generate prioritized maintenance plan text ----------
def plan_line(row):
    if row["readiness_status"] == "READY":
        return "No action needed — continue standard monitoring."
    if row["readiness_status"] == "UNKNOWN":
        return f"Install/verify sensors on {row['asset_type']} {row['asset_id']} — no HUMS data received."
    urgency = "IMMEDIATE" if row["readiness_status"] == "NOT MISSION READY" else "SCHEDULE SOON"
    fail_info = ""
    if pd.notna(row["predicted_failure_days"]):
        fail_info = f" Predicted {row['predicted_failure_component']} failure in ~{row['predicted_failure_days']} days."
    mission_info = f" Next mission in {row['days_to_next_mission']} days."
    return f"[{urgency}] Inspect/service {row['asset_type']} {row['asset_id']}.{fail_info}{mission_info}"


report["maintenance_action"] = report.apply(plan_line, axis=1)
report.to_csv(os.path.join(BASE_DIR, "readiness_report.csv"), index=False)

# ---------- Console output ----------
display_cols = ["priority_rank", "asset_id", "asset_type", "readiness_status",
                 "risk_score", "predicted_failure_days", "predicted_failure_component", "reasons"]
printable: pd.DataFrame = report[display_cols].copy()  # type: ignore[assignment]
printable["predicted_failure_days"] = printable["predicted_failure_days"].apply(  # type: ignore[union-attr]
    lambda x: "—" if pd.isna(x) else x
)
printable["predicted_failure_component"] = printable["predicted_failure_component"].fillna("—")  # type: ignore[union-attr]

print(f"Analysis run: {TODAY.date()}  |  {len(report)} assets processed\n")
print(printable.to_string(index=False))
print("\n--- Sample Maintenance Plan (Top 5) ---")
for _, r in report.head(5).iterrows():
    print(f"{r['priority_rank']}. {r['maintenance_action']}")