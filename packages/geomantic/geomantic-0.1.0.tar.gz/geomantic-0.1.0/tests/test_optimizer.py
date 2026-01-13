"""Tests for geomantic.optimizer module."""

import torch
import numpy as np

from geomantic.optimizer import (
    CircleModel,
    DifferentiableRenderer,
    optimize_circles,
    estimate_optimal_circles,
)


class TestCircleModel:
    """Test CircleModel class."""

    def test_initialization(self, device):
        """Should initialize with correct number of circles."""
        model = CircleModel(n_circles=5).to(device)
        assert model.centers.shape == (5, 2)
        assert model.log_radii.shape == (5,)

    def test_forward_pass_shape(self, device):
        """Forward pass should produce mask of correct shape."""
        model = CircleModel(n_circles=3).to(device)
        # Create a simple grid
        x = torch.linspace(0, 1, 10, device=device)
        y = torch.linspace(0, 1, 10, device=device)
        grid_x, grid_y = torch.meshgrid(x, y, indexing="ij")
        grid = torch.stack([grid_x, grid_y], dim=-1)

        mask = model(grid, sharpness=10.0)
        assert mask.shape == (10, 10)

    def test_mask_values_in_range(self, device):
        """Mask values should be in [0, 1]."""
        model = CircleModel(n_circles=3).to(device)
        x = torch.linspace(0, 1, 20, device=device)
        y = torch.linspace(0, 1, 20, device=device)
        grid_x, grid_y = torch.meshgrid(x, y, indexing="ij")
        grid = torch.stack([grid_x, grid_y], dim=-1)

        mask = model(grid, sharpness=10.0)
        assert torch.all(mask >= 0)
        assert torch.all(mask <= 1)

    def test_sharpness_effect(self, device):
        """Higher sharpness should produce sharper boundaries."""
        model = CircleModel(n_circles=1).to(device)
        # Set specific center and radius
        model.centers.data = torch.tensor([[0.5, 0.5]], device=device)
        model.log_radii.data = torch.tensor([np.log(0.2)], device=device)

        x = torch.linspace(0, 1, 50, device=device)
        y = torch.linspace(0, 1, 50, device=device)
        grid_x, grid_y = torch.meshgrid(x, y, indexing="ij")
        grid = torch.stack([grid_x, grid_y], dim=-1)

        mask_soft = model(grid, sharpness=1.0)
        mask_sharp = model(grid, sharpness=100.0)

        # Sharp mask should have more extreme values (closer to 0 or 1)
        assert mask_sharp.std() > mask_soft.std()


class TestDifferentiableRenderer:
    """Test DifferentiableRenderer class."""

    def test_initialization(self, device):
        """Should initialize with correct resolution."""
        renderer = DifferentiableRenderer(resolution=128, device=device)
        assert renderer.resolution == 128
        assert renderer.device == device

    def test_grid_shape(self, device):
        """Grid should have correct shape."""
        renderer = DifferentiableRenderer(resolution=64, device=device)
        assert renderer.grid.shape == (64, 64, 2)

    def test_rasterize_simple_square(self, unit_square, device):
        """Should rasterize a simple square."""
        from shapely.geometry import Polygon

        renderer = DifferentiableRenderer(resolution=128, device=device)
        mask = renderer.rasterize_polygon(Polygon(unit_square))

        assert mask.shape == (128, 128)
        # Mask should have some interior points (value ~1)
        assert mask.max() > 0.5
        # Mask should have some exterior points (value ~0)
        assert mask.min() < 0.5

    def test_rasterize_triangle(self, equilateral_triangle, device):
        """Should rasterize a triangle."""
        from shapely.geometry import Polygon

        renderer = DifferentiableRenderer(resolution=128, device=device)
        mask = renderer.rasterize_polygon(Polygon(equilateral_triangle))

        assert mask.shape == (128, 128)
        # Triangle should cover less area than a square
        coverage = mask.sum() / (128 * 128)
        assert 0.1 < coverage < 0.9


