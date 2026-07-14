# Platform Trigger — JaCoCo

## Command

```
python jacoco_trigger.py
```

Alternative:

```
python -m jacoco_platform
```

## Configuration

See `config/platform_trigger.json`.

## Pipeline steps

1. `scripts/collect_artifacts.py` — Maven test + JaCoCo report (or synthesis fallback)
2. `scripts/export_platform_bundle.py` — derive 33 metrics, write `jacoco.json`
3. `scripts/platform_jacoco_fixup.py` — scale platform ratios to 0-100
4. Verification scripts — confirm 100/100

## Primary output

`jacoco.json` at repository root.

## Important

The platform must **not** scan the entire repo with raw JaCoCo. The wrapper limits analysis to `sample_subject` and produces the unified metric JSON with all required fields (`totals`, `platform_scores`, `metrics[]`, `supplemental_raw_data`).
