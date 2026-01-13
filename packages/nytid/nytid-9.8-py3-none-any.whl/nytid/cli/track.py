import datetime
import json
import logging
import os
import pathlib
import sys
import subprocess
import typer
import typerconf as config
from typing_extensions import Annotated
from typing import List, Optional, Dict
import time

from nytid import storage

# Configuration keys for track system
TRACKING_DIR_CONFIG = "track.data_dir"
DEFAULT_WEEKLY_LIMIT_CONFIG = "track.weekly_limit"
DEFAULT_DAILY_LIMIT_CONFIG = "track.daily_limit"


def get_tracking_storage() -> storage.StorageRoot:
    """
    Get the StorageRoot for tracking data.

    Uses nytid's StorageRoot system for consistent file management.
    Returns a StorageRoot object that can be used to open tracking data files.
    """
    try:
        tracking_dir = pathlib.Path(config.get(TRACKING_DIR_CONFIG))
    except KeyError:
        # Fallback to default location in user's home directory
        tracking_dir = pathlib.Path.home() / ".nytid" / "tracking"
        # Set the default in config for future use
        config.set(TRACKING_DIR_CONFIG, str(tracking_dir))

    return storage.StorageRoot(tracking_dir)


def get_tracking_dir() -> pathlib.Path:
    """Get the tracking data directory path (for compatibility)"""
    return get_tracking_storage()._StorageRoot__path


def get_tracking_data_file() -> pathlib.Path:
    """Get the path to the tracking data file"""
    return get_tracking_dir() / "tracking_data.json"


def get_current_session_file() -> pathlib.Path:
    """Get the path to the current session file"""
    return get_tracking_dir() / "current_session.json"


def get_default_weekly_limit() -> float:
    """Get the default weekly hour limit from config"""
    try:
        return float(config.get(DEFAULT_WEEKLY_LIMIT_CONFIG))
    except (KeyError, ValueError):
        return DEFAULT_WEEKLY_LIMIT_HOURS


def get_default_daily_limit() -> float:
    """Get the default daily hour limit from config"""
    try:
        return float(config.get(DEFAULT_DAILY_LIMIT_CONFIG))
    except (KeyError, ValueError):
        return DEFAULT_DAILY_LIMIT_HOURS


# Label display separators
LABEL_SEPARATOR = " > "

# Default time limits for work-life balance warnings
DEFAULT_WEEKLY_LIMIT_HOURS = 40.0  # Standard full-time work week
DEFAULT_DAILY_LIMIT_HOURS = 8.0  # Standard work day

cli = typer.Typer(name="track", help="Track time spent on course activities")


def format_duration(duration: datetime.timedelta) -> str:
    """Format a duration in a human-readable way"""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def get_labels_display(labels: List[str]) -> str:
    """Get a display string for labels (as comma-separated tags)"""
    return ", ".join(sorted(labels)) if labels else "No labels"


def complete_active_labels(ctx, args, incomplete):
    """
    Shell completion function for active labels (used by stop command).

    Returns currently tracking labels that match the incomplete string.
    """
    try:
        session = load_active_session()
        active = session.get_active_labels()
        return [label for label in active if label.startswith(incomplete)]
    except:
        return []


def complete_historical_labels(ctx, args, incomplete):
    """
    Shell completion function for historical labels (used by start command).

    Returns previously used labels from tracking history that match the incomplete string.
    """
    try:
        entries = load_completed_entries()
        # Collect all unique labels from historical entries
        all_labels = set()
        for entry in entries:
            all_labels.update(entry.labels)

        # Also include currently active labels
        session = load_active_session()
        all_labels.update(session.get_active_labels())

        return sorted([label for label in all_labels if label.startswith(incomplete)])
    except:
        return []


def parse_offset(offset_str: str) -> datetime.timedelta:
    """
    Parse an offset string into a timedelta.

    Supports formats:
    - Plain number: "30" (minutes)
    - With 'm' suffix: "30m" (minutes)
    - With 'h' suffix: "1.5h" (hours)
    - Negative values: "-30m", "-1.5h"

    Examples:
        parse_offset("30") -> 30 minutes
        parse_offset("-30m") -> -30 minutes
        parse_offset("1.5h") -> 1.5 hours = 90 minutes
        parse_offset("-2h") -> -2 hours = -120 minutes
    """
    offset_str = offset_str.strip()

    # Check for hour suffix
    if offset_str.endswith("h"):
        hours = float(offset_str[:-1])
        return datetime.timedelta(hours=hours)

    # Check for minute suffix
    if offset_str.endswith("m"):
        minutes = float(offset_str[:-1])
        return datetime.timedelta(minutes=minutes)

    # No suffix, assume minutes
    minutes = float(offset_str)
    return datetime.timedelta(minutes=minutes)


