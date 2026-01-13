"""Quaternary plotting library for compositional data."""

from .quaternary import (
    bary_to_cart,
    cart_to_bary,
    tetrahedron,
    add_points,
    add_line,
    add_lines,
    add_surface,
    add_volume,
    style_tetrahedron,
    get_standard_vertices,
)

__version__ = "0.1.0"
__author__ = "Oliver T. Lord"
__email__ = "oliver.lord@bristol.ac.uk"

__all__ = [
    'bary_to_cart',
    'cart_to_bary',
    'tetrahedron',
    'add_points',
    'add_line',
    'add_lines',
    'add_surface',
    'add_volume',
    'style_tetrahedron',
    'get_standard_vertices',
]
