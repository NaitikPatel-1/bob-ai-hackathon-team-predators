# Mission Readiness & Predictive Maintenance Copilot

**Track:** AI
**Problem Statement:** D1 — Defense & Aerospace
**Powered by:** IBM Bob

> **From sensor data → to risk → to prediction → to action.**

---

## 👥 Team

| Role     | Name               | Email                                                       |
| -------- | ------------------ | ----------------------------------------------------------- |
| **Lead** | Naitik Patel       | [d26ec158@charusat.edu.in](mailto:d26ec158@charusat.edu.in) |
| Member   | Vraj Savaj         | [d26ec150@charusat.edu.in](mailto:d26ec150@charusat.edu.in) |
| Member   | Devam Shah         | [d26ec1@charusat.edu.in](mailto:d26ec1@charusat.edu.in)     |
| Member   | Abhikumar Mansuria | [25ec001@charusat.edu.in](mailto:25ec001@charusat.edu.in)   |

---

# 🎯 Problem Statement

Military organizations need to know whether their aircraft, vehicles, and critical equipment are truly **mission-ready**.

Traditional maintenance often relies on fixed calendar schedules rather than the actual condition of components. At the same time, valuable **HUMS (Health and Usage Monitoring System)** sensor data — such as vibration, temperature, and pressure — can contain early indicators of component degradation.

When this information remains unanalyzed:

* Potential failures are detected too late.
* Unexpected equipment failures reduce operational readiness.
* Maintenance resources may be spent on healthy components.
* Recovery from critical failures can take weeks.
* Mission planning becomes more uncertain.

The challenge is to transform raw sensor and maintenance data into **clear, actionable, and explainable readiness intelligence**.

For the detailed problem definition, see [`docs/problem-statement.md`](docs/problem-statement.md).

---

# 💡 Our Solution

**Mission Readiness & Predictive Maintenance Copilot** is an AI-assisted predictive maintenance system designed to help maintenance and mission-planning teams understand the current health of their assets.

The system:

1. Ingests sensor logs and service records.
2. Analyzes sensor behavior over a 30-day window.
3. Classifies asset readiness as:

   * 🟢 **READY**
   * 🟡 **DEGRADED**
   * 🔴 **NOT MISSION READY**
4. Detects degradation trends in critical components.
5. Estimates approximate **time-to-failure** using trend extrapolation.
6. Calculates a risk-based maintenance priority.
7. Generates an explainable maintenance plan.
8. Exposes the analysis through **MCP tools**, allowing IBM Bob to query the system dynamically.

For more details, see [`docs/solution-overview.md`](docs/solution-overview.md).

---

# 🚀 Key Features

## 1. Mission Readiness Classification

The system evaluates asset health using:

* Vibration
* Temperature
* Pressure
* Sensor drift
* Recent service information

Each asset receives a simple and actionable readiness classification:

```text
READY
DEGRADED
NOT MISSION READY
```

The rule-based approach keeps the result **transparent and explainable**.

---

## 2. Predictive Failure Analysis

Instead of only asking:

> "Is the component healthy today?"

the system also asks:

> **"Based on the current degradation trend, approximately how many days remain before the component reaches a critical threshold?"**

Linear trend extrapolation is used to estimate the approximate time until a component crosses its defined critical threshold.

This provides an **early-warning indicator** for maintenance planning.

---

## 3. Prioritized Maintenance Planning

Assets are ranked according to their calculated risk.

The system produces a maintenance plan that answers:

* Which asset should be inspected first?
* Which component is at risk?
* Why is it considered risky?
* How urgent is the maintenance?
* What evidence from the sensor data supports the recommendation?

The goal is not simply to produce a score, but to provide a **human-readable reason behind the recommendation**.

---

## 4. MCP-Powered IBM Bob Integration

The project includes an **MCP (Model Context Protocol) server** that exposes the analysis engine as live tools.

Bob can call tools such as:

```text
get_fleet_summary
get_asset_detail
get_prioritized_maintenance_plan
get_assets_at_risk_before_mission
```

These tools execute the actual analysis pipeline against the project data rather than relying on a manually prepared response.

This makes the MCP integration **load-bearing rather than decorative**.

---

## 5. Interactive Dashboard

A lightweight browser-based dashboard provides:

