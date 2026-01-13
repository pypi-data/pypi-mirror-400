"""
Quaternary Plot Library
=======================

A Python library for creating quaternary (tetrahedral) plots using Plotly.

Author: Oliver T. Lord
License: GPL-3.0
"""

import numpy as np
import plotly.graph_objects as go
from typing import Union, List, Optional, Tuple

__version__ = "0.1.0"

# Standard tetrahedron vertices
def get_standard_vertices() -> np.ndarray:
    """Get standard tetrahedron vertex coordinates."""
    a = 0.5 * np.sqrt(3)
    h = np.sqrt(6) / 3
    return np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.5, a, 0.0],
        [0.5, a/2, h]
    ])

def bary_to_cart(coords, vertices=None):
    """Convert barycentric to Cartesian coordinates."""
    coords = np.asarray(coords, dtype=float)
    if vertices is None:
        vertices = get_standard_vertices()
    else:
        vertices = np.asarray(vertices, dtype=float)
    
    single_point = coords.ndim == 1
    if single_point:
        coords = coords.reshape(1, -1)
    
    if np.any(coords > 1):
        coords = coords / 100.0
    
    bary = coords[:, :3]
    T = (vertices[:3] - vertices[3]).T
    cart = bary @ T.T + vertices[3]
    
    return cart[0] if single_point else cart

def cart_to_bary(coords, vertices=None):
    """Convert Cartesian to barycentric coordinates."""
    coords = np.asarray(coords, dtype=float)
    if vertices is None:
        vertices = get_standard_vertices()
    else:
        vertices = np.asarray(vertices, dtype=float)
    
    single_point = coords.ndim == 1
    if single_point:
        coords = coords.reshape(1, -1)
    
    T = (vertices[:3] - vertices[3]).T
    bary_123 = (coords - vertices[3]) @ np.linalg.inv(T).T
    bary_4 = 1.0 - bary_123.sum(axis=1, keepdims=True)
    bary = np.hstack([bary_123, bary_4])
    
    return bary[0] if single_point else bary

def tetrahedron(labels=['Component 1', 'Component 2', 'Component 3', 'Component 4'],
                vertices=None, show_edges=True, show_labels=True,
                edge_color='black', edge_width=2, label_size=20, **layout_kwargs):
    """Create an empty tetrahedron plot."""
    if vertices is None:
        vertices = get_standard_vertices()
    else:
        vertices = np.asarray(vertices, dtype=float)
    
    traces = []
    
    if show_edges:
        route_indices = [0, 1, 2, 3, 0, 2, 1, 3]
        route = vertices[route_indices]
        x, y, z = route[:, 0], route[:, 1], route[:, 2]
        traces.append(go.Scatter3d(
            x=x, y=y, z=z, mode='lines',
            line=dict(color=edge_color, width=edge_width),
            showlegend=False, hoverinfo='skip'
        ))
    
    if show_labels:
        traces.append(go.Scatter3d(
            x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
            mode='text', text=labels, textfont=dict(size=label_size),
            showlegend=False, hoverinfo='text', hovertext=labels
        ))
    
    fig = go.Figure(data=traces)
    
    default_layout = dict(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            dragmode='orbit',
            aspectmode='data',
            camera=dict(
                projection=dict(type='orthographic'),
                up=dict(x=0, y=0, z=np.sqrt(6)/3),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.3, y=1.3, z=0.1)
            )
        ),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.15,
                   xanchor='center', x=0.5)
    )
    default_layout.update(layout_kwargs)
    fig.update_layout(**default_layout)
    fig._quaternary_vertices = vertices
    
    return fig

