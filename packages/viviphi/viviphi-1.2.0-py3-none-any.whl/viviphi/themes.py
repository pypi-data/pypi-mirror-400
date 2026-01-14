"""Theme system for defining visual styles and animations."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class NodeStyling(BaseModel):
    """Node appearance configuration."""

    style: Literal["glass", "solid", "outlined", "rounded", "sharp"] = "glass"
    fill_color: Optional[str] = None  # If None, uses theme primary_color
    border_color: Optional[str] = None  # If None, uses theme primary_color
    border_width: float = 2.0
    border_radius: float = 4.0  # For rounded style
    opacity: float = 1.0
    shadow: bool = False
    shadow_color: str = "rgba(0, 0, 0, 0.3)"
    shadow_blur: float = 4.0
    shadow_offset: tuple[float, float] = (2.0, 2.0)
    # Icon support
    icon_enabled: bool = False
    icon_font_family: str = "Font Awesome 5 Free"
    icon_size: float = 16.0
    icon_color: Optional[str] = None  # If None, uses border_color


class EdgeStyling(BaseModel):
    """Edge appearance configuration."""

    style: Literal["neon", "clean", "hand-drawn", "dashed", "dotted", "thick"] = "clean"
    color: Optional[str] = None  # If None, uses theme primary_color
    width: float = 2.0
    opacity: float = 0.9
    # Neon glow effects
    glow_enabled: bool = False
    glow_color: Optional[str] = None  # If None, uses edge color
    glow_intensity: float = 10.0
    # Arrow styling
    arrow_size: float = 1.0
    arrow_color: Optional[str] = None  # If None, uses edge color


class BackgroundStyling(BaseModel):
    """Background appearance configuration."""

    color: str = "#1a1a1a"
    pattern: Literal["none", "grid", "dots", "lines", "diagonal"] = "none"
    pattern_color: str = "rgba(255, 255, 255, 0.1)"
    pattern_size: float = 20.0
    gradient_enabled: bool = False
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None
    gradient_direction: Literal[
        "to-bottom", "to-right", "to-bottom-right", "radial"
    ] = "to-bottom"


class AnimationStyling(BaseModel):
    """Animation behavior configuration."""

    duration: float = 1.5
    stagger_delay: float = 0.3
    easing: Literal["ease", "ease-in", "ease-out", "ease-in-out", "linear"] = "ease-out"
    node_fade_duration: float = 0.5
    edge_draw_style: Literal["progressive", "all-at-once", "reverse"] = "progressive"
    # Advanced timing
    edge_start_delay: float = 0.0
    node_start_delay: float = 0.0


class Theme(BaseModel):
    """Comprehensive visual theme for graph animations."""

    # Primary theme colors
    primary_color: str = "#00ff99"
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    text_color: str = "#ffffff"

    # Component styling
    background: BackgroundStyling = Field(default_factory=BackgroundStyling)
    nodes: NodeStyling = Field(default_factory=NodeStyling)
    edges: EdgeStyling = Field(default_factory=EdgeStyling)
    animation: AnimationStyling = Field(default_factory=AnimationStyling)

    # Typography
    font_family: str = "Arial, sans-serif"
    font_size: float = 14.0
    font_weight: Literal["normal", "bold", "lighter", "bolder"] = "normal"

    def __init__(self, **data):
        """Initialize theme with backward compatibility for legacy parameters."""
        # Handle legacy parameters for backward compatibility
        legacy_mappings = {
            "edge_style": ("edges", "style"),
            "node_style": ("nodes", "style"),
            "animation_duration": ("animation", "duration"),
            "stagger_delay": ("animation", "stagger_delay"),
        }

        # Convert legacy background parameter
        if "background" in data and isinstance(data["background"], str):
            data["background"] = BackgroundStyling(color=data["background"])

        # Convert legacy parameters to new structure
        for legacy_key, (component, attr) in legacy_mappings.items():
            if legacy_key in data:
                legacy_value = data.pop(legacy_key)

                # Ensure component exists with proper isolation
                if component not in data:
                    if component == "edges":
                        data[component] = {}
                    elif component == "nodes":
                        data[component] = {}
                    elif component == "animation":
                        data[component] = {}

                # Set the attribute safely
                if isinstance(data[component], dict):
                    data[component][attr] = legacy_value
                elif hasattr(data[component], attr):
                    # Create a copy to avoid modifying shared objects
                    component_data = (
                        data[component].model_dump()
                        if hasattr(data[component], "model_dump")
                        else {}
                    )
                    component_data[attr] = legacy_value

                    if component == "edges":
                        data[component] = EdgeStyling(**component_data)
                    elif component == "nodes":
                        data[component] = NodeStyling(**component_data)
                    elif component == "animation":
                        data[component] = AnimationStyling(**component_data)
                else:  # pragma: no cover
                    # Create new component with the attribute
                    component_data = (
                        data[component].model_dump()
                        if hasattr(data[component], "model_dump")
                        else {}
                    )
                    component_data[attr] = legacy_value

                    if component == "edges":  # pragma: no cover
                        data[component] = EdgeStyling(**component_data)
                    elif component == "nodes":  # pragma: no cover
                        data[component] = NodeStyling(**component_data)
                    elif component == "animation":  # pragma: no cover
                        data[component] = AnimationStyling(**component_data)

        super().__init__(**data)

    # Legacy compatibility properties for backward compatibility
    @property
    def edge_style(self) -> str:
        """Legacy property for backward compatibility."""
        return self.edges.style

    @property
    def node_style(self) -> str:
        """Legacy property for backward compatibility."""
        return self.nodes.style

    @property
    def animation_duration(self) -> float:
        """Legacy property for backward compatibility."""
        return self.animation.duration

    @property
    def stagger_delay(self) -> float:
        """Legacy property for backward compatibility."""
        return self.animation.stagger_delay

    def get_css_template(self) -> str:
        """Generate comprehensive CSS template based on theme settings."""

        # Helper function to get actual colors (fallback to primary if None)
        def get_color(color: Optional[str], fallback: str = None) -> str:
            if color is not None:
                return color
            return fallback or self.primary_color

        edge_color = get_color(self.edges.color)
        node_fill = get_color(self.nodes.fill_color)
        node_border = get_color(self.nodes.border_color)

        # Base CSS with comprehensive styling
        css = f"""
            /* Enhanced Theme CSS - {self.edges.style} edges / {self.nodes.style} nodes */
            
            /* Root Variables */
            :root {{
                --primary-color: {self.primary_color};
                --secondary-color: {self.secondary_color or self.primary_color};
                --accent-color: {self.accent_color or self.primary_color};
                --text-color: {self.text_color};
                --background-color: {self.background.color};
                --edge-color: {edge_color};
                --node-fill: {node_fill};
                --node-border: {node_border};
                --font-family: {self.font_family};
                --font-size: {self.font_size}px;
                --font-weight: {self.font_weight};
            }}
            
            /* Background Styling */
            svg {{
                background: {self._get_background_css()};
                font-family: var(--font-family);
                font-size: var(--font-size);
                font-weight: var(--font-weight);
            }}
            
            {self._get_background_pattern_css()}
            
            /* Base Edge Animation */
            .anim-edge {{
                stroke: var(--edge-color);
                stroke-width: {self.edges.width}px;
                stroke-dasharray: var(--length);
                stroke-dashoffset: var(--length);
                fill: none;
                opacity: {self.edges.opacity};
                animation: draw-flow-with-markers {self.animation.duration}s {self.animation.easing} forwards;
                animation-delay: {self.animation.edge_start_delay}s;
            }}
            
            /* Edge Style Variations */
            {self._get_edge_style_css()}
            
            /* Base Node Animation */
            .anim-node {{
                opacity: 0;
                animation: fade-in-node {self.animation.node_fade_duration}s {self.animation.easing} forwards;
                animation-delay: {self.animation.node_start_delay}s;
            }}
            
            /* Node Style Variations */
            {self._get_node_style_css()}
            
            /* Animation Keyframes */
            {self._get_animation_keyframes()}
            
            /* Text Styling */
            text {{
                fill: var(--text-color);
                font-family: var(--font-family);
                font-size: var(--font-size);
                font-weight: var(--font-weight);
            }}
        """

        return css

    def _get_background_css(self) -> str:
        """Generate background CSS based on styling configuration."""
        if self.background.gradient_enabled and self.background.gradient_start:
            if self.background.gradient_direction == "radial":
                return f"radial-gradient(circle, {self.background.gradient_start}, {self.background.gradient_end or self.background.color})"
            else:
                return f"linear-gradient({self.background.gradient_direction}, {self.background.gradient_start}, {self.background.gradient_end or self.background.color})"
        return self.background.color

    def _get_background_pattern_css(self) -> str:
        """Generate background pattern CSS."""
        if self.background.pattern == "none":
            return ""

        pattern_css = ""
        size = self.background.pattern_size
        color = self.background.pattern_color

        if self.background.pattern == "grid":
            pattern_css = f"""
            svg::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: 
                    linear-gradient({color} 1px, transparent 1px),
                    linear-gradient(90deg, {color} 1px, transparent 1px);
                background-size: {size}px {size}px;
                pointer-events: none;
            }}
            """
        elif self.background.pattern == "dots":
            pattern_css = f"""
            svg::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: radial-gradient(circle, {color} 1px, transparent 1px);
                background-size: {size}px {size}px;
                pointer-events: none;
            }}
            """
        elif self.background.pattern == "lines":
            pattern_css = f"""
            svg::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: linear-gradient({color} 1px, transparent 1px);
                background-size: {size}px {size}px;
                pointer-events: none;
            }}
            """
        elif self.background.pattern == "diagonal":
            pattern_css = f"""
            svg::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: repeating-linear-gradient(45deg, transparent, transparent {size / 2}px, {color} {size / 2}px, {color} {size}px);
                pointer-events: none;
            }}
            """

        return pattern_css

    def _get_edge_style_css(self) -> str:
        """Generate edge-specific styling CSS."""
        edge_color = self.edges.color or self.primary_color
        glow_color = self.edges.glow_color or edge_color

        css = ""

        if self.edges.style == "neon" or self.edges.glow_enabled:
            css += f"""
            .neon-glow, .anim-edge.neon {{
                filter: drop-shadow(0 0 {self.edges.glow_intensity / 3}px {glow_color}) 
                        drop-shadow(0 0 {self.edges.glow_intensity}px {glow_color}) 
                        drop-shadow(0 0 {self.edges.glow_intensity * 1.5}px {glow_color});
                stroke: {edge_color};
            }}
            """

        if self.edges.style == "hand-drawn":
            css += """
            .hand-drawn, .anim-edge.hand-drawn {
                stroke-linecap: round;
                stroke-linejoin: round;
                filter: url(#rough);
            }
            """

        if self.edges.style == "dashed":
            css += f"""
            .dashed, .anim-edge.dashed {{
                stroke-dasharray: {self.edges.width * 4}px {self.edges.width * 2}px;
            }}
            """

        if self.edges.style == "dotted":
            css += f"""
            .dotted, .anim-edge.dotted {{
                stroke-linecap: round;
                stroke-dasharray: {self.edges.width}px {self.edges.width * 2}px;
            }}
            """

        if self.edges.style == "thick":
            css += f"""
            .thick, .anim-edge.thick {{
                stroke-width: {self.edges.width * 2}px;
            }}
            """

        if self.edges.style == "clean":
            css += """
            .clean-edge, .anim-edge.clean {
                stroke-linecap: butt;
                stroke-linejoin: miter;
            }
            """

        return css

    def _get_node_style_css(self) -> str:
        """Generate node-specific styling CSS."""
        fill_color = self.nodes.fill_color or self.primary_color
        border_color = self.nodes.border_color or self.primary_color

        css = ""

        # Base node styles
        if self.nodes.style == "glass":
            css += f"""
            .glass-node, .anim-node.glass {{
                fill: rgba(255, 255, 255, 0.1);
                stroke: {border_color};
                stroke-width: {self.nodes.border_width}px;
                backdrop-filter: blur(10px);
                opacity: {self.nodes.opacity};
            }}
            """

        elif self.nodes.style == "solid":
            css += f"""
            .solid-node, .anim-node.solid {{
                fill: {fill_color};
                stroke: none;
                opacity: {self.nodes.opacity};
            }}
            """

        elif self.nodes.style == "outlined":
            css += f"""
            .outlined-node, .anim-node.outlined {{
                fill: none;
                stroke: {border_color};
                stroke-width: {self.nodes.border_width}px;
                opacity: {self.nodes.opacity};
            }}
            """

        elif self.nodes.style == "rounded":
            css += f"""
            .rounded-node, .anim-node.rounded {{
                fill: {fill_color};
                stroke: {border_color};
                stroke-width: {self.nodes.border_width}px;
                rx: {self.nodes.border_radius}px;
                ry: {self.nodes.border_radius}px;
                opacity: {self.nodes.opacity};
            }}
            """

        elif self.nodes.style == "sharp":
            css += f"""
            .sharp-node, .anim-node.sharp {{
                fill: {fill_color};
                stroke: {border_color};
                stroke-width: {self.nodes.border_width}px;
                stroke-linejoin: miter;
                stroke-miterlimit: 4;
                opacity: {self.nodes.opacity};
            }}
            """

        # Add shadow effect if enabled
        if self.nodes.shadow:
            shadow_x, shadow_y = self.nodes.shadow_offset
            css += f"""
            .anim-node {{
                filter: drop-shadow({shadow_x}px {shadow_y}px {self.nodes.shadow_blur}px {self.nodes.shadow_color});
            }}
            """

        # Add icon support if enabled
        if self.nodes.icon_enabled:
            icon_color = self.nodes.icon_color or border_color
            css += f"""
            .node-icon {{
                font-family: '{self.nodes.icon_font_family}';
                font-size: {self.nodes.icon_size}px;
                fill: {icon_color};
                text-anchor: middle;
                dominant-baseline: central;
            }}
            """

        return css

    def _get_animation_keyframes(self) -> str:
        """Generate animation keyframes based on configuration."""
        css = f"""
        /* Edge Animation Keyframes */
        @keyframes draw-flow-with-markers {{
            0% {{ 
                stroke-dashoffset: var(--length);
                marker-start: none;
                marker-end: none;
            }}
            99% {{ 
                stroke-dashoffset: 0;
                marker-start: none;
                marker-end: none;
            }}
            100% {{ 
                stroke-dashoffset: 0;
                marker-start: var(--marker-start, none);
                marker-end: var(--marker-end, none);
            }}
        }}
        
        /* Node Fade Animation */
        @keyframes fade-in-node {{
            from {{ 
                opacity: 0;
                transform: scale(0.8);
            }}
            to {{ 
                opacity: {self.nodes.opacity};
                transform: scale(1);
            }}
        }}
        
        /* Complex Shape Fade Animation - preserves existing transforms */
        @keyframes fade-in-complex-node {{
            from {{ 
                opacity: 0;
            }}
            to {{ 
                opacity: {self.nodes.opacity};
            }}
        }}
        
        /* Polygon-specific animations that preserve transforms */
        .anim-node polygon {{
            animation: fade-in-complex-node {self.animation.node_fade_duration}s {self.animation.easing} forwards !important;
            transform-box: fill-box !important;
            transform-origin: center !important;
        }}
        
        /* Path-specific animations for database shapes */
        .anim-node path {{
            animation: fade-in-complex-node {self.animation.node_fade_duration}s {self.animation.easing} forwards !important;
            transform-box: fill-box !important;
            transform-origin: center !important;
        }}
        
        /* Force preserve existing transforms for polygons - disable transform animations completely */
        .anim-node polygon[transform] {{
            animation: none !important;
            opacity: {self.nodes.opacity} !important;
        }}
        
        /* Also disable for paths with transforms */  
        .anim-node path[transform] {{
            animation: none !important;
            opacity: {self.nodes.opacity} !important;
        }}
        
        /* Database cylinder alignment will be handled dynamically by the animator */
        
        /* Override for simple shapes that don't have transform conflicts */
        .anim-node rect,
        .anim-node circle,
        .anim-node ellipse {{
            animation: fade-in-node {self.animation.node_fade_duration}s {self.animation.easing} forwards;
        }}
        """

        # Add alternative animation styles based on edge_draw_style
        if self.animation.edge_draw_style == "all-at-once":
            css += """
            @keyframes draw-all-at-once {
                0% { 
                    stroke-dashoffset: var(--length);
                    opacity: 0;
                }
                100% { 
                    stroke-dashoffset: 0;
                    opacity: var(--edge-opacity, 0.9);
                }
            }
            """
        elif self.animation.edge_draw_style == "reverse":
            css += """
            @keyframes draw-reverse {
                0% { 
                    stroke-dashoffset: 0;
                    opacity: var(--edge-opacity, 0.9);
                }
                100% { 
                    stroke-dashoffset: var(--length);
                    opacity: 0;
                }
            }
            """

        return css


# Predefined themes
CYBERPUNK = Theme(
    primary_color="#00ff99",
    text_color="#ffffff",
    background=BackgroundStyling(color="#1a1a1a"),
    edges=EdgeStyling(style="neon", glow_enabled=True, glow_intensity=15.0),
    nodes=NodeStyling(style="glass", border_width=2.0, shadow=True),
    animation=AnimationStyling(duration=1.5, stagger_delay=0.3),
)

CORPORATE = Theme(
    primary_color="#2563eb",
    text_color="#1f2937",
    background=BackgroundStyling(color="#ffffff"),
    edges=EdgeStyling(style="clean", width=1.5, opacity=0.8),
    nodes=NodeStyling(style="solid", border_width=1.0),
    animation=AnimationStyling(duration=1.0, stagger_delay=0.2, easing="ease-in-out"),
)

HAND_DRAWN = Theme(
    primary_color="#374151",
    text_color="#374151",
    background=BackgroundStyling(color="#f9fafb"),
    edges=EdgeStyling(style="hand-drawn", width=2.5, opacity=0.9),
    nodes=NodeStyling(style="outlined", border_width=2.5, border_radius=6.0),
    animation=AnimationStyling(duration=2.0, stagger_delay=0.4, easing="ease"),
)

# 3Blue1Brown-inspired themes (manim library style)
MANIM_CLASSIC = Theme(
    primary_color="#58c4dd",  # Classic 3B1B blue
    text_color="#ffffff",
    background=BackgroundStyling(color="#0c0c0c"),
    edges=EdgeStyling(style="clean", width=2.0, opacity=0.9),
    nodes=NodeStyling(style="solid", border_width=1.5),
    animation=AnimationStyling(duration=1.2, stagger_delay=0.25, easing="ease-out"),
)

MANIM_LIGHT = Theme(
    primary_color="#1f4e79",  # Dark blue for light backgrounds
    text_color="#1f2937",
    background=BackgroundStyling(color="#fefefe"),
    edges=EdgeStyling(style="clean", width=2.0, opacity=0.8),
    nodes=NodeStyling(style="solid", border_width=1.5),
    animation=AnimationStyling(duration=1.2, stagger_delay=0.25, easing="ease-out"),
)

MANIM_AQUA = Theme(
    primary_color="#83d0c9",  # Aqua/teal color
    text_color="#ffffff",
    background=BackgroundStyling(color="#0c0c0c"),
    edges=EdgeStyling(style="clean", width=2.0, opacity=0.9),
    nodes=NodeStyling(style="glass", border_width=2.0, opacity=0.9),
    animation=AnimationStyling(duration=1.4, stagger_delay=0.3, easing="ease-out"),
)

MANIM_ORANGE = Theme(
    primary_color="#fc6255",  # Vibrant orange
    text_color="#ffffff",
    background=BackgroundStyling(color="#0c0c0c"),
    edges=EdgeStyling(style="clean", width=2.5, opacity=0.95),
    nodes=NodeStyling(style="solid", border_width=1.5),
    animation=AnimationStyling(duration=1.0, stagger_delay=0.2, easing="ease-in-out"),
)

MANIM_PROOF = Theme(
    primary_color="#c59df5",  # Purple for mathematical proofs
    text_color="#ffffff",
    background=BackgroundStyling(color="#0c0c0c"),
    edges=EdgeStyling(style="clean", width=2.0, opacity=0.9),
    nodes=NodeStyling(style="glass", border_width=2.0, opacity=0.85),
    animation=AnimationStyling(duration=1.8, stagger_delay=0.35, easing="ease"),
)

# Advanced themed examples showcasing new capabilities
CYBERPUNK_GRID = Theme(
    primary_color="#00ff99",
    secondary_color="#ff006e",
    text_color="#ffffff",
    background=BackgroundStyling(
        color="#0a0a0a",
        pattern="grid",
        pattern_color="rgba(0, 255, 153, 0.1)",
        pattern_size=25.0,
    ),
    edges=EdgeStyling(
        style="neon", width=2.0, glow_enabled=True, glow_intensity=12.0, opacity=0.9
    ),
    nodes=NodeStyling(
        style="glass",
        border_width=2.0,
        shadow=True,
        shadow_color="rgba(0, 255, 153, 0.3)",
        opacity=0.9,
    ),
    animation=AnimationStyling(duration=1.6, stagger_delay=0.25, easing="ease-out"),
)

GRADIENT_SUNSET = Theme(
    primary_color="#ff6b6b",
    secondary_color="#ffd93d",
    accent_color="#6bcf7f",
    text_color="#2c3e50",
    background=BackgroundStyling(
        color="#ff6b6b",
        gradient_enabled=True,
        gradient_start="#ff6b6b",
        gradient_end="#ffd93d",
        gradient_direction="to-bottom-right",
    ),
    edges=EdgeStyling(style="thick", width=3.0, color="#2c3e50", opacity=0.8),
    nodes=NodeStyling(
        style="rounded",
        border_radius=8.0,
        border_width=2.0,
        border_color="#2c3e50",
        fill_color="#ffffff",
        shadow=True,
        shadow_blur=6.0,
        opacity=0.95,
    ),
    animation=AnimationStyling(duration=1.8, stagger_delay=0.4, easing="ease-in-out"),
)

DOTTED_MINIMAL = Theme(
    primary_color="#6366f1",
    text_color="#374151",
    background=BackgroundStyling(
        color="#f8fafc",
        pattern="dots",
        pattern_color="rgba(99, 102, 241, 0.1)",
        pattern_size=15.0,
    ),
    edges=EdgeStyling(style="dotted", width=2.0, opacity=0.7),
    nodes=NodeStyling(style="outlined", border_width=2.0, opacity=1.0),
    animation=AnimationStyling(duration=1.0, stagger_delay=0.15, easing="ease"),
    font_weight="bold",
)
