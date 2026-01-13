#!/usr/bin/env python3
"""
Performance Benchmark for Geomantic

Benchmarks circle packing performance across different polygon complexities.
"""

import time
import numpy as np
from geomantic import pack_polygon


def create_test_polygons():
    """Create test polygons of varying complexity."""
    polygons = {}

    # Simple shapes
    polygons["simple_square"] = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]

    polygons["rectangle_2x1"] = [(0, 0), (2, 0), (2, 1), (0, 1), (0, 0)]

    # Medium complexity
    n_vertices = 20
    angles = np.linspace(0, 2 * np.pi, n_vertices + 1)[:-1]
    polygons["circle_approx_20"] = [(np.cos(a), np.sin(a)) for a in angles]
    polygons["circle_approx_20"].append(polygons["circle_approx_20"][0])

    # Complex shape (star)
    n_points = 10
    angles = np.linspace(0, 2 * np.pi, n_points + 1)[:-1]
    star = []
    for i, a in enumerate(angles):
        r = 1.0 if i % 2 == 0 else 0.5
        star.append((r * np.cos(a), r * np.sin(a)))
    star.append(star[0])
    polygons["star_10_points"] = star

    # Very complex (50+ vertices)
    n_vertices = 50
    angles = np.linspace(0, 2 * np.pi, n_vertices + 1)[:-1]
    # Add some irregularity
    radii = 1.0 + 0.1 * np.random.randn(n_vertices)
    polygons["complex_irregular_50"] = [
        (r * np.cos(a), r * np.sin(a)) for r, a in zip(radii, angles)
    ]
    polygons["complex_irregular_50"].append(polygons["complex_irregular_50"][0])

    return polygons


def benchmark_single_run(polygon, n_circles, iterations, resolution):
    """Benchmark a single configuration."""
    start = time.time()
    circles = pack_polygon(
        polygon,
        n=n_circles,
        iterations=iterations,
        resolution=resolution,
        use_projection=False,
        verbose=False,
    )
    duration = time.time() - start
    return duration, circles


def benchmark_auto_detection(polygon, resolution):
    """Benchmark auto-detection."""
    start = time.time()
    circles = pack_polygon(
        polygon,
        n=None,  # Auto-detect
        iterations=100,  # Fewer iterations for speed
        resolution=resolution,
        use_projection=False,
        verbose=False,
    )
    duration = time.time() - start
    return duration, len(circles)


def main():
    """Run comprehensive performance benchmarks."""
    print("=" * 80)
    print("  GEOMANTIC PERFORMANCE BENCHMARK")
    print("=" * 80)

    polygons = create_test_polygons()

    # Benchmark 1: Fixed circle count, varying polygon complexity
    print("\n1. Varying Polygon Complexity (n=5 circles, 500 iterations, 128 resolution)")
    print("-" * 80)
    print(f"{'Polygon':<25} {'Time (s)':<12} {'Avg/circle (s)':<15}")
    print("-" * 80)

    for name, polygon in polygons.items():
        duration, _ = benchmark_single_run(polygon, n_circles=5, iterations=500, resolution=128)
        avg_per_circle = duration / 5
        print(f"{name:<25} {duration:>10.3f}   {avg_per_circle:>13.4f}")

    # Benchmark 2: Varying circle count
    print("\n2. Varying Circle Count (rectangle_2x1, 500 iterations, 128 resolution)")
    print("-" * 80)
    print(f"{'Circles':<15} {'Time (s)':<12} {'Time/circle (s)':<15}")
    print("-" * 80)

    test_polygon = polygons["rectangle_2x1"]
    for n in [3, 5, 8, 10, 15]:
        duration, _ = benchmark_single_run(
            test_polygon, n_circles=n, iterations=500, resolution=128
        )
        per_circle = duration / n
        print(f"{n:<15} {duration:>10.3f}   {per_circle:>13.4f}")

    # Benchmark 3: Varying resolution
    print("\n3. Varying Resolution (rectangle_2x1, n=5, 500 iterations)")
    print("-" * 80)
    print(f"{'Resolution':<15} {'Time (s)':<12} {'Speedup':<15}")
    print("-" * 80)

    test_polygon = polygons["rectangle_2x1"]
    baseline = None
    for res in [64, 128, 256, 512]:
        duration, _ = benchmark_single_run(
            test_polygon, n_circles=5, iterations=500, resolution=res
        )
        if baseline is None:
            baseline = duration
            speedup_str = "baseline"
        else:
            speedup = baseline / duration
            speedup_str = f"{speedup:.2f}x"
        print(f"{res:<15} {duration:>10.3f}   {speedup_str:>13}")

    # Benchmark 4: Varying iteration count
    print("\n4. Varying Iterations (rectangle_2x1, n=5, resolution=128)")
    print("-" * 80)
    print(f"{'Iterations':<15} {'Time (s)':<12} {'Time/iter (ms)':<15}")
    print("-" * 80)

    test_polygon = polygons["rectangle_2x1"]
    for iters in [100, 500, 1000, 2000]:
        duration, _ = benchmark_single_run(
            test_polygon, n_circles=5, iterations=iters, resolution=128
        )
        per_iter = (duration / iters) * 1000  # Convert to ms
        print(f"{iters:<15} {duration:>10.3f}   {per_iter:>13.4f}")

    # Benchmark 5: Auto-detection
    print("\n5. Auto-Detection Performance (100 iterations/test, resolution=64)")
    print("-" * 80)
    print(f"{'Polygon':<25} {'Time (s)':<12} {'Detected N':<15}")
    print("-" * 80)

    for name, polygon in [
        ("simple_square", polygons["simple_square"]),
        ("rectangle_2x1", polygons["rectangle_2x1"]),
        ("circle_approx_20", polygons["circle_approx_20"]),
    ]:
        duration, n_detected = benchmark_auto_detection(polygon, resolution=64)
        print(f"{name:<25} {duration:>10.3f}   {n_detected:>13}")

    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80)
    print("\nPerformance Tips:")
    print("  - Use lower resolution (64-128) for faster results")
    print("  - Reduce iterations (500-1000) for quick prototyping")
    print("  - Auto-detection is slower but finds optimal circle count")
    print("  - Complex polygons (50+ vertices) may benefit from higher resolution")


if __name__ == "__main__":
    main()
