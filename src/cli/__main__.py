"""
Interactive CLI for exploring WRC rally data.

Flow: select year → select event → select data type → display results → loop.
"""

import asyncio

import questionary
from rich.console import Console
from rich.table import Table

from openwrc.services.session_service import WrcSession
from openwrc.utils.datetime_utils import ms_to_time_str

_DATA_TYPES = ["Standings", "Split Times", "Exit"]


async def main() -> None:
    console = Console()

    years = await WrcSession.list_available_years()
    year_str = await questionary.select(
        "Select a year:", choices=[str(y) for y in years]
    ).ask_async()
    if year_str is None:
        return
    year = int(year_str)

    events = await WrcSession.list_events_for_year(year)
    event_map = {f"{e.name}  ({e.location})": e for e in events}
    event_label = await questionary.select(
        "Select an event:", choices=list(event_map.keys())
    ).ask_async()
    if event_label is None:
        return
    event = event_map[event_label]

    session = await WrcSession.create(event_id=event.event_id)

    while True:
        console.rule(f"[bold]{event.name} {year}[/]")
        data_type = await questionary.select(
            "What would you like to see?", choices=_DATA_TYPES
        ).ask_async()

        if data_type is None or data_type == "Exit":
            break
        try:
            if data_type == "Standings":
                await _show_standings(session, console)
            elif data_type == "Split Times":
                await _show_split_times(session, console)
        except Exception as e:
            console.print(f"[red]Error:[/] {e}")


async def _show_standings(session: WrcSession, console: Console) -> None:
    choice = await questionary.select(
        "View standings after:",
        choices=["Latest stage", "Specific stage"],
    ).ask_async()
    if choice is None:
        return

    if choice == "Latest stage":
        standings = await session.rally_standings()
        if not standings:
            console.print("[yellow]No standings data.[/]")
            return
        last_stage_id = max(s.stage_id for s in standings)
        standings = [s for s in standings if s.stage_id == last_stage_id]
        title = "Standings — Latest Stage"
    else:
        stages = await session.stages()
        stage_map = {f"SS{s.number} — {s.name}": s for s in stages}
        label = await questionary.select(
            "Select stage:", choices=list(stage_map.keys())
        ).ask_async()
        if label is None:
            return
        stage = stage_map[label]
        standings = await session.rally_standings(stage_id=stage.stage_id)
        title = f"Standings after SS{stage.number} — {stage.name}"

    entries = await session.entries()
    car_number = {e.entry_id: e.identifier for e in entries}

    table = Table(title=title, show_lines=False)
    table.add_column("Pos", justify="right", style="bold")
    table.add_column("Car", justify="center")
    table.add_column("Total Time", justify="right")
    table.add_column("Gap to 1st", justify="right", style="dim")

    for s in sorted(standings, key=lambda r: r.position or 9999):
        gap = f"+{ms_to_time_str(s.diff_first_ms)}" if s.diff_first_ms else "—"
        table.add_row(
            str(s.position or "—"),
            car_number.get(s.entry_id, str(s.entry_id)),
            ms_to_time_str(s.total_time_ms) or "—",
            gap,
        )

    console.print(table)


async def _show_split_times(session: WrcSession, console: Console) -> None:
    stages = await session.stages()
    stage_map = {f"SS{s.number} — {s.name}": s for s in stages}
    label = await questionary.select(
        "Select stage:", choices=list(stage_map.keys())
    ).ask_async()
    if label is None:
        return
    stage = stage_map[label]

    splits = await session.split_times(stage_id=stage.stage_id)
    if not splits:
        console.print("[yellow]No split times for this stage.[/]")
        return

    entries = await session.entries()
    car_number = {e.entry_id: e.identifier for e in entries}

    split_points = sorted({s.split_point_id for s in splits})
    table = Table(
        title=f"Split Times — SS{stage.number} {stage.name}", show_lines=False
    )
    table.add_column("Car", justify="center", style="bold")
    for sp in split_points:
        table.add_column(f"SP {sp}", justify="right")

    by_entry: dict[int, dict[int, int]] = {}
    for s in splits:
        by_entry.setdefault(s.entry_id, {})[s.split_point_id] = s.elapsed_duration_ms

    for entry_id, split_data in sorted(by_entry.items()):
        row = [car_number.get(entry_id, str(entry_id))]
        for sp in split_points:
            ms = split_data.get(sp)
            row.append(ms_to_time_str(ms) if ms is not None else "—")
        table.add_row(*row)

    console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
