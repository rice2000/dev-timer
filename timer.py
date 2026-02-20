#!/usr/bin/env python3
"""
timer.py — A command-line project timer for benchmarking software milestones.

Usage:
  python timer.py start "milestone name" --project "project name"
  python timer.py stop --note "optional note"
  python timer.py status
  python timer.py summary
  python timer.py summary --project "project name"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from tabulate import tabulate

# ─── Storage ──────────────────────────────────────────────────────────────────

DATA_FILE = "timer_data.json"

def load_data():
    """Load timer data from the JSON file. Returns a fresh structure if none exists."""
    if not os.path.exists(DATA_FILE):
        return {"active": None, "sessions": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Write timer data back to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─── Time Helpers ─────────────────────────────────────────────────────────────

def now_iso():
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()

def format_duration(seconds):
    """Convert a number of seconds into a human-readable string like '1h 23m 45s'."""
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}h {m:02d}m {s:02d}s"

def elapsed_seconds(start_iso):
    """Return seconds elapsed since a given ISO timestamp."""
    start = datetime.fromisoformat(start_iso)
    now = datetime.now(timezone.utc)
    return (now - start).total_seconds()


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_start(args):
    """
    Start a new timer for a milestone.
    Refuses to start if a timer is already running.
    """
    data = load_data()

    # Block starting a second timer while one is active
    if data["active"]:
        active = data["active"]
        elapsed = format_duration(elapsed_seconds(active["start_time"]))
        print(f"A timer is already running!")
        print(f"  Project  : {active['project']}")
        print(f"  Milestone: {active['milestone']}")
        print(f"  Elapsed  : {elapsed}")
        print(f"\nRun `python timer.py stop` to stop it first.")
        sys.exit(1)

    # Record the new active session
    data["active"] = {
        "project": args.project,
        "milestone": args.milestone,
        "start_time": now_iso(),
    }
    save_data(data)

    print(f"Timer started.")
    print(f"  Project  : {args.project}")
    print(f"  Milestone: {args.milestone}")


def cmd_stop(args):
    """
    Stop the running timer and save the completed session.
    Optionally attaches a note about how the milestone went.
    """
    data = load_data()

    # Nothing to stop
    if not data["active"]:
        print("No timer is currently running.")
        sys.exit(1)

    active = data["active"]
    end_time = now_iso()
    duration = elapsed_seconds(active["start_time"])

    # Build the completed session record
    session = {
        "project": active["project"],
        "milestone": active["milestone"],
        "start_time": active["start_time"],
        "end_time": end_time,
        "duration_seconds": duration,
        "note": args.note or "",
    }

    # Append to the sessions list and clear the active timer
    data["sessions"].append(session)
    data["active"] = None
    save_data(data)

    print(f"Timer stopped.")
    print(f"  Project  : {session['project']}")
    print(f"  Milestone: {session['milestone']}")
    print(f"  Duration : {format_duration(duration)}")
    if session["note"]:
        print(f"  Note     : {session['note']}")


def cmd_status(args):
    """Show whether a timer is running and for how long."""
    data = load_data()

    if not data["active"]:
        print("No timer is currently running.")
        return

    active = data["active"]
    elapsed = elapsed_seconds(active["start_time"])

    print(f"Timer running.")
    print(f"  Project  : {active['project']}")
    print(f"  Milestone: {active['milestone']}")
    print(f"  Elapsed  : {format_duration(elapsed)}")


def cmd_summary(args):
    """
    Print a table of all completed sessions, grouped by project.
    If --project is given, show only that project's sessions.
    """
    data = load_data()
    sessions = data["sessions"]

    # Filter by project name if requested
    if args.project:
        sessions = [s for s in sessions if s["project"].lower() == args.project.lower()]
        if not sessions:
            print(f"No sessions found for project: {args.project}")
            return

    if not sessions:
        print("No completed sessions yet.")
        return

    # Group sessions by project name
    projects = {}
    for s in sessions:
        projects.setdefault(s["project"], []).append(s)

    # Print one table per project
    for project_name, project_sessions in projects.items():
        print(f"\nProject: {project_name}")

        rows = []
        total_seconds = 0

        for s in project_sessions:
            # Parse the ISO date into a readable local date string
            date_str = datetime.fromisoformat(s["end_time"]).strftime("%Y-%m-%d")
            rows.append([
                s["milestone"],
                format_duration(s["duration_seconds"]),
                date_str,
                s["note"] or "—",
            ])
            total_seconds += s["duration_seconds"]

        # Add a total row at the bottom
        rows.append(["Total", format_duration(total_seconds), "", ""])

        print(tabulate(
            rows,
            headers=["Milestone", "Duration", "Date", "Notes"],
            tablefmt="simple",
            colalign=("left", "left", "left", "left"),
        ))


# ─── Argument Parser ──────────────────────────────────────────────────────────

def build_parser():
    """Define the CLI commands and their arguments."""
    parser = argparse.ArgumentParser(
        prog="timer",
        description="Benchmark your dev projects milestone by milestone.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # timer start "milestone" --project "project"
    p_start = subparsers.add_parser("start", help="Start a new timer")
    p_start.add_argument("milestone", help="Name of the milestone")
    p_start.add_argument("--project", required=True, help="Name of the project")

    # timer stop --note "..."
    p_stop = subparsers.add_parser("stop", help="Stop the running timer")
    p_stop.add_argument("--note", default="", help="Optional note about the session")

    # timer status
    subparsers.add_parser("status", help="Show the current timer status")

    # timer summary [--project "..."]
    p_summary = subparsers.add_parser("summary", help="Show all completed sessions")
    p_summary.add_argument("--project", default="", help="Filter by project name")

    return parser


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "summary":
        cmd_summary(args)


if __name__ == "__main__":
    main()
