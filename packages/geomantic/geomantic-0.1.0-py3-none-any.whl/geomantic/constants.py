"""Constants and default parameters for the geomantic package."""

# Physical constants
METERS_PER_DEGREE_LAT = 111320.0
"""Approximate meters per degree of latitude at the equator."""

# Optimization defaults
DEFAULT_RESOLUTION = 256
"""Default grid resolution for differentiable rendering."""

DEFAULT_ITERATIONS = 2000
"""Default number of optimization iterations."""

DEFAULT_LEARNING_RATE = 0.08
"""Default Adam optimizer learning rate."""

START_SHARPNESS = 1.0
"""Starting sharpness value for sigmoid activation (soft circles)."""

END_SHARPNESS = 150.0
"""Ending sharpness value for sigmoid activation (hard circles)."""

# Auto-detection parameters
MIN_AUTO_CIRCLES = 2
"""Minimum number of circles to test in auto-detection."""

MAX_AUTO_CIRCLES = 10
"""Maximum number of circles to test in auto-detection."""

ELBOW_THRESHOLD_RATIO = 0.3
"""Threshold ratio for elbow detection (relative to mean improvement)."""

# Numerical stability
EPSILON = 1e-6
"""Small epsilon value for numerical stability in divisions."""

# Visualization defaults
DEFAULT_DPI = 150
"""Default DPI for saved visualizations."""

DEFAULT_FIGSIZE = (12, 8)
"""Default figure size for visualizations (width, height in inches)."""
