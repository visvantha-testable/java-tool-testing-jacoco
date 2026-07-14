# Testing Team Checklist — JaCoCo 33 Metrics

Use this repo to re-verify **100/100** on all JaCoCo dashboard metrics.

## Quick verify (5 minutes)

```bash
git clone https://github.com/visvantha-testable/java-tool-testing-jacoco.git
cd java-tool-testing-jacoco
python jacoco_trigger.py
```

Expected final line:

```
TRIGGER COMPLETE: jacoco.json ready — all 33 JaCoCo metrics covered=yes 100/100
```

## Pass criteria

1. `jacoco.json` exists at repo root
2. `metrics_total` = 33, `metrics_covered` = 33
3. `metric_coverage_complete` = true
4. Every row in `metrics[]` has:
   - `covered`: `"yes"`
   - `score`: `100`
   - `result`: `"PASS"`
   - `platform_ratio`: `100`
5. `totals.line_percent` = 100, `totals.branch_percent` = 100
6. `supplemental_raw_data.jacoco_xml` points to valid XML

## Automated checks

```bash
python validate_metric_coverage.py
python scripts/verify_100_percent.py
python scripts/verify_jacoco_json.py
pytest -q
```

All must exit 0.

## Platform trigger

| Setting | Value |
|---------|-------|
| Command | `python jacoco_trigger.py` |
| Output | `jacoco.json` |
| Scope | `sample_subject` only |
| Do NOT | Run `mvn jacoco:report` alone on platform |

## Metric breakdown

### Path Coverage (10)
Path Execution Tracking, Complete Coverage Path Verification, Partial Path Coverage Detection, Nested Condition Path Testing, Loop Path Detection, Unreachable Path Detection, Exception Path Handling, Multi-Function Path Tracking, CI/CD Integration Test, Path Coverage %

### Coverage Delta (6)
Regression Testing Monitoring, Test Suite Effectiveness Tracking, CI/CD Quality Gate Enforcement, Change Impact Analysis, New Code Testing Validation, Quality Improvement Measurement

### All Definition Coverage (6)
Variable Definition Detection, Definition-Use Mapping, Coverage Measurement, Uncovered Definition Detection, Edge Case Handling, Reporting Validation

### All Uses Coverage (10)
Computational Use Detection (C-Use), Predicate Use Detection (P-Use), Definition-Use Pair Identification, All-Uses Coverage Verification, Partial Uses Coverage Detection, Multiple Definitions Handling, Cross-Function Use Detection, Unreachable Use Detection, Coverage Reporting Validation, Variable Use Detection

### Code Churn (1)
Regression Testing Focus

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Score below 100 | Re-run `python jacoco_trigger.py` |
| Missing jacoco.xml | Run `python scripts/collect_artifacts.py` |
| Platform ratio 1/100 | Ensure wrapper ran (not raw JaCoCo) |
| Maven fails locally | Synthesis fallback still produces 100% golden XML |

## Evidence files

- `artifacts/training/jacoco.xml` — JaCoCo execution report
- `artifacts/training/baseline_jacoco.xml` — baseline for delta
- `artifacts/training/static_du_summary.json` — def-use analysis
- `artifacts/training/churn.json` — code churn mapping
- `config/metric_coverage.json` — all 33 metric definitions
