#!/usr/bin/env python3
"""
Log time entries to Clockify via API.

Modes:
  single  — one entry via CLI args
  batch   — multiple entries from a YAML file
  weekly  — full week from a recurring schedule file
"""

import argparse
import os
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
import yaml

CLOCKIFY_API_BASE = "https://api.clockify.me/api/v1"
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


# ── API helpers ────────────────────────────────────────────────────────────────

def get_headers(api_key: str) -> dict:
    return {"X-Api-Key": api_key, "Content-Type": "application/json"}


def get_workspace_id(api_key: str, workspace_id: str | None) -> str:
    if workspace_id:
        return workspace_id
    resp = requests.get(f"{CLOCKIFY_API_BASE}/workspaces", headers=get_headers(api_key))
    resp.raise_for_status()
    workspaces = resp.json()
    if not workspaces:
        sys.exit("No workspaces found for this API key.")
    return workspaces[0]["id"]


def find_project_id(api_key: str, workspace_id: str, project_name: str) -> str:
    resp = requests.get(
        f"{CLOCKIFY_API_BASE}/workspaces/{workspace_id}/projects",
        headers=get_headers(api_key),
        params={"name": project_name, "archived": False},
    )
    resp.raise_for_status()
    projects = resp.json()
    for p in projects:
        if p["name"].lower() == project_name.lower():
            return p["id"]
    available = [p["name"] for p in projects]
    sys.exit(f"Project '{project_name}' not found. Available: {available}")


