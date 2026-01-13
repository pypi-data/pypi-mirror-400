"""Tests for geomantic.core module (main API)."""

import pytest
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

from geomantic import pack_polygon


class TestPackPolygonInputParsing:
    """Test input parsing and validation."""

    def test_accepts_list_of_tuples(self, simple_rectangle):
        """Should accept list of (x, y) tuples."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=100)
        assert isinstance(circles, list)
        assert len(circles) == 3

    def test_accepts_shapely_polygon(self, simple_rectangle):
        """Should accept Shapely Polygon object."""
        poly = Polygon(simple_rectangle)
        circles = pack_polygon(poly, n=3, iterations=100)
        assert isinstance(circles, list)
        assert len(circles) == 3

    def test_accepts_geojson_dict(self, simple_rectangle):
        """Should accept GeoJSON-like dictionary."""
        geojson = {"type": "Polygon", "coordinates": [simple_rectangle]}
        circles = pack_polygon(geojson, n=3, iterations=100)
        assert isinstance(circles, list)
        assert len(circles) == 3

    def test_rejects_invalid_type(self):
        """Should raise TypeError for invalid input types."""
        with pytest.raises(TypeError, match="polygon must be"):
            pack_polygon("invalid", n=3)

    def test_rejects_empty_polygon(self):
        """Should raise ValueError for empty polygon."""
        with pytest.raises(ValueError, match="Empty polygon"):
            pack_polygon([], n=3)

    def test_rejects_multipolygon(self):
        """Should raise TypeError for MultiPolygon."""
        multi = MultiPolygon(
            [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])]
        )
        with pytest.raises(TypeError, match="polygon must be"):
            pack_polygon(multi, n=3)


class TestPackPolygonOutputFormat:
    """Test output format and structure."""

    def test_returns_list_of_dicts(self, simple_rectangle):
        """Should return list of dictionaries."""
        circles = pack_polygon(simple_rectangle, n=5, iterations=100)
        assert isinstance(circles, list)
        assert all(isinstance(c, dict) for c in circles)

    def test_dict_has_required_keys(self, simple_rectangle):
        """Each circle dict should have radius, centroid_x, centroid_y."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=100)
        for circle in circles:
            assert "radius" in circle
            assert "centroid_x" in circle
            assert "centroid_y" in circle

    def test_values_are_numeric(self, simple_rectangle):
        """All values should be numeric."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=100)
        for circle in circles:
            assert isinstance(circle["radius"], (int, float))
            assert isinstance(circle["centroid_x"], (int, float))
            assert isinstance(circle["centroid_y"], (int, float))

    def test_radii_are_positive(self, simple_rectangle):
        """All radii should be positive."""
        circles = pack_polygon(simple_rectangle, n=5, iterations=100)
        for circle in circles:
            assert circle["radius"] > 0

    def test_correct_number_of_circles(self, simple_rectangle):
        """Should return exactly n circles when n is specified."""
        for n in [3, 5, 8]:
            circles = pack_polygon(simple_rectangle, n=n, iterations=100)
            assert len(circles) == n


class TestPackPolygonAutoDetection:
    """Test automatic circle count detection."""

    def test_auto_detection_returns_reasonable_count(self, simple_rectangle):
        """Auto-detection should return 2-10 circles."""
        circles = pack_polygon(simple_rectangle, n=None, iterations=100)
        assert 2 <= len(circles) <= 10

    def test_auto_detection_with_small_polygon(self, unit_square):
        """Small polygon should get a reasonable number of circles."""
        circles = pack_polygon(unit_square, n=None, iterations=100)
        assert 2 <= len(circles) <= 10  # Should be within the auto-detect range

    def test_auto_detection_with_complex_shape(self, l_shape):
        """Complex shape should get more circles."""
        circles = pack_polygon(l_shape, n=None, iterations=100)
        assert 3 <= len(circles) <= 10


class TestPackPolygonCartesian:
    """Test Cartesian (non-geographic) mode."""

    def test_cartesian_mode_explicit(self, simple_rectangle):
        """Should work with use_projection=False."""
        circles = pack_polygon(simple_rectangle, n=3, use_projection=False, iterations=100)
        assert len(circles) == 3
        # Check circles are within polygon bounds
        for circle in circles:
            assert 0 <= circle["centroid_x"] <= 2
            assert 0 <= circle["centroid_y"] <= 1

    def test_circles_fit_within_bounds(self, simple_rectangle):
        """Circle centers should be approximately within polygon bounds."""
        circles = pack_polygon(simple_rectangle, n=5, iterations=200)
        for circle in circles:
            # Centers should be roughly within bounds (allowing some tolerance)
            assert -0.5 <= circle["centroid_x"] <= 2.5
            assert -0.5 <= circle["centroid_y"] <= 1.5


class TestPackPolygonGeographic:
    """Test geographic (lat/lon) mode."""

    def test_geographic_mode(self, geographic_polygon):
        """Should work with use_projection=True for lat/lon coords."""
        circles = pack_polygon(geographic_polygon, n=3, use_projection=True, iterations=100)
        assert len(circles) == 3

    def test_geographic_coordinates_in_range(self, geographic_polygon):
        """Geographic coordinates should be in valid lat/lon ranges."""
        circles = pack_polygon(geographic_polygon, n=4, use_projection=True, iterations=100)
        for circle in circles:
            # Longitude should be around -122 (SF)
            assert -123 < circle["centroid_x"] < -121
            # Latitude should be around 37 (SF)
            assert 36 < circle["centroid_y"] < 38

    def test_geographic_radius_is_reasonable(self, geographic_polygon):
        """Radii in geographic mode should be small (degrees)."""
        circles = pack_polygon(geographic_polygon, n=3, use_projection=True, iterations=100)
        for circle in circles:
            # Radius in degrees should be small for small area
            assert 0 < circle["radius"] < 0.1


class TestPackPolygonDeterminism:
    """Test deterministic behavior."""

    def test_deterministic_with_fixed_seed(self, simple_rectangle, random_seed):
        """Should produce same results with same seed."""
        circles1 = pack_polygon(simple_rectangle, n=3, iterations=50)
        # Reset seed
        np.random.seed(random_seed)
        import torch

        torch.manual_seed(random_seed)
        circles2 = pack_polygon(simple_rectangle, n=3, iterations=50)

        # Results should be very similar (allowing for floating point differences)
        for c1, c2 in zip(circles1, circles2):
            assert np.isclose(c1["radius"], c2["radius"], rtol=1e-3)
            assert np.isclose(c1["centroid_x"], c2["centroid_x"], rtol=1e-3)
            assert np.isclose(c1["centroid_y"], c2["centroid_y"], rtol=1e-3)


class TestPackPolygonParameters:
    """Test parameter variations."""

    def test_higher_resolution(self, simple_rectangle):
        """Should work with different resolution values."""
        circles = pack_polygon(simple_rectangle, n=3, resolution=128, iterations=100)
        assert len(circles) == 3

    def test_fewer_iterations(self, simple_rectangle):
        """Should work with fewer iterations (less optimal)."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)
        assert len(circles) == 3

    def test_verbose_mode(self, simple_rectangle, capsys):
        """Verbose mode should print progress."""
        pack_polygon(simple_rectangle, n=2, iterations=100, verbose=True)
        captured = capsys.readouterr()
        # Should have some output when verbose=True
        assert len(captured.out) > 0

    def test_quiet_mode(self, simple_rectangle, capsys):
        """Non-verbose mode should be quiet."""
        pack_polygon(simple_rectangle, n=2, iterations=100, verbose=False)
        captured = capsys.readouterr()
        # Should have minimal or no output when verbose=False
        assert "Iteration" not in captured.out


class TestPackPolygonEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_circle(self, unit_square):
        """Should handle n=1 (single circle)."""
        circles = pack_polygon(unit_square, n=1, iterations=100)
        assert len(circles) == 1
        # Single circle should be roughly centered
        assert 0.3 < circles[0]["centroid_x"] < 0.7
        assert 0.3 < circles[0]["centroid_y"] < 0.7

    def test_many_circles(self, simple_rectangle):
        """Should handle larger number of circles."""
        circles = pack_polygon(simple_rectangle, n=15, iterations=100)
        assert len(circles) == 15

    def test_triangle_shape(self, equilateral_triangle):
        """Should work with triangular polygon."""
        circles = pack_polygon(equilateral_triangle, n=3, iterations=100)
        assert len(circles) == 3

    def test_complex_shape(self, l_shape):
        """Should work with concave polygons."""
        circles = pack_polygon(l_shape, n=5, iterations=100)
        assert len(circles) == 5
