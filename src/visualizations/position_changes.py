"""
Rally position changes across stages.

Shows each driver's overall position after each stage for the full rally.
"""

import asyncio
from collections import defaultdict

from openwrc.models.db.result import RallyStanding
from openwrc.services.session_service import WrcSession


def ms_to_mmss_tenths(ms: int | None) -> str | None:
    if ms is None:
        return None
    total_tenths = ms // 100
    minutes = total_tenths // (60 * 10)
    seconds = (total_tenths // 10) % 60
    tenths = total_tenths % 10
    return f"{minutes:02d}:{seconds:02d}.{tenths}"


def build_position_series(
    standings: list[RallyStanding],
) -> tuple[list[int], dict[int, list[int | None]]]:
    """Return (ordered stage_ids, {entry_id: [position per stage]})."""
    stage_ids_seen: list[int] = []
    stage_ids_set: set[int] = set()
    positions_by_entry: dict[int, dict[int, int | None]] = defaultdict(dict)

    for row in standings:
        if row.stage_id not in stage_ids_set:
            stage_ids_seen.append(row.stage_id)
            stage_ids_set.add(row.stage_id)
        positions_by_entry[row.entry_id][row.stage_id] = row.position

    ordered_stage_ids = sorted(stage_ids_seen)
    series = {
        entry_id: [by_stage.get(s) for s in ordered_stage_ids]
        for entry_id, by_stage in positions_by_entry.items()
    }
    return ordered_stage_ids, series


async def main():
    session = await WrcSession.create(name="monte carlo", year=2026)
    standings = await session.rally_standings()
    stage_ids, series = build_position_series(standings)
    # TODO: chart with preferred library
    for entry_id, positions in series.items():
        print(f"entry {entry_id}: {positions}")


if __name__ == "__main__":
    asyncio.run(main())
