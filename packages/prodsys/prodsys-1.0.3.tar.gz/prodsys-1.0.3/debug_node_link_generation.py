#!/usr/bin/env python3
"""
Debug script for node link generation issues.
Loads a production system JSON, applies node link generation, and analyzes the results.
"""
import json
import sys
from pathlib import Path
from typing import List, Tuple, Set
import math

try:
    from prodsys.models.production_system_data import ProductionSystemData
    from prodsys.util.node_link_generation import node_link_generation
except ImportError as e:
    print(f"Error importing prodsys: {e}")
    print("Make sure prodsys is installed and available")
    sys.exit(1)


def calculate_bounds(locations: List[List[float]]) -> Tuple[float, float, float, float]:
    """Calculate bounding box for a list of [x, y] locations."""
    if not locations:
        return (0, 0, 0, 0)
    
    x_coords = [loc[0] for loc in locations if len(loc) >= 2]
    y_coords = [loc[1] for loc in locations if len(loc) >= 2]
    
    if not x_coords or not y_coords:
        return (0, 0, 0, 0)
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    return (min_x, max_x, min_y, max_y)


def distance(coord1: List[float], coord2: List[float]) -> float:
    """Calculate Euclidean distance between two coordinates."""
    if len(coord1) < 2 or len(coord2) < 2:
        return float('inf')
    dx = coord1[0] - coord2[0]
    dy = coord1[1] - coord2[1]
    return math.sqrt(dx * dx + dy * dy)


def is_within_bounds(location: List[float], min_x: float, max_x: float, 
                     min_y: float, max_y: float, margin: float = 5.0) -> bool:
    """Check if a location is within bounds with a margin."""
    if len(location) < 2:
        return False
    x, y = location[0], location[1]
    return (min_x - margin <= x <= max_x + margin and 
            min_y - margin <= y <= max_y + margin)


def find_nearest_element(node_location: List[float], 
                        elements: List[dict], 
                        element_type: str) -> Tuple[dict, float]:
    """Find the nearest element to a node location."""
    if not elements or len(node_location) < 2:
        return None, float('inf')
    
    nearest = None
    min_dist = float('inf')
    
    for elem in elements:
        if 'location' in elem and elem['location']:
            elem_loc = elem['location']
            if isinstance(elem_loc, (list, tuple)) and len(elem_loc) >= 2:
                dist = distance(node_location, list(elem_loc))
                if dist < min_dist:
                    min_dist = dist
                    nearest = elem
    
    return nearest, min_dist


