"""
Map-related utility functions
"""
import os

def create_google_maps_url(lat1, lon1, lat2, lon2):
    """
    Create a Google Maps URL for directions between two points
    
    Args:
        lat1, lon1: Coordinates of the start point
        lat2, lon2: Coordinates of the end point
        
    Returns:
        str: URL for Google Maps directions
    """
    return f"https://www.google.com/maps/dir/{lat1},{lon1}/{lat2},{lon2}"

def print_route_info(start_node, end_node, G, city_name, output_dir):
    """
    Print and save route information for Google Maps comparison
    
    Args:
        start_node: Starting node ID
        end_node: Destination node ID
        G: NetworkX graph
        city_name: Name of the city
        output_dir: Directory to save information
        
    Returns:
        tuple: (start_lat, start_lon, end_lat, end_lon)
    """
    # Get start and end coordinates
    start_lat = G.nodes[start_node]['y']
    start_lon = G.nodes[start_node]['x']
    end_lat = G.nodes[end_node]['y']
    end_lon = G.nodes[end_node]['x']
    
    # Create Google Maps URL
    google_maps_url = create_google_maps_url(start_lat, start_lon, end_lat, end_lon)
    
    # Print coordinates for Google Maps comparison
    print("\n===== ROUTE INFORMATION FOR GOOGLE MAPS COMPARISON =====")
    print(f"Start Location: {start_lat:.6f}, {start_lon:.6f}")
    print(f"End Location: {end_lat:.6f}, {end_lon:.6f}")
    print(f"Google Maps URL: {google_maps_url}")
    print("=======================================================\n")
    
    # Use a simplified city name for the file
    simple_city_name = city_name.split(',')[0].lower()
    
    # Save coordinates to a file for reference
    coords_file = os.path.join(output_dir, f"{simple_city_name}_coordinates.txt")
    with open(coords_file, 'w') as f:
        f.write(f"City: {city_name}\n")
        f.write(f"Start Node ID: {start_node}\n")
        f.write(f"End Node ID: {end_node}\n")
        f.write(f"Start Location: {start_lat:.6f}, {start_lon:.6f}\n")
        f.write(f"End Location: {end_lat:.6f}, {end_lon:.6f}\n")
        f.write(f"Google Maps URL: {google_maps_url}\n")
    
    return coords_file, (start_lat, start_lon, end_lat, end_lon)

def save_path_stats(coords_file, path, G):
    """
    Save path statistics to the coordinates file
    
    Args:
        coords_file: Path to the coordinates file
        path: List of nodes representing the path
        G: NetworkX graph
    """
    if not path:
        return
        
    with open(coords_file, 'a') as f:
        f.write(f"Path Length: {len(path)} nodes\n")
        # Calculate path distance if possible
        try:
            total_distance = 0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = G.get_edge_data(u, v)[0]
                total_distance += edge_data.get('length', 0)
            f.write(f"Approximate Path Distance: {total_distance/1000:.2f} km\n")
        except Exception:
            pass 