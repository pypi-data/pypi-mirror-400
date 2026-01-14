#!/usr/bin/env python3
"""
Analyze the bug in node_link_generation.py
Shows how the table bounds calculation causes nodes to be placed outside production system.
"""
import json
from pathlib import Path

def find_borders(locations):
    """Simulate find_borders function"""
    if not locations:
        return 0, 0, 0, 0
    
    max_x, max_y = locations[0]
    min_x, min_y = locations[0]
    for loc in locations:
        x, y = loc[0], loc[1]
        if x > max_x:
            max_x = x
        if y > max_y:
            max_y = y
        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y
    return min_x, min_y, max_x, max_y

def analyze_bug(json_file):
    """Analyze the table bounds calculation bug"""
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Get actual production system locations
    locations = []
    print("Production System Locations:")
    for resource in data.get('resource_data', []):
        if resource.get('location'):
            loc = resource['location']
            locations.append(loc)
            print(f"  Resource {resource['ID']}: {loc}")
    
    for source in data.get('source_data', []):
        if source.get('location'):
            loc = source['location']
            locations.append(loc)
            print(f"  Source {source['ID']}: {loc}")
    
    for sink in data.get('sink_data', []):
        if sink.get('location'):
            loc = sink['location']
            locations.append(loc)
            print(f"  Sink {sink['ID']}: {loc}")
    
    print()
    min_x, min_y, max_x, max_y = find_borders(locations)
    
    print(f"Production System Bounds:")
    print(f"  X: [{min_x:.3f}, {max_x:.3f}] (range: {max_x - min_x:.3f})")
    print(f"  Y: [{min_y:.3f}, {max_y:.3f}] (range: {max_y - min_y:.3f})")
    print()
    
    # Show the BUGGY calculation from node_link_generation.py lines 150-153
    print("=" * 80)
    print("BUG ANALYSIS: Table Bounds Calculation (lines 150-153)")
    print("=" * 80)
    print()
    print("Current (BUGGY) calculation:")
    print("  tableXMax = max(1.1 * max_x, 50 + max_x)")
    print("  tableYMax = max(1.1 * max_y, 50 + max_y)")
    print("  tableXMin = min(1.1 * min_x, min_x - 50)")
    print("  tableYMin = min(1.1 * min_y, min_y - 50)")
    print()
    
    tableXMax_buggy = max(1.1 * max_x, 50 + max_x)
    tableYMax_buggy = max(1.1 * max_y, 50 + max_y)
    tableXMin_buggy = min(1.1 * min_x, min_x - 50)
    tableYMin_buggy = min(1.1 * min_y, min_y - 50)
    
    print(f"  tableXMax = max(1.1 * {max_x:.3f}, 50 + {max_x:.3f})")
    print(f"           = max({1.1 * max_x:.3f}, {50 + max_x:.3f})")
    print(f"           = {tableXMax_buggy:.3f}  ← WAY TOO LARGE!")
    print()
    
    print(f"  tableXMin = min(1.1 * {min_x:.3f}, {min_x:.3f} - 50)")
    print(f"           = min({1.1 * min_x:.3f}, {min_x - 50:.3f})")
    print(f"           = {tableXMin_buggy:.3f}  ← WAY TOO SMALL (NEGATIVE!)")
    print()
    
    print(f"  tableYMax = max(1..1 * {max_y:.3f}, 50 + {max_y:.3f})")
    print(f"           = max({1.1 * max_y:.3f}, {50 + max_y:.3f})")
    print(f"           = {tableYMax_buggy:.3f}  ← WAY TOO LARGE!")
    print()
    
    print(f"  tableYMin = min(1.1 * {min_y:.3f}, {min_y:.3f} - 50)")
    print(f"           = min({1.1 * min_y:.3f}, {min_y - 50:.3f})")
    print(f"           = {tableYMin_buggy:.3f}  ← WAY TOO SMALL (NEGATIVE!)")
    print()
    
    print(f"Generated Table Bounds (BUGGY):")
    print(f"  X: [{tableXMin_buggy:.3f}, {tableXMax_buggy:.3f}] (range: {tableXMax_buggy - tableXMin_buggy:.3f})")
    print(f"  Y: [{tableYMin_buggy:.3f}, {tableYMax_buggy:.3f}] (range: {tableYMax_buggy - tableYMin_buggy:.3f})")
    print()
    
    print("PROBLEM:")
    print(f"  The algorithm adds 50 units in EACH direction, regardless of production system size!")
    print(f"  For small production systems (range ~2-4 units), this creates a table that is:")
    print(f"  - {abs(tableXMin_buggy - min_x):.1f} units too far LEFT")
    print(f"  - {tableXMax_buggy - max_x:.1f} units too far RIGHT")
    print(f"  - {abs(tableYMin_buggy - min_y):.1f} units too far DOWN")
    print(f"  - {tableYMax_buggy - max_y:.1f} units too far UP")
    print()
    
    # Show what nodes were actually generated
    print("=" * 80)
    print("GENERATED NODES (from terminal output)")
    print("=" * 80)
    generated_nodes = [
        ("node_1", [4.0, 2.0], "✓ OK"),
        ("node_2", [-43.0, -49.0], "✗ OUTSIDE"),
        ("node_3", [-43.0, -15.0], "✗ OUTSIDE"),
        ("node_4", [-43.0, 19.0], "✗ OUTSIDE"),
        ("node_5", [-43.0, 53.0], "✗ OUTSIDE"),
        ("node_6", [-14.0, -34.0], "✗ OUTSIDE"),
        ("node_7", [-14.0, 33.0], "✗ OUTSIDE"),
        ("node_8", [15.0, -49.0], "✗ OUTSIDE"),
        ("node_9", [15.0, 48.0], "✗ OUTSIDE"),
        ("node_10", [30.0, -20.0], "✗ OUTSIDE"),
        ("node_11", [34.0, 14.0], "✗ OUTSIDE"),
        ("node_12", [49.0, -49.0], "✗ OUTSIDE"),
        ("node_13", [49.0, 43.0], "✗ OUTSIDE"),
    ]
    
    print(f"\nNode locations match the buggy table bounds:")
    print(f"  X range: [{tableXMin_buggy:.1f}, {tableXMax_buggy:.1f}]")
    print(f"  Y range: [{tableYMin_buggy:.1f}, {tableYMax_buggy:.1f}]")
    print()
    
    for node_id, loc, status in generated_nodes:
        x, y = loc
        in_table = (tableXMin_buggy <= x <= tableXMax_buggy and 
                   tableYMin_buggy <= y <= tableYMax_buggy)
        in_production = (min_x <= x <= max_x and min_y <= y <= max_y)
        print(f"  {node_id:10s} [{x:6.1f}, {y:6.1f}] - ", end="")
        if in_production:
            print("✓ in production system")
        elif in_table:
            print("✗ in table bounds but outside production system")
        else:
            print("✗ outside even table bounds!")
    
    print()
    print("=" * 80)
    print("RECOMMENDED FIX")
    print("=" * 80)
    print()
    print("The hardcoded '+50' and '-50' values should be PROPORTIONAL to the production system size.")
    print()
    print("Option 1: Use percentage-based margin")
    margin_pct = 0.1  # 10% margin
    range_x = max_x - min_x
    range_y = max_y - min_y
    margin_x = max(range_x * margin_pct, 1.0)  # At least 1 unit
    margin_y = max(range_y * margin_pct, 1.0)  # At least 1 unit
    
    tableXMax_fixed = max_x + margin_x
    tableYMax_fixed = max_y + margin_y
    tableXMin_fixed = min_x - margin_x
    tableYMin_fixed = min_y - margin_y
    
    print(f"  margin_x = max(range_x * {margin_pct}, 1.0) = max({range_x:.3f} * {margin_pct}, 1.0) = {margin_x:.3f}")
    print(f"  margin_y = max(range_y * {margin_pct}, 1.0) = max({range_y:.3f} * {margin_pct}, 1.0) = {margin_y:.3f}")
    print()
    print(f"Fixed Table Bounds:")
    print(f"  X: [{tableXMin_fixed:.3f}, {tableXMax_fixed:.3f}] (range: {tableXMax_fixed - tableXMin_fixed:.3f})")
    print(f"  Y: [{tableYMin_fixed:.3f}, {tableYMax_fixed:.3f}] (range: {tableYMax_fixed - tableYMin_fixed:.3f})")
    print()
    print("Option 2: Use minimum absolute margin (e.g., 5 units)")
    abs_margin = 5.0
    tableXMax_fixed2 = max_x + abs_margin
    tableYMax_fixed2 = max_y + abs_margin
    tableXMin_fixed2 = min_x - abs_margin
    tableYMin_fixed2 = min_y - abs_margin
    
    print(f"  Using fixed margin: {abs_margin} units")
    print(f"Fixed Table Bounds (abs margin):")
    print(f"  X: [{tableXMin_fixed2:.3f}, {tableXMax_fixed2:.3f}]")
    print(f"  Y: [{tableYMin_fixed2:.3f}, {tableYMax_fixed2:.3f}]")
    print()

if __name__ == "__main__":
    import sys
    json_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("buggy_example.json")
    analyze_bug(json_file)

