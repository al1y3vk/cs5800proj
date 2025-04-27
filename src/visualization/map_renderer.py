"""
Map rendering component

This module provides classes for rendering maps and visualizations
"""
import matplotlib.pyplot as plt
import osmnx as ox
from src.utils.visualization_utils import (
    setup_map_figure, draw_nodes, draw_edge_path, clear_collections_and_lines
)

class MapRenderer:
    """Base class for map rendering"""
    
    def __init__(self, G, figsize=(12, 10)):
        """
        Initialize with graph
        
        Args:
            G: NetworkX graph
            figsize: Figure size
        """
        self.G = G
        self.figsize = figsize
        self.fig = None
        self.ax = None
        self.nodes, self.edges = ox.graph_to_gdfs(G)
        
    def setup(self, title):
        """
        Setup the figure for rendering
        
        Args:
            title: Title for the figure
            
        Returns:
            self for method chaining
        """
        self.fig, self.ax = setup_map_figure(title, self.figsize)
        return self
        
    def render_base_map(self):
        """
        Render the base map (street network)
        
        Returns:
            self for method chaining
        """
        self.edges.plot(ax=self.ax, linewidth=0.5, color='gray', alpha=0.5)
        return self
        
    def clear(self, keep_base=True):
        """
        Clear all rendered elements except the base map
        
        Args:
            keep_base: Whether to keep the base map
            
        Returns:
            self for method chaining
        """
        if keep_base and self.ax.collections:
            keep_collections = [self.ax.collections[0]]
        else:
            keep_collections = []
            
        clear_collections_and_lines(self.ax, keep_collections)
        return self
        
    def show(self, block=True):
        """
        Show the figure
        
        Args:
            block: Whether to block execution until figure is closed
            
        Returns:
            self for method chaining
        """
        plt.ion()
        self.fig.canvas.draw()
        
        if block:
            plt.ioff()
            plt.show(block=True)
        else:
            plt.pause(0.001)
            
        return self
        
    def save(self, filepath, dpi=300):
        """
        Save the figure to a file
        
        Args:
            filepath: Path to save the figure
            dpi: Resolution
            
        Returns:
            self for method chaining
        """
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        return self


class AStarMapRenderer(MapRenderer):
    """Map renderer specialized for A* algorithm visualization"""
    
    def __init__(self, G, figsize=(12, 10)):
        """Initialize with graph"""
        super().__init__(G, figsize)
        self.colormap = plt.cm.plasma
        
    def render_visited_nodes(self, visited_nodes):
        """
        Render visited nodes with color gradient
        
        Args:
            visited_nodes: List of visited node IDs
            
        Returns:
            self for method chaining
        """
        draw_nodes(
            self.ax, self.nodes, visited_nodes,
            size=20, alpha=0.7, zorder=2, colormap=self.colormap
        )
        return self
        
    def render_frontier(self, open_set, visited_nodes):
        """
        Render frontier nodes (open set)
        
        Args:
            open_set: Set of nodes in the frontier
            visited_nodes: List of already visited nodes
            
        Returns:
            self for method chaining
        """
        frontier_nodes = [n for n in open_set if n not in visited_nodes]
        draw_nodes(
            self.ax, self.nodes, frontier_nodes,
            size=20, color='cyan', alpha=0.5, zorder=1
        )
        return self
        
    def render_current_node(self, node_id):
        """
        Highlight current node being processed
        
        Args:
            node_id: ID of the current node
            
        Returns:
            self for method chaining
        """
        draw_nodes(
            self.ax, self.nodes, [node_id],
            size=100, color='yellow', alpha=1.0, zorder=3
        )
        return self
        
    def zoom_to_area_of_interest(self, nodes_of_interest, buffer_factor=0.2):
        """
        Zoom the map to focus on the area containing the nodes of interest
        
        Args:
            nodes_of_interest: List of node IDs to focus on
            buffer_factor: Amount of buffer space around the nodes (0.2 = 20% extra space)
            
        Returns:
            self for method chaining
        """
        if not nodes_of_interest or len(nodes_of_interest) == 0:
            return self
            
        # Get coordinates for the nodes of interest
        points = self.nodes.loc[nodes_of_interest]
        
        # Get bounds
        min_x, min_y = points.x.min(), points.y.min()
        max_x, max_y = points.x.max(), points.y.max()
        
        # Calculate the width and height of the bounding box
        width = max_x - min_x
        height = max_y - min_y
        
        # Apply buffer - increase the area by the buffer factor
        buffer_x = width * buffer_factor
        buffer_y = height * buffer_factor
        
        # Set the axis limits with the buffer
        self.ax.set_xlim(min_x - buffer_x, max_x + buffer_x)
        self.ax.set_ylim(min_y - buffer_y, max_y + buffer_y)
        
        return self
        
    def render_start_end(self, start_node, end_node):
        """
        Render start and end nodes
        
        Args:
            start_node: Start node ID
            end_node: End node ID
            
        Returns:
            self for method chaining
        """
        draw_nodes(
            self.ax, self.nodes, [start_node],
            size=150, color='green', alpha=1.0, zorder=4
        )
        draw_nodes(
            self.ax, self.nodes, [end_node],
            size=150, color='red', alpha=1.0, zorder=4
        )
        
        # Zoom to the area containing start and end points
        self.zoom_to_area_of_interest([start_node, end_node], buffer_factor=0.3)
        
        return self
        
    def render_path(self, path, color='blue', width=2, alpha=0.7, zorder=3):
        """
        Render a path
        
        Args:
            path: List of node IDs forming the path
            color: Path color
            width: Line width
            alpha: Transparency
            zorder: Z-order for drawing
            
        Returns:
            self for method chaining
        """
        if len(path) > 1:
            draw_edge_path(
                self.ax, self.G, self.nodes, path,
                color=color, width=width, alpha=alpha, zorder=zorder
            )
        return self
        
    def update_title(self, title):
        """
        Update the figure title
        
        Args:
            title: New title
            
        Returns:
            self for method chaining
        """
        self.ax.set_title(title, fontsize=16)
        return self
        
    def update_legend(self, has_path=False):
        """
        Update the legend
        
        Args:
            has_path: Whether a final path exists
            
        Returns:
            self for method chaining
        """
        if self.ax.get_legend():
            self.ax.get_legend().remove()
            
        if has_path:
            self.ax.legend(['Visited Nodes', 'Final Path', 'Start', 'End'], loc='best')
        else:
            handles, labels = self.ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            self.ax.legend(by_label.values(), by_label.keys(), loc='best')
            
        return self 