# Solution Overview

## Core mechanism

The system runs a three-stage pipeline on every asset in the fleet:

1. **Readiness Classification** — a rule-based engine compares each
   asset's latest sensor readings and 30-day trend against calibrated
   thresholds (vibration, temperature, pressure) and flags overdue
   service records. Assets are bucketed into READY / DEGRADED / NOT
   MISSION READY, with a numeric risk score driving the ranking.

2. **Failure Prediction** — rather than only reacting to values already
   past threshold, the engine fits a linear trend to each sensor's
   recent history and extrapolates forward to estimate **how many days
   until it crosses the critical threshold**, and which component will
   fail first. This is what lets the system say "this asset will fail
   in 5.9 days" instead of just "this asset looks bad."

3. **Prioritized, Explainable Plan Generation** — every flagged asset
   gets a plain-English list of *why* it was flagged (not a black-box
   score) and a recommended action (IMMEDIATE / SCHEDULE SOON), ranked
   fleet-wide by risk so commanders see the worst problem first.

## What makes it different from naive alternatives

A naive approach would just threshold the latest sensor reading
("temperature > 90°C = bad"). That catches failures only after they've
already happened. Our engine tracks **drift over time** and predicts
the crossing point in advance — closer to genuinely predictive
maintenance rather than reactive alerting. It also cross-references
overdue service records, so an asset with borderline sensor readings
*and* a skipped inspection is correctly weighted as higher risk than
either signal alone would suggest.

## Key design decisions

- **Rule-based over black-box ML**: with a 3-day build window and a
  domain where explainability directly matters to evaluators (defense
  maintenance decisions need to be auditable), a transparent
  threshold+trend model was chosen over an opaque classifier. Every
  score can be traced back to a specific sensor reading.
- **Mission-window-aware prediction**: the system doesn't just rank by
  risk — `get_assets_at_risk_before_mission` answers the actual
  commander question: will this asset fail *before* it's needed next.
- **MCP as the Bob integration layer**: rather than hardcoding a Bob
  prompt with pasted-in numbers, the analysis engine is exposed as
  live MCP tools. Bob calls real data every time, so the integration
  is genuinely load-bearing, not decorative.

## What the user experience looks like

A maintenance officer opens the dashboard to see the fleet-wide status
at a glance, filters to "NOT MISSION READY," and clicks into an asset to
see its sensor trend and reasons. Separately, a commander can ask Bob
directly in natural language — "what's going to fail before next
week's mission?" — and Bob calls the same underlying tools to answer
conversationally, with the option to generate a full briefing document.
