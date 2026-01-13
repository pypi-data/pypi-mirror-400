#!/usr/bin/env python3
"""
Optimization Parameters Example

Demonstrates the effect of varying optimization parameters.
"""

from geomantic import pack_polygon, visualize_packing


def main():
    """Run examples with different optimization parameters."""
    print("=" * 70)
    print("  Optimization Parameters Examples")
    print("=" * 70)

    # Test polygon: simple rectangle
    rectangle = [(0, 0), (2, 0), (2, 1), (0, 1), (0, 0)]

    # Example 1: Varying iterations
    print("\n1. Effect of Iteration Count (n=5, resolution=128)")
    print("-" * 70)
    for iterations in [100, 500, 1000, 2000]:
        circles = pack_polygon(rectangle, n=5, iterations=iterations, verbose=False)
        avg_radius = sum(c["radius"] for c in circles) / len(circles)
        print(f"  Iterations: {iterations:4d} | Avg radius: {avg_radius:.4f}")
        visualize_packing(
            rectangle,
            circles,
            title=f"Circle Packing: {iterations} iterations",
            save_path=f"examples/output/params_iter_{iterations}.png",
        )
        print(f"  Saved: examples/output/params_iter_{iterations}.png")

    # Example 2: Varying resolution
    print("\n2. Effect of Resolution (n=5, iterations=1000)")
    print("-" * 70)
    for resolution in [64, 128, 256]:
        circles = pack_polygon(
            rectangle, n=5, resolution=resolution, iterations=1000, verbose=False
        )
        avg_radius = sum(c["radius"] for c in circles) / len(circles)
        print(f"  Resolution: {resolution:3d} | Avg radius: {avg_radius:.4f}")
        visualize_packing(
            rectangle,
            circles,
            title=f"Circle Packing: resolution={resolution}",
            save_path=f"examples/output/params_res_{resolution}.png",
        )
        print(f"  Saved: examples/output/params_res_{resolution}.png")

    # Example 3: Varying circle count
    print("\n3. Effect of Circle Count (iterations=1000, resolution=128)")
    print("-" * 70)
    for n_circles in [3, 5, 8, 12]:
        circles = pack_polygon(rectangle, n=n_circles, iterations=1000, verbose=False)
        coverage = sum(c["radius"] ** 2 for c in circles)  # Approximate coverage
        print(f"  Circles: {n_circles:2d} | Total coverage (π*Σr²): {coverage:.4f}")
        visualize_packing(
            rectangle,
            circles,
            title=f"Circle Packing: {n_circles} circles",
            save_path=f"examples/output/params_n_{n_circles}.png",
        )
        print(f"  Saved: examples/output/params_n_{n_circles}.png")

    print("\n" + "=" * 70)
    print("Parameter exploration complete!")
    print("\nKey Takeaways:")
    print("  - More iterations → better optimization (diminishing returns after ~1000)")
    print("  - Higher resolution → more accurate but slower")
    print("  - More circles → better coverage but smaller circles")
    print("=" * 70)


if __name__ == "__main__":
    main()
