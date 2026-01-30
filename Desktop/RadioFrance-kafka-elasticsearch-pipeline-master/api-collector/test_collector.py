#!/usr/bin/env python3
"""
Test script to validate Radio France API connection and collector logic
without needing Kafka running.
"""

import os
import sys
import time
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set test environment
os.environ["RADIOFRANCE_API_TOKEN"] = os.getenv(
    "RADIOFRANCE_API_KEY", "1976083a-bd25-4a42-8c7c-f216690d4fdd"
)
os.environ["RADIOFRANCE_API_URL"] = "https://openapi.radiofrance.fr/v1/graphql"

from radiofrance_realtime_collector import RadioFranceCollector, MAIN_STATIONS


def test_api_connection():
    """Test that we can connect to Radio France API."""
    print("=" * 60)
    print("TEST 1: API Connection")
    print("=" * 60)

    collector = RadioFranceCollector()

    # Test with single station
    test_station = "FRANCEINTER"
    print(f"\nQuerying {test_station}...")

    grid_data = collector.get_current_broadcast_grid(test_station)

    if grid_data is None:
        print("❌ FAILED: API request returned None")
        return False

    if not grid_data:
        print(
            "⚠️  WARNING: API returned empty grid (might be normal if nothing broadcasting)"
        )
        return True

    print(f"✅ SUCCESS: Received {len(grid_data)} broadcasts")
    print(f"   API requests made: {collector.request_count}")

    # Show first broadcast
    if grid_data:
        first = grid_data[0]
        print(f"\n   First broadcast type: {collector.extract_content_type(first)}")
        if "diffusion" in first:
            print(f"   Title: {first['diffusion'].get('title', 'N/A')}")
        elif "track" in first:
            track = first["track"]
            print(
                f"   Track: {track.get('title', 'N/A')} by {track.get('mainArtists', 'N/A')}"
            )

    return True


def test_data_processing():
    """Test that we can process API data into documents."""
    print("\n" + "=" * 60)
    print("TEST 2: Data Processing")
    print("=" * 60)

    collector = RadioFranceCollector()

    # Get data from a few stations
    test_stations = ["FRANCEINTER", "FIP", "FRANCECULTURE"]

    total_docs = 0
    for station in test_stations:
        print(f"\nProcessing {station}...")

        grid_data = collector.get_current_broadcast_grid(station)

        if not grid_data:
            print(f"   No data for {station}")
            continue

        documents = collector.process_broadcast_data(station, grid_data)

        print(f"   ✅ Created {len(documents)} documents")
        total_docs += len(documents)

        # Show sample document
        if documents:
            sample = documents[0]
            print(f"   Sample fields: {list(sample.keys())}")
            print(f"   - Content type: {sample['content_type']}")
            print(f"   - Station: {sample['station_name']}")
            print(f"   - Is current: {sample['is_current']}")

            if sample.get("current_show"):
                print(f"   - Show: {sample['current_show'].get('title', 'N/A')}")
                print(f"   - Themes: {len(sample.get('themes', []))} themes")
                if sample.get("themes"):
                    print(f"     Examples: {sample['themes'][:2]}")

            if sample.get("current_track"):
                print(f"   - Track: {sample['current_track'].get('title', 'N/A')}")

    print(
        f"\n✅ TOTAL: Processed {total_docs} documents from {len(test_stations)} stations"
    )
    return total_docs > 0


def test_json_serialization():
    """Test that documents can be JSON serialized (for Kafka)."""
    print("\n" + "=" * 60)
    print("TEST 3: JSON Serialization")
    print("=" * 60)

    collector = RadioFranceCollector()

    grid_data = collector.get_current_broadcast_grid("FRANCEINTER")

    if not grid_data:
        print("⚠️  No data to test serialization")
        return True

    documents = collector.process_broadcast_data("FRANCEINTER", grid_data)

    try:
        for i, doc in enumerate(documents[:3]):  # Test first 3
            json_str = json.dumps(doc)
            # Try to parse it back
            parsed = json.loads(json_str)
            print(f"✅ Document {i+1}: {len(json_str)} bytes, {len(parsed)} fields")

        print(f"\n✅ All {len(documents)} documents are JSON serializable")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_theme_extraction():
    """Test theme extraction from taxonomies."""
    print("\n" + "=" * 60)
    print("TEST 4: Theme Extraction")
    print("=" * 60)

    collector = RadioFranceCollector()

    # France Culture typically has rich themes
    grid_data = collector.get_current_broadcast_grid("FRANCECULTURE")

    if not grid_data:
        print("⚠️  No data for theme testing")
        return True

    documents = collector.process_broadcast_data("FRANCECULTURE", grid_data)

    total_themes = 0
    docs_with_themes = 0
    unique_themes = set()

    for doc in documents:
        themes = doc.get("themes", [])
        if themes:
            docs_with_themes += 1
            total_themes += len(themes)
            unique_themes.update(themes)

    print(f"✅ Theme analysis:")
    print(f"   - {docs_with_themes}/{len(documents)} documents have themes")
    print(f"   - {total_themes} total theme associations")
    print(f"   - {len(unique_themes)} unique themes")

    if unique_themes:
        print(f"\n   Sample themes:")
        for theme in list(unique_themes)[:5]:
            print(f"   - {theme}")

    return True


def save_sample_output():
    """Save sample output to file for inspection."""
    print("\n" + "=" * 60)
    print("SAVING SAMPLE DATA")
    print("=" * 60)

    collector = RadioFranceCollector()

    # Collect from a few stations
    all_docs = []
    for station in ["FRANCEINTER", "FIP", "FRANCECULTURE"]:
        grid_data = collector.get_current_broadcast_grid(station)
        if grid_data:
            docs = collector.process_broadcast_data(station, grid_data)
            all_docs.extend(docs[:2])  # First 2 from each

    output_file = "export/samples/radiofrance_sample_output.json"
    os.makedirs("export/samples", exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        for doc in all_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"✅ Saved {len(all_docs)} sample documents to {output_file}")
    print(f"   You can inspect this file to see the data structure")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RADIO FRANCE COLLECTOR TEST SUITE")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print(
        f"API Token: {'***' + os.getenv('RADIOFRANCE_API_TOKEN', '')[-4:] if os.getenv('RADIOFRANCE_API_TOKEN') else 'NOT SET'}"
    )

    tests = [
        ("API Connection", test_api_connection),
        ("Data Processing", test_data_processing),
        ("JSON Serialization", test_json_serialization),
        ("Theme Extraction", test_theme_extraction),
        ("Sample Output", save_sample_output),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, s in results if s)
    print(f"\n{passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Collector is ready to run.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
