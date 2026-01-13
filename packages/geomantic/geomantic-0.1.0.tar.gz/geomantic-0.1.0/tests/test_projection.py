"""Tests for geomantic.projection module."""

import pytest
import numpy as np
from shapely.geometry import Polygon

from geomantic.projection import MetricProjector, MetricNormalizer


class TestMetricProjector:
    """Test MetricProjector class for GPS↔UTM transformations."""

    def test_initialization_with_polygon(self, geographic_polygon):
        """Should initialize and auto-detect UTM zone from polygon."""
        poly = Polygon(geographic_polygon)
        projector = MetricProjector(polygon=poly)
        # San Francisco should have a UTM CRS
        assert projector.utm is not None
        assert projector.wgs84 is not None

    def test_initialization_with_manual_zone(self):
        """Should initialize with manual UTM zone."""
        projector = MetricProjector(utm_zone=10)
        assert projector.utm is not None

    def test_initialization_without_args_raises(self):
        """Should raise ValueError if no polygon or zone provided."""
        with pytest.raises(ValueError, match="Must provide either"):
            MetricProjector()

    def test_poly_to_meters(self, geographic_polygon):
        """Should convert GPS coordinates to metric (UTM)."""
        poly = Polygon(geographic_polygon)
        projector = MetricProjector(polygon=poly)

        poly_meters = projector.poly_to_meters(poly)

        assert isinstance(poly_meters, Polygon)
        # UTM coordinates should be large numbers (hundreds of thousands)
        bounds = poly_meters.bounds
        assert all(abs(coord) > 1000 for coord in bounds)

    def test_coords_to_gps(self, geographic_polygon):
        """Should convert metric coordinates back to GPS."""
        poly = Polygon(geographic_polygon)
        projector = MetricProjector(polygon=poly)

        # Convert to meters
        poly_meters = projector.poly_to_meters(poly)
        centroid_meters = poly_meters.centroid

        # Convert back to GPS
        lon, lat = projector.coords_to_gps(centroid_meters.x, centroid_meters.y)

        # Should be close to original centroid
        original_centroid = poly.centroid
        assert abs(lon - original_centroid.x) < 0.001
        assert abs(lat - original_centroid.y) < 0.001

    def test_round_trip_preserves_coordinates(self, geographic_polygon):
        """GPS → meters → GPS should preserve coordinates."""
        poly = Polygon(geographic_polygon)
        projector = MetricProjector(polygon=poly)

        # Round trip
        poly_meters = projector.poly_to_meters(poly)
        coords_meters = list(poly_meters.exterior.coords)

        coords_back = []
        for x_m, y_m in coords_meters:
            lon, lat = projector.coords_to_gps(x_m, y_m)
            coords_back.append((lon, lat))

        poly_back = Polygon(coords_back)

        # Should match within reasonable tolerance
        original_coords = np.array(poly.exterior.coords)
        back_coords = np.array(poly_back.exterior.coords)

        assert np.allclose(original_coords, back_coords, atol=1e-6)

    def test_different_utm_zones(self):
        """Should work with polygons in different UTM zones."""
        # New York (UTM zone 18N)
        ny_polygon = Polygon([(-74.0, 40.7), (-73.9, 40.7), (-73.9, 40.8), (-74.0, 40.8)])
        projector_ny = MetricProjector(polygon=ny_polygon)

        # San Francisco (UTM zone 10N)
        sf_polygon = Polygon([(-122.4, 37.8), (-122.3, 37.8), (-122.3, 37.9), (-122.4, 37.9)])
        projector_sf = MetricProjector(polygon=sf_polygon)

        # Different UTM zones (different EPSG codes)
        assert projector_ny.utm != projector_sf.utm


class TestMetricNormalizer:
    """Test MetricNormalizer class for scaling to [0,1]."""

    def test_initialization(self):
        """Should initialize with a polygon."""
        # Create a simple polygon in meters
        poly_meters = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])

        normalizer = MetricNormalizer(poly_meters)

        assert normalizer.center_x is not None
        assert normalizer.center_y is not None
        assert normalizer.scale is not None

    def test_normalize(self):
        """Should normalize polygon to [0,1] range."""
        poly_meters = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])

        normalizer = MetricNormalizer(poly_meters)
        poly_norm = normalizer.normalize(poly_meters)

        # Normalized coordinates should be roughly in [0, 1]
        coords = np.array(poly_norm.exterior.coords)
        assert np.all(coords >= -0.1)  # Allow small margin
        assert np.all(coords <= 1.1)

        # Should have one dimension at or near the padding boundary
        x_range = coords[:, 0].max() - coords[:, 0].min()
        y_range = coords[:, 1].max() - coords[:, 1].min()
        max_range = max(x_range, y_range)
        assert 0.6 < max_range <= 1.0  # Should use most of the space

    def test_denormalize(self):
        """Should denormalize back to original scale."""
        poly_meters = Polygon([(100, 50), (200, 50), (200, 150), (100, 150)])

        normalizer = MetricNormalizer(poly_meters)

        # Create some normalized circle parameters
        centers_norm = np.array([[0.5, 0.5], [0.3, 0.7]])
        radii_norm = np.array([0.1, 0.15])

        # Denormalize
        centers_back, radii_back = normalizer.denormalize(centers_norm, radii_norm)

        # Centers should be in meters (around 100-200 range)
        assert centers_back.shape == (2, 2)
        assert radii_back.shape == (2,)
        assert np.all(centers_back > 0)
        assert np.all(radii_back > 0)

    def test_round_trip(self):
        """Normalize → denormalize should preserve polygon."""
        poly_meters = Polygon([(0, 0), (500, 0), (500, 250), (0, 250)])

        normalizer = MetricNormalizer(poly_meters)

        # Normalize
        poly_norm = normalizer.normalize(poly_meters)

        # Get some points from normalized polygon
        coords_norm = np.array(poly_norm.exterior.coords[:-1])  # Exclude last (duplicate) point

        # Denormalize points
        centers_norm = coords_norm
        radii_norm = np.ones(len(coords_norm)) * 0.1

        centers_back, _ = normalizer.denormalize(centers_norm, radii_norm)

        # Should be close to original coordinates
        original_coords = np.array(poly_meters.exterior.coords[:-1])
        assert np.allclose(centers_back, original_coords, atol=1.0)

    def test_aspect_ratio_preserved(self):
        """Should preserve aspect ratio when normalizing."""
        # Wide rectangle: 400m x 100m
        poly_meters = Polygon([(0, 0), (400, 0), (400, 100), (0, 100)])

        normalizer = MetricNormalizer(poly_meters)
        poly_norm = normalizer.normalize(poly_meters)

        coords = np.array(poly_norm.exterior.coords)
        x_range = coords[:, 0].max() - coords[:, 0].min()
        y_range = coords[:, 1].max() - coords[:, 1].min()

        # Aspect ratio should be preserved
        original_aspect = 400.0 / 100.0
        normalized_aspect = x_range / y_range if y_range > 0 else float("inf")
        assert abs(normalized_aspect - original_aspect) < 0.1


