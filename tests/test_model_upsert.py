"""
Test script to validate which API models can be directly converted to DB models using existing upsert utilities.
"""

import asyncio
import json
import os
from datetime import datetime
from openwrc.clients.wrc_api_client import WrcApiClient
from openwrc.storage.data_store_service import WrcDataStore
from openwrc.storage.crud_utils import (
    upsert_from_api,
    upsert_event_metadata,
    upsert_rally_metadata,
    upsert_event_itinerary,
    upsert_rally_entries,
    upsert_drivers,
    upsert_codrivers,
)
from openwrc.models.db.event import EventMetadata, RallyMetadata, EventClass, Entry
from openwrc.models.db.entities import (
    Country,
    Group,
    Manufacturer,
    Entrant,
    Person,
)
from openwrc.models.db.itinerary import (
    Itinerary,
    ItineraryLeg,
    ItinerarySection,
    Stage,
    Control,
    StartList,
    StartListItem,
)


async def test_model_conversion():
    """Test which API models can be directly converted to DB models."""

    db_file = "test_upsert.db"
    client = WrcApiClient()
    store = WrcDataStore(db_path=db_file)

    try:
        # Initialize database
        await store.init_db()

        print("🧪 Testing API to DB model conversions...\n")

        # Get some real data from API
        event_id = 635  # Example event ID
        rally_id = 703  # Example rally ID

        results = {}

        # Test 1: EventMetadata (use dedicated upsert function)
        print("1️⃣  Testing EventMetadata...")
        try:
            api_event = await client.get_event_metadata(event_id=event_id)
            async with store.SessionLocal() as session:
                await upsert_event_metadata(session, api_event)
                await session.commit()
            results["EventMetadata"] = "✅ SUCCESS"
        except Exception as e:
            results["EventMetadata"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 2: Country
        print("2️⃣  Testing Country...")
        try:
            api_event = await client.get_event_metadata(event_id=event_id)
            async with store.SessionLocal() as session:
                db_country = await upsert_from_api(session, api_event.country, Country)
                await session.commit()
            results["Country"] = "✅ SUCCESS"
        except Exception as e:
            results["Country"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 3: RallyMetadata (use dedicated upsert function)
        print("3️⃣  Testing RallyMetadata...")
        try:
            api_event = await client.get_event_metadata(event_id=event_id)
            async with store.SessionLocal() as session:
                await upsert_rally_metadata(session, api_event)
                await session.commit()
            results["RallyMetadata"] = "✅ SUCCESS"
        except Exception as e:
            results["RallyMetadata"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 4: EventClass
        print("4️⃣  Testing EventClass...")
        try:
            api_event = await client.get_event_metadata(event_id=event_id)
            event_class = api_event.event_classes[0]
            async with store.SessionLocal() as session:
                db_class = await upsert_from_api(session, event_class, EventClass)
                await session.commit()
            results["EventClass"] = "✅ SUCCESS"
        except Exception as e:
            results["EventClass"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Get entries for person/entity tests
        try:
            api_entries = await client.get_rally_entries(
                event_id=event_id, rally_id=rally_id
            )
            if api_entries:
                first_entry = api_entries[0]
            else:
                first_entry = None
        except Exception as e:
            print(f"⚠️  Could not fetch entries: {e}")
            first_entry = None

        # Test 5: Person (Driver) - use upsert_drivers
        print("5️⃣  Testing Driver...")
        try:
            if first_entry:
                api_entries = await client.get_rally_entries(
                    event_id=event_id, rally_id=rally_id
                )
                drivers = [entry.driver for entry in api_entries]
                async with store.SessionLocal() as session:
                    await upsert_drivers(session, drivers)
                    await session.commit()
                results["Driver"] = "✅ SUCCESS"
            else:
                results["Driver"] = "⚠️  SKIPPED: No entries found"
        except Exception as e:
            results["Driver"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 6: Person (CoDriver) - use upsert_codrivers
        print("6️⃣  Testing CoDriver...")
        try:
            if first_entry:
                api_entries = await client.get_rally_entries(
                    event_id=event_id, rally_id=rally_id
                )
                codrivers = [entry.codriver for entry in api_entries if entry.codriver]
                async with store.SessionLocal() as session:
                    await upsert_codrivers(session, codrivers)
                    await session.commit()
                results["CoDriver"] = "✅ SUCCESS"
            else:
                results["CoDriver"] = "⚠️  SKIPPED: No entries found"
        except Exception as e:
            results["CoDriver"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 7: Manufacturer
        print("7️⃣  Testing Manufacturer...")
        try:
            if first_entry:
                async with store.SessionLocal() as session:
                    db_manufacturer = await upsert_from_api(
                        session, first_entry.manufacturer, Manufacturer
                    )
                    await session.commit()
                results["Manufacturer"] = "✅ SUCCESS"
            else:
                results["Manufacturer"] = "⚠️  SKIPPED: No entries found"
        except Exception as e:
            results["Manufacturer"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 8: Entrant
        print("8️⃣  Testing Entrant...")
        try:
            if first_entry:
                async with store.SessionLocal() as session:
                    db_entrant = await upsert_from_api(
                        session, first_entry.entrant, Entrant
                    )
                    await session.commit()
                results["Entrant"] = "✅ SUCCESS"
            else:
                results["Entrant"] = "⚠️  SKIPPED: No entries found"
        except Exception as e:
            results["Entrant"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 9: Group
        print("9️⃣  Testing Group...")
        try:
            if first_entry:
                async with store.SessionLocal() as session:
                    db_group = await upsert_from_api(session, first_entry.group, Group)
                    await session.commit()
                results["Group"] = "✅ SUCCESS"
            else:
                results["Group"] = "⚠️  SKIPPED: No entries found"
        except Exception as e:
            results["Group"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 10: Entry (requires working upsert_rally_entries)
        print("🔟 Testing Entry...")
        try:
            results["Entry"] = "⚠️  SKIPPED: upsert_rally_entries incomplete"
        except Exception as e:
            results["Entry"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 11: Itinerary
        print("1️⃣1️⃣  Testing Itinerary...")
        try:
            api_event = await client.get_event_metadata(event_id=event_id)
            api_itinerary = await client.get_event_itineraries(
                event_id=event_id, itinerary_id=api_event.rallies[0].itinerary_id
            )
            async with store.SessionLocal() as session:
                await upsert_event_itinerary(session, api_itinerary, rally_id=rally_id)
                await session.commit()
            results["Itinerary"] = "✅ SUCCESS"
        except Exception as e:
            results["Itinerary"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 12-15: ItineraryLeg, Section, Stage, Control (depend on Itinerary)
        print("1️⃣2️⃣  Testing ItineraryLeg...")
        results["ItineraryLeg"] = "⚠️  SKIPPED: No dedicated upsert function yet"

        print("1️⃣3️⃣  Testing ItinerarySection...")
        results["ItinerarySection"] = "⚠️  SKIPPED: No dedicated upsert function yet"

        print("1️⃣4️⃣  Testing Stage...")
        results["Stage"] = "⚠️  SKIPPED: No dedicated upsert function yet"

        print("1️⃣5️⃣  Testing Control...")
        results["Control"] = "⚠️  SKIPPED: No dedicated upsert function yet"

        # Test 16: StartList (depends on working itinerary upsert)
        print("1️⃣6️⃣  Testing StartList...")
        try:
            results["StartList"] = "⚠️  SKIPPED: Depends on Itinerary"
        except Exception as e:
            results["StartList"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Test 17: StartListItem
        print("1️⃣7️⃣  Testing StartListItem...")
        try:
            api_event = await client.get_event_metadata(event_id=event_id)
            api_itinerary = await client.get_event_itineraries(
                event_id=event_id, itinerary_id=api_event.rallies[0].itinerary_id
            )
            start_list_id = None
            for leg in api_itinerary.itinerary_legs:
                if leg.start_list_id:
                    start_list_id = leg.start_list_id
                    break

            if start_list_id:
                api_start_list = await client.get_event_start_list(
                    event_id=event_id, start_list_id=start_list_id
                )
                if api_start_list.start_list_items:
                    item = api_start_list.start_list_items[0]
                    async with store.SessionLocal() as session:
                        db_item = await upsert_from_api(session, item, StartListItem)
                        await session.commit()
                    results["StartListItem"] = "✅ SUCCESS"
                else:
                    results["StartListItem"] = "⚠️  SKIPPED: No items in start list"
            else:
                results["StartListItem"] = "⚠️  SKIPPED: No start list ID found"
        except Exception as e:
            results["StartListItem"] = f"❌ FAILED: {type(e).__name__}: {str(e)[:100]}"

        # Print summary
        print("\n" + "=" * 80)
        print("📊 RESULTS SUMMARY")
        print("=" * 80)

        success_count = sum(1 for v in results.values() if "✅" in v)
        failed_count = sum(1 for v in results.values() if "❌" in v)
        skipped_count = sum(1 for v in results.values() if "⚠️" in v)

        for model_name, result in results.items():
            print(f"{model_name:20s} | {result}")

        print("=" * 80)
        print(
            f"✅ Success: {success_count} | ❌ Failed: {failed_count} | ⚠️  Skipped: {skipped_count}"
        )
        print("=" * 80)

        if failed_count > 0:
            print("\n💡 Models that failed need custom mapper functions!")

        # Write results to JSON
        output = {
            "timestamp": datetime.now().isoformat(),
            "test_params": {"event_id": event_id, "rally_id": rally_id},
            "summary": {
                "success": success_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "total": len(results),
            },
            "results": {
                model: {
                    "status": (
                        "success"
                        if "✅" in result
                        else ("failed" if "❌" in result else "skipped")
                    ),
                    "message": result,
                }
                for model, result in results.items()
            },
        }

        output_file = "tests/model_upsert_test_results.json"
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\n📄 Results written to: {output_file}")

    finally:
        # Cleanup: Close engine and delete test database
        await store.engine.dispose()

        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"🧹 Cleaned up test database: {db_file}")


if __name__ == "__main__":
    asyncio.run(test_model_conversion())
