# v24.4.16 Web UI CSV Field Union Fix

## Fixed issue

The Web UI official-runner bridge could fail after a few delegated samples with:

```text
ValueError: dict contains fields not in fieldnames
```

This happened because `sg_platform/app.py::write_csv_rows()` used only the first row's keys as CSV fieldnames. Later rows produced by different defense groups or enterprise/protected-asset checks can include additional columns such as:

- `raw_result`
- `model_refusal`
- `business_risk_level`
- `enterprise_action`
- `response_action_type`
- `registry_match_rule`
- `secret_sensitivity`
- `data_classification`

## Change

`write_csv_rows()` now builds a stable union of all keys across all rows and writes with `extrasaction="ignore"`.

## Scope

This only fixes Web UI CSV consolidation after the official runner completes. It does not change:

- attack prompts
- scoring logic
- invalid-sample logic
- protected asset logic
- G-group defense behavior
