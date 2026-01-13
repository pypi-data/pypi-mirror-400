"""Basic usage examples for quaternary-plots library."""

import quaternary as quat
import numpy as np

def example_1_empty():
    """Create an empty tetrahedron."""
    print("Example 1: Empty tetrahedron")
    fig = quat.tetrahedron(labels=['A', 'B', 'C', 'D'])
    fig.show()

def example_2_points():
    """Add scattered points."""
    print("Example 2: Scatter points")
    fig = quat.tetrahedron()
    points = np.random.dirichlet(alpha=[1, 1, 1, 1], size=50) * 100
    fig = quat.add_points(fig, points, name='Random', color='blue')
    fig.show()

def example_3_complete():
    """Complete example with multiple elements."""
    print("Example 3: Complete visualization")
    
    fig = quat.tetrahedron(labels=['CaCO3', 'MgCO3', 'Na2CO3', 'K2CO3'])
    
    exp_data = np.array([
        [40, 30, 20, 10],
        [35, 35, 20, 10],
        [30, 40, 20, 10],
        [25, 25, 25, 25],
    ])
    fig = quat.add_points(fig, exp_data, name='Experiments', 
                         color='red', size=12, symbol='diamond')
    
    fig = quat.add_line(fig, [60, 20, 10, 10], [20, 40, 30, 10],
                       name='Tie line', color='blue', width=3, dash='dash')
    
    fig = quat.style_tetrahedron(fig, width=900, height=900)
    fig.show()

if __name__ == '__main__':
    example_1_empty()
    example_2_points()
    example_3_complete()
