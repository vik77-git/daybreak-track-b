#!/usr/bin/env python3
"""Verification checks for the Daybreak dry-run queue. Standard library only."""
from pathlib import Path
import csv, json, shutil, tempfile

import importlib.util

_queue_spec = importlib.util.spec_from_file_location("daybreak_queue", Path(__file__).resolve().parents[1] / "queue.py")
_queue = importlib.util.module_from_spec(_queue_spec)
_queue_spec.loader.exec_module(_queue)
run = _queue.run

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "data"
OUT = ROOT / "output" / "checks"


def copy_data(dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for name in ["cases.csv", "events.csv", "requests.csv", "scenario.json"]:
        shutil.copy2(DATA / name, dst / name)


def read_actions(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def mutate_request(data_dir: Path, request_id: str, field: str, value: str):
    p = data_dir / "requests.csv"
    with p.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = f.readline if False else None
    for row in rows:
        if row["request_id"] == request_id:
            row[field] = value
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def assert_baseline_and_proposed():
    base_out = OUT / "baseline"
    prop_out = OUT / "proposed"
    b = run(DATA, base_out, "baseline")
    p = run(DATA, prop_out, "proposed")
    assert b["action_count"] == 3, b
    assert p["action_count"] == 2, p

    # One baseline case (C018) is removed because receipt is already recorded.
    assert {a["case_id"] for a in b["actions"]} == {"C009", "C018", "C024"}
    assert {a["case_id"] for a in p["actions"]} == {"C009", "C024"}

    # Grouping prevents duplicate actions for a case with multiple missing items.
    c009 = next(a for a in p["actions"] if a["case_id"] == "C009")
    assert c009["items"] == "fault_photo;site_access"
    c024 = next(a for a in p["actions"] if a["case_id"] == "C024")
    assert c024["items"] == "fault_photo;serial_number"

    return b, p


def assert_changed_input_under_48h():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        copy_data(td)
        # 47 hours before the fixed snapshot: expected C024 disappears.
        mutate_request(td, "R024", "last_requested_at", "2026-09-05T10:00+05:30")
        mutate_request(td, "R026", "last_requested_at", "2026-09-05T10:00+05:30")
        out = td / "out"
        result = run(td, out, "proposed")
        assert result["action_count"] == 1, result
        assert {a["case_id"] for a in result["actions"]} == {"C009"}
        decisions = read_actions(out / "proposed_row_decisions.csv")
        c024 = [r for r in decisions if r["request_id"] in {"R024", "R026"}]
        assert all(r["decision"] == "uncertain" and r["reason"] == "under_48h_since_request" for r in c024)


def assert_no_action_input():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        copy_data(td)
        # Make every missing-information request either received or closed.
        p = td / "requests.csv"
        with p.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        closed_case_ids = {"C001","C005","C013","C019"}
        for row in rows:
            if row["item"] in {"fault_photo","serial_number","site_access"}:
                if row["case_id"] not in closed_case_ids:
                    row["received_at"] = "2026-09-06T12:00+05:30"
        with p.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader(); writer.writerows(rows)
        result = run(td, td / "out", "proposed")
        assert result["action_count"] == 0, result
        assert result["decision_counts"].get("propose", 0) == 0


if __name__ == "__main__":
    b, p = assert_baseline_and_proposed()
    assert_changed_input_under_48h()
    assert_no_action_input()
    print("PASS: baseline vs proposed comparison")
    print("PASS: changed input (47h) becomes uncertain/no action")
    print("PASS: valid no-action input completes successfully")