* Fleet-level readiness overview
* Asset-level health information
* Sensor trends
* Risk indicators
* Maintenance priorities
* Predictive failure information

The dashboard is built using vanilla HTML, CSS, and JavaScript.

**No frontend build system is required.**

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │     Sensor Logs      │
                         │    Service Records   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Analysis Engine   │
                         │                      │
                         │  Python + Pandas     │
                         │  Python + NumPy      │
                         └──────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
       ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
       │    Readiness   │  │    Failure     │  │  Maintenance   │
       │   Classifier   │  │   Prediction   │  │    Ranking     │
       └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
               │                   │                   │
               └───────────────────┼───────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │    Analysis Output   │
                         └──────────┬───────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                       ▼                         ▼
              ┌─────────────────┐       ┌─────────────────┐
              │  Web Dashboard  │       │   MCP Server    │
              └─────────────────┘       └────────┬────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │    IBM Bob      │
                                        │  Agent / Ask    │
                                        └─────────────────┘
```

---

# 🔄 End-to-End Workflow

```text
        RAW DATA
           │
           ▼
 ┌─────────────────────┐
 │ Sensor + Service    │
 │ Data Ingestion      │
 └──────────┬──────────┘
            │
            ▼
 ┌─────────────────────┐
 │ Data Processing &   │
 │ 30-Day Analysis     │
 └──────────┬──────────┘
            │
            ▼
 ┌─────────────────────┐
 │ Sensor Trend        │
 │ Analysis            │
 └──────────┬──────────┘
            │
            ▼
 ┌─────────────────────┐
 │ Readiness           │
 │ Classification      │
 └──────────┬──────────┘
            │
            ▼
 ┌─────────────────────┐
 │ Failure Trend &     │
 │ Time-to-Failure     │
 └──────────┬──────────┘
            │
            ▼
 ┌─────────────────────┐
 │ Risk Scoring &      │
 │ Maintenance Ranking │
 └──────────┬──────────┘
            │
            ▼
 ┌─────────────────────┐
 │ Explainable         │
 │ Maintenance Plan    │
 └──────────┬──────────┘
            │
       ┌────┴────┐
       ▼         ▼
 Dashboard      MCP
                 │
                 ▼
              IBM Bob
```

---

# 🛠️ Technology Stack

| Component          | Technology              |
| ------------------ | ----------------------- |
| Analysis Engine    | Python                  |
| Data Processing    | Pandas                  |
| Numerical Analysis | NumPy                   |
| AI Integration     | MCP                     |
| MCP SDK            | Python `mcp` SDK        |
| Dashboard          | HTML / CSS / JavaScript |
| AI Assistant       | IBM Bob                 |
| Frontend Build     | None required           |

---

# 📁 Project Structure

```text
Mission-Readiness-Predictive-Maintenance-Copilot/
│
├── docs/
│   ├── problem-statement.md
│   ├── solution-overview.md
│   └── setup-guide.md
│
├── src/
│   ├── analyze.py
│   ├── dashboard.html
│   │
│   └── mcp_server/
│       ├── ...
│       └── README_bob_integration.md
│
├── demo/
│   └── screenshots/
│
└── README.md
```

---

# 💻 How to Run Locally

The project is designed to run locally without requiring the IBM Bob MCP connection.

## Prerequisites

Make sure your system has:

* Python 3.x
* pip
* A modern web browser

---

## 1. Clone the Repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

Move into the project directory:

```bash
cd <YOUR-PROJECT-FOLDER>
```

> Replace `<YOUR-GITHUB-REPOSITORY-URL>` and `<YOUR-PROJECT-FOLDER>` with your actual repository details.

---

## 2. Install Dependencies

Install the required Python packages:

```bash
pip install pandas numpy "mcp<2"
```

If your system uses `python3`:

```bash
python3 -m pip install pandas numpy "mcp<2"
```

---

## 3. Run the Analysis Engine

Navigate to the source directory:

```bash
cd src
```

Run the analysis:

```bash
python analyze.py
```

Or:

```bash
python3 analyze.py
```

The analysis engine processes the available sensor and service data and performs the predictive-maintenance analysis.

---

## 4. Open the Dashboard

After running the analysis, open:

```text
src/dashboard.html
```

You can:

* Double-click `dashboard.html`
* Open it directly in a browser

No Node.js, npm, or frontend build process is required.

---

# 🤖 IBM Bob + MCP Setup

The project includes an MCP server that allows **IBM Bob to interact with the predictive-maintenance analysis through live tools**.

The MCP server is located inside:

```text
src/mcp_server/
```

Detailed Bob integration instructions are available here:

[`src/mcp_server/README_bob_integration.md`](src/mcp_server/README_bob_integration.md)

---

# ⚠️ Important: MCP Configuration on a New System

The **local analysis engine and dashboard work independently of the existing IBM Bob MCP connection**.

However, if the project is copied or cloned onto a **different computer**, the MCP connection may need to be configured again.

### Why?

The MCP configuration can contain a **machine-specific absolute file path** pointing to the MCP server.

For example, the original system might contain:

```text
C:\Users\username\Mission-Copilot\src\mcp_server\server.py
```

After moving the project to another system, the actual path might be:

```text
D:\Projects\Mission-Copilot\src\mcp_server\server.py
```

In this situation, the project itself is not necessarily broken.

The MCP configuration simply needs to point to the **new local path**.

---

## 🔧 If IBM Bob Cannot Connect to MCP

If Bob cannot access the MCP tools after moving the project to another system:

### Step 1

Open the MCP configuration in IBM Bob.

### Step 2

Check the configured MCP server path.

### Step 3

Replace the old machine-specific path with the current path of:

```text
src/mcp_server/
```

### Step 4

Make sure Python and all required dependencies are installed.

```bash
pip install pandas numpy "mcp<2"
```

### Step 5

Restart or reload the MCP connection.

### Step 6

Test the MCP tools again.

---

> **Important:** An unavailable MCP connection does **not** prevent the core Python analysis engine or the local dashboard from running.

The MCP layer is an integration layer on top of the core predictive-maintenance system.

---

# 🧠 How the Analysis Works

The system analyzes sensor behavior over a **30-day observation window**.

---

## Step 1 — Data Ingestion

Sensor logs and service records are loaded into the analysis pipeline.

```text
Sensor Logs
     +
