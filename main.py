from openwrc.services.event_service import EventInfoService


def main():
    client = EventInfoService()
    data = client.get_rally_stages(555, 603)

    print("Hello from openwrc!")
    for stage in data:
        print(f"\n\n{stage.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
