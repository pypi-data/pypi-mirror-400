# Geomantic Examples Gallery

This directory contains example scripts demonstrating various uses of the Geomantic circle packing library.

## Running Examples

Each example can be run independently:

```bash
python examples/01_basic_shapes.py
python examples/03_custom_polygons.py
python examples/04_optimization_params.py
python examples/sf_zipcodes_demo.py
python examples/benchmark.py
```

## Example Scripts

### 1. Basic Shapes (`01_basic_shapes.py`)

Demonstrates circle packing with common geometric shapes:
- **Rectangle**: 3x1 rectangle with 8 circles
- **Square**: Unit square with auto-detected circle count
- **Triangle**: Equilateral triangle with 3 circles
- **Pentagon**: Regular pentagon with 5 circles
- **Hexagon**: Regular hexagon with 7 circles

**Output**: `examples/output/rectangle_8_circles.png`, `square_auto.png`, etc.

### 2. San Francisco ZIP Codes (`sf_zipcodes_demo.py`)

Real-world example using geographic coordinates (lat/lon) for SF ZIP code boundaries.
- Demonstrates `use_projection=True` for geographic data
- Automatic UTM projection for metric accuracy
- Ensures circles remain circular on Earth's surface

**Output**: `circle_packing_94123.png`

### 3. Custom Polygons (`03_custom_polygons.py`)

Shows circle packing with irregular and complex shapes:
- **5-Point Star**: Classic star shape
- **L-Shape**: Concave polygon
- **8-Point Star**: More complex star
- **Irregular Polygon**: Non-convex shape
- **12-Point Star**: Auto-detection on complex shape

**Output**: `examples/output/star_5_point.png`, `l_shape.png`, etc.

### 4. Optimization Parameters (`04_optimization_params.py`)

Explores the effect of varying optimization parameters:
- **Iterations**: 100, 500, 1000, 2000
- **Resolution**: 64, 128, 256
- **Circle Count**: 3, 5, 8, 12

Demonstrates trade-offs between accuracy and speed.

**Output**: `examples/output/params_iter_*.png`, `params_res_*.png`, etc.

### 5. Performance Benchmark (`benchmark.py`)

Comprehensive performance benchmarking:
- Varying polygon complexity
- Varying circle counts
- Varying resolution
- Varying iterations
- Auto-detection performance

Useful for understanding performance characteristics and optimization opportunities.

## Output Gallery

All generated visualizations are saved to `examples/output/`.

Sample outputs:

### Basic Shapes
![Rectangle](output/rectangle_8_circles.png)
![Square](output/square_auto.png)
![Triangle](output/triangle_3_circles.png)
![Pentagon](output/pentagon_5_circles.png)
![Hexagon](output/hexagon_7_circles.png)

### Custom Polygons
![5-Point Star](output/star_5_point.png)
![L-Shape](output/l_shape.png)
![8-Point Star](output/star_8_point.png)

### Parameter Variations
![100 Iterations](output/params_iter_100.png)
![2000 Iterations](output/params_iter_2000.png)

## Tips for Best Results

1. **For quick prototyping**: Use `resolution=64-128` and `iterations=500-1000`
2. **For publication-quality**: Use `resolution=256` and `iterations=2000`
3. **For geographic data**: Always use `use_projection=True`
4. **For auto-detection**: Expect 2-3x slower than fixed circle count
5. **For complex polygons**: Increase resolution to 256 or higher

## Creating Your Own Examples

```python
from geomantic import pack_polygon, visualize_packing

# Define your polygon
my_polygon = [(x1, y1), (x2, y2), ..., (xn, yn)]

# Pack circles
circles = pack_polygon(my_polygon, n=5, iterations=1000)

# Visualize
visualize_packing(my_polygon, circles, save_path="my_output.png")
```

For geographic data:

```python
# Use lat/lon coordinates
geo_polygon = [(-122.4, 37.8), (-122.3, 37.8), ...]

# Enable projection
circles = pack_polygon(geo_polygon, n=5, use_projection=True)

visualize_packing(geo_polygon, circles, projection_mode="geographic")
```

## Requirements

All examples require the Geomantic package to be installed:

```bash
pip install -e .
```

Or install from PyPI:

```bash
pip install geomantic
```
