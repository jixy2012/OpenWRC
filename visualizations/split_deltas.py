"""
Stage split deltas to leader.

Shows each driver's time gap to the stage leader at each split point.
"""

import asyncio
from collections import defaultdict

from openwrc.models.db.result import SplitTime
from openwrc.services.session_service import WrcSession


def ms_to_mmss_tenths(ms: int | None) -> str | None:
    if ms is None:
        return None
    total_tenths = ms // 100
    minutes = total_tenths // (60 * 10)
    seconds = (total_tenths // 10) % 60
    tenths = total_tenths % 10
    return f"{minutes:02d}:{seconds:02d}.{tenths}"


def build_delta_series(
    split_times: list[SplitTime],
) -> tuple[list[int], dict[int, list[int | None]]]:
    """Return (ordered split_point_ids, {entry_id: [delta_to_leader per split]})."""
    by_entry: dict[int, dict[int, int]] = defaultdict(dict)
    split_ids: set[int] = set()

    for row in split_times:
        split_ids.add(row.split_point_id)
        by_entry[row.entry_id][row.split_point_id] = row.elapsed_duration_ms

    ordered_splits = sorted(split_ids)

    aligned: dict[int, list[int | None]] = {
        entry_id: [by_split.get(s) for s in ordered_splits]
        for entry_id, by_split in by_entry.items()
    }

    min_by_split: list[int | None] = [
        min((aligned[e][i] for e in aligned if aligned[e][i] is not None), default=None)
        for i in range(len(ordered_splits))
    ]

    deltas: dict[int, list[int | None]] = {
        entry_id: [
            (
                (ms - min_by_split[i])
                if (ms is not None and min_by_split[i] is not None)
                else None
            )
            for i, ms in enumerate(series)
        ]
        for entry_id, series in aligned.items()
    }

    return ordered_splits, deltas


async def main():
    session = await WrcSession.create(name="monte carlo", year=2026)
    split_times = await session.split_times(stage_number=1)
    split_ids, deltas = build_delta_series(split_times)
    # TODO: chart with preferred library
    for entry_id, series in deltas.items():
        formatted = [ms_to_mmss_tenths(d) for d in series]
        print(f"entry {entry_id}: {formatted}")


if __name__ == "__main__":
    asyncio.run(main())
