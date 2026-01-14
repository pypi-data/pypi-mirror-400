"""Viviphi: Turn static graphs into beautiful animations."""

from .graph import Graph
from .enums import OrderType
from .themes import (
    Theme,
    NodeStyling,
    EdgeStyling,
    BackgroundStyling,
    AnimationStyling,
    CYBERPUNK,
    CORPORATE,
    HAND_DRAWN,
    MANIM_CLASSIC,
    MANIM_LIGHT,
    MANIM_AQUA,
    MANIM_ORANGE,
    MANIM_PROOF,
    CYBERPUNK_GRID,
    GRADIENT_SUNSET,
    DOTTED_MINIMAL,
)

__all__ = [
    "Graph",
    "OrderType",
    "Theme",
    "NodeStyling",
    "EdgeStyling",
    "BackgroundStyling",
    "AnimationStyling",
    "CYBERPUNK",
    "CORPORATE",
    "HAND_DRAWN",
    "MANIM_CLASSIC",
    "MANIM_LIGHT",
    "MANIM_AQUA",
    "MANIM_ORANGE",
    "MANIM_PROOF",
    "CYBERPUNK_GRID",
    "GRADIENT_SUNSET",
    "DOTTED_MINIMAL",
]
