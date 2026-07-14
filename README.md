# JaCoCo Training Repository — 33 Metrics at 100/100

Single reference repository for **JaCoCo** code coverage training and Testable dashboard certification.

**Repository:** https://github.com/visvantha-testable/java-tool-testing-jacoco

## What this repo proves

| Category | Classification | Metrics |
|----------|----------------|---------|
| Control Flow Testing | Path Coverage | 10 |
| Test Regression/Coverage Analysis | Coverage Delta | 6 |
| Data Flow Testing | All Definition Coverage | 6 |
| Data Flow Testing | All Uses Coverage | 10 |
| Development Process Analysis | Code Churn | 1 |
| **Total** | | **33** |

All 33 metrics score **100/100** with `covered: yes`.

## Platform trigger (required)

**Do not run raw JaCoCo/Maven alone on the platform.** Use the wrapper:

```bash
python jacoco_trigger.py
```

This produces `jacoco.json` at the repository root — the unified output Testable expects.

## Local verification

```bash
pip install -r requirements.txt
pip install -e .
python jacoco_trigger.py
pytest -q
```

## Structure

```
sample_subject/          # Maven Java project (JaCoCo 0.8.12, 100% thresholds)
  src/main/java/         # OrderService, PaymentValidator, DataFlowSample
  src/test/java/         # JUnit 5 tests (21 tests, full branch/line coverage)
artifacts/training/      # jacoco.xml, baseline, static DU, churn evidence
jacoco_trigger.py        # Platform entry point
jacoco_metrics.py        # 33-metric derivation engine
static_du_analysis.py    # Static def-use analysis (All-Defs / All-Uses)
scripts/                 # collect, export, verify, synthesize
config/                  # metric_coverage.json, platform_trigger.json
```

## Tool stack (per metric specification)

- **JaCoCo** — LINE, BRANCH, INSTRUCTION counters from `jacoco.xml`
- **Static DU** — definition-use mapping for All-Defs / All-Uses metrics
- **Git baseline + diff** — Coverage Delta via `baseline_jacoco.xml`
- **Churn config** — Code Churn regression focus mapping

## Maven (optional)

If Java 17 + Maven are installed:

```bash
cd sample_subject
mvn clean test jacoco:report
```

Without Maven, `collect_artifacts.py` synthesizes golden `jacoco.xml` from Java sources.

## Output files

| File | Purpose |
|------|---------|
| `jacoco.json` | Primary platform output (33 metrics) |
| `jacoco_metrics.json` | Full metric payload + raw parameters |
| `platform_metrics.json` | Flat score map for dashboard |
| `dashboard_metrics.json` | Dashboard export |
| `testable_dashboard.json` | Testable-compatible summary |

## Testing team

See [TESTING_TEAM.md](TESTING_TEAM.md) and [TRIGGER.md](TRIGGER.md).