Service Records
     │
     ▼
Data Processing
```

---

## Step 2 — Sensor Trend Analysis

The system analyzes key parameters such as:

```text
┌──────────────┐
│  Vibration   │
├──────────────┤
│ Temperature  │
├──────────────┤
│  Pressure    │
└──────────────┘
```

The system evaluates both the current sensor values and their trends.

---

## Step 3 — Readiness Classification

Sensor conditions are compared against predefined thresholds.

```text
                 SENSOR CONDITION
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
         NORMAL       WARNING     CRITICAL
            │           │           │
            ▼           ▼           ▼
          READY      DEGRADED    NOT MISSION
                                  READY
```

---

## Step 4 — Failure Prediction

If a sensor demonstrates a concerning trend, linear extrapolation is used to estimate when it may reach its critical threshold.

Conceptually:

```text
Sensor
Value
  │
  │                         X Critical Threshold
  │                       /
  │                     /
  │                   /
  │                /
  │             /
  │          /
  │       /
  │    /
  │___/____________________________ Time
            │
            │
       Current Point

                 ↓

        Estimated Time-to-Failure
```

The result is an approximate prediction rather than an exact failure date.

---

## Step 5 — Risk Assessment

The system uses the analysis results to identify assets requiring attention.

```text
                    ASSET RISK
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
        Low           Medium         High
          │             │             │
          ▼             ▼             ▼
       Monitor       Inspect       Priority
```

---

## Step 6 — Maintenance Prioritization

Assets are ranked according to risk and urgency.

```text
HIGH RISK
   │
   ▼
Asset A → Immediate Attention
   │
   ▼
Asset B → High Priority
   │
   ▼
Asset C → Inspection Recommended
   │
   ▼
Asset D → Monitor
   │
   ▼
LOW RISK
```

---

# 🧠 Explainability by Design

The system intentionally uses a **rule-based readiness classifier** rather than an opaque machine-learning model.

This allows users to understand:

> **Why was this asset classified as risky?**

For example:

```text
Asset: AIRCRAFT-05

Status:
NOT MISSION READY

Reason:
Vibration is increasing above the acceptable
trend while temperature is approaching the
defined critical threshold.

Prediction:
Component may reach the critical threshold
in approximately X days.

