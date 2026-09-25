#!/usr/bin/env python3
"""
Daybreak Repairs - dry-run missing-information follow-up queue.

Standard library only. Uses scenario.json snapshot time, never system time.
No messages are sent. Output is a reviewable action queue plus row-level decisions.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


MISSING_INFO_ITEMS = {"fault_photo", "serial_number", "site_access"}
CLOSED_CASE_STATUSES = {"completed", "cancelled", "scheduled"}


def parse_dt(value: str | None) -> datetime | None:
    if not value or not value.strip():
        return None
    return datetime.fromisoformat(value)


def load_csv(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize_int(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def build_event_index(events: List[dict]) -> Tuple[Dict[str, dict], Dict[str, datetime]]:
    # Stable event_id is the identity: duplicate exported deliveries must not
    # inflate activity or counts.
    unique = {}
    for e in events:
        unique.setdefault(e["event_id"], e)

    latest_reply: Dict[str, datetime] = {}
    for e in unique.values():
        if e["event_type"] != "customer_reply":
            continue
        dt = parse_dt(e["occurred_at"])
        if dt is None:
            continue
        case_id = e["case_id"]
        if case_id not in latest_reply or dt > latest_reply[case_id]:
            latest_reply[case_id] = dt
    return unique, latest_reply


def classify(
    request: dict,
    case_status: str,
    snapshot: datetime,
    min_gap_hours: int,
    latest_reply: Dict[str, datetime],
    proposed: bool,
) -> Tuple[str, str, float | None]:
    if request["status"] != "pending":
        return "excluded", "request_not_pending", None

    if case_status in CLOSED_CASE_STATUSES:
        return "excluded", "case_closed_or_scheduled", None

    if normalize_int(request.get("followup_allowed")) != 1:
        return "excluded", "followup_not_allowed", None

    last_requested = parse_dt(request.get("last_requested_at"))
    if last_requested is None:
        return "uncertain", "missing_last_requested_at", None

    age_hours = (snapshot - last_requested).total_seconds() / 3600
    if age_hours < min_gap_hours:
        return "uncertain", "under_48h_since_request", age_hours

    # Proposed method's reconciliation layer.
    if proposed:
        received_at = parse_dt(request.get("received_at"))
        if received_at is not None:
            return "excluded", "received_at_present", age_hours

        reply_at = latest_reply.get(request["case_id"])
        if reply_at is not None and reply_at >= last_requested:
            return "excluded", "customer_reply_after_request", age_hours

    return "propose", "eligible_after_checks", age_hours


def run(data_dir: Path, out_dir: Path, mode: str = "proposed") -> dict:
    cases = load_csv(data_dir / "cases.csv")
    requests = load_csv(data_dir / "requests.csv")
    events = load_csv(data_dir / "events.csv")
    scenario = json.loads((data_dir / "scenario.json").read_text(encoding="utf-8"))

    snapshot = parse_dt(scenario["snapshot_at"])
    assert snapshot is not None
    min_gap = int(scenario["minimum_followup_gap_hours"])

    cases_by_id = {row["case_id"]: row for row in cases}
    unique_events, latest_reply = build_event_index(events)

    decisions = []
    candidate_by_case = defaultdict(list)
    for r in requests:
        if r["item"] not in MISSING_INFO_ITEMS:
            continue

        status, reason, age_hours = classify(
            r,
            cases_by_id[r["case_id"]]["status"],
            snapshot,
            min_gap,
            latest_reply,
            proposed=(mode == "proposed"),
        )
        row = {
            "request_id": r["request_id"],
            "case_id": r["case_id"],
            "item": r["item"],
            "request_status": r["status"],
            "case_status": cases_by_id[r["case_id"]]["status"],
            "last_requested_at": r["last_requested_at"],
            "received_at": r["received_at"],
            "followup_allowed": r["followup_allowed"],
            "hours_since_last_request": None if age_hours is None else round(age_hours, 2),
            "decision": status,
            "reason": reason,
            "contact_address": r["contact_address"],
        }
        decisions.append(row)
        if status == "propose":
            candidate_by_case[r["case_id"]].append(row)

    actions = []
    for case_id, rows in sorted(candidate_by_case.items()):
        items = sorted({r["item"] for r in rows})
        request_ids = sorted(r["request_id"] for r in rows)
        actions.append({
            "case_id": case_id,
            "contact_address": cases_by_id[case_id] and next(
                (r["contact_address"] for r in rows if r["contact_address"]), ""
            ),
            "items": ";".join(items),
            "source_request_ids": ";".join(request_ids),
            "reason": "Missing information remains unresolved and the last request is at least 48 hours old; no receipt signal was found.",
            "draft_subject": "Daybreak Repairs — information needed for your repair request",
            "draft_body": (
                "DRY RUN — DO NOT SEND. Daybreak Repairs is missing: "
                + ", ".join(items)
                + ". Please reply with the requested information when convenient."
            ),
        })

    decision_counts = defaultdict(int)
    for d in decisions:
        decision_counts[d["decision"]] += 1

    result = {
        "mode": mode,
        "snapshot_at": scenario["snapshot_at"],
        "dry_run_only": bool(scenario["dry_run_only"]),
        "unique_event_count": len(unique_events),
        "source_event_rows": len(events),
        "decision_counts": dict(sorted(decision_counts.items())),
        "action_count": len(actions),
        "actions": actions,
        "claim_scope": (
            "The local experiment verifies deterministic reconciliation behavior "
            "against the supplied CSV snapshot; it does not verify any vendor API."
        ),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / f"{mode}_row_decisions.csv", decisions, list(decisions[0].keys()) if decisions else [
        "request_id", "case_id", "item", "request_status", "case_status",
        "last_requested_at", "received_at", "followup_allowed",
        "hours_since_last_request", "decision", "reason", "contact_address"
    ])
    write_csv(out_dir / f"{mode}_actions.csv", actions, [
        "case_id", "contact_address", "items", "source_request_ids",
        "reason", "draft_subject", "draft_body"
    ])
    (out_dir / f"{mode}_summary.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["baseline", "proposed"], default="proposed")
    args = parser.parse_args()
    result = run(args.data_dir, args.out_dir, args.mode)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()