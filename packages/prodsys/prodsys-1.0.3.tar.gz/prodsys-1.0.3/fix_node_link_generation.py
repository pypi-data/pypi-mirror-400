#!/usr/bin/env python3
"""
Fix node link generation by using dynamic area calculation.
Demonstrates how to use the 'area' parameter to bypass the buggy bounds calculation.
"""
import json
from pathlib import Path
from typing import List, Tuple

try:
    from prodsys.models.production_system_data import ProductionSystemData
    from prodsys.util.node_link_generation.node_link_generation import (
        generator,
        convert_nx_to_prodsys,
        apply_nodes_links
    )
except ImportError as e:
    print(f"Error importing prodsys: {e}")
    print("Make sure prodsys is installed and available")
    exit(1)


def find_borders(locations: List[List[float]]) -> Tuple[float, float, float, float]:
    """Calculate bounding box for a list of [x, y] locations."""
    if not locations:
        return (0, 0, 0, 0)
    
    x_coords = [loc[0] for loc in locations if len(loc) >= 2]
    y_coords = [loc[1] for loc in locations if len(loc) >= 2]
    
    if not x_coords or not y_coords:
        return (0, 0, 0, 0)
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    return (min_x, min_y, max_x, max_y)


def calculate_proper_table_bounds(
    locations: List[List[float]],
    margin_percent: float = 0.1,
    min_margin: float = 1.0,
    max_margin: float = 10.0
) -> dict:
    """
    Calculate proper table bounds with proportional margins.
    
    Args:
        locations: List of [x, y] coordinates from resources/sources/sinks
        margin_percent: Percentage of range to use as margin (default 10%)
        min_margin: Minimum margin in units (default 1.0)
        max_margin: Maximum margin in units (default 10.0)
    
    Returns:
        Dictionary with table bounds in the format expected by the generator
    """
    if not locations:
        raise ValueError("No locations provided")
    
    min_x, min_y, max_x, max_y = find_borders(locations)
    
    # Calculate proportional margins
    range_x = max_x - min_x
    range_y = max_y - min_y
    
    # Margin is percentage of range, but clamped between min and max
    margin_x = max(range_x * margin_percent, min_margin)
    margin_x = min(margin_x, max_margin)
    
    margin_y = max(range_y * margin_percent, min_margin)
    margin_y = min(margin_y, max_margin)
    
    # Calculate table bounds with proportional margins
    tableXMax = max_x + margin_x
    tableYMax = max_y + margin_y
    tableXMin = min_x - margin_x
    tableYMin = min_y - margin_y
    
    # Return in format expected by the generator function
    return {
        "corner_nodes": [
            {"pose": [tableXMin, tableYMin, 0]},
            {"pose": [tableXMax, tableYMin, 0]},
            {"pose": [tableXMax, tableYMax, 0]},
            {"pose": [tableXMin, tableYMax, 0]}
        ],
        "center_node": [
            {"pose": [(tableXMin + tableXMax) / 2, (tableYMin + tableYMax) / 2, 0]}
        ]
    }