Recommendation:
Prioritize inspection and maintenance.
```

This makes the system's recommendations easier for maintenance personnel to understand, verify, and act upon.

---

# 🔌 MCP Tools

The MCP server exposes live analysis capabilities to IBM Bob.

## Available Tools

### `get_fleet_summary`

Provides an overall view of fleet readiness and risk.

---

### `get_asset_detail`

Provides detailed health and sensor information for a selected asset.

---

### `get_prioritized_maintenance_plan`

Returns assets ranked according to maintenance priority.

---

### `get_assets_at_risk_before_mission`

Identifies assets that may present a mission risk before deployment.

---

# 🔄 MCP Interaction Flow

```text
                 USER
                   │
                   ▼
              IBM BOB
                   │
                   │ Tool Request
                   ▼
             MCP SERVER
                   │
                   ▼
          ANALYSIS ENGINE
                   │
                   ▼
             CURRENT DATA
                   │
                   ▼
          PREDICTIVE ANALYSIS
                   │
                   ▼
          EXPLAINABLE RESULT
                   │
                   ▼
             MCP SERVER
                   │
                   ▼
              IBM BOB
                   │
                   ▼
                 USER
```

This means Bob can retrieve **live results from the actual analysis pipeline** instead of relying on a static, manually prepared response.

---

# 🧪 Demo Data & Validation

The project currently uses **synthetic sensor and service data**.

The dataset contains intentionally injected degradation and failure signatures for demonstration and validation.

The validation process included intentionally planting at-risk assets and checking whether the analysis pipeline could identify them.

```text
5 Injected At-Risk Assets
          │
          ▼
   Analysis Pipeline
          │
          ▼
    Risk Calculation
          │
          ▼
   Ranked Asset List
          │
          ▼
5 At-Risk Assets
Correctly Surfaced
```

This provided a controlled way to validate the classifier and risk-ranking logic before preparing the final demonstration.

---

# 📊 Example Output

A simplified example of the system's output:

```text
┌────────────┬──────────────────────┬──────────────┐
│ Asset      │ Readiness            │ Risk         │
├────────────┼──────────────────────┼──────────────┤
│ Aircraft-01│ READY                │ LOW          │
│ Aircraft-02│ DEGRADED             │ MEDIUM       │
│ Aircraft-03│ READY                │ LOW          │
│ Aircraft-04│ DEGRADED             │ HIGH         │
│ Aircraft-05│ NOT MISSION READY    │ CRITICAL     │
└────────────┴──────────────────────┴──────────────┘
```

The actual values depend on the dataset being analyzed.

---

# ⚠️ Known Limitations

## 1. Synthetic Data

The current sensor and service records are synthetic and are intended for demonstration purposes.

They are **not live HUMS telemetry**.

The architecture is designed so that a real data source can replace the demonstration dataset without requiring fundamental changes to the classifier, predictor, or MCP interface.

---

## 2. Rule-Based Classification

The readiness classifier uses predefined thresholds instead of a trained machine-learning model.

This was chosen deliberately to provide:

* Explainability
* Predictable behavior
* Easy validation
* Fast implementation
* Transparent decision-making

The thresholds are **illustrative demo values** and are not calibrated against real fleet failure histories.

---

## 3. Linear Failure Prediction

Failure-day estimates currently use simple linear trend extrapolation.

Real-world equipment degradation can be nonlinear and may depend on:

* Operating conditions
* Environmental factors
* Component age
* Load conditions
* Maintenance history
* Multiple interacting failure modes

Therefore:

> **Predicted failure dates should be treated as directional early-warning signals, not precise countdowns.**

---

## 4. MCP Environment Dependency

The MCP integration depends on the local machine's configuration.

When the repository is moved to another system, the MCP server path may need to be updated in IBM Bob.

This does **not** affect the standalone Python analysis engine or dashboard.

---

# 🏆 What We're Most Proud Of

The MCP integration is **genuinely load-bearing**.

Bob does not simply receive a pasted or manually prepared summary.

Instead, Bob can call live tools such as:

```text
get_fleet_summary
get_asset_detail
get_prioritized_maintenance_plan
get_assets_at_risk_before_mission
```

These tools execute the actual analysis pipeline against the current project data.

The resulting architecture is:

```text
                 USER
                   │
                   ▼
               IBM BOB
                   │
                   ▼
              MCP TOOL
                   │
                   ▼
        ACTUAL ANALYSIS ENGINE
                   │
                   ▼
             CURRENT DATA
                   │
                   ▼
         PREDICTIVE ANALYSIS
                   │
                   ▼
        EXPLAINABLE RESULT
                   │
                   ▼
               IBM BOB
                   │
                   ▼
                 USER
