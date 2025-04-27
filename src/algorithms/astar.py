"""
A* Pathfinding Algorithm Implementation
"""
import heapq
import osmnx as ox
import time
import math
import numpy as np
from enum import Enum

class HeuristicType(Enum):
    """Available heuristics"""
    EUCLIDEAN = 1      # Straight-line distance (simplest)
    MANHATTAN = 2      # Sum of absolute differences (for grid-like street layouts)
    DIAGONAL = 3       # Allows diagonal movement (faster than Manhattan)
    HAVERSINE = 4      # Circle distance accounting for Earth's curvature
    CUSTOM = 5         # Custom function if needed

class UpdateType(Enum):
    """Type of update sent from algorithm thread to visualization thread"""
    VISITED_NODE = 1
    OPEN_SET = 2
    PATH_UPDATE = 3
    COMPLETE = 4
    PROGRESS = 5
    SAVE_GIF = 6

def calculate_heuristic(G, current, target, heuristic_type=HeuristicType.HAVERSINE, custom_heuristic=None):
    """
    Calculate heuristic cost from current node to target based on selected strategy
    
    Args:
        G: NetworkX graph
        current: Current node ID
        target: Target node ID
        heuristic_type: Type of heuristic to use
        custom_heuristic: Optional custom heuristic function
        
    Returns:
        Estimated cost from current to target
    """
    current_y, current_x = G.nodes[current]['y'], G.nodes[current]['x']
    target_y, target_x = G.nodes[target]['y'], G.nodes[target]['x']
    
    if heuristic_type == HeuristicType.EUCLIDEAN:
        # Simple straight-line distance (not accounting for Earth's curvature)
        # Less accurate for large distances but computationally efficient
        return math.sqrt((target_y - current_y)**2 + (target_x - current_x)**2) * 111000  # approx meters
        
    elif heuristic_type == HeuristicType.MANHATTAN:
        # Sum of absolute differences (better for grid-like street networks)
        return (abs(target_y - current_y) + abs(target_x - current_x)) * 111000  # approx meters
        
    elif heuristic_type == HeuristicType.DIAGONAL:
        # Allows diagonal movement (faster than Manhattan)
        dx = abs(target_x - current_x)
        dy = abs(target_y - current_y)
        return max(dx, dy) * 111000  # approx meters
        
    elif heuristic_type == HeuristicType.HAVERSINE:
        # Great circle distance (accounts for Earth's curvature)
        # Most accurate for geographic routing
        return ox.distance.great_circle(current_y, current_x, target_y, target_x)
        
    elif heuristic_type == HeuristicType.CUSTOM and custom_heuristic:
        # Use provided custom heuristic function
        return custom_heuristic(G, current, target)
        
    # Default to Haversine distance if type not recognized or custom function not provided
    return ox.distance.great_circle(current_y, current_x, target_y, target_x)

