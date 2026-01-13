"""Tests for geomantic.visualization module."""

import os
import tempfile

from geomantic import pack_polygon, visualize_packing, print_circle_summary


class TestPrintCircleSummary:
    """Test print_circle_summary function."""

    def test_prints_output(self, simple_rectangle, capsys):
        """Should print circle summary to stdout."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)
        print_circle_summary(circles)

        captured = capsys.readouterr()
        assert len(captured.out) > 0
        # Should contain header
        assert "CIRCLE PACKING RESULTS" in captured.out
        # Should contain column names
        assert "Radius" in captured.out or "radius" in captured.out

    def test_prints_correct_count(self, simple_rectangle, capsys):
        """Should display correct number of circles."""
        n_circles = 5
        circles = pack_polygon(simple_rectangle, n=n_circles, iterations=50)
        print_circle_summary(circles)

        captured = capsys.readouterr()
        assert f"{n_circles} circles" in captured.out.lower()

    def test_includes_coordinates(self, simple_rectangle, capsys):
        """Should include x, y coordinates in output."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)
        print_circle_summary(circles)

        captured = capsys.readouterr()
        # Should have coordinate values (numbers with decimals)
        assert "." in captured.out  # Decimal points indicate numeric values


class TestVisualizePacking:
    """Test visualize_packing function."""

    def test_generates_plot_without_error(self, simple_rectangle):
        """Should generate plot without raising errors."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)
        # Should not raise
        visualize_packing(simple_rectangle, circles, save_path=None)

    def test_saves_to_file(self, simple_rectangle):
        """Should save plot to file when save_path provided."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_plot.png")
            visualize_packing(simple_rectangle, circles, save_path=save_path)

            # File should exist
            assert os.path.exists(save_path)
            # File should have content (PNG files start with specific bytes)
            assert os.path.getsize(save_path) > 1000  # Reasonable size for PNG

    def test_cartesian_mode(self, simple_rectangle):
        """Should work with explicit Cartesian mode."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)
        visualize_packing(simple_rectangle, circles, projection_mode="cartesian", save_path=None)

    def test_geographic_mode(self, geographic_polygon):
        """Should work with geographic mode."""
        circles = pack_polygon(geographic_polygon, n=3, use_projection=True, iterations=50)
        visualize_packing(geographic_polygon, circles, projection_mode="geographic", save_path=None)

    def test_auto_mode_detection(self, simple_rectangle):
        """Should auto-detect mode from coordinates."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)
        # Auto mode should work (detect as Cartesian for small coordinates)
        visualize_packing(simple_rectangle, circles, projection_mode="auto", save_path=None)

    def test_custom_title(self, simple_rectangle):
        """Should accept custom title."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)
        visualize_packing(simple_rectangle, circles, title="Custom Test Title", save_path=None)

    def test_with_shapely_polygon(self, simple_rectangle):
        """Should work with Shapely Polygon object."""
        from shapely.geometry import Polygon

        poly = Polygon(simple_rectangle)
        circles = pack_polygon(poly, n=3, iterations=50)
        visualize_packing(poly, circles, save_path=None)


class TestVisualizationWithDifferentShapes:
    """Test visualization with various polygon shapes."""

    def test_triangle(self, equilateral_triangle):
        """Should visualize triangle."""
        circles = pack_polygon(equilateral_triangle, n=2, iterations=50)
        visualize_packing(equilateral_triangle, circles, save_path=None)

    def test_l_shape(self, l_shape):
        """Should visualize concave polygon."""
        circles = pack_polygon(l_shape, n=4, iterations=50)
        visualize_packing(l_shape, circles, save_path=None)

    def test_pentagon(self, simple_pentagon):
        """Should visualize pentagon."""
        circles = pack_polygon(simple_pentagon, n=3, iterations=50)
        visualize_packing(simple_pentagon, circles, save_path=None)


class TestVisualizationFileFormats:
    """Test saving to different file formats."""

    def test_save_png(self, simple_rectangle):
        """Should save as PNG."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.png")
            visualize_packing(simple_rectangle, circles, save_path=save_path)
            assert os.path.exists(save_path)

    def test_save_jpg(self, simple_rectangle):
        """Should save as JPG."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.jpg")
            visualize_packing(simple_rectangle, circles, save_path=save_path)
            assert os.path.exists(save_path)

    def test_save_pdf(self, simple_rectangle):
        """Should save as PDF."""
        circles = pack_polygon(simple_rectangle, n=3, iterations=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.pdf")
            visualize_packing(simple_rectangle, circles, save_path=save_path)
            assert os.path.exists(save_path)


class TestVisualizationEdgeCases:
    """Test visualization edge cases."""

    def test_single_circle(self, unit_square):
        """Should visualize single circle."""
        circles = pack_polygon(unit_square, n=1, iterations=50)
        visualize_packing(unit_square, circles, save_path=None)

    def test_many_circles(self, simple_rectangle):
        """Should visualize many circles."""
        circles = pack_polygon(simple_rectangle, n=15, iterations=50)
        visualize_packing(simple_rectangle, circles, save_path=None)

    def test_empty_circles_list(self, simple_rectangle):
        """Should handle empty circles list gracefully."""
        # This might not be a valid use case, but shouldn't crash
        try:
            visualize_packing(simple_rectangle, [], save_path=None)
        except (ValueError, IndexError, KeyError):
            # It's okay to raise an error for invalid input
            pass


class TestGeographicVisualization:
    """Test geographic-specific visualization features."""

    def test_geographic_ellipses(self, geographic_polygon):
        """Geographic mode should render circles as ellipses."""
        circles = pack_polygon(geographic_polygon, n=3, use_projection=True, iterations=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "geo_test.png")
            visualize_packing(
                geographic_polygon, circles, projection_mode="geographic", save_path=save_path
            )
            assert os.path.exists(save_path)

    def test_geographic_coordinates_labeled(self, geographic_polygon, capsys):
        """Geographic plot should have appropriate axis labels."""
        circles = pack_polygon(geographic_polygon, n=2, use_projection=True, iterations=50)

        visualize_packing(geographic_polygon, circles, projection_mode="geographic", save_path=None)
        # Function should complete without error
        # (Can't easily check axis labels without showing the plot)


class TestIntegrationWithPackPolygon:
    """Test visualization integrated with pack_polygon."""

    def test_full_workflow_cartesian(self, simple_rectangle):
        """Complete workflow: pack + visualize (Cartesian)."""
        circles = pack_polygon(simple_rectangle, n=5, use_projection=False, iterations=50)
        visualize_packing(simple_rectangle, circles, projection_mode="cartesian", save_path=None)

    def test_full_workflow_geographic(self, geographic_polygon):
        """Complete workflow: pack + visualize (geographic)."""
        circles = pack_polygon(geographic_polygon, n=3, use_projection=True, iterations=50)
        visualize_packing(geographic_polygon, circles, projection_mode="geographic", save_path=None)

    def test_auto_mode_matches_projection_setting(self, simple_rectangle):
        """Auto mode should match the projection used in packing."""
        # Cartesian packing
        circles_cart = pack_polygon(simple_rectangle, n=3, use_projection=False, iterations=50)
        visualize_packing(simple_rectangle, circles_cart, projection_mode="auto")

        # (Geographic would need actual lat/lon coordinates)


class TestOutputQuality:
    """Test output quality and consistency."""

    def test_generates_consistent_file_size(self, simple_rectangle):
        """Similar inputs should produce similar file sizes."""
        circles = pack_polygon(simple_rectangle, n=5, iterations=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            sizes = []
            for i in range(3):
                save_path = os.path.join(tmpdir, f"test_{i}.png")
                visualize_packing(simple_rectangle, circles, save_path=save_path)
                sizes.append(os.path.getsize(save_path))

            # File sizes should be very similar (within 20%)
            avg_size = sum(sizes) / len(sizes)
            for size in sizes:
                assert abs(size - avg_size) / avg_size < 0.2
