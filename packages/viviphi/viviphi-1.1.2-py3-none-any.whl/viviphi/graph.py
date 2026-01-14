"""Main Graph class for creating animated SVGs from Mermaid definitions."""

from typing import Literal, Optional
from pathlib import Path

from .themes import Theme, CYBERPUNK
from .enums import OrderType
from .animator import SVGAnimator
from .mermaid import MermaidRenderer


class Graph:
    """Main interface for creating animated SVGs from Mermaid graph definitions."""

    def __init__(self, mermaid_definition: str) -> None:
        """Initialize with a Mermaid graph definition.

        Args:
            mermaid_definition: Standard Mermaid.js graph syntax string
        """
        self.mermaid_definition = mermaid_definition
        self._renderer = MermaidRenderer()

    def animate(
        self,
        theme: Theme = CYBERPUNK,
        speed: Literal["slow", "normal", "fast"] = "normal",
        order_type: OrderType = OrderType.ORDERED,
        output: Optional[str] = None,
    ) -> str:
        """Generate an animated SVG from the Mermaid definition.

        Args:
            theme: Visual theme to apply
            speed: Animation speed setting
            order_type: How animations are ordered (ORDERED, SEQUENTIAL, or RANDOM)
            output: Optional output file path

        Returns:
            Animated SVG content as string
        """
        # Adjust theme timing based on speed
        speed_multipliers = {"slow": 2.0, "normal": 1.0, "fast": 0.5}
        multiplier = speed_multipliers[speed]

        adjusted_theme = theme.model_copy(deep=True)
        adjusted_theme.animation.duration *= multiplier
        adjusted_theme.animation.stagger_delay *= multiplier

        # Step 1: Render Mermaid to static SVG using headless browser
        static_svg = self._renderer.render_to_svg(self.mermaid_definition)

        # Step 2: Process with animator to add CSS animations
        animator = SVGAnimator(static_svg)
        animated_svg = animator.process(adjusted_theme, order_type=order_type)

        # Step 4: Save to file if requested
        if output:
            output_path = Path(output)
            output_path.write_text(animated_svg, encoding="utf-8")

        return animated_svg

    def preview(self, theme: Theme = CYBERPUNK) -> str:
        """Generate a quick preview without saving to file.

        Args:
            theme: Visual theme to apply

        Returns:
            Animated SVG content as string
        """
        return self.animate(theme=theme, speed="normal")