def analyze_node_link_generation(json_file: Path):
    """Load production system, generate nodes, and analyze results."""
    
    print("=" * 80)
    print(f"Node Link Generation Debug Script")
    print(f"Loading: {json_file}")
    print("=" * 80)
    print()
    
    # Load JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"Production System ID: {data.get('ID', 'Unknown')}")
    print()
    
    # Extract location information BEFORE generation
    print("--- BEFORE NODE LINK GENERATION ---")
    print()
    
    # Collect all valid locations
    resource_locations = []
    source_locations = []
    sink_locations = []
    port_locations = []
    existing_node_locations = []
    
    print("Resources:")
    for resource in data.get('resource_data', []):
        loc = resource.get('location')
        res_id = resource.get('ID', 'Unknown')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            resource_locations.append(list(loc))
            print(f"  {res_id}: [{loc[0]:.3f}, {loc[1]:.3f}]")
        else:
            print(f"  {res_id}: MISSING LOCATION!")
    
    print()
    print("Sources:")
    for source in data.get('source_data', []):
        loc = source.get('location')
        src_id = source.get('ID', 'Unknown')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            source_locations.append(list(loc))
            print(f"  {src_id}: [{loc[0]:.3f}, {loc[1]:.3f}]")
        else:
            print(f"  {src_id}: MISSING LOCATION!")
    
    print()
    print("Sinks:")
    for sink in data.get('sink_data', []):
        loc = sink.get('location')
        sink_id = sink.get('ID', 'Unknown')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            sink_locations.append(list(loc))
            print(f"  {sink_id}: [{loc[0]:.3f}, {loc[1]:.3f}]")
        else:
            print(f"  {sink_id}: MISSING LOCATION!")
    
    print()
    print("Ports (sample):")
    for port in data.get('port_data', [])[:5]:  # Show first 5
        loc = port.get('location')
        port_id = port.get('ID', 'Unknown')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            port_locations.append(list(loc))
            print(f"  {port_id}: [{loc[0]:.3f}, {loc[1]:.3f}]")
    
    print()
    print("Existing Nodes BEFORE generation:")
    existing_node_ids = set()
    for node in data.get('node_data', []):
        loc = node.get('location')
        node_id = node.get('ID', 'Unknown')
        existing_node_ids.add(node_id)
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            existing_node_locations.append(list(loc))
            print(f"  {node_id}: [{loc[0]:.3f}, {loc[1]:.3f}]")
        else:
            print(f"  {node_id}: MISSING LOCATION!")
    
    print()
    
    # Calculate bounds - ONLY from resources, sources, and sinks (not existing nodes which may be wrong)
    production_system_locations = resource_locations + source_locations + sink_locations
    if production_system_locations:
        min_x, max_x, min_y, max_y = calculate_bounds(production_system_locations)
        margin_x = max((max_x - min_x) * 0.1, 5.0) if max_x != min_x else 5.0
        margin_y = max((max_y - min_y) * 0.1, 5.0) if max_y != min_y else 5.0
        
        print(f"Production System Bounds (resources, sources, sinks only):")
        print(f"  X: [{min_x:.3f}, {max_x:.3f}], Y: [{min_y:.3f}, {max_y:.3f}]")
        print(f"  Valid Location Bounds (with 10% margin):")
        print(f"  X: [{min_x - margin_x:.3f}, {max_x + margin_x:.3f}]")
        print(f"  Y: [{min_y - margin_y:.3f}, {max_y + margin_y:.3f}]")
    else:
        print("ERROR: No valid locations found in resources/sources/sinks!")
        return
    
    # Check existing nodes against production system bounds
    print()
    print("Existing Nodes Analysis (before generation):")
    bad_existing_nodes = []
    for node in data.get('node_data', []):
        node_id = node.get('ID', 'Unknown')
        loc = node.get('location')
        if loc and isinstance(loc, (list, tuple)) and len(loc) >= 2:
            node_loc = list(loc)
            in_bounds = is_within_bounds(node_loc, min_x, max_x, min_y, max_y, 
                                        margin=max(margin_x, margin_y))
            if not in_bounds:
                bad_existing_nodes.append((node_id, node_loc))
                x, y = node_loc[0], node_loc[1]
                dist_from_center = distance(node_loc, [(min_x+max_x)/2, (min_y+max_y)/2])
                print(f"  ✗ {node_id}: [{x:8.3f}, {y:8.3f}] - {dist_from_center:.2f} units from center")
            else:
                x, y = node_loc[0], node_loc[1]
                print(f"  ✓ {node_id}: [{x:8.3f}, {y:8.3f}] - OK")
    
    if bad_existing_nodes:
        print(f"\n  ⚠ WARNING: {len(bad_existing_nodes)} existing nodes are OUTSIDE the production system!")
        print(f"     Production system is in area X: [{min_x:.2f}, {max_x:.2f}], Y: [{min_y:.2f}, {max_y:.2f}]")
        print(f"     But these nodes are far away from this area.")
    
    print()
    print("--- APPLYING NODE LINK GENERATION ---")
    print()
    
    # Convert to ProductionSystemData
    try:
        production_system = ProductionSystemData.model_validate(data)
        print("✓ Successfully loaded ProductionSystemData")
    except Exception as e:
        print(f"✗ Error loading ProductionSystemData: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Verify locations after conversion
    print("\nVerifying locations after conversion:")
    resources_after_conv = production_system.resource_data
    sources_after_conv = production_system.source_data
    sinks_after_conv = production_system.sink_data
    
    locations_after_conv = []
    for r in resources_after_conv:
        if hasattr(r, 'location') and r.location:
            locations_after_conv.append(list(r.location) if hasattr(r.location, '__iter__') else r.location)
    for s in sources_after_conv:
        if hasattr(s, 'location') and s.location:
            locations_after_conv.append(list(s.location) if hasattr(s.location, '__iter__') else s.location)
    for sk in sinks_after_conv:
        if hasattr(sk, 'location') and sk.location:
            locations_after_conv.append(list(sk.location) if hasattr(sk.location, '__iter__') else sk.location)
    
    print(f"  Found {len(locations_after_conv)} locations after conversion")
    if not locations_after_conv:
        print("  ✗ WARNING: No locations found after conversion!")
    else:
        print(f"  ✓ Locations preserved: {locations_after_conv[:3]}...")  # Show first 3
    
    print()
    
    # Apply node link generation
    try:
        node_link_generation.generate_and_apply_network(production_system)
        production_system.write("updated.json")
        print("✓ Node link generation completed")
    except Exception as e:
        print(f"✗ Error during node link generation: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("--- AFTER NODE LINK GENERATION ---")
    print()
    
    # Analyze generated nodes
    all_nodes = production_system.node_data
    new_nodes = [n for n in all_nodes if n.ID not in existing_node_ids]
    existing_nodes_after = [n for n in all_nodes if n.ID in existing_node_ids]
    
    print(f"Total nodes: {len(all_nodes)}")
    print(f"  Existing nodes: {len(existing_nodes_after)}")
    print(f"  Newly generated nodes: {len(new_nodes)}")
    print()
    
    # Check all nodes
    problematic_nodes = []
    nodes_in_bounds = []
    nodes_out_of_bounds = []
    
    print("All Nodes AFTER generation:")
    for node in all_nodes:
        node_id = node.ID
        is_existing = node_id in existing_node_ids
        
        if not hasattr(node, 'location') or not node.location:
            status = "✗ MISSING LOCATION"
            problematic_nodes.append((node_id, "missing_location", None, is_existing))
        else:
            node_loc = list(node.location) if hasattr(node.location, '__iter__') else [node.location]
            if len(node_loc) < 2:
                status = "✗ INVALID LOCATION FORMAT"
                problematic_nodes.append((node_id, "invalid_format", node_loc, is_existing))
            else:
                x, y = node_loc[0], node_loc[1]
                in_bounds = is_within_bounds(node_loc, min_x, max_x, min_y, max_y, 
                                            margin=max(margin_x, margin_y))
                
                if in_bounds:
                    status = "✓"
                    nodes_in_bounds.append((node_id, node_loc, is_existing))
                else:
                    status = "✗ OUT OF BOUNDS"
                    nodes_out_of_bounds.append((node_id, node_loc, is_existing))
                    problematic_nodes.append((node_id, "out_of_bounds", node_loc, is_existing))
                
                print(f"  {status} {node_id}: [{x:8.3f}, {y:8.3f}] {'(existing)' if is_existing else '(generated)'}")
    
    print()
    print("--- ANALYSIS ---")
    print()
    
    print(f"Nodes within bounds: {len(nodes_in_bounds)}")
    print(f"Nodes out of bounds: {len(nodes_out_of_bounds)}")
    print(f"Problematic nodes: {len(problematic_nodes)}")
    print()
    
    if nodes_out_of_bounds:
        print("OUT OF BOUNDS NODES:")
        print(f"  Production system bounds: X: [{min_x:.3f}, {max_x:.3f}], Y: [{min_y:.3f}, {max_y:.3f}]")
        print()
        
        # Sort by distance from production system
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        nodes_with_dist = []
        for node_id, node_loc, is_existing in nodes_out_of_bounds:
            dist_from_center = distance(node_loc, [center_x, center_y])
            nodes_with_dist.append((node_id, node_loc, is_existing, dist_from_center))
        nodes_with_dist.sort(key=lambda x: x[3], reverse=True)  # Sort by distance, furthest first
        
        for node_id, node_loc, is_existing, dist_from_center in nodes_with_dist:
            x, y = node_loc[0], node_loc[1]
            status_label = "EXISTING (already bad)" if is_existing else "GENERATED (newly bad)"
            
            # Find nearest resource/source/sink
            nearest_resource, dist_r = find_nearest_element(node_loc, 
                [{"ID": r.ID, "location": list(r.location) if hasattr(r.location, '__iter__') else r.location} 
                 for r in resources_after_conv if hasattr(r, 'location') and r.location], "resource")
            nearest_source, dist_s = find_nearest_element(node_loc,
                [{"ID": s.ID, "location": list(s.location) if hasattr(s.location, '__iter__') else s.location} 
                 for s in sources_after_conv if hasattr(s, 'location') and s.location], "source")
            nearest_sink, dist_sk = find_nearest_element(node_loc,
                [{"ID": sk.ID, "location": list(sk.location) if hasattr(sk.location, '__iter__') else sk.location} 
                 for sk in sinks_after_conv if hasattr(sk, 'location') and sk.location], "sink")
            
            min_dist = min(dist_r, dist_s, dist_sk)
            nearest = None
            if min_dist == dist_r and nearest_resource:
                nearest = ("resource", nearest_resource['ID'], dist_r)
            elif min_dist == dist_s and nearest_source:
                nearest = ("source", nearest_source['ID'], dist_s)
            elif min_dist == dist_sk and nearest_sink:
                nearest = ("sink", nearest_sink['ID'], dist_sk)
            
            print(f"  ✗ {node_id} [{x:8.3f}, {y:8.3f}] - {status_label}")
            print(f"     Distance from production system center: {dist_from_center:.2f} units")
            if nearest:
                print(f"     Nearest production element: {nearest[0]} '{nearest[1]}' at {nearest[2]:.2f} units")
            
            # Calculate how far outside bounds
            if x < min_x - margin_x:
                print(f"     → {min_x - margin_x - x:.2f} units too far LEFT")
            elif x > max_x + margin_x:
                print(f"     → {x - (max_x + margin_x):.2f} units too far RIGHT")
            if y < min_y - margin_y:
                print(f"     → {min_y - margin_y - y:.2f} units too far DOWN")
            elif y > max_y + margin_y:
                print(f"     → {y - (max_y + margin_y):.2f} units too far UP")
            print()
    
    print()
    
    # Check node connections
    print("Checking node connections in LinkTransportProcesses:")
    link_processes = [
        p for p in production_system.process_data
        if hasattr(p, 'type') and 'LinkTransport' in str(p.type)
    ]
    
    print(f"  Found {len(link_processes)} LinkTransportProcess(es)")
    
    node_ids_in_links = set()
    resource_ids = {r.ID for r in resources_after_conv}
    source_ids = {s.ID for s in sources_after_conv}
    sink_ids = {sk.ID for sk in sinks_after_conv}
    all_node_ids = {n.ID for n in all_nodes}
    
    for process in link_processes:
        process_id = process.ID
        if hasattr(process, 'links') and process.links:
            links = process.links
            print(f"  Process '{process_id}': {len(links)} links")
            
            for link in links:
                if isinstance(link, (list, tuple)) and len(link) >= 2:
                    from_id, to_id = link[0], link[1]
                    node_ids_in_links.add(from_id)
                    node_ids_in_links.add(to_id)
    
    disconnected_nodes = all_node_ids - node_ids_in_links - resource_ids - source_ids - sink_ids
    
    if disconnected_nodes:
        print(f"\n  ⚠ WARNING: {len(disconnected_nodes)} nodes not connected to any links:")
        for node_id in sorted(disconnected_nodes):
            node = next((n for n in all_nodes if n.ID == node_id), None)
            if node and hasattr(node, 'location') and node.location:
                loc = list(node.location) if hasattr(node.location, '__iter__') else [node.location]
                if len(loc) >= 2:
                    print(f"    {node_id}: [{loc[0]:.3f}, {loc[1]:.3f}]")
    else:
        print("  ✓ All nodes are connected")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\nProduction System Location:")
    print(f"  X: [{min_x:.3f}, {max_x:.3f}] (range: {max_x - min_x:.3f})")
    print(f"  Y: [{min_y:.3f}, {max_y:.3f}] (range: {max_y - min_y:.3f})")
    print(f"  Center: [{(min_x+max_x)/2:.3f}, {(min_y+max_y)/2:.3f}]")
    
    print(f"\nNode Link Generation Results:")
    print(f"  Total nodes: {len(all_nodes)}")
    print(f"  Existing nodes (preserved): {len(existing_nodes_after)}")
    print(f"  Newly generated nodes: {len(new_nodes)}")
    print(f"  Nodes within bounds: {len(nodes_in_bounds)}")
    print(f"  Nodes out of bounds: {len(nodes_out_of_bounds)}")
    
    if problematic_nodes:
        existing_bad = [p for p in problematic_nodes if p[3]]
        generated_bad = [p for p in problematic_nodes if not p[3]]
        
        print(f"\n✗ PROBLEM IDENTIFIED:")
        print(f"  {len(problematic_nodes)} problematic nodes found!")
        
        if existing_bad:
            print(f"\n  {len(existing_bad)} EXISTING nodes are badly positioned:")
            print(f"    → These nodes were already in the JSON file with wrong coordinates")
            print(f"    → The node_link_generation algorithm KEPT them instead of fixing/replacing them")
            print(f"    → This suggests the algorithm preserves existing nodes without validation")
        
        if generated_bad:
            print(f"\n  {len(generated_bad)} NEWLY GENERATED nodes are badly positioned:")
            print(f"    → The algorithm created these nodes in wrong locations")
            print(f"    → This is a bug in the generation algorithm itself")
        
        print("\nROOT CAUSE ANALYSIS:")
        if existing_bad and len(generated_bad) == 0:
            print("  → node_link_generation.generate_and_apply_network() preserves existing nodes")
            print("  → It does NOT validate or fix existing node positions")
            print("  → It only generates NEW nodes, but keeps all existing ones as-is")
            print("  → Solution: Delete bad nodes before running generation, OR")
            print("             Fix the algorithm to validate/reposition existing nodes")
        elif generated_bad:
            print("  → The generation algorithm is placing nodes incorrectly")
            print("  → Possible causes:")
            print("     - Coordinate system mismatch (e.g., meters vs millimeters)")
            print("     - Algorithm using wrong reference points")
            print("     - Algorithm not using resource/source/sink locations correctly")
            print("     - Bug in the external prodsys library")
        
        print("\nRECOMMENDATIONS:")
        print("  1. CLEAR EXISTING BAD NODES before running generation:")
        print("     - Delete all nodes in node_data that are outside bounds")
        print("     - Or manually set them to locations near resources/sources/sinks")
        print("  2. FIX THE GENERATION ENDPOINT to:")
        print("     - Delete existing nodes before generation (if desired)")
        print("     - Or validate and fix/reject bad nodes after generation")
        print("  3. REPORT BUG to prodsys library:")
        print("     - node_link_generation should validate node positions")
        print("     - Or provide option to replace existing nodes")
        
    else:
        print("\n✓ No problematic nodes found!")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug node link generation")
    parser.add_argument("json_file", type=Path, help="Path to production system JSON file")
    
    args = parser.parse_args()
    
    if not args.json_file.exists():
        print(f"Error: File not found: {args.json_file}")
        sys.exit(1)
    
    analyze_node_link_generation(args.json_file)

