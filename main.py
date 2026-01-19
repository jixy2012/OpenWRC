from openwrc.services.event_service import EventInfoService


def main():
    service = EventInfoService()
    # data = service.get_single_stage_results_by_order(555, 603, 15)
    # data = service.get_single_stage_results_by_id(555, 603, 10279)
    data = service.get_rally_itinerary_id(555, 603)

    print("Hello from openwrc!")
    print(f"id: {data}")
    # for stage in data:
    #     print(f"\n\n{stage.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