def a_star_realtime(G, start_node, end_node, update_queue, stop_event, weight='travel_time', heuristic_type=HeuristicType.HAVERSINE,
                   custom_heuristic=None):
    """
    A* pathfinding algorithm implementation with multiple heuristic options.
    
    Args:
        G: NetworkX graph
        start_node: Starting node ID
        end_node: Destination node ID
        update_queue: Queue to send updates to visualization thread
        stop_event: Threading event to signal algorithm to stop
        weight: Edge weight attribute to use (default: 'travel_time')
        heuristic_type: Type of heuristic to use for estimating remaining cost
        custom_heuristic: Custom heuristic function (if heuristic_type is CUSTOM)
        
    The function will put updates into the queue in the format:
    (UpdateType.XXXX, data) where data depends on the update type.
    """
    # Hardcoded visualization parameters
    update_interval = 5
    node_delay = 0.02    
    batch_size = 5       
    target_runtime = 8.0 
    
    # Estimate the number of nodes we'll explore based on straight-line distance
    start_y, start_x = G.nodes[start_node]['y'], G.nodes[start_node]['x']
    end_y, end_x = G.nodes[end_node]['y'], G.nodes[end_node]['x']
    
    # Calculate the direct distance between points
    h_distance = ox.distance.great_circle(start_y, start_x, end_y, end_x)
    
    # Estimate nodes to explore based on distance and graph density
    estimated_nodes = min(
        3000,  # Cap to avoid excessive delays on short paths
        max(
            300,  # Minimum nodes to ensure smooth visualization
            int(h_distance * 5)  # Scale factor based on distance
        )
    )
    
    # Calculate adaptive delay for target runtime
    batches = math.ceil(estimated_nodes / batch_size)
    adaptive_delay = target_runtime / batches if batches > 0 else node_delay
    
    # Use the adaptive delay, but cap it to prevent extreme values
    node_delay = min(max(adaptive_delay, 0.001), 0.1)  # Reduced max delay
    
    # Track the nodes in the open set (frontier)
    open_set_nodes = set([start_node])
    
    # Priority queue with (f_score, node_counter, node_id)
    node_sequence = 0
    open_set = [(0, node_sequence, start_node)]
    heapq.heapify(open_set)
    
    # Cost from start to current node
    g_score = {node: float('inf') for node in G.nodes()}
    g_score[start_node] = 0
    
    # Estimated total cost
    f_score = {node: float('inf') for node in G.nodes()}
    
    # Initial f_score estimate
    initial_h = calculate_heuristic(G, start_node, end_node, heuristic_type, custom_heuristic)
    f_score[start_node] = initial_h
    
    # To reconstruct path
    came_from = {}
    
    # Local visited nodes list
    local_visited = []
    
    # Main search loop
    found_path = None
    node_counter = 0
    batch_counter = 0
    batch_nodes = []
    current_path = []
    start_time = time.time()
    
    # Log starting parameters
    print(f"Starting A* with {heuristic_type.name} heuristic")
    
    # Add the start node to visited nodes
    local_visited.append(start_node)
    batch_nodes.append(start_node)
    
    while open_set and not stop_event.is_set():
        # Process a batch of nodes
        batch_counter += 1
        batch_start_time = time.time()
        
        # Process up to batch_size nodes at once
        for _ in range(min(batch_size, len(open_set))):
            if not open_set or stop_event.is_set():
                break
                
            # Get node with lowest f_score
            _, _, current_node = heapq.heappop(open_set)
            if current_node in open_set_nodes:
                open_set_nodes.remove(current_node)
            else:
                continue  # This node was already processed
            
            # Add to visited nodes
            local_visited.append(current_node)
            batch_nodes.append(current_node)
            node_counter += 1
            
            # Send progress update sparingly (reduced frequency for better performance)
            if node_counter % 100 == 0:
                progress = min(100, (node_counter / estimated_nodes * 100)) if estimated_nodes > 0 else 0
                update_queue.put((UpdateType.PROGRESS, progress))
            
            # Check if we reached the target
            if current_node == end_node:
                # Reconstruct path
                found_path = [current_node]
                while current_node in came_from:
                    current_node = came_from[current_node]
                    found_path.append(current_node)
                found_path.reverse()
                break
            
            # Update current best path if needed and not too costly
            if current_node != start_node and node_counter % 10 == 0:  # Reduced frequency
                # Build the current best path to the current node
                current_path = [current_node]
                temp_node = current_node
                while temp_node in came_from:
                    temp_node = came_from[temp_node]
                    current_path.append(temp_node)
                current_path.reverse()
            
            # Explore neighbors
            for neighbor in G.neighbors(current_node):
                if stop_event.is_set():
                    break
                    
                # Skip already visited nodes for performance
                if neighbor in local_visited:
                    continue
                
                # Calculate basic edge cost from graph
                edge_cost = G[current_node][neighbor][0].get(weight, 1.0)
                
                # Calculate tentative g_score
                tentative_g = g_score[current_node] + edge_cost
                
                if tentative_g < g_score[neighbor]:
                    # This path is better
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g
                    
                    # Calculate heuristic using the selected method
                    h = calculate_heuristic(G, neighbor, end_node, heuristic_type, custom_heuristic)
                    
                    # Calculate f_score (g + h)
                    f_score[neighbor] = tentative_g + h
                    
                    # Add to open set if not already there
                    if neighbor not in open_set_nodes:
                        node_sequence += 1
                        heapq.heappush(open_set, (f_score[neighbor], node_sequence, neighbor))
                        open_set_nodes.add(neighbor)
        
        # Send the batch updates to the visualization less frequently
        if batch_nodes and batch_counter % 2 == 0:  # Reduced frequency
            # Send all visited nodes in this batch as one update
            update_queue.put((UpdateType.VISITED_NODE, batch_nodes.copy()))
            batch_nodes.clear()
            
            # Update current best path
            if current_path:
                update_queue.put((UpdateType.PATH_UPDATE, current_path))
            
            # Send open set updates periodically
            if batch_counter % update_interval == 0:
                update_queue.put((UpdateType.OPEN_SET, list(open_set_nodes)))
        
        # If we found a path, break out of the loop
        if found_path:
            break

        # Apply a small delay for visualization
        batch_elapsed = time.time() - batch_start_time
        if batch_elapsed < node_delay:
            time.sleep(node_delay - batch_elapsed)
    
    # Log final timing info
    elapsed = time.time() - start_time
    print(f"A* processing completed in {elapsed:.2f}s, visited {len(local_visited)} nodes")
    
    # Calculate route statistics if a path was found
    if found_path:
        # Calculate total distance and estimated time
        total_distance = 0
        total_time = 0
        
        for i in range(len(found_path) - 1):
            u, v = found_path[i], found_path[i + 1]
            if u in G and v in G[u]:
                edge_data = G[u][v][0]
                total_distance += edge_data.get('length', 0)
                total_time += edge_data.get('travel_time', 0)
        
        print(f"Route statistics: {len(found_path)} nodes, {total_distance:.2f}m, {total_time:.2f}s")
        
        # Send the final update including a signal to save animation as GIF
        update_queue.put((UpdateType.COMPLETE, (found_path, local_visited, {
            'distance': total_distance,
            'time': total_time,
            'nodes': len(found_path),
            'save_gif': True  # Flag to indicate we want to save a GIF
        })))
        
        # Request the visualization thread to save the animation as a GIF
        gif_filename = f"astar_{heuristic_type.name.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.gif"
        update_queue.put((UpdateType.SAVE_GIF, gif_filename))
        
    elif not stop_event.is_set():
        update_queue.put((UpdateType.COMPLETE, ([], local_visited, {
            'distance': 0,
            'time': 0,
            'nodes': 0
        })))
        
    return found_path 