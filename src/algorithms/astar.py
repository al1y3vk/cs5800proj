"""
A* Pathfinding Algorithm Implementation
"""
import heapq
import osmnx as ox
import time
import math
from enum import Enum

class UpdateType(Enum):
    """Type of update sent from algorithm thread to visualization thread"""
    VISITED_NODE = 1
    OPEN_SET = 2
    PATH_UPDATE = 3
    COMPLETE = 4

def a_star_realtime(G, start_node, end_node, update_queue, stop_event, weight='travel_time', 
                    update_interval=5, node_delay=0.05, batch_size=1, target_runtime=12.0):
    """
    A* pathfinding algorithm implementation that supports real-time visualization updates.
    
    Args:
        G: NetworkX graph
        start_node: Starting node ID
        end_node: Destination node ID
        update_queue: Queue to send updates to visualization thread
        stop_event: Threading event to signal algorithm to stop
        weight: Edge weight attribute to use (default: 'travel_time')
        update_interval: How often to send open set updates (in nodes visited)
        node_delay: Delay in seconds between processing nodes (slower = more visible animation)
        batch_size: Number of nodes to process in a batch before delaying
        target_runtime: Target visualization runtime in seconds (default: 12.0)
        
    The function will put updates into the queue in the format:
    (UpdateType.XXXX, data) where data depends on the update type.
    """
    # Estimate the number of nodes we'll explore based on straight-line distance
    # and graph density to adjust our timing
    start_y, start_x = G.nodes[start_node]['y'], G.nodes[start_node]['x']
    end_y, end_x = G.nodes[end_node]['y'], G.nodes[end_node]['x']
    
    # Calculate the direct distance between points
    h_distance = ox.distance.great_circle(start_y, start_x, end_y, end_x)
    
    # Estimate nodes to explore based on distance and graph density
    # This is a heuristic that can be adjusted
    estimated_nodes = min(
        3000,  # Cap to avoid excessive delays on short paths
        max(
            300,  # Minimum nodes to ensure smooth visualization
            int(h_distance * 5)  # Scale factor based on distance
        )
    )
    
    # Calculate adaptive delay for target runtime
    # We'll explore approximately estimated_nodes/batch_size batches
    batches = math.ceil(estimated_nodes / batch_size)
    adaptive_delay = target_runtime / batches if batches > 0 else node_delay
    
    # Use the adaptive delay, but cap it to prevent extreme values
    node_delay = min(max(adaptive_delay, 0.001), 0.2)
    
    # Track the nodes in the open set (frontier)
    open_set_nodes = set([start_node])
    
    # Priority queue with (f_score, node_id)
    open_set = [(0, start_node)]
    
    # Cost from start to current node
    g_score = {node: float('inf') for node in G.nodes()}
    g_score[start_node] = 0
    
    # Estimated total cost
    f_score = {node: float('inf') for node in G.nodes()}
    
    # Initial f_score estimate using straight-line distance
    h = ox.distance.great_circle(start_y, start_x, end_y, end_x)
    f_score[start_node] = h
    
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
    print(f"Estimated nodes: {estimated_nodes}, Adaptive delay: {node_delay:.4f}s, Batch size: {batch_size}")
    
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
            current_f, current_node = open_set.pop(0)
            open_set_nodes.remove(current_node)
            
            # Add to visited nodes
            local_visited.append(current_node)
            batch_nodes.append(current_node)
            node_counter += 1
            
            # Check if we reached the target
        if current_node == end_node:
            # Reconstruct path
                found_path = [current_node]
            while current_node in came_from:
                current_node = came_from[current_node]
                    found_path.append(current_node)
                found_path.reverse()
                break
            
            # Update current best path if needed
            if current_node != start_node:
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
                    
            # Calculate tentative g_score
            tentative_g = g_score[current_node] + G[current_node][neighbor][0][weight]
            
            if tentative_g < g_score[neighbor]:
                # This path is better
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g
                
                # Heuristic calculation (straight-line distance)
                neighbor_y, neighbor_x = G.nodes[neighbor]['y'], G.nodes[neighbor]['x']
                h = ox.distance.great_circle(neighbor_y, neighbor_x, end_y, end_x)
                f_score[neighbor] = tentative_g + h
                
                # Add to open set if not already there
                    if neighbor not in open_set_nodes:
                        # Find the right position to insert based on f_score (to maintain sorted order)
                        insert_idx = 0
                        for idx, (f, _) in enumerate(open_set):
                            if f_score[neighbor] < f:
                                insert_idx = idx
                                break
                            else:
                                insert_idx = idx + 1
                        
                        open_set.insert(insert_idx, (f_score[neighbor], neighbor))
                        open_set_nodes.add(neighbor)
        
        # Send the batch updates to the visualization
        if batch_nodes:
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
            
        # Dynamic delay between batches
        elapsed = time.time() - start_time
        processed_ratio = node_counter / estimated_nodes if estimated_nodes > 0 else 0
        
        # Adjust delay if we have enough data and if we're not at the end
        if 0.1 <= processed_ratio <= 0.9:
            time_ratio = elapsed / (target_runtime * processed_ratio)
            if time_ratio < 0.8:  # Too fast
                node_delay *= 1.05  # Increase delay by 5%
            elif time_ratio > 1.2:  # Too slow
                node_delay *= 0.95  # Decrease delay by 5%
            # Cap the delay
            node_delay = min(max(node_delay, 0.001), 0.2)
        
        # Apply the delay between batches
        batch_elapsed = time.time() - batch_start_time
        if batch_elapsed < node_delay:
            time.sleep(node_delay - batch_elapsed)
    
    # Log final timing info
    elapsed = time.time() - start_time
    print(f"A* processing completed in {elapsed:.2f}s, visited {len(local_visited)} nodes")
    
    # Send the final update
    if found_path:
        update_queue.put((UpdateType.COMPLETE, (found_path, local_visited)))
    elif not stop_event.is_set():
        update_queue.put((UpdateType.COMPLETE, ([], local_visited))) 