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


# ── Cached lookups ─────────────────────────────────────────────────────────────
# Avoid repeated API calls for the same project/client/tag within a batch.

_client_cache: dict[str, str] = {}   # name → id
_project_cache: dict[str, str] = {}  # "name|client_id" → id
_tag_cache: dict[str, str] = {}      # name → id


def find_client_id(api_key: str, workspace_id: str, client_name: str) -> str:
    key = client_name.lower()
    if key in _client_cache:
        return _client_cache[key]
    resp = requests.get(
        f"{CLOCKIFY_API_BASE}/workspaces/{workspace_id}/clients",
        headers=get_headers(api_key),
        params={"name": client_name},
    )
    resp.raise_for_status()
    for c in resp.json():
        if c["name"].lower() == key:
            _client_cache[key] = c["id"]
            return c["id"]
    sys.exit(f"Client '{client_name}' not found in Clockify.")


def find_project_id(
    api_key: str,
    workspace_id: str,
    project_name: str,
    client_name: str | None = None,
) -> str:
    client_id = find_client_id(api_key, workspace_id, client_name) if client_name else None
    cache_key = f"{project_name.lower()}|{client_id or ''}"
    if cache_key in _project_cache:
        return _project_cache[cache_key]

    params: dict = {"name": project_name, "archived": False}
    if client_id:
        params["clients"] = client_id

    resp = requests.get(
        f"{CLOCKIFY_API_BASE}/workspaces/{workspace_id}/projects",
        headers=get_headers(api_key),
        params=params,
    )
    resp.raise_for_status()
    for p in resp.json():
        if p["name"].lower() == project_name.lower():
            _project_cache[cache_key] = p["id"]
            return p["id"]

    suffix = f" (client: {client_name})" if client_name else ""
    sys.exit(f"Project '{project_name}'{suffix} not found in Clockify.")


def find_tag_ids(api_key: str, workspace_id: str, tag_names: list[str]) -> list[str]:
    ids = []
    for name in tag_names:
        key = name.lower()
        if key not in _tag_cache:
            resp = requests.get(
                f"{CLOCKIFY_API_BASE}/workspaces/{workspace_id}/tags",
                headers=get_headers(api_key),
                params={"name": name},
            )
            resp.raise_for_status()
            matched = [t for t in resp.json() if t["name"].lower() == key]
            if not matched:
                sys.exit(f"Tag '{name}' not found in Clockify.")
            _tag_cache[key] = matched[0]["id"]
        ids.append(_tag_cache[key])
    return ids


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

    project_label = entry.get("project", "—")
    if client := entry.get("client"):
        project_label = f"{project_label} [{client}]"

    tag_label = ""
    if tags := entry.get("tags"):
        tag_label = f" | tags={','.join(tags)}"

    label = (
        f"  {'[DRY]' if dry_run else '[OK] '} "
        f"{date_str} {entry['start']}-{entry['end']} ({duration:.1f}h) "
        f"| {entry.get('description', '')} | project={project_label}{tag_label}"
    )

    if dry_run:
        print(label)
        return

    project_id = None
    if project_name := entry.get("project"):
        project_id = find_project_id(
            api_key, workspace_id, project_name, client_name=entry.get("client")
        )
    elif pid := entry.get("project_id"):
        project_id = pid

    # Resolve tag names to IDs (merge with any explicit tag_ids)
    resolved_tag_ids: list[str] = list(entry.get("tag_ids") or [])
    if tag_names := entry.get("tags"):
        resolved_tag_ids += find_tag_ids(api_key, workspace_id, tag_names)

    result = create_entry(
        api_key=api_key,
        workspace_id=workspace_id,
        description=entry.get("description", ""),
        start=start_iso,
        end=end_iso,
        project_id=project_id,
        billable=entry.get("billable", False),
        tag_ids=resolved_tag_ids or None,
    )
    print(f"{label} | id={result['id']}")


def _entry_date_obj(entry: dict) -> date:
    return (
        datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if isinstance(entry["date"], str)
        else entry["date"]
    )


def validate_no_overlaps(entries: list[dict], tz_name: str) -> None:
    """Abort if any two entries in this batch overlap on the same day."""
    by_date: dict[str, list[dict]] = {}
    for e in entries:
        key = _entry_date_obj(e).isoformat()
        by_date.setdefault(key, []).append(e)

    errors = []
    for day, day_entries in sorted(by_date.items()):
        sorted_entries = sorted(day_entries, key=lambda e: e["start"])
        for i in range(len(sorted_entries) - 1):
            a, b = sorted_entries[i], sorted_entries[i + 1]
            if a["end"] > b["start"]:
                errors.append(
                    f"  {day}: '{a.get('description', '?')}' {a['start']}-{a['end']} "
                    f"overlaps '{b.get('description', '?')}' {b['start']}-{b['end']}"
                )

    if errors:
        sys.exit("Overlap detected — no entries were created:\n" + "\n".join(errors))


