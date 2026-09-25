# Handover

- Name: Vikram
- Email used for this application: vikram14markiv@gmail.com
- Chosen track: Track B - Find the worthwhile automation
- Why this track (one or two sentences): I selected this narrow missing-information workflow because the supplied data exposes repeat follow-ups, stale request states and a clear reconciliation problem that can be tested locally without a paid integration.
- Approximate total time, including setup and handover: 2 hours (approx).

## Run and verify

Prerequisite: Python 3.10+, no third-party packages, no credentials.

From the extracted `track-b` folder:

```text
python starter.py
python experiment/queue.py --data-dir data --out-dir experiment/output/baseline --mode baseline
python experiment/queue.py --data-dir data --out-dir experiment/output/proposed --mode proposed
python experiment/checks/test_queue.py
```

On Windows, `py` can replace `python`; on macOS/Linux, `python3` can replace it.

Expected clean-check output:

```text
PASS: baseline vs proposed comparison
PASS: changed input (47h) becomes uncertain/no action
PASS: valid no-action input completes successfully
```

Core outputs:
- `experiment/output/baseline/baseline_actions.csv`
- `experiment/output/proposed/proposed_actions.csv`
- `experiment/output/proposed/proposed_row_decisions.csv`
- `experiment/output/proposed/proposed_summary.json`
- `experiment/output/changed_47h/proposed_summary.json`
- `experiment/output/no_action/proposed_summary.json`

## What I delivered

`DECISION.md` recommends a process change rather than two engineering weeks of custom AI work. The experiment compares a status-only baseline with a deterministic reconciliation queue, groups multiple requests into one case-level draft and never sends anything.

`SOURCES.md` contains four current external sources. The main technical claim is that safe follow-up depends on a receipt signal rather than a stale `pending` state; vendor documentation is used to verify file-request capabilities, while the local prototype verifies the reconciliation logic.

## Evidence and limits

Observed on the supplied snapshot:

- 128 event rows became 124 stable events after removing four repeated event deliveries.
- 400 minutes of coordinator effort are known after deduplication; three stable events have missing effort values.
- 12 missing-information requests are pending. The baseline yields 5 eligible request rows / 3 case-level drafts. The proposed reconciliation yields 4 request rows / 2 case-level drafts.
- The clean checks pass. The execution host also printed an unrelated `artifact_tool` spreadsheet-runtime warmup traceback to stderr; the Python commands exited with code 0 and the prototype itself has no exception.
- Changed input: moving C024 requests to 47 hours before the fixed snapshot was expected to remove C024 from the action queue; observed action count fell from 2 to 1, leaving only C009.
- Valid no-action input: marking all open missing-information requests as received was expected to produce zero proposed actions; observed action count was 0.

The experiment does not verify a live OneDrive/Dropbox/Jotform integration, customer adoption, hidden phone effort, staff hourly cost, revenue impact or compliance/legal consent. It is a dry run only.

The first real-world question is whether a coordinator can review the exception queue twice weekly in no more than 10 minutes while avoiding stale/duplicate follow-ups. The next step is a two-week pilot with actual review time and contact outcomes.

## Tools and judgment

1. **AI-assisted analysis → keep deterministic rules.** I used ChatGPT (GPT-5.6 Luna) to structure the investigation and draft the experiment, then checked the logic by running the code against the supplied CSVs.
2. **Vendor capability research → do not overclaim it.** OneDrive/Dropbox documentation was checked for file-request behavior and limitations; no vendor API was called.
3. **Automation scope → process first.** The sample did not justify a custom AI build from the measured reminder effort, so I kept the prototype standard-library Python and made all customer contact dry-run only.

# TOOL-USE SUMMARY

## Tools used

| Tool / technology | Model / version | Use |
|---|---|---|
| ChatGPT | OpenAI GPT-5.6 Luna | Research assistance, evidence interpretation, experiment design, documentation drafting, requirement checking and review |
| Python | Python 3.x (local) | Read the supplied CSV/JSON evidence, run the prototype, generate outputs, and execute verification checks |
| Git / GitHub | Git CLI / GitHub repository | Version control, submission packaging, and making the final assessment materials accessible to the reviewer |
| Web research | Official product/technical documentation | Verify the external technical claim used in the recommendation |

## How AI output was checked

AI output was treated as an implementation and reasoning aid, not as evidence by itself.

I checked the work by:

1. Running the prototype locally against the supplied `cases.csv`, `events.csv`, `requests.csv`, and `scenario.json`.
2. Comparing the proposed reconciliation workflow with a simple baseline on the same inputs.
3. Running the verification cases, including a deliberately changed input and a valid no-action input.
4. Checking calculations against the source records rather than accepting generated numbers without verification.
5. Checking the key external capability claim against original product/technical documentation.
6. Reviewing the final repository structure against the Track B submission requirements.

## Concrete examples of correction / rejection

One issue caught during the assessment was that the first uploaded archive contained **Track A** rather than the required **Track B** evidence pack. That data was not used for the assessment. After the correct Track B files were provided, the analysis and experiment were based on those supplied records.

Another check identified why a naive status-only follow-up rule could propose an unnecessary action: a request could remain marked as pending even though the case/event state made the request stale or otherwise inconsistent. The proposed workflow therefore reconciles the request with the current case/event evidence before generating a draft action.

The experiment was also tested with a changed input around the timing boundary and with a valid input that produced **no proposed actions**, confirming that the program reports a no-work condition without failing.

## AI/tool decision boundary

AI was used to accelerate analysis, implementation, and documentation. The final decision, calculations, verification results, source validation, and submission contents were checked against executable tests, supplied evidence, and external documentation.

No paid external AI API or production messaging service was used by the prototype. The experiment is a dry run and generates proposed actions/drafts only.

## Model / effort setting

**Model:** OpenAI GPT-5.6 Luna

**User-configured effort setting:** No separate user-configured effort setting was used or recorded.