def parse_at_time(
    at_str: str, reference_time: datetime.datetime = None
) -> datetime.datetime:
    """
    Parse an absolute time string into a datetime.

    Supports formats:
    - "HH:MM" - time today in 24-hour format
    - "YYYY-MM-DD HH:MM" - specific date and time

    Examples:
        parse_at_time("14:30") -> today at 14:30
        parse_at_time("2024-12-13 14:30") -> Dec 13, 2024 at 14:30

    Args:
        at_str: The time string to parse
        reference_time: The reference time for relative parsing (default: now)

    Returns:
        datetime object representing the specified time
    """
    if reference_time is None:
        reference_time = datetime.datetime.now()

    at_str = at_str.strip()

    # Try parsing "YYYY-MM-DD HH:MM" format
    try:
        return datetime.datetime.strptime(at_str, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    # Try parsing "HH:MM" format (time today)
    try:
        time_obj = datetime.datetime.strptime(at_str, "%H:%M").time()
        return datetime.datetime.combine(reference_time.date(), time_obj)
    except ValueError:
        pass

    raise ValueError(
        f"Invalid time format: '{at_str}'. "
        f"Use 'HH:MM' (24-hour) or 'YYYY-MM-DD HH:MM'"
    )


class TrackingEntry:
    """
    Represents a completed time tracking entry.

    This class encapsulates all information about a single tracked work session,
    including the time span, flat labels (tags), and optional description.
    Once created, instances are immutable records of completed work.
    """

    def __init__(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        labels: List[str],
        description: str = "",
    ):
        """
        Initialize a tracking entry.

        Args:
            start_time: When the tracked work began
            end_time: When the tracked work ended
            labels: List of independent labels/tags (e.g., ['DD1310', 'lecture', 'prep'])
            description: Optional description of the work performed
        """
        self.start_time = start_time
        self.end_time = end_time
        self.labels = sorted(list(set(labels)))  # Ensure unique and sorted
        self.description = description

    def duration(self) -> datetime.timedelta:
        """
        Calculate the duration of this tracking entry.

        Returns:
            The time difference between end_time and start_time
        """
        return self.end_time - self.start_time

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with all entry data in JSON-serializable format
        """
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "labels": self.labels,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrackingEntry":
        """
        Create from dictionary (JSON deserialization).

        Args:
            data: Dictionary containing serialized entry data

        Returns:
            New TrackingEntry instance
        """
        return cls(
            start_time=datetime.datetime.fromisoformat(data["start_time"]),
            end_time=datetime.datetime.fromisoformat(data["end_time"]),
            labels=data["labels"],
            description=data.get("description", ""),
        )


class ActiveSession:
    """
    Manages the current tracking state with independent flat labels.

    This class maintains a dictionary of currently active tracking labels,
    where each label tracks independently with its own start time and notes.
    Labels can be started, stopped, and annotated independently.

    The session tracks the order in which labels were started to support
    LIFO (Last In, First Out) stopping behavior. Labels started together
    in one command form a "batch" that can be stopped together.
    """

    def __init__(self):
        """Initialize an empty active session."""
        # Dictionary mapping label -> (start_time, notes, batch_id)
        self.active_labels: Dict[str, tuple] = {}
        # Ordered list of labels by start time (most recent last)
        self.label_order: List[str] = []
        # Track which labels were started together (batch_id -> list of labels)
        self.batches: Dict[int, List[str]] = {}
        # Next batch ID to use
        self.next_batch_id: int = 1
        # Remember last stopped labels for resume functionality
        self.last_stopped: List[str] = []

    def start_labels(
        self, labels: List[str], start_time: datetime.datetime
    ) -> List[str]:
        """
        Start tracking for the given labels.

        If a label is already being tracked, it's ignored (continues existing tracking).
        This prevents duplicate tracking of the same label.

        Labels started together in one call form a "batch" and can be stopped together.

        Args:
            labels: List of labels to start tracking
            start_time: When tracking of these labels began

        Returns:
            List of labels that were actually started (excludes already-active labels)
        """
        started = []
        batch_id = self.next_batch_id
        self.next_batch_id += 1

        for label in labels:
            if label not in self.active_labels:
                self.active_labels[label] = (start_time, "", batch_id)
                self.label_order.append(label)
                started.append(label)

        # Track this batch
        if started:
            self.batches[batch_id] = started

        return started

    def stop_labels(
        self,
        labels: List[str] = None,
        end_time: datetime.datetime = None,
        count: int = None,
        stop_batch: bool = True,
    ) -> List[TrackingEntry]:
        """
        Stop tracking for specified labels and return completed entries.

        Args:
            labels: List of labels to stop. If None and count is None, stops most recent batch.
            end_time: When tracking ended. If None, uses current time.
            count: Number of most recently started labels to stop. If None, uses batch logic.
            stop_batch: If True (default), stopping without arguments stops the most recent batch.

        Returns:
            List of TrackingEntry objects for the stopped labels
        """
        if end_time is None:
            end_time = datetime.datetime.now()

        # Determine which labels to stop
        if labels is None and count is None:
            if stop_batch and self.label_order:
                # Stop the most recent batch (labels started together)
                # Find the most recently started label and get its batch
                most_recent = self.label_order[-1]
                start_time, notes, batch_id = self.active_labels[most_recent]

                # Get all labels from this batch that are still active
                if batch_id in self.batches:
                    labels = [
                        l for l in self.batches[batch_id] if l in self.active_labels
                    ]
                else:
                    # Fallback if batch info is missing
                    labels = [most_recent]
            else:
                # Stop most recently started label only
                if not self.label_order:
                    return []
                labels = [self.label_order[-1]]
        elif count is not None:
            # Stop the N most recently started labels
            labels = self.label_order[-count:] if self.label_order else []
        # else: use the provided labels list

        # Remember stopped labels for resume functionality
        self.last_stopped = labels.copy() if labels else []

        entries = []
        for label in labels:
            if label in self.active_labels:
                start_time, notes, batch_id = self.active_labels.pop(label)
                self.label_order.remove(label)
                # Create entry with just this label
                entry = TrackingEntry(start_time, end_time, [label], notes)
                entries.append(entry)

        return entries

    def add_notes(self, label: str, notes: str) -> bool:
        """
        Add or update notes for an active label.

        Args:
            label: The label to annotate
            notes: The notes/description to add

        Returns:
            True if notes were added, False if label is not active
        """
        if label in self.active_labels:
            start_time, _, batch_id = self.active_labels[label]
            self.active_labels[label] = (start_time, notes, batch_id)
            return True
        return False

    def get_active_labels(self) -> List[str]:
        """
        Get list of currently active labels.

        Returns:
            Sorted list of active label names
        """
        return sorted(self.active_labels.keys())

    def get_label_info(self, label: str) -> Optional[tuple]:
        """
        Get information about a specific active label.

        Args:
            label: The label to query

        Returns:
            Tuple of (start_time, notes, batch_id) if label is active, None otherwise
        """
        return self.active_labels.get(label)

    def is_active(self) -> bool:
        """
        Check if there are any active tracking labels.

        Returns:
            True if any labels are being tracked, False otherwise
        """
        return len(self.active_labels) > 0

    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary with session state in JSON-serializable format
        """
        return {
            "active_labels": {
                label: (start_time.isoformat(), notes, batch_id)
                for label, (start_time, notes, batch_id) in self.active_labels.items()
            },
            "label_order": self.label_order,
            "batches": self.batches,
            "next_batch_id": self.next_batch_id,
            "last_stopped": self.last_stopped,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActiveSession":
        """
        Create from dictionary (JSON deserialization).

        Args:
            data: Dictionary containing serialized session data

        Returns:
            New ActiveSession instance with restored state
        """
        session = cls()
        active_labels_data = data.get("active_labels", {})

        # Handle both old format (label_stack) and new format (active_labels)
        if "label_stack" in data and not active_labels_data:
            # Convert old hierarchical format to flat labels
            batch_id = session.next_batch_id
            for label, start_time_str in data["label_stack"]:
                start_time = datetime.datetime.fromisoformat(start_time_str)
                session.active_labels[label] = (start_time, "", batch_id)
                session.label_order.append(label)
            session.next_batch_id += 1
        else:
            # Use new flat format
            for label, label_data in active_labels_data.items():
                start_time_str = label_data[0]
                notes = label_data[1] if len(label_data) > 1 else ""
                batch_id = label_data[2] if len(label_data) > 2 else 0

                start_time = datetime.datetime.fromisoformat(start_time_str)
                session.active_labels[label] = (start_time, notes, batch_id)

            # Restore label order if available, otherwise sort by start time
            if "label_order" in data:
                session.label_order = data["label_order"]
            else:
                # Build order from start times for backward compatibility
                session.label_order = sorted(
                    session.active_labels.keys(),
                    key=lambda l: session.active_labels[l][0],
                )

            # Restore batch information
            if "batches" in data:
                session.batches = {int(k): v for k, v in data["batches"].items()}
            if "next_batch_id" in data:
                session.next_batch_id = data["next_batch_id"]
            if "last_stopped" in data:
                session.last_stopped = data["last_stopped"]

        return session


def ensure_tracking_dir():
    """
    Ensure the tracking directory exists.

    Creates the tracking data directory if it doesn't exist, including
    any necessary parent directories. Uses the configured location.
    """
    get_tracking_dir().mkdir(parents=True, exist_ok=True)


def load_tracking_data() -> List[TrackingEntry]:
    """
    Load historical tracking data from the persistent storage file.

    Returns:
        List of TrackingEntry objects, or empty list if file doesn't exist
        or contains invalid data
    """
    tracking_file = get_tracking_data_file()
    if not tracking_file.exists():
        return []

    try:
        with open(tracking_file, "r") as f:
            data = json.load(f)
            return [TrackingEntry.from_dict(entry) for entry in data]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logging.warning(f"Error loading tracking data from {tracking_file}: {e}")
        return []


def save_tracking_data(entries: List[TrackingEntry]):
    """
    Save tracking data to persistent storage.

    Args:
        entries: List of TrackingEntry objects to save
    """
    ensure_tracking_dir()
    tracking_file = get_tracking_data_file()
    with open(tracking_file, "w") as f:
        json.dump([entry.to_dict() for entry in entries], f, indent=2)


def add_completed_entries(new_entries: List[TrackingEntry]):
    """
    Add newly completed entries to the historical tracking data.

    This function implements an append-only approach to maintain data integrity.
    It loads existing data, appends new entries, and saves the combined dataset.

    Args:
        new_entries: List of TrackingEntry objects to add to historical data
    """
    if not new_entries:
        return

    existing_entries = load_tracking_data()
    existing_entries.extend(new_entries)
    save_tracking_data(existing_entries)


def load_active_session() -> ActiveSession:
    """
    Load the current active session from persistent storage.

    Returns:
        ActiveSession object with restored state, or empty session if
        file doesn't exist or contains invalid data
    """
    session_file = get_current_session_file()
    if not session_file.exists():
        return ActiveSession()

    try:
        with open(session_file, "r") as f:
            data = json.load(f)
            return ActiveSession.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logging.warning(f"Error loading active session from {session_file}: {e}")
        return ActiveSession()


def save_active_session(session: ActiveSession):
    """
    Save the current active session to persistent storage.

    Args:
        session: ActiveSession object to save
    """
    ensure_tracking_dir()
    session_file = get_current_session_file()
    with open(session_file, "w") as f:
        json.dump(session.to_dict(), f, indent=2)


@cli.command()
def status():
    """
    Show current tracking status.
    """
    session = load_active_session()

    if not session.is_active():
        typer.echo("No active tracking")
        return

    typer.echo("Currently tracking:")
    current_time = datetime.datetime.now()

    # Show each active label with its duration and notes
    for label in session.get_active_labels():
        info = session.get_label_info(label)
        if info:
            start_time, notes, batch_id = info
            duration = current_time - start_time
            notes_display = f" - {notes}" if notes else ""
            typer.echo(f"  {label}: {format_duration(duration)}{notes_display}")


@cli.command()
def start(
    labels: List[str] = typer.Argument(
        None,
        help="Labels to track. If empty, resumes last stopped labels.",
        autocompletion=complete_historical_labels,
    ),
    offset: Optional[str] = typer.Option(
        None,
        "--offset",
        "-o",
        help="Offset start time (e.g., '-30m', '-1.5h', '30' for minutes)",
    ),
    at: Optional[str] = typer.Option(
        None,
        "--at",
        help="Start at specific time (e.g., '14:30' or '2024-12-13 14:30')",
    ),
):
    """
    Start tracking time with the given labels.

    If no labels are provided, resumes tracking the most recently stopped labels.

    Examples:
      nytid track start DD1310 lecture preparation
      nytid track start DD1310 --offset -30m        # Started 30 minutes ago
      nytid track start meeting --at 14:30          # Started at 2:30 PM today
      nytid track start                             # Resume last stopped labels
    """
    session = load_active_session()

    # If no labels provided, try to resume last stopped labels
    if not labels:
        if session.last_stopped:
            labels = session.last_stopped
            typer.echo(f"Resuming: {', '.join(sorted(labels))}")
        else:
            typer.echo(
                "Error: No labels specified and no previous labels to resume", err=True
            )
            typer.echo("Usage: nytid track start <label1> [label2] ...", err=True)
            raise typer.Exit(1)
    # Check for conflicting options
    if offset is not None and at is not None:
        typer.echo("Error: Cannot use both --offset and --at options", err=True)
        raise typer.Exit(1)

    # Calculate start time
    start_time = datetime.datetime.now()

    if at is not None:
        try:
            start_time = parse_at_time(at)
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
    elif offset is not None:
        try:
            offset_delta = parse_offset(offset)
            start_time += offset_delta
        except ValueError as e:
            typer.echo(f"Error parsing offset '{offset}': {e}", err=True)
            raise typer.Exit(1)
    started = session.start_labels(labels, start_time)
    already_tracking = [l for l in labels if l not in started]

    save_active_session(session)

    if started:
        typer.echo(f"Started tracking: {', '.join(sorted(started))}")
    if already_tracking:
        typer.echo(f"Already tracking: {', '.join(sorted(already_tracking))}")

    all_active = session.get_active_labels()
    typer.echo(f"Active labels: {', '.join(all_active)}")
    if at is not None or offset is not None:
        typer.echo(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")


@cli.command()
def stop(
    labels: Optional[List[str]] = typer.Argument(
        None, help="Specific labels to stop", autocompletion=complete_active_labels
    ),
    all_labels: bool = typer.Option(
        False, "--all", "-a", help="Stop all active labels"
    ),
    offset: Optional[str] = typer.Option(
        None,
        "--offset",
        "-o",
        help="Offset stop time (e.g., '-30m', '-1.5h', '30' for minutes)",
    ),
    at: Optional[str] = typer.Option(
        None, "--at", help="Stop at specific time (e.g., '14:30' or '2024-12-13 14:30')"
    ),
):
    """
    Stop tracking. By default, stops the most recently started batch of labels.

    When labels are started together in one command, they form a "batch" and
    are stopped together. For example:
      nytid track start DD1310          # Start DD1310 (batch 1)
      nytid track start lecture prep    # Start lecture and prep (batch 2)
      nytid track stop                  # Stops batch 2 (lecture and prep)
      nytid track stop                  # Stops batch 1 (DD1310)

    Use --all to stop all active tracking, or specify labels to stop specific ones.

    Examples:
      nytid track stop                   # Stop most recent batch
      nytid track stop --all             # Stop all active labels
      nytid track stop DD1310            # Stop only DD1310 label
      nytid track stop DD1310 lecture    # Stop DD1310 and lecture labels
      nytid track stop --offset -30m     # Stopped 30 minutes ago
      nytid track stop --at 16:00        # Stopped at 4:00 PM
    """
    session = load_active_session()

    if not session.is_active():
        typer.echo("No active tracking session", err=True)
        raise typer.Exit(1)

    # Check for conflicting options
    if offset is not None and at is not None:
        typer.echo("Error: Cannot use both --offset and --at options", err=True)
        raise typer.Exit(1)

    # Calculate end time
    end_time = datetime.datetime.now()

    if at is not None:
        try:
            end_time = parse_at_time(at)
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
    elif offset is not None:
        try:
            offset_delta = parse_offset(offset)
            end_time += offset_delta
        except ValueError as e:
            typer.echo(f"Error parsing offset '{offset}': {e}", err=True)
            raise typer.Exit(1)

    # Determine what to stop
    if all_labels:
        # Stop all active labels
        completed_entries = session.stop_labels(
            count=len(session.label_order), end_time=end_time
        )
    elif labels:
        # Stop specified labels
        completed_entries = session.stop_labels(labels, end_time)
    else:
        # Default: stop most recently started batch
        completed_entries = session.stop_labels(end_time=end_time, stop_batch=True)

    if not completed_entries:
        if labels:
            typer.echo(
                f"None of the specified labels are currently tracking: {', '.join(labels)}",
                err=True,
            )
        else:
            typer.echo("No active tracking to stop", err=True)
        raise typer.Exit(1)

    # Save session
    save_active_session(session)

    # Save completed entries
    add_completed_entries(completed_entries)

    # Display what was completed
    for entry in completed_entries:
        typer.echo(
            f"Stopped: {get_labels_display(entry.labels)} ({format_duration(entry.duration())})"
        )

    # Show remaining active labels
    if session.is_active():
        remaining = session.get_active_labels()
        typer.echo(f"Still tracking: {', '.join(remaining)}")
    else:
        typer.echo("All tracking stopped")

    # Show time information if not current time
    if at is not None or offset is not None:
        typer.echo(f"Stop time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")


@cli.command()
def notes(
    label: str = typer.Argument(..., help="Label to add notes to"),
    note_text: str = typer.Argument(..., help="Notes/description to add"),
):
    """
    Add or update notes for an active tracking label.

    Example:
      nytid track notes DD1310 "Discussing course structure with TA"
    """
    session = load_active_session()

    if not session.is_active():
        typer.echo("No active tracking session", err=True)
        raise typer.Exit(1)

    if session.add_notes(label, note_text):
        save_active_session(session)
        typer.echo(f"Added notes to '{label}': {note_text}")
    else:
        typer.echo(f"Label '{label}' is not currently being tracked", err=True)
        active = session.get_active_labels()
        if active:
            typer.echo(f"Active labels: {', '.join(active)}")
        raise typer.Exit(1)


@cli.command()
def add(
    labels: List[str] = typer.Argument(..., help="Labels for the time entry"),
    duration_minutes: int = typer.Option(
        ..., "--duration", "-d", help="Duration in minutes"
    ),
    start_offset_minutes: int = typer.Option(
        0,
        "--start-offset",
        help="Start time offset in minutes from now (negative for past)",
    ),
    description: str = typer.Option(
        "", "--description", help="Description for this time entry"
    ),
):
    """
    Add a time entry for work done when not at the computer.
    Useful for recording time spent in meetings, at whiteboards, etc.
    """
    if not labels:
        typer.echo("Error: At least one label is required", err=True)
        raise typer.Exit(1)

    if duration_minutes <= 0:
        typer.echo("Error: Duration must be positive", err=True)
        raise typer.Exit(1)

    # Calculate times
    now = datetime.datetime.now()
    start_time = now + datetime.timedelta(minutes=start_offset_minutes)
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)

    # Create and save entry
    entry = TrackingEntry(start_time, end_time, labels, description)
    add_completed_entries([entry])

    typer.echo(
        f"Added entry: {get_labels_display(labels)} ({format_duration(entry.duration())})"
    )
    if description:
        typer.echo(f"Description: {description}")
    typer.echo(f"Time: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")


@cli.command()
def run(
    command_args: List[str] = typer.Argument(..., help="Command and arguments to run"),
    labels: List[str] = typer.Option(
        [], "--label", "-l", help="Additional labels for this tracking session"
    ),
):
    """
    Run a command and track the time spent.
    The command name is automatically used as a label, and the full command with arguments is stored as a description.
    Additional labels can be provided with --label/-l options.
    """
    if not command_args:
        typer.echo("Error: Command is required", err=True)
        raise typer.Exit(1)

    # Use the command name as the primary label
    command_name = command_args[0]
    full_command = " ".join(command_args)

    # Combine command name with any additional labels
    all_labels = [command_name] + labels

    start_time = datetime.datetime.now()

    # Load current session and start tracking labels
    session = load_active_session()
    started = session.start_labels(all_labels, start_time)

    # Add the full command as a note/description for the command label
    if command_name in session.active_labels:
        start_time, _, batch_id = session.active_labels[command_name]
        session.active_labels[command_name] = (start_time, full_command, batch_id)

    save_active_session(session)

    typer.echo(
        f"Running '{full_command}' and tracking with labels: {', '.join(sorted(all_labels))}"
    )

    try:
        # Run the command
        result = subprocess.run(command_args, capture_output=False)
        exit_code = result.returncode
    except KeyboardInterrupt:
        typer.echo("\nCommand interrupted", err=True)
        exit_code = 130
    except FileNotFoundError:
        typer.echo(f"Command not found: {command_name}", err=True)
        exit_code = 127

    # Stop tracking the labels we started and save completed entries
    end_time = datetime.datetime.now()
    completed_entries = session.stop_labels(started, end_time)

    # Save state
    save_active_session(session)
    add_completed_entries(completed_entries)

    duration = end_time - start_time
    typer.echo(f"Command completed in {format_duration(duration)}")

    raise typer.Exit(exit_code)


@cli.command()
def stats(
    labels: List[str] = typer.Argument(
        None, help="Filter statistics by specific labels (shows all if not specified)"
    ),
    days: int = typer.Option(7, "--days", help="Number of days to include in stats"),
    weekly_limit: Optional[float] = typer.Option(
        None,
        "--weekly-limit",
        help="Weekly hour limit for warnings (uses config default if not specified)",
    ),
    daily_limit: Optional[float] = typer.Option(
        None,
        "--daily-limit",
        help="Daily hour limit for warnings (uses config default if not specified)",
    ),
):
    """
    Show statistics about tracked time.

    Can filter by specific labels to see time spent on particular activities.
    For example: nytid track stats DD1310 lecture

    Uses configured default limits for warnings unless overridden by command options.
    Default limits can be set using:
      nytid config track.weekly_limit -s 40.0
      nytid config track.daily_limit -s 8.0
    """
    # Use config defaults if not specified
    if weekly_limit is None:
        weekly_limit = get_default_weekly_limit()
    if daily_limit is None:
        daily_limit = get_default_daily_limit()

    entries = load_tracking_data()

    if not entries:
        typer.echo("No tracking data available")
        return

    now = datetime.datetime.now()
    cutoff_date = now - datetime.timedelta(days=days)

    # Filter entries within the time range
    recent_entries = [e for e in entries if e.start_time >= cutoff_date]

    # Filter by labels if specified
    if labels:
        recent_entries = [
            e for e in recent_entries if any(label in e.labels for label in labels)
        ]
        label_filter_msg = f" for labels: {', '.join(labels)}"
    else:
        label_filter_msg = ""

    if not recent_entries:
        if labels:
            typer.echo(f"No tracking data in the last {days} days for specified labels")
        else:
            typer.echo(f"No tracking data in the last {days} days")
        return

    # Calculate totals
    total_time = sum((e.duration() for e in recent_entries), datetime.timedelta())
    total_hours = total_time.total_seconds() / 3600

    typer.echo(f"Statistics for the last {days} days{label_filter_msg}:")
    typer.echo(f"Total time: {format_duration(total_time)} ({total_hours:.1f} hours)")
    typer.echo(f"Average per day: {total_hours/days:.1f} hours")

    # Check against limits
    if total_hours > (weekly_limit * days / 7):
        typer.echo(
            f"⚠️  Warning: Exceeding weekly limit of {weekly_limit} hours per week",
            err=True,
        )

    # Daily breakdown
    typer.echo(f"\nDaily breakdown:")
    daily_totals = {}
    for entry in recent_entries:
        date = entry.start_time.date()
        if date not in daily_totals:
            daily_totals[date] = datetime.timedelta()
        daily_totals[date] += entry.duration()

    for date in sorted(daily_totals.keys(), reverse=True):
        duration = daily_totals[date]
        hours = duration.total_seconds() / 3600
        warning = " ⚠️" if hours > daily_limit else ""
        typer.echo(f"  {date}: {format_duration(duration)} ({hours:.1f}h){warning}")

    # Label breakdown
    if labels:
        # When filtering by labels, show co-occurring labels
        # (labels that appeared together with the filter labels)
        typer.echo(f"\nTime breakdown for co-occurring labels:")
        typer.echo(
            f"  (shows other labels that appeared alongside {', '.join(labels)})"
        )
        co_occurring_label_totals = {}
        for entry in recent_entries:
            for label in entry.labels:
                # Skip the filter labels themselves
                if label not in labels:
                    if label not in co_occurring_label_totals:
                        co_occurring_label_totals[label] = datetime.timedelta()
                    co_occurring_label_totals[label] += entry.duration()

        if co_occurring_label_totals:
            for label, duration in sorted(
                co_occurring_label_totals.items(), key=lambda x: x[1], reverse=True
            ):
                hours = duration.total_seconds() / 3600
                percentage = (
                    duration.total_seconds() / total_time.total_seconds()
                ) * 100
                typer.echo(
                    f"  {label}: {format_duration(duration)} ({hours:.1f}h, {percentage:.1f}%)"
                )
        else:
            typer.echo(f"  (no other labels co-occurred with {', '.join(labels)})")
    else:
        # When not filtering, show all label totals
        typer.echo(f"\nTime by labels:")
        label_totals = {}
        for entry in recent_entries:
            for label in entry.labels:
                if label not in label_totals:
                    label_totals[label] = datetime.timedelta()
                label_totals[label] += entry.duration()

        for label, duration in sorted(
            label_totals.items(), key=lambda x: x[1], reverse=True
        ):
            hours = duration.total_seconds() / 3600
            percentage = (duration.total_seconds() / total_time.total_seconds()) * 100
            typer.echo(
                f"  {label}: {format_duration(duration)} ({hours:.1f}h, {percentage:.1f}%)"
            )


@cli.command()
def export(
    format: str = typer.Option(
        "ics", "--format", "-f", help="Export format (ics, json, csv)"
    ),
    days: int = typer.Option(30, "--days", help="Number of days to export"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file (stdout if not specified)"
    ),
):
    """
    Export tracking data in various formats.
    Supports ICS (calendar), JSON, and CSV formats.
    """
    entries = load_tracking_data()

    if not entries:
        typer.echo("No tracking data to export", err=True)
        return

    # Filter by date range
    now = datetime.datetime.now()
    cutoff_date = now - datetime.timedelta(days=days)
    filtered_entries = [e for e in entries if e.start_time >= cutoff_date]

    if not filtered_entries:
        typer.echo(f"No tracking data in the last {days} days", err=True)
        return

    # Generate export data
    if format.lower() == "ics":
        export_data = export_to_ics(filtered_entries)
    elif format.lower() == "json":
        export_data = export_to_json(filtered_entries)
    elif format.lower() == "csv":
        export_data = export_to_csv(filtered_entries)
    else:
        typer.echo(f"Unsupported format: {format}", err=True)
        raise typer.Exit(1)

    # Output to file or stdout
    if output:
        with open(output, "w") as f:
            f.write(export_data)
        typer.echo(f"Exported {len(filtered_entries)} entries to {output}")
    else:
        print(export_data)


def export_to_ics(entries: List[TrackingEntry]) -> str:
    """Export entries to ICS format"""
    try:
        import ics.icalendar
        import ics.event
    except ImportError:
        typer.echo("ICS export requires the 'ics' package", err=True)
        raise typer.Exit(1)

    calendar = ics.icalendar.Calendar()

    for entry in entries:
        event = ics.event.Event()
        event.name = f"Work: {get_labels_display(entry.labels)}"
        event.begin = entry.start_time
        event.end = entry.end_time

        if entry.description:
            event.description = entry.description

        # Add labels as categories
        if entry.labels:
            event.categories = set(entry.labels)

        calendar.events.add(event)

    return str(calendar)


def export_to_json(entries: List[TrackingEntry]) -> str:
    """Export entries to JSON format"""
    return json.dumps([entry.to_dict() for entry in entries], indent=2)


def export_to_csv(entries: List[TrackingEntry]) -> str:
    """Export entries to CSV format"""
    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        ["Start Time", "End Time", "Duration (minutes)", "Labels", "Description"]
    )

    # Write entries
    for entry in entries:
        duration_minutes = entry.duration().total_seconds() / 60
        labels_str = LABEL_SEPARATOR.join(entry.labels)
        writer.writerow(
            [
                entry.start_time.isoformat(),
                entry.end_time.isoformat(),
                f"{duration_minutes:.1f}",
                labels_str,
                entry.description,
            ]
        )

    return output.getvalue()
