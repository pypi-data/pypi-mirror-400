#!/usr/bin/env python3
"""
Basic Shapes Example

Demonstrates circle packing with common geometric shapes.
"""

import numpy as np
from geomantic import pack_polygon, visualize_packing, print_circle_summary


def main():
    """Run examples with basic shapes."""
    print("=" * 70)
    print("  Basic Shapes Circle Packing Examples")
    print("=" * 70)

    # Example 1: Rectangle
    print("\n1. Rectangle (3x1)")
    print("-" * 70)
    rectangle = [(0, 0), (3, 0), (3, 1), (0, 1), (0, 0)]
    circles = pack_polygon(rectangle, n=8, iterations=1000)
    print_circle_summary(circles)
    visualize_packing(
        rectangle,
        circles,
        title="Circle Packing: Rectangle (3x1) with 8 circles",
        save_path="examples/output/rectangle_8_circles.png",
    )
    print("Saved: examples/output/rectangle_8_circles.png")

    # Example 2: Square with auto-detection
    print("\n2. Square (auto-detect optimal circles)")
    print("-" * 70)
    square = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
    circles = pack_polygon(square, n=None, iterations=1000)  # Auto-detect
    print(f"Auto-detected {len(circles)} circles")
    print_circle_summary(circles)
    visualize_packing(
        square,
        circles,
        title=f"Circle Packing: Unit Square (auto: {len(circles)} circles)",
        save_path="examples/output/square_auto.png",
    )
    print("Saved: examples/output/square_auto.png")

    # Example 3: Equilateral Triangle
    print("\n3. Equilateral Triangle")
    print("-" * 70)
    triangle = [(0, 0), (1, 0), (0.5, 0.866), (0, 0)]
    circles = pack_polygon(triangle, n=3, iterations=1000)
    print_circle_summary(circles)
    visualize_packing(
        triangle,
        circles,
        title="Circle Packing: Equilateral Triangle with 3 circles",
        save_path="examples/output/triangle_3_circles.png",
    )
    print("Saved: examples/output/triangle_3_circles.png")

    # Example 4: Regular Pentagon
    print("\n4. Regular Pentagon")
    print("-" * 70)
    n_sides = 5
    angles = np.linspace(0, 2 * np.pi, n_sides + 1)[:-1]
    pentagon = [(np.cos(a), np.sin(a)) for a in angles]
    pentagon.append(pentagon[0])  # Close the polygon
    circles = pack_polygon(pentagon, n=5, iterations=1000)
    print_circle_summary(circles)
    visualize_packing(
        pentagon,
        circles,
        title="Circle Packing: Regular Pentagon with 5 circles",
        save_path="examples/output/pentagon_5_circles.png",
    )
    print("Saved: examples/output/pentagon_5_circles.png")

    # Example 5: Hexagon
    print("\n5. Regular Hexagon")
    print("-" * 70)
    n_sides = 6
    angles = np.linspace(0, 2 * np.pi, n_sides + 1)[:-1]
    hexagon = [(np.cos(a), np.sin(a)) for a in angles]
    hexagon.append(hexagon[0])
    circles = pack_polygon(hexagon, n=7, iterations=1000)
    print_circle_summary(circles)
    visualize_packing(
        hexagon,
        circles,
        title="Circle Packing: Regular Hexagon with 7 circles",
        save_path="examples/output/hexagon_7_circles.png",
    )
    print("Saved: examples/output/hexagon_7_circles.png")

    print("\n" + "=" * 70)
    print("All examples complete! Check examples/output/ for visualizations.")
    print("=" * 70)


if __name__ == "__main__":
    main()
