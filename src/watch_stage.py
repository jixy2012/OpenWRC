"""
Print live split point results for a stage as they arrive.

Usage:
    python src/watch_stage.py

TODO: split times only cover intermediate timing gates — they do not include the
stage finish time. To show a complete picture (splits + final time) the live stream
needs to also poll the stage results endpoint
(/{event_id}/stages/{stage_id}/stagetimes.json?rallyId={rally_id}) in parallel and
merge the final elapsed time as a synthetic "finish" split point in the output.
The LiveStreamService should expose a combined channel that subscribes to both
split times and stage times for a given stage.
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timezone

from openwrc.services.live_stream_service import LiveStreamService

EVENT_ID = 637
RALLY_ID = 705
STAGE_ID = 10671


def _ms_to_mmss(ms: int | None) -> str:
    if ms is None:
        return "—"
    total_tenths = ms // 100
    minutes = total_tenths // 600
    seconds = (total_tenths % 600) // 10
    tenths = total_tenths % 10
    return f"{minutes}:{seconds:02d}.{tenths}"


def _print_split_table(entries) -> None:
    # group by split_point_id
    by_split: dict[int, list] = defaultdict(list)
    for e in entries:
        by_split[e.split_point_id].append(e)

    now = datetime.now(tz=timezone.utc).strftime("%H:%M:%S")
    print(f"\n[{now}] Stage {STAGE_ID} — split times")

    for split_id in sorted(
        by_split, key=lambda sid: min(e.elapsed_duration_ms or 0 for e in by_split[sid])
    ):
        rows = sorted(by_split[split_id], key=lambda e: e.elapsed_duration_ms or 0)
        print(f"\n  Split point {split_id}")
        print(f"  {'entry_id':<12} {'elapsed':>10}")
        print(f"  {'-'*12} {'-'*10}")
        for e in rows:
            print(f"  {e.entry_id:<12} {_ms_to_mmss(e.elapsed_duration_ms):>10}")

    print()


async def main() -> None:
    service = LiveStreamService()
    print(f"Watching stage {STAGE_ID} (event={EVENT_ID}, rally={RALLY_ID})...")
    print("Ctrl+C to stop.")
    async for data in service.subscribe(
        event_id=EVENT_ID,
        rally_id=RALLY_ID,
        stage_id=STAGE_ID,
    ):
        _print_split_table(data)


if __name__ == "__main__":
    asyncio.run(main())
