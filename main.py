#!/usr/bin/env python3
"""
A* Pathfinding Visualization - Main Script
"""
import argparse
import sys
from src.data.graph import get_city_graph, get_diverse_nodes
from src.visualization.map_viz import visualize_realtime_search
from src.utils.helpers import Timer, create_directories, print_graph_info

# City presets with full names for easy selection
CITY_PRESETS = {
    "baku": "Baku, Azerbaijan",
    "seattle": "Seattle, Washington, USA",
    "tokyo": "Tokyo, Japan",
    "london": "London, United Kingdom",
    "seoul": "Seoul, South Korea",
    "nyc": "New York City, New York, USA",
}

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='A* Pathfinding Visualization')
    
    # City selection options - either preset or full name
    city_group = parser.add_mutually_exclusive_group()
    city_group.add_argument('--preset', type=str, choices=list(CITY_PRESETS.keys()), 
                      help=f'Use a preset city: {", ".join(CITY_PRESETS.keys())}')
    city_group.add_argument('--city', type=str, default='Seattle, Washington, USA',
                        help='Custom city to visualize (default: Seattle, Washington, USA)')
    
    # Other arguments
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to save output (default: output)')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory to store cached data (default: data)')
    parser.add_argument('--no-display', action='store_true',
                        help='Do not display the visualization')
    parser.add_argument('--no-save', action='store_true',
                        help='Do not save the final result')
    parser.add_argument('--delay', type=float, default=0.05,
                        help='Delay between processing nodes (seconds, default: 0.05)')
    parser.add_argument('--batch-size', type=int, default=20,
                        help='Number of nodes to process in each batch (default: 20)')
    parser.add_argument('--runtime', type=float, default=12.0,
                        help='Target runtime for visualization in seconds (default: 12.0)')
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_args()
    
    # Determine which city to use
    if args.preset:
        city_name = CITY_PRESETS[args.preset]
    else:
        city_name = args.city
    
    # Create necessary directories
    create_directories([args.output_dir, args.data_dir])
    
    # Get city graph with error handling
    try:
        with Timer(f"Loading graph for {city_name}"):
            G = get_city_graph(city_name, cache_dir=args.data_dir)
        print_graph_info(G)
    except Exception as e:
        print(f"Error loading graph for {city_name}: {e}")
        if args.preset:
            print("Try using a different preset city or a custom city name.")
            print(f"Available presets: {', '.join(CITY_PRESETS.keys())}")
        sys.exit(1)
    
    # Pick start and end nodes for a more interesting path
    start_node, end_node = get_diverse_nodes(G)
    print(f"Path from node {start_node} to {end_node}")
    
    # Visualize the A* search in real-time
    with Timer("A* visualization"):
        try:
            path, visited_nodes = visualize_realtime_search(
                G, start_node, end_node, 
                weight='travel_time',
                city_name=city_name,
                output_dir=args.output_dir,
                save_result=not args.no_save,
                node_delay=args.delay,
                batch_size=args.batch_size,
                target_runtime=args.runtime
            )
            if path:
                print(f"Path found with {len(path)} nodes")
                print(f"Visited {len(visited_nodes)} nodes during search")
            else:
                print("No path found.")
        except Exception as e:
            print(f"Error during visualization: {e}")
    
    print(f"Visualization complete. Images saved to {args.output_dir}")

if __name__ == "__main__":
    main() 