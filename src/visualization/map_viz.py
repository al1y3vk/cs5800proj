"""
Map visualization functionality
"""
import os
import time
import matplotlib.pyplot as plt

from src.utils.map_utils import print_route_info, save_path_stats
from src.algorithms.astar import a_star_realtime, UpdateType
from src.visualization.visualization_state import VisualizationState, AlgorithmRunner
from src.visualization.map_renderer import AStarMapRenderer

def visualize_realtime_search(G, start_node, end_node, weight='travel_time', city_name="City", 
                         output_dir="output", save_result=True, node_delay=0.05, batch_size=20, 
                         target_runtime=12.0):
    """
    Visualize the A* search algorithm in real-time as it explores the graph
    
    Args:
        G: NetworkX graph representing the street network
        start_node: Starting node ID
        end_node: Destination node ID
        weight: Edge weight attribute to use (default: 'travel_time')
        city_name: Name of the city for the title
        output_dir: Directory to save the output
        save_result: Whether to save the final result image
        node_delay: Delay between processing nodes (controls animation speed)
        batch_size: Number of nodes to process in a batch before delaying
        target_runtime: Target runtime for visualization in seconds
        
    Returns:
        tuple: (path, visited_nodes) - the path found and nodes visited during search
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Use the original city name for display
    display_city_name = city_name.split(',')[0]
    
    # Get route information for Google Maps comparison
    coords_file, _ = print_route_info(start_node, end_node, G, city_name, output_dir)
    
    # Initialize renderer
    renderer = AStarMapRenderer(G)
    renderer.setup(f"A* Search in {display_city_name}")
    renderer.render_base_map()
    renderer.render_start_end(start_node, end_node)
    renderer.show(block=False)
    
    # Initialize visualization state
    vis_state = VisualizationState()
    vis_state.update_interval = 0.1  # Update screen at most this many times per second
    
    # Set up the algorithm runner
    algorithm_args = (G, start_node, end_node, weight, node_delay, batch_size)
    runner = AlgorithmRunner(a_star_realtime, algorithm_args)
    
    # Start the algorithm
    runner.start()
    
    # Main visualization loop - process updates from the algorithm thread
    try:
        while runner.is_alive() or runner.has_updates():
            # Get next update if available
            update = runner.get_update()
            
            if update is not None:
                update_type, update_data = update
                vis_state.update_from_algorithm(update_type, update_data)
            
            # Check if we should update the display
            if update is not None and vis_state.should_update_display():
                # Clear previous rendering but keep base map
                renderer.clear(keep_base=True)
                
                # Draw visited nodes with color gradient
                renderer.render_visited_nodes(vis_state.visited_nodes)
                
                # Draw current frontier (open set)
                renderer.render_frontier(vis_state.current_open_set, vis_state.visited_nodes)
                
                # Highlight current node if we have one
                if not vis_state.completed and vis_state.visited_nodes:
                    current_node = vis_state.visited_nodes[-1]
                    renderer.render_current_node(current_node)
                
                # Always redraw start and end points
                renderer.render_start_end(start_node, end_node)
                
                # Draw the current best path
                if len(vis_state.current_best_path) > 1:
                    renderer.render_path(vis_state.current_best_path, color='blue')
                
                # If completed, draw the final path
                if vis_state.completed and vis_state.final_path:
                    renderer.render_path(
                        vis_state.final_path, 
                        color='green', 
                        width=3, 
                        alpha=1.0, 
                        zorder=5
                    )
                
                # Update the title
                if vis_state.completed:
                    if vis_state.final_path:
                        renderer.update_title(
                            f"A* Search Complete in {display_city_name} - "
                            f"Path found with {len(vis_state.final_path)} nodes"
                        )
                    else:
                        renderer.update_title(
                            f"A* Search in {display_city_name} - No path found"
                        )
                else:
                    renderer.update_title(
                        f"A* Search in {display_city_name} - "
                        f"Nodes explored: {len(vis_state.visited_nodes)}"
                    )
                
                # Update legend
                renderer.update_legend(has_path=vis_state.completed and vis_state.final_path)
                
                # Refresh the display
                renderer.show(block=False)
            
            # Handle completed state if needed
            if vis_state.completed and vis_state.final_path and save_result:
                # Use a simplified city name for the file
                simple_city_name = city_name.split(',')[0].lower()
                save_name = f"{simple_city_name}_astar_realtime.png"
                save_path = os.path.join(output_dir, save_name)
                renderer.save(save_path)
                print(f"Saved final result to {save_path}")
                
                # Update coordinates file with path statistics
                save_path_stats(coords_file, vis_state.final_path, G)
                
                # We only need to save once
                save_result = False
                
            # Brief pause to avoid hogging the CPU
            if not update:
                time.sleep(0.01)
        
        # Wait for user to close the window
        renderer.show(block=True)
        
    except KeyboardInterrupt:
        print("Visualization interrupted by user.")
    finally:
        # Ensure we clean up the algorithm thread
        runner.stop()
    
    return vis_state.final_path, vis_state.visited_nodes 