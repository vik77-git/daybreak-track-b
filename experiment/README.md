# Daybreak missing-information queue experiment

## Purpose
Test whether a deterministic, reviewable reconciliation queue can reduce false/stale follow-up proposals without an LLM or external messaging service.

## Baseline
`status == pending` + open/non-scheduled case + follow-up allowed + known request time + >=48h.

## Proposed
Baseline plus receipt reconciliation using `received_at` and `customer_reply` events. Proposed contacts are grouped by `case_id`, so multiple missing items produce one draft.

## Safety
Dry run only. No external messages. Uses the fixed snapshot time from `scenario.json`.

## Run
From `track-b/experiment/`:

```text
python queue.py --data-dir ../data --out-dir output/baseline --mode baseline
python queue.py --data-dir ../data --out-dir output/proposed --mode proposed
python checks/test_queue.py
```

## Outputs
- `output/proposed/proposed_actions.csv`
- `output/proposed/proposed_row_decisions.csv`
- `output/proposed/proposed_summary.json`
- analogous baseline outputs