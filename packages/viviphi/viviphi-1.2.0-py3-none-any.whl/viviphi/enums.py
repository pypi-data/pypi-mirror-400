"""Enums used throughout the viviphi package."""

from enum import Enum


class OrderType(Enum):
    """Enum for controlling animation ordering."""

    ORDERED = "ordered"  # Sequential based on semantic graph order
    SEQUENTIAL = "sequential"  # Sequential based on index order
    RANDOM = "random"  # Random order
