"""
Helper utility functions
"""
import os
import time

def create_directories(directories):
    """
    Create multiple directories if they don't exist
    
    Args:
        directories: List of directory paths to create
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensured directory exists: {directory}")

class Timer:
    """Simple timer class for measuring execution time"""
    
    def __init__(self, name="Operation"):
        """
        Initialize timer
        
        Args:
            name: Name of the operation being timed
        """
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        """Start the timer when entering a context"""
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Print elapsed time when exiting the context"""
        elapsed_time = time.time() - self.start_time
        print(f"{self.name} completed in {elapsed_time:.2f} seconds")
        
def print_graph_info(G):
    """
    Print information about a graph
    
    Args:
        G: NetworkX graph
    """
    print(f"Graph Info:")
    print(f"  Nodes: {len(G.nodes())}")
    print(f"  Edges: {len(G.edges())}")
    if len(G.nodes()) > 0:
        node = list(G.nodes())[0]
        print(f"  Sample node attributes: {G.nodes[node].keys()}")
    if len(G.edges()) > 0:
        edge = list(G.edges())[0]
        print(f"  Sample edge attributes: {G.edges[edge[0], edge[1], 0].keys()}") 