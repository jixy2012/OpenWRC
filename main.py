from src.openwrc.clients.event_client import WrcApiClient


def main():
    client = WrcApiClient()
    data = client.get_event_metadata(555)

    print("Hello from openwrc!")
    print(f"\n\n{data.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