def add_points(fig, coords, vertices=None, name='Points', color=None,
               size=8, symbol='circle', opacity=0.8, show_legend=True, **scatter_kwargs):
    """Add points to quaternary plot."""
    if vertices is None:
        vertices = getattr(fig, '_quaternary_vertices', get_standard_vertices())
    
    coords = np.asarray(coords, dtype=float)
    cart = bary_to_cart(coords, vertices)
    
    if cart.ndim == 1:
        cart = cart.reshape(1, -1)
    
    marker_dict = dict(size=size, symbol=symbol, opacity=opacity)
    if color is not None:
        marker_dict['color'] = color
    
    trace = go.Scatter3d(
        x=cart[:, 0], y=cart[:, 1], z=cart[:, 2],
        mode='markers', name=name, marker=marker_dict,
        showlegend=show_legend, **scatter_kwargs
    )
    
    fig.add_trace(trace)
    return fig

def add_line(fig, start, end, vertices=None, name='Line',
             color='blue', width=3, dash=None, show_legend=True, **scatter_kwargs):
    """Add a line between two points."""
    if vertices is None:
        vertices = getattr(fig, '_quaternary_vertices', get_standard_vertices())
    
    start_cart = bary_to_cart(start, vertices)
    end_cart = bary_to_cart(end, vertices)
    
    line_dict = dict(color=color, width=width)
    if dash is not None:
        line_dict['dash'] = dash
    
    trace = go.Scatter3d(
        x=[start_cart[0], end_cart[0]],
        y=[start_cart[1], end_cart[1]],
        z=[start_cart[2], end_cart[2]],
        mode='lines', name=name, line=line_dict,
        showlegend=show_legend, **scatter_kwargs
    )
    
    fig.add_trace(trace)
    return fig

def add_lines(fig, coords_pairs, vertices=None, name='Lines',
              color='blue', width=3, dash=None, show_legend=True, **scatter_kwargs):
    """Add multiple lines to quaternary plot."""
    if vertices is None:
        vertices = getattr(fig, '_quaternary_vertices', get_standard_vertices())
    
    coords_pairs = np.asarray(coords_pairs)
    
    for i, (start, end) in enumerate(coords_pairs):
        show_this = show_legend and (i == 0)
        fig = add_line(fig, start, end, vertices=vertices, name=name,
                      color=color, width=width, dash=dash,
                      show_legend=show_this, **scatter_kwargs)
    
    return fig

def add_surface(fig, coords, vertices=None, name='Surface',
                color='lightblue', opacity=0.5, show_legend=True, **mesh_kwargs):
    """Add a surface defined by points."""
    if vertices is None:
        vertices = getattr(fig, '_quaternary_vertices', get_standard_vertices())
    
    coords = np.asarray(coords, dtype=float)
    cart = bary_to_cart(coords, vertices)
    
    if cart.shape[0] < 4:
        raise ValueError(f"Need at least 4 points for surface, got {cart.shape[0]}")
    
    from scipy.spatial import ConvexHull
    hull = ConvexHull(cart)
    
    trace = go.Mesh3d(
        x=cart[:, 0], y=cart[:, 1], z=cart[:, 2],
        i=hull.simplices[:, 0],
        j=hull.simplices[:, 1],
        k=hull.simplices[:, 2],
        name=name, color=color, opacity=opacity,
        showlegend=show_legend, **mesh_kwargs
    )
    
    fig.add_trace(trace)
    return fig

def add_volume(fig, coords, vertices=None, name='Volume',
               color='lightgreen', opacity=0.3, show_legend=True, **mesh_kwargs):
    """Add a volume defined by points."""
    return add_surface(fig, coords, vertices=vertices, name=name,
                      color=color, opacity=opacity, show_legend=show_legend,
                      **mesh_kwargs)

def style_tetrahedron(fig, camera_eye=None, bgcolor='white',
                     width=None, height=None, **layout_kwargs):
    """Apply styling to quaternary plot."""
    updates = {}
    
    if camera_eye is not None:
        updates['scene'] = dict(
            camera=dict(eye=dict(x=camera_eye[0], y=camera_eye[1], z=camera_eye[2]))
        )
    
    if bgcolor is not None:
        if 'scene' not in updates:
            updates['scene'] = {}
        updates['scene']['bgcolor'] = bgcolor
    
    if width is not None:
        updates['width'] = width
    
    if height is not None:
        updates['height'] = height
    
    updates.update(layout_kwargs)
    fig.update_layout(**updates)
    
    return fig
