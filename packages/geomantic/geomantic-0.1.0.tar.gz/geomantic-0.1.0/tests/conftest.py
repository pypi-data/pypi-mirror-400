"""Shared pytest fixtures for geomantic tests."""

import pytest
import torch
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


@pytest.fixture(scope="session", autouse=True)
def matplotlib_backend():
    """Set matplotlib to non-interactive backend for testing.

    This prevents plt.show() from opening GUI windows during tests.
    The 'Agg' backend renders to memory only.
    """
    matplotlib.use("Agg")
    # Also disable interactive mode
    plt.ioff()
    yield
    # Cleanup after all tests
    plt.close("all")


@pytest.fixture(autouse=True)
def cleanup_plots():
    """Close all matplotlib figures after each test.

    Prevents memory leaks from accumulating plot figures.
    """
    yield
    plt.close("all")


@pytest.fixture
def simple_rectangle():
    """2x1 rectangle for basic Cartesian tests."""
    return [(0, 0), (2, 0), (2, 1), (0, 1), (0, 0)]


@pytest.fixture
def unit_square():
    """1x1 square for simple tests."""
    return [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]


@pytest.fixture
def equilateral_triangle():
    """Equilateral triangle for symmetry tests."""
    return [(0, 0), (1, 0), (0.5, 0.866), (0, 0)]


@pytest.fixture
def l_shape():
    """L-shaped polygon for concave shape tests."""
    return [
        (0, 0),
        (2, 0),
        (2, 1),
        (1, 1),
        (1, 2),
        (0, 2),
        (0, 0),
    ]


@pytest.fixture
def simple_pentagon():
    """Regular pentagon for testing."""
    angles = np.linspace(0, 2 * np.pi, 6)[:-1]  # 5 points
    points = [(np.cos(a), np.sin(a)) for a in angles]
    points.append(points[0])  # Close the polygon
    return points


@pytest.fixture
def geographic_polygon():
    """Small geographic polygon in San Francisco (lat/lon)."""
    # Small square in SF Marina District
    return [
        (-122.44, 37.80),
        (-122.43, 37.80),
        (-122.43, 37.81),
        (-122.44, 37.81),
        (-122.44, 37.80),
    ]


@pytest.fixture(params=["cpu"])
def device(request):
    """PyTorch device for reproducible tests.

    Only CPU by default. Can be extended to test CUDA if available.
    """
    return request.param


@pytest.fixture
def random_seed():
    """Fixed random seed for reproducible tests."""
    seed = 42
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    return seed
