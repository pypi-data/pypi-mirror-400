# Geomantic

[![Tests](https://github.com/horeilly/geomantic/workflows/Tests/badge.svg)](https://github.com/horeilly/geomantic/actions)
[![Coverage](https://codecov.io/gh/horeilly/geomantic/branch/main/graph/badge.svg)](https://codecov.io/gh/horeilly/geomantic)
[![PyPI](https://img.shields.io/pypi/v/geomantic.svg)](https://pypi.org/project/geomantic/)
[![Python](https://img.shields.io/pypi/pyversions/geomantic.svg)](https://pypi.org/project/geomantic/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## TL;DR
A Python package to approximate an irregular polygon as a set of circles, with optional auto-detection of optimal circle count. Accepts standard polygon input, produces both raw circle data and a visualization, and is engineered with DevOps hygiene suitable for portfolio/demo use.

## Installation

```bash
pip install geomantic
```

## Quick Start

```python
from geomantic import pack_polygon, visualize_packing

# Define a polygon (list of coordinate tuples)
polygon = [(0, 0), (2, 0), (2, 1), (0, 1)]

# Pack circles into the polygon (auto-detect optimal count)
circles = pack_polygon(polygon)

# Visualize the result
visualize_packing(polygon, circles)
```

**For geographic data (lat/lon coordinates):**

```python
# Use projection for geographic coordinates
circles = pack_polygon(
    polygon,
    n=5,  # Or None for auto-detection
    use_projection=True  # Ensures circles stay circular on Earth's surface
)
```

## Architecture

Geomantic uses a modular architecture with four main components:

```
geomantic/
├── core.py          # Main API: pack_polygon() orchestrates the pipeline
├── optimizer.py     # PyTorch-based optimization engine
├── projection.py    # Geographic coordinate transformations (WGS84 ↔ UTM)
└── visualization.py # Plotting and output utilities
```

**Key modules:**

- **`core.py`**: Main entry point with `pack_polygon()` function. Handles input parsing, projection setup, normalization, and result formatting.

- **`optimizer.py`**: Contains the differentiable rendering optimization:
  - `CircleModel`: PyTorch neural network with learnable circle positions and radii
  - `DifferentiableRenderer`: Rasterizes polygons to binary masks
  - `optimize_circles()`: Gradient descent optimization with IoU loss
  - Smart initialization samples circle positions inside the polygon
  - Containment and repulsion penalties prevent circles from escaping or collapsing

- **`projection.py`**: Coordinate transformation utilities:
  - `MetricProjector`: WGS84 ↔ UTM transformations with auto-zone detection
  - `MetricNormalizer`: Scales coordinates to [0,1] normalized space for optimization

- **`visualization.py`**: Visualization tools including `visualize_packing()` and `print_circle_summary()`

**Optimization pipeline:**
```
Input Polygon → [Projection to UTM] → Normalization →
PyTorch Optimization (IoU + Containment + Repulsion) →
Denormalization → [Projection back to WGS84] → Circle Results
```

## Project Goals

### Problem Statement
Traditional geometric approximation methods struggle with irregular polygons, especially when physical interpretability matters. Geographic boundaries (ZIP codes, districts, protected areas) often need to be simplified for:
- **Spatial analysis**: Coverage estimation, service area planning, accessibility modeling
- **Visualization**: Reducing visual complexity while preserving spatial meaning
- **Approximation**: Replacing complex polygons with analytically tractable primitives

Existing solutions either produce poor approximations (convex hulls, bounding boxes) or lack geographic awareness (treating lat/lon as Cartesian coordinates produces distorted circles).

### What Geomantic Solves
**1. Physically Accurate Geographic Approximation**
- Automatically projects WGS84 coordinates to UTM before optimization, ensuring circles remain circular on Earth's surface
- Handles latitude-dependent longitude scaling for correct distance calculations
- Eliminates the "stretched ellipse" problem common in naive lat/lon circle fitting

**2. Smart Optimization with Constraints**
- Uses differentiable rendering with PyTorch for gradient-based optimization (faster convergence than genetic algorithms)
- Containment penalties keep circles inside polygon boundaries (critical for concave shapes)
- Repulsion penalties prevent circle collapse, ensuring diverse coverage
- Auto-detection finds optimal circle count using elbow method on IoU loss

**3. Production-Ready Engineering**
- Type-safe codebase with full mypy compliance
- Comprehensive test coverage with pytest
- Pre-commit hooks for code quality (Black, flake8, mypy)
- CI/CD pipeline with multi-version Python testing (3.8-3.12)
- Installable via pip with minimal dependencies

### Use Cases
- **Urban planning**: Approximate service areas (fire stations, schools) for quick distance calculations
- **Ecology**: Simplify habitat boundaries for circular buffer analysis
- **Marketing**: Convert trade areas or ZIP code boundaries to radial coverage zones
- **Education**: Demonstrate optimization techniques, differentiable rendering, and coordinate projections
- **Data visualization**: Replace complex polygons with simpler circular representations for cleaner maps

### What Geomantic Is NOT
- **Not a general-purpose polygon simplification tool** (use Shapely's `simplify()` for that)
- **Not optimized for real-time applications** (optimization takes seconds to minutes depending on complexity)
- **Not a commercial SaaS product** (open-source library for integration into your own tools)
- **Not a replacement for precise geometric operations** (approximation introduces error by design)

## User Stories
- As a Data Scientist, I want to fit circles to arbitrary polygons, so that I can demonstrate geometric optimization in presentations.
- As a developer, I want to import this as a Python library, so that I can integrate it into Jupyter notebooks or pipelines.
- As a hobbyist, I want to visualize the packing, so that I can experiment and tweak inputs for different shapes.

## Functional Requirements
- Core Algorithm (Priority: High)
  - Accept input polygon (list of coordinates or GeoJSON).
  - Accept optional n; otherwise autodetect using suitable metric (e.g., elbow method).
  - Grid-based differentiable rasterization for circle fitting.
  - Compute suitable initial centroids.
- API/Interface (Priority: High)
  - Python function/class interface.
  - Output: Array of dictionaries, each with radius, centroid_x, centroid_y.
- Visualization (Priority: Medium)
  - Function to generate an image (matplotlib, etc.) showing polygon outline and circles.
- Packaging (Priority: High)
  - Installable via pip (or equivalent, e.g., Poetry support).
- Testing & Code Quality (Priority: High)
  - Unit tests for inputs/outputs, edge cases, and algorithm steps.
  - Automated linting and type-checking, e.g., with flake8/black/pylint and mypy.
- DevOps & Deployment (Priority: Medium)
  - GitHub Actions to run tests/linting on commit/push.
  - (Optional) Terraform/GCP scripts for potential future hosting.

## User Experience
- User installs via pip.
- Imports in notebook/script: from geomantic import pack_polygon
- Calls main function, passing polygon and options.
- Receives output (list of circles), optionally calls viz function for output.
- Views resulting image in notebook or as file.

## Technical Considerations
- Python-first; minimal non-Python dependencies.
- Codebase ready for CI (GitHub Actions).
- Focus on modularity/testability: split main algorithm from I/O and viz.
- Type hints and docstrings throughout.
- Testing: Use pytest; test basic input validation, algorithm output, and (if feasible) some image output.

## Success Metrics
- All primary features covered by automated tests and CI.
- Can be imported and run in a clean virtualenv.
- Generates accurate results for at least 3 "typical" test polygons.
- README/docs clear enough for DS/engineering peers to use and understand.