def fix_node_link_generation(
    input_file: Path,
    output_file: Path = None,
    margin_percent: float = 0.1,
    min_margin: float = 1.0,
    max_margin: float = 10.0,
    style: str = "grid",
    simple_connection: bool = True
):
    """
    Fix node link generation for a production system.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file (default: input_file with '_fixed' suffix)
        margin_percent: Percentage margin for table bounds (default 0.1 = 10%)
        min_margin: Minimum margin in units (default 1.0)
        max_margin: Maximum margin in units (default 10.0)
        style: Generation style ('grid' or 'random', default 'grid')
        simple_connection: Use simple connection mode (default True)
    """
    print("=" * 80)
    print("Fix Node Link Generation with Dynamic Area Calculation")
    print("=" * 80)
    print()
    
    # Load production system
    print(f"Loading: {input_file}")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    print(f"Production System ID: {data.get('ID', 'Unknown')}")
    print()
    
    # Extract locations from resources, sources, and sinks
    print("Extracting locations from production system...")
    locations = []
    
    for resource in data.get('resource_data', []):
        loc = resource.get('location')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            locations.append(list(loc))
            print(f"  Resource {resource.get('ID', 'Unknown')}: {loc}")
    
    for source in data.get('source_data', []):
        loc = source.get('location')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            locations.append(list(loc))
            print(f"  Source {source.get('ID', 'Unknown')}: {loc}")
    
    for sink in data.get('sink_data', []):
        loc = sink.get('location')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            locations.append(list(loc))
            print(f"  Sink {sink.get('ID', 'Unknown')}: {loc}")
    
    if not locations:
        raise ValueError("No valid locations found in resources, sources, or sinks!")
    
    print()
    
    # Calculate production system bounds
    min_x, min_y, max_x, max_y = find_borders(locations)
    print(f"Production System Bounds:")
    print(f"  X: [{min_x:.3f}, {max_x:.3f}] (range: {max_x - min_x:.3f})")
    print(f"  Y: [{min_y:.3f}, {max_y:.3f}] (range: {max_y - min_y:.3f})")
    print()
    
    # Calculate proper table bounds dynamically
    print(f"Calculating proper table bounds with:")
    print(f"  Margin: {margin_percent * 100}% of range")
    print(f"  Min margin: {min_margin} units")
    print(f"  Max margin: {max_margin} units")
    print()
    
    proper_area = calculate_proper_table_bounds(
        locations,
        margin_percent=margin_percent,
        min_margin=min_margin,
        max_margin=max_margin
    )
    
    # Extract bounds from area for display
    corners = proper_area['corner_nodes']
    tableXMin = corners[0]['pose'][0]
    tableYMin = corners[0]['pose'][1]
    tableXMax = corners[1]['pose'][0]
    tableYMax = corners[2]['pose'][1]
    
    print(f"Calculated Table Bounds:")
    print(f"  X: [{tableXMin:.3f}, {tableXMax:.3f}] (range: {tableXMax - tableXMin:.3f})")
    print(f"  Y: [{tableYMin:.3f}, {tableYMax:.3f}] (range: {tableYMax - tableYMin:.3f})")
    print()
    
    # Show comparison with buggy calculation
    print("Comparison with buggy calculation:")
    buggy_tableXMax = max(1.1 * max_x, 50 + max_x)
    buggy_tableXMin = min(1.1 * min_x, min_x - 50)
    buggy_tableYMax = max(1.1 * max_y, 50 + max_y)
    buggy_tableYMin = min(1.1 * min_y, min_y - 50)
    
    print(f"  Buggy bounds would be:")
    print(f"    X: [{buggy_tableXMin:.3f}, {buggy_tableXMax:.3f}] (range: {buggy_tableXMax - buggy_tableXMin:.3f})")
    print(f"    Y: [{buggy_tableYMin:.3f}, {buggy_tableYMax:.3f}] (range: {buggy_tableYMax - buggy_tableYMin:.3f})")
    print(f"  Difference: {abs(buggy_tableXMax - buggy_tableXMin) - abs(tableXMax - tableXMin):.1f} units wider!")
    print()
    
    # Convert to ProductionSystemData
    print("Converting to ProductionSystemData...")
    production_system = ProductionSystemData.model_validate(data)
    print("✓ Successfully loaded")
    print()
    
    # Count existing nodes
    existing_node_count = len(production_system.node_data)
    print(f"Existing nodes: {existing_node_count}")
    
    # Generate network with proper area bounds
    print()
    print("Generating node-link network with corrected bounds...")
    print(f"  Style: {style}")
    print(f"  Simple connection: {simple_connection}")
    print()
    
    # The generator expects area as a list of table configurations
    # Wrap our single table in a list
    area_list = [proper_area]
    
    G = generator(
        production_system,
        area=area_list,  # Use our dynamically calculated area (as list)
        visualize=False,
        style=style,
        simple_connection=simple_connection
    )
    
    nodes, links = convert_nx_to_prodsys(production_system, G)
    
    print(f"Generated:")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Links: {len(links)}")
    print()
    
    # Apply nodes and links
    print("Applying nodes and links to production system...")
    apply_nodes_links(production_system, nodes, links)
    print("✓ Applied")
    print()
    
    # Show generated nodes
    print("Generated Nodes:")
    for node in production_system.node_data:
        if hasattr(node, 'location') and node.location:
            loc = list(node.location) if hasattr(node.location, '__iter__') else [node.location]
            if len(loc) >= 2:
                x, y = loc[0], loc[1]
                # Check if within production system bounds
                in_bounds = (min_x <= x <= max_x and min_y <= y <= max_y)
                status = "✓" if in_bounds else "⚠"
                print(f"  {status} {node.ID}: [{x:8.3f}, {y:8.3f}]")
    
    print()
    
    # Convert back to dict for saving
    print("Converting back to dictionary format...")
    updated_dict = production_system.model_dump(mode='json')
    
    # Preserve API-specific fields if they exist
    api_fields = ['created_at', 'updated_at', 'owner_id', 'cashflow_data', 'derived_from', 'registered']
    for field in api_fields:
        if field in data:
            updated_dict[field] = data[field]
    
    # Determine output file
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_fixed{input_path.suffix}"
    
    # Save updated production system
    print(f"Saving to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(updated_dict, f, indent=4)
    
    print("✓ Saved successfully!")
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Nodes before: {existing_node_count}")
    print(f"Nodes after: {len(production_system.node_data)}")
    print(f"Links generated: {len(links)}")
    print()
    print("The production system now has properly positioned nodes within")
    print("the production system bounds using dynamic area calculation!")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix node link generation using dynamic area calculation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default settings
  python fix_node_link_generation.py buggy_example.json
  
  # Custom output file
  python fix_node_link_generation.py buggy_example.json -o fixed_output.json
  
  # Custom margin settings
  python fix_node_link_generation.py buggy_example.json --margin 0.15 --min-margin 2.0 --max-margin 15.0
  
  # Use random style instead of grid
  python fix_node_link_generation.py buggy_example.json --style random
        """
    )
    
    parser.add_argument("input_file", type=Path, help="Path to input production system JSON file")
    parser.add_argument("-o", "--output", type=Path, help="Path to output JSON file (default: input_file_fixed.json)")
    parser.add_argument("--margin", type=float, default=0.1, help="Margin as percentage of range (default: 0.1 = 10%%)")
    parser.add_argument("--min-margin", type=float, default=1.0, help="Minimum margin in units (default: 1.0)")
    parser.add_argument("--max-margin", type=float, default=10.0, help="Maximum margin in units (default: 10.0)")
    parser.add_argument("--style", choices=["grid", "random"], default="grid", help="Generation style (default: grid)")
    parser.add_argument("--simple-connection", action="store_true", default=True, help="Use simple connection mode (default: True)")
    parser.add_argument("--no-simple-connection", dest="simple_connection", action="store_false", help="Disable simple connection mode")
    
    args = parser.parse_args()
    
    if not args.input_file.exists():
        print(f"Error: File not found: {args.input_file}")
        exit(1)
    
    try:
        fix_node_link_generation(
            input_file=args.input_file,
            output_file=args.output,
            margin_percent=args.margin,
            min_margin=args.min_margin,
            max_margin=args.max_margin,
            style=args.style,
            simple_connection=args.simple_connection
        )
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

