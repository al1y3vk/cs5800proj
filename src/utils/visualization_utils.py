"""
Visualization utility functions

Contains helper functions for map visualization components.
"""
import matplotlib.pyplot as plt
import numpy as np


def setup_map_figure(title, figsize=(12, 10)):
    """
    Create and setup a figure and axis for map visualization
    
    Args:
        title: Title for the plot
        figsize: Size of the figure as (width, height) tuple
        
    Returns:
        tuple: (fig, ax) - the created figure and axis
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(title, fontsize=16)
    ax.set_axis_off()
    # Don't add an empty legend at creation time - we'll add it later when we have items
    plt.tight_layout()
    return fig, ax


def draw_nodes(ax, nodes, node_ids, size=20, color='red', alpha=0.7, zorder=2, colormap=None):
    """
    Draw nodes on the map
    
    Args:
        ax: Matplotlib axis
        nodes: GeoDataFrame of nodes
        node_ids: List of node IDs to draw
        size: Size of node markers
        color: Color of nodes (used if colormap is None)
        alpha: Transparency
        zorder: Z-order for drawing
        colormap: Optional matplotlib colormap for coloring by index
        
    Returns:
        List of scatter artists created
    """
    scatters = []
    
    if colormap:
        # Draw with color gradient
        for i, node_id in enumerate(node_ids):
            node = nodes.loc[node_id]
            color_idx = min(i / max(1, len(node_ids)), 1.0)
            scatter = ax.scatter(
                node.x, node.y, 
                color=colormap(color_idx), 
                s=size, alpha=alpha, zorder=zorder
            )
            scatters.append(scatter)
    else:
        # Draw all with same color
        for node_id in node_ids:
            node = nodes.loc[node_id]
            scatter = ax.scatter(
                node.x, node.y, 
                color=color, s=size, alpha=alpha, zorder=zorder
            )
            scatters.append(scatter)
            
    return scatters


def draw_edge_path(ax, G, nodes, path, color='blue', width=2, alpha=0.7, zorder=3):
    """
    Draw a path consisting of connected edges
    
    Args:
        ax: Matplotlib axis
        G: NetworkX graph
        nodes: GeoDataFrame of nodes
        path: List of node IDs forming the path
        color: Color of the path
        width: Line width
        alpha: Transparency
        zorder: Z-order for drawing
        
    Returns:
        List of line artists created
    """
    lines = []
    
    if len(path) < 2:
        return lines
        
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if G.has_edge(u, v):
            try:
                edge_data = G.get_edge_data(u, v)[0]
                if 'geometry' in edge_data:
                    xs, ys = edge_data['geometry'].xy
                    line = ax.plot(xs, ys, color=color, linewidth=width, zorder=zorder, alpha=alpha)[0]
                else:
                    # No geometry, plot straight line
                    u_node = nodes.loc[u]
                    v_node = nodes.loc[v]
                    line = ax.plot([u_node.x, v_node.x], [u_node.y, v_node.y], 
                                  color=color, linewidth=width, zorder=zorder, alpha=alpha)[0]
            except Exception:
                # Fall back to straight line
                u_node = nodes.loc[u]
                v_node = nodes.loc[v]
                line = ax.plot([u_node.x, v_node.x], [u_node.y, v_node.y], 
                              color=color, linewidth=width, zorder=zorder, alpha=alpha)[0]
            
            lines.append(line)
    
    return lines


def clear_artists(artists):
    """
    Clear a list of matplotlib artists from their axes
    
    Args:
        artists: List of matplotlib artists to remove
    """
    for artist in artists:
        if artist in artist.axes.collections:
            artist.remove()
        elif artist in artist.axes.lines:
            artist.remove()


def clear_collections_and_lines(ax, keep_collections=None):
    """
    Clear all collections and lines from an axis except those specified to keep
    
    Args:
        ax: Matplotlib axis
        keep_collections: List of collection objects to keep
    """
    if keep_collections is None:
        keep_collections = []
        
    # Clear collections (points)
    for artist in ax.collections[:]:
        if artist not in keep_collections:
            artist.remove()
    
    # Clear lines (paths)
    for artist in ax.lines[:]:
        artist.remove() 