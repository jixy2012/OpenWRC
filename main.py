from src.openwrc.clients.wrc_api_client import WrcApiClient


def main():
    client = WrcApiClient()
    data = client.get_event_itineraries(555, 1343)

    print("Hello from openwrc!")
    print(f"\n\n{data.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
