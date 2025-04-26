"""
Graph data handling functionality
"""
import os
import pickle
import osmnx as ox
import numpy as np

# Configure OSMnx
ox.settings.use_cache = True
ox.settings.log_console = True

def get_city_graph(city_name, cache_dir="data"):
    """
    Download or load cached street networks for a city
    
    Args:
        city_name: Name of the city to get graph for
        cache_dir: Directory to store cached data
        
    Returns:
        NetworkX graph representing the city's street network
    """
    # Make sure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)
    
    # Get a simplified city name for the cache file to avoid formatting issues
    simple_city_name = city_name.split(',')[0].lower()
    
    # Create cache file path
    cache_file = os.path.join(cache_dir, f"{simple_city_name}_graph.pkl")
    
    # Try to load from cache first
    if os.path.exists(cache_file):
        print(f"Loading {city_name} from cache...")
        try:
            with open(cache_file, 'rb') as f:
                G = pickle.load(f)
            print(f"Loaded graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
            return G
        except Exception as e:
            print(f"Error loading cache: {e}")
    
    # Download if not cached
    print(f"Downloading {city_name} street network...")
    G = ox.graph_from_place(city_name, network_type='drive')
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    
    # Save to cache
    print(f"Saving network to cache...")
    with open(cache_file, 'wb') as f:
        pickle.dump(G, f)
    
    return G

def get_diverse_nodes(G, distance_factor=0.015):
    """
    Find diverse nodes in different parts of a graph for better path visualization
    
    Args:
        G: NetworkX graph
        distance_factor: How far from center to look for nodes
        
    Returns:
        tuple: (start_node, end_node) suggested nodes for path calculation
    """
    all_nodes = list(G.nodes())
    
    # Try to pick nodes that are reasonably far apart
    # Get centroid of graph
    center_y = np.mean([data['y'] for _, data in G.nodes(data=True)])
    center_x = np.mean([data['x'] for _, data in G.nodes(data=True)])
    
    # Find a node in northwest part
    northwest_nodes = []
    for node, data in G.nodes(data=True):
        if data['y'] > center_y + distance_factor and data['x'] < center_x - distance_factor:
            northwest_nodes.append(node)
    
    # Find a node in southeast part
    southeast_nodes = []
    for node, data in G.nodes(data=True):
        if data['y'] < center_y - distance_factor and data['x'] > center_x + distance_factor:
            southeast_nodes.append(node)
    
    if northwest_nodes and southeast_nodes:
        start_node = northwest_nodes[len(northwest_nodes)//3]  
        end_node = southeast_nodes[len(southeast_nodes)//3]  
    else:
        # Fallback if we couldn't find good nodes
        start_node = all_nodes[len(all_nodes)//4]
        end_node = all_nodes[3*len(all_nodes)//4]
    
    return start_node, end_node 