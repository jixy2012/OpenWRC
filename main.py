import asyncio

# from openwrc.analytics.event_timeseries import stage_delta_to_leader_timeseries
from openwrc.services.result_service import RallyResultService
from openwrc.services.event_service import EventInfoService
from openwrc.services.entry_service import RallyEntryService


async def main():
    service = RallyResultService()
    service = EventInfoService()
    service = RallyEntryService()
    # service = await WrcSession.create(event_id=635)
    # data = await service.get_event_metadata(524)
    data = await service.get_rally_entries(635, 703)
    # data = await service.get_event_shakedown_results(635)
    # data = await service.get_event_metadata(635)
    # data = service.get_cumulative_stage_results_by_id(555, 603, 10281)
    # data = service.get_rally_itinerary_id(555, 603)
    # data = await service.get_stage_split_time_results_by_order(635, 703, 1)

    print("Hello from openwrc!")

    # await rally_position_changes_timeseries(555, 603)
    # print(f"{data.model_dump_json(indent=2)}")
    for stage in data:
        print(f"\n\n{stage.model_dump_json(indent=2)}")
    # await stage_delta_to_leader_timeseries(event_id=635, rally_id=703, stage_order=2)
    # print(service.current_itinerary_leg_number)


if __name__ == "__main__":
    asyncio.run(main())
