# Experiment evidence

## Central claim

Safe follow-up should require a receipt signal in addition to request status. A stale `pending` field must not override evidence that the requested item was received.

## Baseline vs proposed

| Measure | Baseline | Proposed |
|---|---:|---:|
| Missing-info request rows considered | 12 | 12 |
| Eligible request rows | 5 | 4 |
| Case-level dry-run drafts | 3 | 2 |
| C018 follow-up | Proposed | Suppressed because `received_at` is present |
| Duplicate case actions | None | None; C009 and C024 are grouped by case |

The baseline deliberately uses only the published workflow constraints: pending request, open/non-scheduled case, follow-up allowed, known request time, and at least 48 elapsed hours. The proposed method adds receipt reconciliation from `received_at` and `customer_reply`.

## Verification checks

1. **Edge / stale state:** C018 remains `pending` but has a recorded receipt and a matching customer-reply event. Expected before run: suppress contact. Observed: C018 is not in the proposed queue.
2. **Changed input:** R024 and R026 were changed from 72+ hours old to 47 hours old relative to the fixed snapshot. Expected before run: C024 drops out because the 48-hour rule is not met. Observed: proposed action count changed from 2 to 1 and only C009 remained.
3. **No-action condition:** all open missing-information requests were changed to have a receipt. Expected before run: zero proposed actions. Observed: zero; the program completed normally.

## What the local mock proves

It proves deterministic queue behavior, stable IDs, grouping, duplicate-event handling, explicit uncertain states, and suppression when a receipt signal exists. It does not prove the behavior of a live OneDrive, Dropbox or Jotform account.