#!/usr/bin/env python3
"""
Log time entries to Clockify via API.

Usage:
  Single entry:
    python log_hours.py --date 2024-01-15 --start 09:00 --end 17:00 \
                        --description "Development" --project "My Project"

  Batch from file:
    python log_hours.py --file entries.yml
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta

import requests
import yaml

CLOCKIFY_API_BASE = "https://api.clockify.me/api/v1"


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


def parse_datetime(date_str: str, time_str: str) -> str:
    """Return ISO 8601 UTC string for a local date+time."""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    # Treat as UTC; adjust here if you need local timezone conversion
    dt_utc = dt.replace(tzinfo=timezone.utc)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


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
    payload = {
        "start": start,
        "end": end,
        "description": description,
        "billable": billable,
    }
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


def process_entry(api_key: str, workspace_id: str, entry: dict) -> None:
    date = entry["date"]
    start_iso = parse_datetime(date, entry["start"])
    end_iso = parse_datetime(date, entry["end"])

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
    duration_h = (
        datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
        - datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    ).seconds / 3600
    print(
        f"  [OK] {date} {entry['start']}-{entry['end']} ({duration_h:.1f}h) "
        f"| {entry.get('description', '')} | id={result['id']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Log hours to Clockify")
    parser.add_argument("--api-key", default=os.environ.get("CLOCKIFY_API_KEY"))
    parser.add_argument("--workspace-id", default=os.environ.get("CLOCKIFY_WORKSPACE_ID"))

    sub = parser.add_subparsers(dest="mode")

    # Single-entry mode
    single = sub.add_parser("single", help="Log a single time entry")
    single.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
    single.add_argument("--start", required=True, help="Start time (HH:MM)")
    single.add_argument("--end", required=True, help="End time (HH:MM)")
    single.add_argument("--description", required=True)
    single.add_argument("--project", help="Project name")
    single.add_argument("--project-id", help="Project ID (alternative to --project)")
    single.add_argument("--billable", action="store_true")

    # Batch mode
    batch = sub.add_parser("batch", help="Log multiple entries from a YAML file")
    batch.add_argument("--file", required=True, help="YAML entries file")

    args = parser.parse_args()

    if not args.api_key:
        sys.exit("Error: CLOCKIFY_API_KEY not set (use --api-key or env var).")

    workspace_id = get_workspace_id(args.api_key, args.workspace_id)
    print(f"Workspace ID: {workspace_id}")

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
        process_entry(args.api_key, workspace_id, entry)

    elif args.mode == "batch":
        with open(args.file) as f:
            data = yaml.safe_load(f)
        entries = data.get("entries", [])
        print(f"Processing {len(entries)} entries...")
        errors = 0
        for i, entry in enumerate(entries, 1):
            try:
                process_entry(args.api_key, workspace_id, entry)
            except Exception as exc:
                print(f"  [FAIL] Entry {i}: {exc}")
                errors += 1
        if errors:
            sys.exit(f"{errors}/{len(entries)} entries failed.")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
