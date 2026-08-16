#!/usr/bin/env python3
"""Master orchestrator for Japan Trip Optimizer.

Usage:
    python src/optimize.py              # Use existing data, build UI
    python src/optimize.py --research   # Generate search matrix only
    python src/optimize.py --full       # Research + build (requires browser)
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def generate_search_matrix():
    """Phase 1: Generate flight search matrix."""
    print("🔍 Phase 1: Generating flight search matrix...")
    
    from src.research.schemas import FlightSearchSpace
    from src.research.google_flights_encoder import generate_search_matrix as gen_matrix
    
    space_data = json.loads((ROOT / "data/search_space.json").read_text())
    space = FlightSearchSpace(**space_data)
    
    matrix = gen_matrix(space)
    
    # Save to file
    output = ROOT / "data/flight_search_matrix.json"
    output.write_text(json.dumps(matrix, indent=2, ensure_ascii=False))
    
    print(f"   ✓ Generated {len(matrix)} search combinations")
    print(f"   ✓ Saved to {output}")
    
    return matrix


def research_flights(matrix, max_searches=None):
    """Phase 2: Scrape flights (requires browser_exec)."""
    print(f"\n✈️  Phase 2: Researching flights...")
    print("   ⚠️  This requires browser automation and will take time.")
    print("   ⚠️  Skipping for now — use manual data from trip_data.json")
    
    # TODO: Implement when browser_exec is available
    # from src.research.flight_scraper import scrape_google_flights_batch
    # observations = scrape_google_flights_batch(matrix, output_path, delay_seconds=10)
    
    return []


def generate_itinerary_variants():
    """Phase 3: Generate itinerary variants for existing flights."""
    print("\n🗺️  Phase 3: Generating itinerary variants...")
    
    from src.itinerary import generate_route_variants
    from datetime import datetime
    
    # Load existing flight data
    data = json.loads((ROOT / "data/trip_data.json").read_text())
    
    variants = {}
    for flight in data["flight_options"]:
        out = datetime.fromisoformat(flight["departure_date"])
        ret = datetime.fromisoformat(flight["return_date"])
        nights = (ret - out).days
        
        variant = generate_route_variants(
            flight.get("arrival_city", flight.get("arrival_airport", "Tokyo")),
            flight.get("departure_city", flight.get("departure_airport", "Tokyo")),
            nights
        )
        
        variants[flight["id"]] = variant
    
    # Save variants
    output = ROOT / "data/itinerary_variants.json"
    output.write_text(json.dumps(variants, indent=2, ensure_ascii=False))
    
    print(f"   ✓ Generated {len(variants)} itinerary variants")
    print(f"   ✓ Saved to {output}")
    
    return variants


def generate_accommodation_queries(variants):
    """Phase 4: Generate accommodation search queries."""
    print("\n🏨 Phase 4: Generating accommodation queries...")
    
    from src.accommodation import build_accommodation_queries
    from datetime import datetime
    
    data = json.loads((ROOT / "data/trip_data.json").read_text())
    
    all_queries = {}
    for flight in data["flight_options"]:
        variant = variants.get(flight["id"])
        if not variant:
            continue
        
        queries = build_accommodation_queries(
            flight["departure_date"],
            variant["route"],
            variant["nights"]
        )
        
        all_queries[flight["id"]] = queries
    
    # Save queries
    output = ROOT / "data/accommodation_queries.json"
    output.write_text(json.dumps(all_queries, indent=2, ensure_ascii=False))
    
    print(f"   ✓ Generated accommodation queries for {len(all_queries)} flights")
    print(f"   ✓ Saved to {output}")
    
    return all_queries


def build_ui():
    """Phase 5: Build HTML outputs."""
    print("\n🎨 Phase 5: Building HTML outputs...")
    
    # Build configurator
    import subprocess
    print("   Building configurator...")
    subprocess.run([".venv/bin/python", "src/build_configurator.py"], cwd=ROOT, check=True)
    
    # Build optimizer
    from src.build_optimizer import build_optimizer
    output = ROOT / "outputs/japan-optimizer.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    html = build_optimizer()
    output.write_text(html, encoding="utf-8")
    
    print(f"   ✓ {ROOT / 'outputs/japan-configurator.html'}")
    print(f"   ✓ {output}")


def main():
    parser = argparse.ArgumentParser(description="Japan Trip Optimizer")
    parser.add_argument("--research", action="store_true", help="Generate search matrix only")
    parser.add_argument("--full", action="store_true", help="Full pipeline including flight research")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Japan Trip Optimizer")
    print("=" * 60)
    
    if args.research:
        generate_search_matrix()
        return
    
    if args.full:
        matrix = generate_search_matrix()
        research_flights(matrix)
    
    # Always generate variants and queries
    variants = generate_itinerary_variants()
    generate_accommodation_queries(variants)
    
    # Build UI
    build_ui()
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)
    print("\nOutputs:")
    print("  - outputs/japan-configurator.html")
    print("  - outputs/japan-optimizer.html")
    print("\nData:")
    print("  - data/itinerary_variants.json")
    print("  - data/accommodation_queries.json")
    print("\nOpen in browser:")
    print("  file://" + str(ROOT / "outputs/japan-optimizer.html"))


if __name__ == "__main__":
    main()