def create_entry(
    api_key: str,
    workspace_id: str,
    description: str,
    start: str,
    end: str,
    project_id: str | None = None,
    billable: bool = False,
    tag_ids: list[str] | None = None,
) -> dict:
    payload = {"start": start, "end": end, "description": description, "billable": billable}
    if project_id:
        payload["projectId"] = project_id
    if tag_ids:
        payload["tagIds"] = tag_ids

    resp = requests.post(
        f"{CLOCKIFY_API_BASE}/workspaces/{workspace_id}/time-entries",
        headers=get_headers(api_key),
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()


# ── Datetime helpers ───────────────────────────────────────────────────────────

def to_utc(date_obj: date, time_str: str, tz_name: str = "UTC") -> str:
    """Convert a local date+time string to ISO 8601 UTC."""
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        sys.exit(f"Unknown timezone '{tz_name}'. Try: pip install tzdata")
    t = datetime.strptime(time_str, "%H:%M").time()
    dt_local = datetime.combine(date_obj, t, tzinfo=tz)
    return dt_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hours_between(start_iso: str, end_iso: str) -> float:
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    delta = datetime.strptime(end_iso, fmt) - datetime.strptime(start_iso, fmt)
    return delta.seconds / 3600


def week_monday(week_str: str | None) -> date:
    """Return the Monday of the requested week. Defaults to current week."""
    if week_str:
        d = datetime.strptime(week_str, "%Y-%m-%d").date()
        return d - timedelta(days=d.weekday())
    today = date.today()
    return today - timedelta(days=today.weekday())


# ── Entry processing ───────────────────────────────────────────────────────────

def process_entry(
    api_key: str,
    workspace_id: str,
    entry: dict,
    tz_name: str = "UTC",
    dry_run: bool = False,
) -> None:
    date_obj = (
        datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if isinstance(entry["date"], str)
        else entry["date"]
    )
    date_str = date_obj.isoformat()
    start_iso = to_utc(date_obj, entry["start"], tz_name)
    end_iso = to_utc(date_obj, entry["end"], tz_name)
    duration = hours_between(start_iso, end_iso)
    label = (
        f"  {'[DRY]' if dry_run else '[OK] '} "
        f"{date_str} {entry['start']}-{entry['end']} ({duration:.1f}h) "
        f"| {entry.get('description', '')} | project={entry.get('project', '—')}"
    )

    if dry_run:
        print(label)
        return

    project_id = None
    if project_name := entry.get("project"):
        project_id = find_project_id(api_key, workspace_id, project_name)
    elif pid := entry.get("project_id"):
        project_id = pid

    result = create_entry(
        api_key=api_key,
        workspace_id=workspace_id,
        description=entry.get("description", ""),
        start=start_iso,
        end=end_iso,
        project_id=project_id,
        billable=entry.get("billable", False),
        tag_ids=entry.get("tag_ids"),
    )
    print(f"{label} | id={result['id']}")


def run_entries(
    api_key: str,
    workspace_id: str,
    entries: list[dict],
    tz_name: str = "UTC",
    dry_run: bool = False,
) -> None:
    errors = 0
    for i, entry in enumerate(entries, 1):
        try:
            process_entry(api_key, workspace_id, entry, tz_name=tz_name, dry_run=dry_run)
        except Exception as exc:
            print(f"  [FAIL] Entry {i}: {exc}")
            errors += 1
    if errors:
        sys.exit(f"{errors}/{len(entries)} entries failed.")


# ── Weekly schedule builder ────────────────────────────────────────────────────

def build_weekly_entries(schedule_data: dict, monday: date) -> list[dict]:
    """
    Expand the schedule into concrete entries for the week starting on `monday`.

    Priority: weeks[YYYY-MM-DD][day] > default[day]
    A day set to an empty list ([]) means day off — skip it.
    """
    default_days: dict = schedule_data.get("default", {})
    week_key = monday.isoformat()
    week_override: dict = schedule_data.get("weeks", {}).get(week_key, {})

    entries = []
    for offset, day_name in enumerate(WEEKDAYS):
        day_date = monday + timedelta(days=offset)

        if day_name in week_override:
            day_entries = week_override[day_name]
        elif day_name in default_days:
            day_entries = default_days[day_name]
        else:
            continue

        if not day_entries:  # explicit empty list = day off
            continue

        for slot in day_entries:
            entries.append({**slot, "date": day_date})

    return entries


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Log hours to Clockify")
    parser.add_argument("--api-key", default=os.environ.get("CLOCKIFY_API_KEY"))
    parser.add_argument("--workspace-id", default=os.environ.get("CLOCKIFY_WORKSPACE_ID"))

    sub = parser.add_subparsers(dest="mode")

    # single
    single = sub.add_parser("single", help="Log one time entry")
    single.add_argument("--date", required=True, help="YYYY-MM-DD")
    single.add_argument("--start", required=True, help="HH:MM")
    single.add_argument("--end", required=True, help="HH:MM")
    single.add_argument("--description", required=True)
    single.add_argument("--project")
    single.add_argument("--project-id")
    single.add_argument("--billable", action="store_true")
    single.add_argument("--timezone", default="UTC", help="Local timezone (e.g. America/Argentina/Buenos_Aires)")

    # batch
    batch = sub.add_parser("batch", help="Log entries from a YAML file")
    batch.add_argument("--file", required=True)
    batch.add_argument("--dry-run", action="store_true", help="Preview without creating")

    # weekly
    weekly = sub.add_parser("weekly", help="Log a full week from a schedule file")
    weekly.add_argument("--schedule", required=True, help="Path to weekly_schedule.yml")
    weekly.add_argument("--week", help="Monday of target week (YYYY-MM-DD). Defaults to current week.")
    weekly.add_argument("--dry-run", action="store_true", help="Preview without creating")

    args = parser.parse_args()

    if not args.api_key:
        sys.exit("Error: CLOCKIFY_API_KEY not set.")

    workspace_id = get_workspace_id(args.api_key, args.workspace_id)
    print(f"Workspace: {workspace_id}")

    if args.mode == "single":
        entry = {
            "date": args.date,
            "start": args.start,
            "end": args.end,
            "description": args.description,
            "billable": args.billable,
        }
        if args.project:
            entry["project"] = args.project
        if args.project_id:
            entry["project_id"] = args.project_id
        process_entry(args.api_key, workspace_id, entry, tz_name=args.timezone)

    elif args.mode == "batch":
        with open(args.file) as f:
            data = yaml.safe_load(f)
        entries = data.get("entries", [])
        tz_name = data.get("timezone", "UTC")
        print(f"Timezone: {tz_name} | {len(entries)} entries{' (dry run)' if args.dry_run else ''}")
        run_entries(args.api_key, workspace_id, entries, tz_name=tz_name, dry_run=args.dry_run)

    elif args.mode == "weekly":
        with open(args.schedule) as f:
            schedule_data = yaml.safe_load(f)
        tz_name = schedule_data.get("timezone", "UTC")
        monday = week_monday(args.week)
        sunday = monday + timedelta(days=6)
        entries = build_weekly_entries(schedule_data, monday)
        print(
            f"Week {monday} → {sunday} | Timezone: {tz_name} | "
            f"{len(entries)} entries{' (dry run)' if args.dry_run else ''}"
        )
        if not entries:
            print("No entries to log for this week.")
            return
        run_entries(args.api_key, workspace_id, entries, tz_name=tz_name, dry_run=args.dry_run)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
