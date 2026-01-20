from openwrc.services.entry_service import RallyEntryService
from openwrc.services.event_service import EventInfoService
from openwrc.services.result_service import RallyResultService
import plotly.graph_objects as go

event_service = EventInfoService()
result_service = RallyResultService()
entry_service = RallyEntryService()


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
