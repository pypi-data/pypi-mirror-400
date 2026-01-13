import os

from .runinfo import Snapshot, Interval
from .formats import naming, log_reader

__all__ = ["generate_snapshots", "generate_intervals"]


def generate_snapshots(folder: str | list[str]) -> list[Snapshot]:
    """Read the timelog.bin in the folder(s) and generate the list of Snapshots"""
    snapshots: list[Snapshot] = []

    for f in folder if isinstance(folder, list) else [folder]:
        # read the timelog.bin file in the folder
        timelog = log_reader.read_timelog(os.path.join(f, naming.timelog_filename()))

        # generate a snapshot for each entry in the timelog and append
        snapshots.extend(
            Snapshot(
                time=entry["time"],
                count=entry["row_count"],
                n=entry["index"],
                folder=f
            ) for entry in timelog
        )

    return snapshots


def generate_intervals(folder: str | list[str]) -> list[Interval]:
    """Read the timelog.bin in the folder(s) and generate the list of Intervals"""

    snapshots = generate_snapshots(folder)

    return [
        Interval(start, end) for start, end in zip(snapshots[:-1], snapshots[1:])
    ]
