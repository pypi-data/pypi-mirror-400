"""
Optimization engine for circle packing using differentiable rendering.

This module contains the PyTorch-based optimization logic that fits circles
to polygons using gradient descent and soft rasterization.
"""

from typing import Tuple, Optional, List
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from matplotlib.path import Path
from shapely.geometry import Polygon

from .constants import EPSILON, ELBOW_THRESHOLD_RATIO


class DifferentiableRenderer:
    """
    Renders shapes to a grid using differentiable operations.

    This class creates a spatial grid and provides methods for rasterizing
    polygons and circles in a way that supports gradient-based optimization.

    Attributes:
        resolution: Grid resolution (resolution × resolution pixels)
        device: PyTorch device ('cuda' or 'cpu')
        grid: Tensor of shape (resolution, resolution, 2) containing (x, y) coords
    """

    def __init__(self, resolution: int, device: str):
        """
        Initialize the renderer with a spatial grid.

        Args:
            resolution: Number of pixels per dimension
            device: PyTorch device string ('cuda' or 'cpu')
        """
        self.resolution = resolution
        self.device = device
        linspace = torch.linspace(0, 1, resolution, device=device)
        y, x = torch.meshgrid(linspace, linspace, indexing="ij")
        self.grid = torch.stack([x, y], dim=-1)

    def rasterize_polygon(self, polygon: Polygon) -> torch.Tensor:
        """
        Convert a polygon to a binary mask on the grid.

        Args:
            polygon: Shapely polygon in [0, 1] normalized coordinates

        Returns:
            Binary tensor of shape (resolution, resolution)
        """
        x, y = np.meshgrid(np.linspace(0, 1, self.resolution), np.linspace(0, 1, self.resolution))
        points = np.vstack((x.flatten(), y.flatten())).T
        path = Path(list(polygon.exterior.coords))
        mask = path.contains_points(points).reshape(self.resolution, self.resolution)
        return torch.tensor(mask, dtype=torch.float32, device=self.device)


class CircleModel(nn.Module):
    """
    Neural network representing a set of circles with learnable parameters.

    This model optimizes circle positions and sizes using gradient descent.
    Circle radii are stored in log-space for numerical stability.

    Attributes:
        centers: Learnable tensor of shape (n_circles, 2) for circle centers
        log_radii: Learnable tensor of shape (n_circles,) for log(radius)
    """

    def __init__(
        self,
        n_circles: int,
        init_scale: float = 0.2,
        target_polygon: Optional[Polygon] = None,
    ):
        """
        Initialize circle parameters with random values.

        Args:
            n_circles: Number of circles to optimize
            init_scale: Scale of initialization (centers in [0.4±init_scale])
            target_polygon: Optional polygon to sample initial positions from interior
        """
        super().__init__()
        # Initialize centers inside the polygon if provided
        if target_polygon is not None:
            centers_init = self._sample_points_inside_polygon(target_polygon, n_circles)
        else:
            # Fallback: Initialize centers near the middle of [0, 1] space
            centers_init = torch.rand(n_circles, 2) * init_scale + (0.5 - init_scale / 2)

        self.centers = nn.Parameter(centers_init)
        # Initialize radii to small values (log space)
        self.log_radii = nn.Parameter(torch.ones(n_circles) * -3.0)

    def _sample_points_inside_polygon(self, polygon: Polygon, n_points: int) -> torch.Tensor:
        """
        Sample random points from inside a polygon using rejection sampling.

        Args:
            polygon: Shapely polygon in [0, 1] normalized coordinates
            n_points: Number of points to sample

        Returns:
            Tensor of shape (n_points, 2) with points inside the polygon
        """
        from shapely.geometry import Point

        min_x, min_y, max_x, max_y = polygon.bounds
        points: List[List[float]] = []

        # Rejection sampling: generate random points until we have enough inside
        max_attempts = n_points * 1000  # Prevent infinite loop
        attempts = 0

        while len(points) < n_points and attempts < max_attempts:
            x = np.random.uniform(min_x, max_x)
            y = np.random.uniform(min_y, max_y)
            if polygon.contains(Point(x, y)):
                points.append([x, y])
            attempts += 1

        # If we couldn't sample enough points (very thin polygon), fill with centroid
        while len(points) < n_points:
            cx, cy = polygon.centroid.x, polygon.centroid.y
            # Add small jitter
            points.append(
                [cx + np.random.uniform(-0.05, 0.05), cy + np.random.uniform(-0.05, 0.05)]
            )

        return torch.tensor(points, dtype=torch.float32)

    def forward(self, grid: torch.Tensor, sharpness: float) -> torch.Tensor:
        """
        Render circles to a soft mask using differentiable operations.

        Uses sigmoid-based soft masking and log-sum-exp for differentiable union.

        Args:
            grid: Spatial grid tensor of shape (H, W, 2)
            sharpness: Sigmoid sharpness parameter (higher = harder edges)

        Returns:
            Soft mask tensor of shape (H, W) representing union of circles
        """
        radii = torch.exp(self.log_radii)

        # Compute distances from each grid point to each circle center
        dists = torch.norm(grid.unsqueeze(0) - self.centers.view(-1, 1, 1, 2), dim=-1)

        # Soft circle masks using sigmoid
        circle_masks = torch.sigmoid(sharpness * (radii.view(-1, 1, 1) - dists))

        # Clamp to avoid log(0) issues
        eps = 1e-6
        circle_masks = torch.clamp(circle_masks, min=eps, max=1 - eps)

        # Differentiable union: 1 - prod(1 - mask_i) = 1 - exp(sum(log(1 - mask_i)))
        union_mask = 1.0 - torch.exp(torch.sum(torch.log(1 - circle_masks), dim=0))

        return union_mask


