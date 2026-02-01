from collections import defaultdict
from openwrc.services.entry_service import RallyEntryService
from openwrc.services.event_service import EventInfoService
from openwrc.services.result_service import RallyResultService
import plotly.graph_objects as go

event_service = EventInfoService()
result_service = RallyResultService()
entry_service = RallyEntryService()


def ms_to_mmss_tenths(ms: int | None) -> str | None:
    if ms is None:
        return None
    total_tenths = ms // 100  # 1 tenth = 100ms
    minutes = total_tenths // (60 * 10)
    seconds = (total_tenths // 10) % 60
    tenths = total_tenths % 10
    return f"{minutes:02d}:{seconds:02d}.{tenths}"


async def rally_position_changes_timeseries(event_id: int, rally_id: int):
    results = await result_service.get_cumulative_rally_results_by_stage(
        rally_id=rally_id, event_id=event_id
    )
    stages = await event_service.get_rally_stages(event_id=event_id, rally_id=rally_id)
    entries = await entry_service.get_rally_entries(
        event_id=event_id, rally_id=rally_id
    )

    entries_by_entry_id = {entry.entry_id: entry.driver.abbv_name for entry in entries}
    results_by_entry_id = {}
    stage_names = {stage.stage_id: stage.name for stage in stages}
    stage_order = []
    for results_by_stage in results.cumulative_stage_results:
        stage_order.append(stage_names[results_by_stage.stage_id])
        for result in results_by_stage.results:
            entry_driver_name = entries_by_entry_id[result.entry_id]
            if entry_driver_name not in results_by_entry_id:
                results_by_entry_id[entry_driver_name] = []
            results_by_entry_id[entry_driver_name].append(result.position)
    fig = go.Figure()

    for entry_driver_name, positions in results_by_entry_id.items():

        if any(p is not None and p <= 15 for p in positions):
            fig.add_trace(
                go.Scatter(
                    x=stage_order,
                    y=positions,
                    mode="lines+markers",
                    name=f"{entry_driver_name}",
                    hovertemplate=f"<b>{entry_driver_name}</b><br>Stage: %{{x}}<br>Position: %{{y}}<extra></extra>",
                )
            )

    fig.update_layout(
        title="rally position changes",
        xaxis_title="stages",
        yaxis_title="position",
        yaxis={"autorange": False, "range": [16, 0], "dtick": 1},
        hovermode="closest",
        height=1100,
    )
    fig.write_html("plot.html")


async def stage_delta_to_leader_timeseries(
    event_id: int, rally_id: int, stage_order: int
):
    stage_time_splits = await result_service.get_stage_split_time_results_by_order(
        event_id=event_id, rally_id=rally_id, order=stage_order
    )

    entries_by_entry_id = await entry_service.get_entry_id_to_driver_name(
        event_id=event_id, rally_id=rally_id
    )
    splits_times_by_entry_id = defaultdict(dict)
    split_ids = set()
    for result in stage_time_splits:
        split_ids.add(result.split_point_id)
        driver_name = entries_by_entry_id[result.entry_id]

        splits_times_by_entry_id[driver_name][
            result.split_point_id
        ] = result.elapsed_duration_ms

    split_ids = sorted(split_ids)

    # Align each driver's split series onto the same split_id order,
    # using None for missing splits.
    aligned_by_driver: dict[str, list[int | None]] = {
        driver: [by_split.get(split_id) for split_id in split_ids]
        for driver, by_split in splits_times_by_entry_id.items()
    }

    # Compute leader (min) per split, ignoring None.
    min_by_split: list[int | None] = []
    for i in range(len(split_ids)):
        vals = [
            aligned_by_driver[driver][i]
            for driver in aligned_by_driver
            if aligned_by_driver[driver][i] is not None
        ]
        min_by_split.append(min(vals) if vals else None)

    # Compute delta-to-leader per driver, preserving None gaps.
    split_time_delta_to_leader: dict[str, list[int | None]] = {}
    for driver, series in aligned_by_driver.items():
        split_time_delta_to_leader[driver] = [
            (
                (ms - min_by_split[i])
                if (ms is not None and min_by_split[i] is not None)
                else None
            )
            for i, ms in enumerate(series)
        ]

    fig = go.Figure()

    for entry_driver_name, deltas_to_leader in split_time_delta_to_leader.items():
        y_formatted = [ms_to_mmss_tenths(y) for y in deltas_to_leader]
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(split_ids) + 1)),
                y=deltas_to_leader,
                customdata=y_formatted,
                mode="lines+markers",
                name=f"{entry_driver_name}",
                hovertemplate=(
                    f"<b>{entry_driver_name}</b>"
                    "<br>Split: %{x}"
                    "<br>Δ to leader: %{customdata}<extra></extra>"
                ),
                connectgaps=False,
            )
        )

    fig.update_layout(
        title="stage split deltas to leader",
        xaxis_title="splits",
        yaxis_title="deltas",
        yaxis={"range": [0, 30_000]},  # 0–30 seconds (ms)
        hovermode="closest",
        height=1100,
    )
    fig.write_html("plot.html")