class TestIntegratedProjectionWorkflow:
    """Test complete projection + normalization workflow."""

    def test_full_pipeline(self, geographic_polygon):
        """Test GPS → UTM → normalized → denormalized → GPS."""
        poly_gps = Polygon(geographic_polygon)

        # Step 1: GPS to meters
        projector = MetricProjector(polygon=poly_gps)
        poly_meters = projector.poly_to_meters(poly_gps)

        # Step 2: Normalize to [0,1]
        normalizer = MetricNormalizer(poly_meters)
        poly_norm = normalizer.normalize(poly_meters)

        # Normalized values in [0,1] (with padding)
        coords_norm = np.array(poly_norm.exterior.coords)
        assert np.all(coords_norm >= -0.1)
        assert np.all(coords_norm <= 1.1)

        # Step 3: Simulate circle optimization result
        centers_norm = np.array([[0.3, 0.3], [0.7, 0.7]])
        radii_norm = np.array([0.1, 0.1])

        # Step 4: Denormalize back to meters
        centers_meters, radii_meters = normalizer.denormalize(centers_norm, radii_norm)

        # Should be valid meter coordinates
        assert centers_meters.shape == (2, 2)
        assert np.all(np.abs(centers_meters) > 100)  # Should be in UTM range

        # Step 5: Convert back to GPS
        for cx_m, cy_m in centers_meters:
            lon, lat = projector.coords_to_gps(cx_m, cy_m)
            # Should be valid GPS coordinates
            assert -180 < lon < 180
            assert -90 < lat < 90

    def test_circle_radius_conversion(self):
        """Test converting circle radius through projection."""
        # Small square in SF
        poly_gps = Polygon([(-122.44, 37.80), (-122.43, 37.80), (-122.43, 37.81), (-122.44, 37.81)])

        projector = MetricProjector(polygon=poly_gps)
        poly_meters = projector.poly_to_meters(poly_gps)

        normalizer = MetricNormalizer(poly_meters)

        # Simulate a circle with radius 0.1 in normalized space
        centers_norm = np.array([[0.5, 0.5]])
        radii_norm = np.array([0.1])

        # Convert to meters
        _, radii_meters = normalizer.denormalize(centers_norm, radii_norm)

        # Radius in meters should be reasonable (tens to hundreds of meters)
        assert 10 < radii_meters[0] < 10000


class TestEdgeCases:
    """Test edge cases in projection and normalization."""

    def test_very_small_polygon(self):
        """Should handle very small geographic areas."""
        # 10m x 10m square in SF (approximately)
        poly_gps = Polygon(
            [
                (-122.4000, 37.8000),
                (-122.3999, 37.8000),
                (-122.3999, 37.8001),
                (-122.4000, 37.8001),
            ]
        )

        projector = MetricProjector(polygon=poly_gps)
        poly_meters = projector.poly_to_meters(poly_gps)

        normalizer = MetricNormalizer(poly_meters)
        poly_norm = normalizer.normalize(poly_meters)

        coords = np.array(poly_norm.exterior.coords)
        assert np.all(coords >= -0.2)
        assert np.all(coords <= 1.2)

    def test_elongated_polygon(self):
        """Should handle very elongated shapes."""
        # Very wide, thin polygon
        poly_gps = Polygon(
            [
                (-122.5, 37.8),
                (-122.3, 37.8),
                (-122.3, 37.801),
                (-122.5, 37.801),
            ]
        )

        projector = MetricProjector(polygon=poly_gps)
        poly_meters = projector.poly_to_meters(poly_gps)

        normalizer = MetricNormalizer(poly_meters)
        poly_norm = normalizer.normalize(poly_meters)

        # Should still normalize correctly
        coords = np.array(poly_norm.exterior.coords)
        assert np.all(coords >= -0.2)
        assert np.all(coords <= 1.2)
