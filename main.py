import asyncio
from openwrc.services.result_service import RallyResultService


async def main():
    service = RallyResultService()
    # data = service.get_single_stage_results_by_order(555, 603, 15)
    data = await service.get_cumulative_rally_results_by_stage(555, 603)
    # data = service.get_cumulative_stage_results_by_id(555, 603, 10281)
    # data = service.get_rally_itinerary_id(555, 603)

    print("Hello from openwrc!")
    print(f"{data.model_dump_json(indent=2)}")
    # for stage in data:
    #     print(f"\n\n{stage.model_dump_json(indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