```

We also validated the classifier against our intentionally injected failure signatures **before preparing the demonstration**.

All five planted at-risk assets were correctly surfaced among the highest-risk assets in the ranked output.

---

# 🎯 Design Philosophy

The project is built around three core principles.

## 🔮 Predictive

Identify degradation **before** it becomes an operational failure.

---

## 🔍 Explainable

Show users **why** an asset is considered risky rather than producing an unexplained score.

---

## ⚡ Actionable

Convert raw sensor information into **prioritized maintenance decisions**.

---

# 🌐 Local vs. IBM Bob Architecture

The project can be viewed as two layers:

```text
┌─────────────────────────────────────────────┐
│            CORE LOCAL SYSTEM                │
│                                             │
│  Sensor Data → Analysis → Prediction       │
│                   ↓                         │
│              Dashboard                     │
│                                             │
│          Works independently                │
└──────────────────────┬──────────────────────┘
                       │
                       │ Optional Integration
                       ▼
┌─────────────────────────────────────────────┐
│              IBM BOB LAYER                  │
│                                             │
│             IBM Bob                        │
│                ↓                            │
│            MCP Server                       │
│                ↓                            │
│        Analysis Engine                      │
│                                             │
│   MCP path may require reconfiguration      │
│   when moved to another computer            │
└─────────────────────────────────────────────┘
```

This separation ensures that the core predictive-maintenance functionality remains usable even if the external MCP connection needs to be reconfigured.

---

# ▶️ Quick Start

For the fastest local demonstration:

```bash
# Clone repository
git clone <YOUR-GITHUB-REPOSITORY-URL>

# Enter project
cd <YOUR-PROJECT-FOLDER>

# Install dependencies
pip install pandas numpy "mcp<2"

# Enter source directory
cd src

# Run analysis
python analyze.py
```

Then open:

```text
dashboard.html
```

---

# 🤖 Quick MCP Reminder

If the local dashboard works but IBM Bob cannot access the MCP tools:

```text
Dashboard works
      +
Python analysis works
      +
MCP connection fails
      ↓
Check MCP configuration/path
```

The most common issue after moving the repository to another computer is a **machine-specific MCP server path**.

Update the path in the IBM Bob MCP configuration and reload the connection.

For complete MCP instructions:

[`src/mcp_server/README_bob_integration.md`](src/mcp_server/README_bob_integration.md)

---

# 📸 Demo

Screenshots and demonstration material are available in:

[`demo/screenshots/`](demo/screenshots/)

---

# 📚 Documentation

Additional documentation:

* [`docs/problem-statement.md`](docs/problem-statement.md) — Detailed problem definition
* [`docs/solution-overview.md`](docs/solution-overview.md) — Solution architecture and approach
* [`docs/setup-guide.md`](docs/setup-guide.md) — Detailed local setup instructions
* [`src/mcp_server/README_bob_integration.md`](src/mcp_server/README_bob_integration.md) — IBM Bob + MCP integration

---

# ⚡ Quick Reference

| Task                 | Command / Location                         |
| -------------------- | ------------------------------------------ |
| Install dependencies | `pip install pandas numpy "mcp<2"`         |
| Enter source         | `cd src`                                   |
| Run analysis         | `python analyze.py`                        |
| Dashboard            | `src/dashboard.html`                       |
| MCP server           | `src/mcp_server/`                          |
| MCP documentation    | `src/mcp_server/README_bob_integration.md` |
| Demo screenshots     | `demo/screenshots/`                        |

---

# ⚠️ Disclaimer

This project is a **prototype developed for demonstration and evaluation purposes**.

The sensor data is synthetic, the thresholds are illustrative, and the failure predictions are directional estimates.

The system should not be used as the sole basis for real-world aircraft, vehicle, equipment, or mission-critical maintenance decisions.

---

# 🚀 Mission Readiness & Predictive Maintenance Copilot

### **From sensor data → to risk → to prediction → to action.**
