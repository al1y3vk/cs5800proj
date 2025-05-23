"""
Visualization state and data processing

This module contains classes for managing the state of visualizations and processing data
for rendering.
"""
import time
import threading
import queue
from enum import Enum
from src.algorithms.astar import UpdateType


class VisualizationState:
    """
    Class to manage the state for real-time visualization
    """
    
    def __init__(self):
        """Initialize visualization state"""
        # Algorithm state
        self.visited_nodes = []
        self.current_open_set = set()
        self.current_best_path = []
        self.final_path = None
        self.completed = False
        self.save_gif_requested = False
        self.gif_filename = None
        
        # Drawing state
        self.last_update_time = time.time()
        self.update_interval = 0.1  # seconds
        
    def should_update_display(self, force=False):
        """
        Check if the display should be updated based on time interval
        
        Args:
            force: If True, always return True
            
        Returns:
            bool: Whether to update the display
        """
        if force or self.completed:
            return True
            
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            self.last_update_time = current_time
            return True
        return False
        
    def update_from_algorithm(self, update_type, update_data):
        """
        Update state based on algorithm update
        
        Args:
            update_type: The type of update (from UpdateType enum)
            update_data: The data associated with the update
        """
        if update_type == UpdateType.VISITED_NODE:
            # Handle both single node and batch updates
            if isinstance(update_data, list):
                # Batch update
                self.visited_nodes.extend(update_data)
            else:
                # Single node update (for backward compatibility)
                self.visited_nodes.append(update_data)
            
        elif update_type == UpdateType.OPEN_SET:
            self.current_open_set = set(update_data)
            
        elif update_type == UpdateType.PATH_UPDATE:
            self.current_best_path = update_data
            
        elif update_type == UpdateType.COMPLETE:
            if len(update_data) == 2:
                # Backward compatibility with older versions
                self.final_path, full_visited = update_data
                self.stats = {}
            else:
                # New version with statistics
                self.final_path, full_visited, self.stats = update_data
                
            self.completed = True
            # Make sure we have all visited nodes
            if len(full_visited) > len(self.visited_nodes):
                self.visited_nodes = full_visited
                
            # Check if we should save GIF
            if self.stats and self.stats.get('save_gif', False):
                self.save_gif_requested = True
        
        elif update_type == UpdateType.PROGRESS:
            # Progress updates are handled by the visualization
            pass
            
        elif update_type == UpdateType.SAVE_GIF:
            # Request to save a GIF
            self.save_gif_requested = True
            self.gif_filename = update_data


class AlgorithmRunner:
    """
    Class to manage running algorithm in background thread
    """
    
    def __init__(self, algorithm_func, algorithm_args):
        """
        Initialize with algorithm function and its arguments
        
        Args:
            algorithm_func: Function to run in background
            algorithm_args: Arguments to pass to the function
        """
        self.algorithm_func = algorithm_func
        self.algorithm_args = algorithm_args
        self.update_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = None
        
    def start(self):
        """Start the algorithm thread"""
        if self.thread is not None and self.thread.is_alive():
            return
            
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop the algorithm thread"""
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            
    def _run(self):
        """Run the algorithm function with arguments"""
        # Get the base arguments
        G, start_node, end_node, weight = self.algorithm_args[:4]
        
        if len(self.algorithm_args) >= 6:
            # Call with updated parameters
            self.algorithm_func(
                G, start_node, end_node, 
                self.update_queue, self.stop_event, 
                weight, 
                heuristic_type=self.algorithm_args[4] if len(self.algorithm_args) > 4 else None,
                custom_heuristic=self.algorithm_args[5] if len(self.algorithm_args) > 5 else None
            )
        else:
            # Backwards compatibility - use defaults
            self.algorithm_func(G, start_node, end_node, self.update_queue, self.stop_event, weight)
                           
    def get_update(self, timeout=0.05):
        """
        Get an update from the algorithm if available
        
        Args:
            timeout: How long to wait for an update
            
        Returns:
            tuple or None: (update_type, update_data) if available, None otherwise
        """
        try:
            return self.update_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def is_alive(self):
        """Check if the algorithm thread is still running"""
        return self.thread is not None and self.thread.is_alive()
        
    def has_updates(self):
        """Check if there are updates in the queue"""
        return not self.update_queue.empty() 