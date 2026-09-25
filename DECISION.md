# Decision note — Daybreak Repairs

## Decision

**Change the process now; do not spend the two engineering weeks on custom AI automation yet.** Pilot a deterministic, reviewable missing-information queue using the existing inbox/spreadsheet as the system of record. If Daybreak already has Microsoft 365 Business, test OneDrive File Requests as an optional collection mechanism; do not buy a new platform based on this sample alone.

### User and workflow

The narrow problem is **collecting missing information before a technician can progress a case**: fault photos, serial numbers, or site-access details. The sample has 24 cases and 12 pending missing-information requests. It cannot validate the owner's “eight hours a week” claim because the export omits some calls and only logs coordinator effort; customer waiting time, technician time and financial benefit are not measured.

### What the data says

| Calculation | Result | Treatment |
|---|---:|---|
| Event rows → stable events | 128 → 124 | 4 duplicate deliveries removed by `event_id`; duplicates add no effort |
| Logged coordinator effort | 400 min known | 3 stable events have missing `active_minutes`; blank is not zero |
| Pending missing-info requests | 12 | `fault_photo`, `serial_number`, `site_access` only |
| Basic eligible → reconciled | 5 requests / 3 case drafts → 4 requests / 2 case drafts | Applied state, permission, timing and receipt checks |

C018 is the key reconciliation case: its request says `pending`, but `received_at` is populated and the event says the photo arrived in another thread. A status-only queue would draft a follow-up; the proposed queue suppresses it. C009 and C024 remain actionable and are grouped by case, preventing duplicate contacts when multiple items are missing. C022 is uncertain because the request time is missing. C016 is uncertain because only 46 hours have elapsed at the fixed snapshot. C012 is excluded because follow-up is forbidden. Closed/cancelled/scheduled cases are excluded.

Quote approval is a smaller opportunity in this snapshot: 3 approval requests exist; one passes basic filters, one is opt-out, and one is only 46 hours old.

### Alternatives

**Existing tool — OneDrive File Request.** Microsoft documents that OneDrive for Business can collect files through a link from people without OneDrive, storing uploads in a selected folder. That fits fault photos, but it is file collection, not request-state reconciliation, and the feature requires OneDrive for Business. Current India pricing lists Business Basic at ₹170/user/month with Teams or ₹130 without Teams, annual billing, before GST.

**Process-only change.** Keep the shared inbox and spreadsheet, but make each request canonical: case ID, item, last-requested time, receipt signal, permission and next action. Review exceptions twice a week. Cost assumption: ₹0 new software; review time must be measured.

**Custom build.** A rules engine is feasible, but this sample does not establish enough recoverable admin time to justify two engineering weeks.

### Technical claim tested

The critical claim is: **safe follow-up needs a reliable receipt signal, not just a stale `pending` status.** Vendor documentation supports the file-collection side: a successful OneDrive request produces an upload in a known folder and notification, but it does not prove Daybreak's existing records will reconcile automatically. The local prototype therefore tests only the reconciliation logic. It suppresses C018 and passes changed-input checks. It does **not** verify a Microsoft integration.

### Net value estimate

The directly observed chasing effort is **9 logged reminder minutes over 14 days** (4.5 min/week). Assume two 5-minute queue reviews in the same period: **10 min review − 9 min reminder effort = −1 min net coordinator time per 14 days**, with **₹0 tool cost**. Coordinator hourly cost, unlogged chasing and customer-value effects are unknown, so no INR savings claim is made. This uncertain/negative time case argues against custom engineering while leaving error reduction as a pilot benefit.

### Next experiment and stop/continue rule

Run the queue twice a week for two weeks and record **review minutes, proposed contacts, stale/duplicate contacts avoided, and cases resolved without another reminder**. Continue only if the pilot shows at least **15 coordinator minutes saved per week or a clear reduction in stale/duplicate follow-ups without more than 10 review minutes per week**. Otherwise stop and keep the process manual.