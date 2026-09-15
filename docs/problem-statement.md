# Problem Statement

## Who is affected

Maintenance officers, fleet commanders, and operations planners at military
organisations responsible for aircraft, ground vehicles, radar, generators,
and communications equipment. Any unit that must certify assets as
"mission-ready" before a deployment window.

## Why existing solutions don't solve it

Maintenance today runs on **fixed calendar schedules** — an asset is
serviced every N days regardless of its actual condition. This has two
failure modes:

- **Over-maintenance**: healthy assets get pulled in for unnecessary
  service, wasting technician hours and downtime.
- **Under-maintenance**: an asset that is degrading faster than the
  schedule assumes fails unexpectedly, often right before or during a
  mission window.

HUMS (Health & Usage Monitoring System) sensors already collect the data
that would catch this — vibration, temperature, pressure, fault codes —
but it sits in raw logs. No one is continuously correlating sensor drift
against mission timelines to answer the one question that matters:
**"what will break before we need it next?"**

## Quantified pain

- The US military spends **$90B/year** on maintenance; shifting from
  calendar-based to predictive approaches is estimated to save billions
  annually by catching failures weeks in advance instead of reacting to
  them.
- When a platform fails unexpectedly, operational readiness drops and
  recovery can take **weeks**, not days.
- In our simulated fleet of 20 assets, **25% (5 assets)** showed a clear
  progressive failure signature in the last 30 days of sensor data —
  none of which would have been caught by a calendar-based schedule.

## Why this matters now

Sensor instrumentation is already in place across modern military
platforms. The bottleneck isn't data collection — it's analysis and
explanation at the speed commanders need it. An AI copilot that reads
the same sensor streams humans already have access to, and turns them
into a ranked, explainable action plan, closes that gap without any new
hardware investment.