def optimize_circles(
    target_polygon: Polygon,
    n_circles: int,
    resolution: int = 256,
    iterations: int = 2000,
    learning_rate: float = 0.08,
    start_sharpness: float = 1.0,
    end_sharpness: float = 150.0,
    device: Optional[str] = None,
    verbose: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Optimize circle positions and sizes to approximate a polygon.

    Uses gradient descent with IoU loss and sharpness annealing to find
    optimal circle configurations.

    Args:
        target_polygon: Shapely polygon in [0, 1] normalized coordinates
        n_circles: Number of circles to fit
        resolution: Grid resolution for rasterization
        iterations: Number of optimization steps
        learning_rate: Adam optimizer learning rate
        start_sharpness: Initial sigmoid sharpness
        end_sharpness: Final sigmoid sharpness
        device: PyTorch device ('cuda', 'cpu', or None for auto)
        verbose: Whether to print progress

    Returns:
        Tuple of (centers, radii) in normalized [0, 1] coordinates
        - centers: np.ndarray of shape (n_circles, 2)
        - radii: np.ndarray of shape (n_circles,)
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # Setup renderer and target mask
    renderer = DifferentiableRenderer(resolution, device)
    target_mask = renderer.rasterize_polygon(target_polygon)

    if target_mask.sum() == 0:
        raise ValueError("Target polygon produced empty mask. Check polygon coordinates.")

    # Initialize model with polygon-aware initialization
    model = CircleModel(n_circles, target_polygon=target_polygon).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Sharpness annealing schedule
    sharpness_schedule = np.linspace(start_sharpness, end_sharpness, iterations)

    # Optimization loop
    for i in range(iterations):
        optimizer.zero_grad()

        # Generate circle mask
        generated_mask = model(renderer.grid, sharpness_schedule[i])

        # IoU loss: 1 - (intersection / union)
        intersection = (generated_mask * target_mask).sum()
        union = generated_mask.sum() + target_mask.sum() - intersection
        iou_loss = 1.0 - (intersection / (union + 1e-6))

        # Containment penalty: penalize circles whose centers are outside polygon
        containment_penalty = 0.0
        from shapely.geometry import Point

        for center in model.centers:
            cx, cy = center[0].item(), center[1].item()
            if not target_polygon.contains(Point(cx, cy)):
                # Distance to nearest edge (approximated by distance to centroid)
                poly_cx, poly_cy = target_polygon.centroid.x, target_polygon.centroid.y
                dist = torch.sqrt((center[0] - poly_cx) ** 2 + (center[1] - poly_cy) ** 2)
                containment_penalty += dist * 0.1  # Weight the penalty

        # Repulsion penalty: discourage circles from overlapping too much
        # This prevents all circles from collapsing to the same position
        repulsion_penalty = 0.0
        if n_circles > 1:
            for i in range(n_circles):
                for j in range(i + 1, n_circles):
                    dist = torch.norm(model.centers[i] - model.centers[j])
                    # Penalize circles that are too close (exponential repulsion)
                    min_dist = 0.05  # Minimum desired separation
                    if dist < min_dist:
                        repulsion_penalty += (min_dist - dist) ** 2

        # Combined loss with penalties
        loss = iou_loss + containment_penalty + repulsion_penalty * 0.5

        loss.backward()
        optimizer.step()

        if verbose and i % 200 == 0:
            iou_str = f"{iou_loss.item():.4f}"
            cont_str = (
                f"{containment_penalty:.4f}"
                if isinstance(containment_penalty, torch.Tensor)
                else f"{containment_penalty:.4f}"
            )
            rep_str = (
                f"{repulsion_penalty.item():.4f}"
                if isinstance(repulsion_penalty, torch.Tensor)
                else f"{repulsion_penalty:.4f}"
            )
            print(
                f"Iteration {i:04d} | IoU: {iou_str} | Contain: {cont_str} | "
                f"Repulsion: {rep_str} | Total: {loss.item():.4f}"
            )

    # Extract optimized parameters
    centers = model.centers.detach().cpu().numpy()
    radii = torch.exp(model.log_radii).detach().cpu().numpy()

    return centers, radii


def estimate_optimal_circles(
    target_polygon: Polygon,
    min_circles: int = 2,
    max_circles: int = 10,
    resolution: int = 128,
    iterations: int = 500,
    device: Optional[str] = None,
) -> int:
    """
    Estimate optimal number of circles using elbow method on IoU loss.

    Runs quick optimizations for different circle counts and finds the
    point of diminishing returns.

    Args:
        target_polygon: Shapely polygon in [0, 1] normalized coordinates
        min_circles: Minimum number of circles to test
        max_circles: Maximum number of circles to test
        resolution: Grid resolution (lower for speed)
        iterations: Number of iterations per test (lower for speed)
        device: PyTorch device ('cuda', 'cpu', or None for auto)

    Returns:
        Estimated optimal number of circles
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    renderer = DifferentiableRenderer(resolution, device)
    target_mask = renderer.rasterize_polygon(target_polygon)

    losses = []

    for n in range(min_circles, max_circles + 1):
        centers, radii = optimize_circles(
            target_polygon,
            n_circles=n,
            resolution=resolution,
            iterations=iterations,
            device=device,
            verbose=False,
        )

        # Evaluate final loss using optimized circles
        model = CircleModel(n).to(device)
        # Set optimized parameters
        model.centers.data = torch.tensor(centers, device=device, dtype=torch.float32)
        model.log_radii.data = torch.log(torch.tensor(radii, device=device, dtype=torch.float32))

        # Compute final loss with high sharpness
        with torch.no_grad():
            gen_mask = model(renderer.grid, sharpness=100.0)
            intersection = (gen_mask * target_mask).sum()
            union = gen_mask.sum() + target_mask.sum() - intersection
            loss = 1.0 - (intersection / (union + EPSILON))

        losses.append(loss.item())

    # Find elbow using simple derivative threshold
    losses = np.array(losses)
    if len(losses) < 3:
        return min_circles

    # Calculate rate of improvement
    improvements = -np.diff(losses)
    # Find where improvement drops below threshold (elbow point)
    threshold = np.mean(improvements) * ELBOW_THRESHOLD_RATIO
    elbow_idx = np.where(improvements < threshold)[0]

    if len(elbow_idx) > 0:
        return int(min_circles + elbow_idx[0])
    else:
        return max_circles
