"""
utils — funkcje pomocnicze.
"""

from .geometry import (
    midpoint,
    normal_vector,
    compute_hyperplane
)

from .validation import (
    check_xy,
    check_class_labels
)

__all__ = [
    "midpoint",
    "normal_vector",
    "compute_hyperplane",
    "check_xy",
    "check_class_labels",
]