def get_current_user_id(api_key: str) -> str:
    resp = requests.get(f"{CLOCKIFY_API_BASE}/user", headers=get_headers(api_key))
    resp.raise_for_status()
    return resp.json()["id"]


def get_existing_entries(
    api_key: str, workspace_id: str, user_id: str, start_utc: str, end_utc: str
) -> list[dict]:
    """Fetch all existing time entries in the given UTC range (handles pagination)."""
    entries, page = [], 1
    while True:
        resp = requests.get(
            f"{CLOCKIFY_API_BASE}/workspaces/{workspace_id}/user/{user_id}/time-entries",
            headers=get_headers(api_key),
            params={"start": start_utc, "end": end_utc, "page": page, "page-size": 50},
        )
        resp.raise_for_status()
        batch = resp.json()
        entries.extend(batch)
        if len(batch) < 50:
            break
        page += 1
    return entries


def validate_against_clockify(
    api_key: str, workspace_id: str, entries: list[dict], tz_name: str
) -> None:
    """Abort if any new entry overlaps with an already-existing Clockify entry."""
    if not entries:
        return

    # Build UTC intervals for all new entries
    new_intervals = [
        (to_utc(_entry_date_obj(e), e["start"], tz_name),
         to_utc(_entry_date_obj(e), e["end"], tz_name),
         e)
        for e in entries
    ]

    range_start = min(s for s, _, _ in new_intervals)
    range_end   = max(en for _, en, _ in new_intervals)

    print(f"Checking existing Clockify entries from {range_start} to {range_end}...")
    user_id = get_current_user_id(api_key)
    existing = get_existing_entries(api_key, workspace_id, user_id, range_start, range_end)

    errors = []
    for new_start, new_end, entry in new_intervals:
        date_str = _entry_date_obj(entry).isoformat()
        for ex in existing:
            interval = ex.get("timeInterval", {})
            ex_start = interval.get("start", "")
            ex_end   = interval.get("end", "")
            if not ex_end:
                continue  # skip running timers
            if new_start < ex_end and new_end > ex_start:
                # Convert existing times to local HH:MM for readability
                ex_s = ex_start[11:16]
                ex_e = ex_end[11:16]
                errors.append(
                    f"  {date_str}: '{entry.get('description', '?')}' "
                    f"{entry['start']}-{entry['end']} overlaps existing "
                    f"'{ex.get('description', '?')}' {ex_s}-{ex_e} (UTC)"
                )

    if errors:
        sys.exit(
            "Overlap with existing Clockify entries — no entries were created:\n"
            + "\n".join(errors)
        )


def run_entries(
    api_key: str,
    workspace_id: str,
    entries: list[dict],
    tz_name: str = "UTC",
    dry_run: bool = False,
) -> None:
    validate_no_overlaps(entries, tz_name)
    validate_against_clockify(api_key, workspace_id, entries, tz_name)
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

        if not day_entries:
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
    single.add_argument("--client", help="Client name to disambiguate project")
    single.add_argument("--project-id")
    single.add_argument("--tags", nargs="+", help="Tag names")
    single.add_argument("--billable", action="store_true")
    single.add_argument("--timezone", default="UTC")

    # batch
    batch = sub.add_parser("batch", help="Log entries from a YAML file")
    batch.add_argument("--file", required=True)
    batch.add_argument("--dry-run", action="store_true")

    # weekly
    weekly = sub.add_parser("weekly", help="Log a full week from a schedule file")
    weekly.add_argument("--schedule", required=True)
    weekly.add_argument("--week", help="Monday of target week (YYYY-MM-DD). Defaults to current week.")
    weekly.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if not args.api_key:
        sys.exit("Error: CLOCKIFY_API_KEY not set.")

    workspace_id = get_workspace_id(args.api_key, args.workspace_id)
    print(f"Workspace: {workspace_id}")

    if args.mode == "single":
        missing = [f for f, v in [("--date", args.date), ("--start", args.start), ("--end", args.end), ("--description", args.description)] if not v]
        if missing:
            sys.exit(f"Error: missing required fields for single mode: {', '.join(missing)}")
        entry = {
            "date": args.date,
            "start": args.start,
            "end": args.end,
            "description": args.description,
            "billable": args.billable,
        }
        if args.project:
            entry["project"] = args.project
        if args.client:
            entry["client"] = args.client
        if args.project_id:
            entry["project_id"] = args.project_id
        if args.tags:
            entry["tags"] = args.tags
        validate_against_clockify(args.api_key, workspace_id, [entry], tz_name=args.timezone)
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
