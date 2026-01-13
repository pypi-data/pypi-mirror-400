#!/usr/bin/env python3
"""
Custom Polygons Example

Demonstrates circle packing with irregular and complex shapes.
"""

import numpy as np
from geomantic import pack_polygon, visualize_packing, print_circle_summary


def create_star(n_points=5, outer_radius=1.0, inner_radius=0.4):
    """Create a star polygon."""
    angles = np.linspace(0, 2 * np.pi, n_points * 2 + 1)[:-1]
    points = []
    for i, a in enumerate(angles):
        r = outer_radius if i % 2 == 0 else inner_radius
        points.append((r * np.cos(a), r * np.sin(a)))
    points.append(points[0])
    return points


def create_l_shape():
    """Create an L-shaped polygon."""
    return [
        (0, 0),
        (2, 0),
        (2, 1),
        (1, 1),
        (1, 2),
        (0, 2),
        (0, 0),
    ]


def create_crescent():
    """Create a crescent moon shape (approximate)."""
    # Using a simplified irregular shape for demonstration
    # (Proper crescent would require more complex geometry)
    return [
        (1.0, 0.0),
        (0.9, 0.4),
        (0.7, 0.7),
        (0.3, 0.9),
        (-0.2, 1.0),
        (-0.6, 0.8),
        (-0.9, 0.5),
        (-1.0, 0.0),
        (-0.9, -0.5),
        (-0.6, -0.8),
        (-0.2, -1.0),
        (0.3, -0.9),
        (0.7, -0.7),
        (0.9, -0.4),
        (1.0, 0.0),
    ]


def main():
    """Run examples with custom polygons."""
    print("=" * 70)
    print("  Custom Polygon Circle Packing Examples")
    print("=" * 70)

    # Example 1: 5-point Star
    print("\n1. Five-Point Star")
    print("-" * 70)
    star = create_star(n_points=5)
    circles = pack_polygon(star, n=8, iterations=1500)
    print_circle_summary(circles)
    visualize_packing(
        star,
        circles,
        title="Circle Packing: 5-Point Star",
        save_path="examples/output/star_5_point.png",
    )
    print("Saved: examples/output/star_5_point.png")

    # Example 2: L-Shape
    print("\n2. L-Shaped Polygon (concave)")
    print("-" * 70)
    l_shape = create_l_shape()
    circles = pack_polygon(l_shape, n=6, iterations=1500)
    print_circle_summary(circles)
    visualize_packing(
        l_shape,
        circles,
        title="Circle Packing: L-Shape (Concave Polygon)",
        save_path="examples/output/l_shape.png",
    )
    print("Saved: examples/output/l_shape.png")

    # Example 3: 8-point Star
    print("\n3. Eight-Point Star")
    print("-" * 70)
    star8 = create_star(n_points=8, inner_radius=0.5)
    circles = pack_polygon(star8, n=12, iterations=1500)
    print_circle_summary(circles)
    visualize_packing(
        star8,
        circles,
        title="Circle Packing: 8-Point Star",
        save_path="examples/output/star_8_point.png",
    )
    print("Saved: examples/output/star_8_point.png")

    # Example 4: Irregular shape
    print("\n4. Irregular Polygon")
    print("-" * 70)
    crescent = create_crescent()
    circles = pack_polygon(crescent, n=10, iterations=1500)
    print_circle_summary(circles)
    visualize_packing(
        crescent,
        circles,
        title="Circle Packing: Irregular Polygon",
        save_path="examples/output/irregular.png",
    )
    print("Saved: examples/output/irregular.png")

    # Example 5: Auto-detect on complex shape
    print("\n5. Complex Star (auto-detect)")
    print("-" * 70)
    complex_star = create_star(n_points=12, inner_radius=0.3)
    circles = pack_polygon(complex_star, n=None, iterations=1000)
    print(f"Auto-detected {len(circles)} circles")
    print_circle_summary(circles)
    visualize_packing(
        complex_star,
        circles,
        title=f"Circle Packing: 12-Point Star (auto: {len(circles)} circles)",
        save_path="examples/output/star_12_point_auto.png",
    )
    print("Saved: examples/output/star_12_point_auto.png")

    print("\n" + "=" * 70)
    print("All examples complete! Check examples/output/ for visualizations.")
    print("=" * 70)


if __name__ == "__main__":
    main()