class TestOptimizeCircles:
    """Test optimize_circles function."""

    def test_returns_correct_shapes(self, simple_rectangle, device):
        """Should return arrays of correct shapes."""
        from shapely.geometry import Polygon

        centers, radii = optimize_circles(
            Polygon(simple_rectangle),
            n_circles=5,
            resolution=64,
            iterations=50,
            device=device,
            verbose=False,
        )
        assert centers.shape == (5, 2)
        assert radii.shape == (5,)

    def test_loss_decreases(self, simple_rectangle, device, random_seed):
        """Loss should decrease over iterations."""
        # Run optimization and track loss manually
        from shapely.geometry import Polygon
        from geomantic.optimizer import DifferentiableRenderer, CircleModel
        import torch.optim as optim

        renderer = DifferentiableRenderer(resolution=64, device=device)
        target_mask = renderer.rasterize_polygon(Polygon(simple_rectangle))

        model = CircleModel(n_circles=3).to(device)
        optimizer = optim.Adam(model.parameters(), lr=0.08)

        losses = []
        for i in range(100):
            optimizer.zero_grad()
            sharpness = 1.0 + (100.0 - 1.0) * (i / 100)
            gen_mask = model(renderer.grid, sharpness=sharpness)
            intersection = (gen_mask * target_mask).sum()
            union = gen_mask.sum() + target_mask.sum() - intersection
            loss = 1.0 - (intersection / (union + 1e-6))
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        # Loss should generally decrease
        initial_loss = np.mean(losses[:10])
        final_loss = np.mean(losses[-10:])
        assert final_loss < initial_loss

    def test_radii_are_positive(self, simple_rectangle, device):
        """All returned radii should be positive."""
        from shapely.geometry import Polygon

        _, radii = optimize_circles(
            Polygon(simple_rectangle),
            n_circles=4,
            resolution=64,
            iterations=50,
            device=device,
            verbose=False,
        )
        assert np.all(radii > 0)

    def test_centers_within_bounds(self, simple_rectangle, device):
        """Circle centers should be approximately within polygon bounds."""
        from shapely.geometry import Polygon

        centers, _ = optimize_circles(
            Polygon(simple_rectangle),
            n_circles=5,
            resolution=64,
            iterations=100,
            device=device,
            verbose=False,
        )
        # Rectangle is (0,0) to (2,1), allow some margin
        assert np.all(centers[:, 0] >= -0.5)
        assert np.all(centers[:, 0] <= 2.5)
        assert np.all(centers[:, 1] >= -0.5)
        assert np.all(centers[:, 1] <= 1.5)

    def test_different_iteration_counts(self, unit_square, device):
        """Should work with different iteration counts."""
        from shapely.geometry import Polygon

        for iterations in [10, 50, 100]:
            centers, radii = optimize_circles(
                Polygon(unit_square),
                n_circles=3,
                resolution=64,
                iterations=iterations,
                device=device,
                verbose=False,
            )
            assert centers.shape == (3, 2)
            assert radii.shape == (3,)


class TestEstimateOptimalCircles:
    """Test estimate_optimal_circles function."""

    def test_returns_integer(self, simple_rectangle, device):
        """Should return an integer circle count."""
        from shapely.geometry import Polygon

        n_optimal = estimate_optimal_circles(
            Polygon(simple_rectangle),
            min_circles=2,
            max_circles=6,
            resolution=64,
            iterations=50,
            device=device,
        )
        assert isinstance(n_optimal, (int, np.integer))

    def test_within_specified_range(self, simple_rectangle, device):
        """Should return value within min/max range."""
        from shapely.geometry import Polygon

        n_optimal = estimate_optimal_circles(
            Polygon(simple_rectangle),
            min_circles=3,
            max_circles=7,
            resolution=64,
            iterations=50,
            device=device,
        )
        assert 3 <= n_optimal <= 7

    def test_reasonable_for_small_polygon(self, unit_square, device):
        """Small polygon should get a reasonable number of circles."""
        from shapely.geometry import Polygon

        n_optimal = estimate_optimal_circles(
            Polygon(unit_square),
            min_circles=2,
            max_circles=10,
            resolution=64,
            iterations=50,
            device=device,
        )
        # Should be within the specified range
        assert 2 <= n_optimal <= 10

    def test_reasonable_for_large_polygon(self, simple_rectangle, device):
        """Larger polygon might need more circles."""
        from shapely.geometry import Polygon

        n_optimal = estimate_optimal_circles(
            Polygon(simple_rectangle),
            min_circles=2,
            max_circles=10,
            resolution=64,
            iterations=50,
            device=device,
        )
        assert 2 <= n_optimal <= 10


class TestSharpnessAnnealing:
    """Test sharpness annealing behavior."""

    def test_sharpness_increases_over_time(self):
        """Sharpness should increase from start to end over iterations."""
        from geomantic.constants import START_SHARPNESS, END_SHARPNESS

        iterations = 100

        sharpness_values = []
        for i in range(iterations):
            sharpness = START_SHARPNESS + (END_SHARPNESS - START_SHARPNESS) * (i / iterations)
            sharpness_values.append(sharpness)

        # First value should be start
        assert np.isclose(sharpness_values[0], START_SHARPNESS)
        # Last value should be close to end (not exact due to division)
        assert np.isclose(sharpness_values[-1], END_SHARPNESS, rtol=0.01)
        # Should be monotonically increasing
        assert all(
            sharpness_values[i] <= sharpness_values[i + 1] for i in range(len(sharpness_values) - 1)
        )


class TestDeviceHandling:
    """Test PyTorch device handling."""

    def test_cpu_device(self, simple_rectangle):
        """Should work with CPU device."""
        from shapely.geometry import Polygon

        centers, radii = optimize_circles(
            Polygon(simple_rectangle),
            n_circles=3,
            resolution=64,
            iterations=50,
            device="cpu",
            verbose=False,
        )
        assert centers.shape == (3, 2)
        assert radii.shape == (3,)

    def test_auto_device_selection(self, simple_rectangle):
        """Should auto-select device when device=None."""
        from shapely.geometry import Polygon

        centers, radii = optimize_circles(
            Polygon(simple_rectangle),
            n_circles=3,
            resolution=64,
            iterations=50,
            device=None,  # Auto-select
            verbose=False,
        )
        assert centers.shape == (3, 2)
        assert radii.shape == (3,)
