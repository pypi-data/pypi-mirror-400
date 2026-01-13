# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with pytest (82% coverage, 89 tests)
- GitHub Actions CI/CD pipeline for automated testing and quality checks
- Performance benchmarking tools
- Example gallery with basic shapes and advanced use cases
- Constants module for magic numbers
- MIT License
- Smart initialization: circles now start inside polygon using rejection sampling
- Containment penalty: keeps circles inside polygon during optimization
- Repulsion penalty: prevents circles from collapsing to same position
- Enhanced verbose output showing IoU, containment, and repulsion losses

### Fixed
- Critical performance bug in `estimate_optimal_circles()` causing 2x slowdown
- **Critical bug: circles escaping outside polygon boundaries** for concave shapes (L-shapes, stars, etc.)
- **Circle collapse issue** where multiple circles converged to identical positions
- Algorithm now robust for concave and irregular polygons

### Changed
- Migrated from setup.py to modern pyproject.toml (PEP 621)
- Moved demo script from main.py to geomantic.demo module
- Updated `CircleModel` to accept `target_polygon` parameter for polygon-aware initialization
- Combined loss function now includes IoU + containment + repulsion penalties

## [0.1.0] - 2026-01-03

### Added
- Core circle packing API (`pack_polygon()` function)
- Geographic projection support (WGS84 ↔ UTM)
- Auto-detection of optimal circle count using elbow method
- Visualization tools (`visualize_packing()`, `print_circle_summary()`)
- Support for Shapely Polygon, coordinate lists, and GeoJSON inputs
- PyTorch-based differentiable rendering optimization
- Comprehensive docstrings and type hints

### Technical Details
- Modular architecture (core, optimizer, projection, visualization modules)
- Configurable resolution and iteration parameters
- Support for both Cartesian and geographic coordinate systems
- Sharpness annealing for improved optimization stability
