"""SVG Animation engine for transforming static SVGs into animated ones."""

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING
from svgpathtools import parse_path

if TYPE_CHECKING:
    from .themes import Theme

from .enums import OrderType


class SVGAnimator:
    """Transforms static SVG content into CSS-animated SVG."""

    def __init__(self, static_svg_content: str) -> None:
        """Initialize with static SVG content.

        Args:
            static_svg_content: Raw SVG string content
        """
        # Register namespace to prevent ns0: prefixes in output
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        self.root = ET.fromstring(static_svg_content)
        self.ns = {"svg": "http://www.w3.org/2000/svg"}
        self._reversed_markers = set()  # Track created reversed markers

    def _create_reversed_marker(self, marker_id: str) -> None:
        """Create a reversed version of a marker by flipping its geometry.

        Args:
            marker_id: ID of the original marker to reverse
        """
        # Avoid creating duplicates
        reversed_id = f"{marker_id}_reversed"
        if reversed_id in self._reversed_markers:
            return

        # Find the original marker
        original_marker = self.root.find(
            f".//svg:defs/svg:marker[@id='{marker_id}']", self.ns
        )
        if original_marker is None:
            return

        # Create a copy of the original marker
        reversed_marker = ET.fromstring(ET.tostring(original_marker))
        reversed_marker.set("id", reversed_id)

        # Reverse the marker geometry by applying a transformation
        # For extension arrows, we need to flip them horizontally
        marker_paths = reversed_marker.findall(".//svg:path", self.ns)
        for path in marker_paths:
            d_attr = path.get("d", "")
            if d_attr:
                # For extension arrows, flip the path horizontally around x=9.5 (middle of 0-18 range)
                # This effectively reverses the arrow direction
                if "extension" in marker_id.lower():
                    # Simple horizontal flip for extension markers - reverse x coordinates around center
                    flipped_d = self._flip_path_horizontally(
                        d_attr, 18
                    )  # 18 is refX value
                    path.set("d", flipped_d)

        # Add the reversed marker to the defs section
        defs = self.root.find(".//svg:defs", self.ns)
        if defs is not None:
            defs.append(reversed_marker)
            self._reversed_markers.add(reversed_id)

    def _is_node_shape_path(self, path) -> bool:
        """Check if path defines a node shape rather than an edge.

        Args:
            path: SVG path element

        Returns:
            True if path is part of a node shape, False if it's an edge
        """
        # Check if path is inside a node group (not marker) by searching the tree
        # Find all groups and check their IDs
        all_groups = self.root.findall(".//svg:g", self.ns)

        for group in all_groups:
            group_id = group.get("id", "")
            if group_id.startswith("flowchart-"):
                # Check if this path is contained within this node group
                group_paths = group.findall(".//svg:path", self.ns)
                if path in group_paths:
                    return True

        return False

    def _flip_path_horizontally(self, path_d: str, width: float) -> str:
        """Flip a path horizontally around its center.

        Args:
            path_d: SVG path d attribute
            width: Width to flip around (usually marker width)

        Returns:
            Flipped path d attribute
        """
        import re

        # For simple extension markers like "M 1,7 L18,13 V 1 Z"
        # Flip x coordinates: x_new = width - x_old
        def flip_coords(match):
            x = float(match.group(1))
            y = match.group(2)
            flipped_x = width - x
            return f"{flipped_x},{y}"

        # Replace coordinate pairs (x,y)
        flipped = re.sub(r"(\d+(?:\.\d+)?),(\d+(?:\.\d+)?)", flip_coords, path_d)
        return flipped

    def _hide_all_animatable_elements(self) -> None:
        """Hide all animatable elements immediately to prevent FOUC.

        This adds initial styling to prevent flash before CSS animations start.
        Only hides elements that don't already have transforms or specific styling.
        """
        # Get all paths that are not inside markers (edges and node shapes)
        all_paths = self.root.findall(".//svg:path", self.ns)
        marker_paths = self.root.findall(".//svg:marker//svg:path", self.ns)
        marker_path_set = set(marker_paths)

        animatable_paths = [path for path in all_paths if path not in marker_path_set]

        # Get all node elements (excluding those inside markers)
        all_rects = self.root.findall(".//svg:rect", self.ns)
        all_circles = self.root.findall(".//svg:circle", self.ns)
        all_ellipses = self.root.findall(".//svg:ellipse", self.ns)
        all_polygons = self.root.findall(".//svg:polygon", self.ns)

        marker_rects = self.root.findall(".//svg:marker//svg:rect", self.ns)
        marker_circles = self.root.findall(".//svg:marker//svg:circle", self.ns)
        marker_ellipses = self.root.findall(".//svg:marker//svg:ellipse", self.ns)
        marker_polygons = self.root.findall(".//svg:marker//svg:polygon", self.ns)

        marker_elements_set = set(
            marker_rects + marker_circles + marker_ellipses + marker_polygons
        )

        animatable_nodes = []
        for element_list in [all_rects, all_circles, all_ellipses, all_polygons]:
            for element in element_list:
                if element not in marker_elements_set:
                    animatable_nodes.append(element)

        # Hide edges by setting initial stroke-dashoffset to hide the line
        for path in animatable_paths:
            # Don't hide paths that are part of node shapes or have transforms
            if not self._is_node_shape_path(path) and not path.get("transform"):
                existing_style = path.get("style", "")
                # For edges, we'll rely on CSS animation starting state rather than opacity
                # This prevents breaking the stroke-dasharray animation
                pass

        # Hide nodes that will be animated (but preserve those with transforms)
        for element in animatable_nodes:
            # Skip elements that have transforms (like database cylinders)
            if not element.get("transform"):
                existing_style = element.get("style", "")
                # Add opacity: 0 only to elements without transforms
                if existing_style:
                    if "opacity:" not in existing_style:
                        new_style = f"{existing_style}; opacity: 0"
                        element.set("style", new_style)
                else:
                    element.set("style", "opacity: 0")

    def _fix_database_alignment(self) -> None:
        """Dynamically fix database cylinder alignment by analyzing the visual structure.

        Database nodes should have the text label positioned on the 'wall' of the cylinder,
        not on the top or bottom. This analyzes the cylinder geometry to find the proper
        vertical center and aligns both elements accordingly.
        """
        # Find all database node groups
        all_groups = self.root.findall(".//svg:g", self.ns)

        for group in all_groups:
            # Look for database nodes containing both a path (cylinder) and text label
            paths = group.findall(".//svg:path", self.ns)
            labels = group.findall(".//svg:g[@class='label']", self.ns)

            if not paths or not labels:
                continue

            for path in paths:
                path_d = path.get("d", "")
                # Check if this is a database cylinder (has the characteristic "a" arc commands)
                # Database cylinders have: M x,y a rx,ry ... (arc for top ellipse)
                if "a " in path_d and path.get("transform"):
                    # Extract cylinder geometry from the path data
                    import re

                    # Parse the path: M x,y a rx,ry ... l 0,height a rx,ry ...
                    path_parts = re.search(
                        r"M\s+([-\d.]+),([-\d.]+)\s+a\s+([-\d.]+),([-\d.]+)[^l]+l\s+0,([-\d.]+)",
                        path_d,
                    )
                    if path_parts:
                        # Extract cylinder dimensions
                        start_y = float(path_parts.group(2))
                        height = float(path_parts.group(5))

                        # Calculate the visual center of the cylinder wall
                        # This should be at the middle of the cylinder height, accounting for the ellipse
                        cylinder_visual_center_y = start_y + (height / 2)

                        # Find the corresponding text label
                        for label in labels:
                            label_transform = label.get("transform", "")
                            path_transform = path.get("transform", "")

                            if (
                                "translate(" in label_transform
                                and "translate(" in path_transform
                            ):
                                label_match = re.search(
                                    r"translate\(([-\d.]+),\s*([-\d.]+)\)",
                                    label_transform,
                                )
                                path_match = re.search(
                                    r"translate\(([-\d.]+),\s*([-\d.]+)\)",
                                    path_transform,
                                )

                                if label_match and path_match:
                                    label_x, label_y = (
                                        float(label_match.group(1)),
                                        float(label_match.group(2)),
                                    )
                                    path_x, path_y = (
                                        float(path_match.group(1)),
                                        float(path_match.group(2)),
                                    )

                                    # Calculate the target Y position for proper alignment
                                    # Text should be at the visual center of the cylinder wall
                                    target_y = path_y + cylinder_visual_center_y

                                    # Align both elements to the calculated center
                                    if (
                                        abs(target_y - label_y) > 1.0
                                    ):  # Only fix if there's significant misalignment
                                        # Move the text label to the cylinder wall center
                                        new_label_transform = (
                                            f"translate({label_x}, {target_y})"
                                        )
                                        label.set("transform", new_label_transform)

                                        # Also adjust the cylinder if needed to ensure proper visual alignment
                                        # The cylinder should be positioned so its wall center aligns with text
                                        cylinder_adjust_y = (
                                            target_y - cylinder_visual_center_y
                                        )
                                        new_path_transform = (
                                            f"translate({path_x}, {cylinder_adjust_y})"
                                        )
                                        path.set("transform", new_path_transform)
                                        break

    def process(self, theme: "Theme", order_type: OrderType = OrderType.ORDERED) -> str:
        """Process the SVG with a specific theme.

        Args:
            theme: Theme object containing styling preferences
            order_type: How animations are ordered (ORDERED, SEQUENTIAL, or RANDOM)

        Returns:
            Animated SVG as string
        """
        # 1. Inject theme CSS
        style_el = ET.Element("style")
        style_el.text = theme.get_css_template()
        self.root.insert(0, style_el)

        # 1.5. Fix database cylinder alignment dynamically
        self._fix_database_alignment()

        # 1.6. Immediately hide all elements that will be animated to prevent FOUC
        self._hide_all_animatable_elements()

        # 2. Process Paths (Edges) - separate line paths from arrow tip paths
        all_paths = self.root.findall(".//svg:path", self.ns)

        # Find paths inside markers (arrow tips)
        marker_paths = self.root.findall(".//svg:marker//svg:path", self.ns)
        marker_path_set = set(marker_paths)

        # Separate paths into lines (outside markers), arrow tips (inside markers), and node shapes
        line_paths = []
        arrow_tip_paths = []
        node_shape_paths = []

        for path in all_paths:
            if path in marker_path_set:
                arrow_tip_paths.append(path)
            elif self._is_node_shape_path(path):
                node_shape_paths.append(path)
            else:
                line_paths.append(path)

        # Process line paths first
        for i, path in enumerate(line_paths):
            d_string = path.get("d")
            if not d_string:
                continue

            try:
                # Calculate geometry using svgpathtools
                path_obj = parse_path(d_string)
                length = path_obj.length()

                # Check semantic direction data to ensure proper animation flow
                flow_direction = path.get("data-flow-direction", "forward")
                marker_start = path.get("marker-start", "none")
                marker_end = path.get("marker-end", "none")

                # Determine if path needs reversal based on marker placement vs semantic direction
                needs_reversal = False
                if flow_direction == "forward":
                    # Forward flow should have marker at end of path animation
                    # If marker-start is set (arrow at beginning), path needs reversal
                    if marker_start != "none" and marker_end == "none":
                        needs_reversal = True
                elif flow_direction == "backward":
                    # Backward flow should have marker at start of path animation
                    # If marker-end is set (arrow at end), path needs reversal
                    if marker_end != "none" and marker_start == "none":
                        needs_reversal = True

                if needs_reversal:
                    # Reverse the path for proper tail-to-tip animation
                    path_obj = path_obj.reversed()
                    path.set("d", path_obj.d())
                    length = path_obj.length()

                    # Fix marker orientation by creating reversed marker definitions
                    if marker_start != "none":
                        marker_id = marker_start.replace("url(#", "").replace(")", "")
                        self._create_reversed_marker(marker_id)
                        marker_start = f"url(#{marker_id}_reversed)"

                    if marker_end != "none":
                        marker_id = marker_end.replace("url(#", "").replace(")", "")
                        self._create_reversed_marker(marker_id)
                        marker_end = f"url(#{marker_id}_reversed)"

                    # Swap marker attributes to match reversed path
                    path.set("marker-start", marker_end)
                    path.set("marker-end", marker_start)
                    # Update local variables
                    marker_start, marker_end = marker_end, marker_start

                # Calculate delay based on order type
                if order_type == OrderType.ORDERED:
                    # Use semantic ordering based on graph topology
                    animation_order = path.get("data-animation-order")
                    if animation_order is not None:
                        delay = int(animation_order) * theme.stagger_delay
                    else:
                        # Fallback to index-based timing
                        delay = i * theme.stagger_delay
                elif order_type == OrderType.SEQUENTIAL:
                    # Use simple index-based sequential timing
                    delay = i * theme.stagger_delay
                elif order_type == OrderType.RANDOM:
                    # Random delay between 0 and max sequential delay
                    import random

                    max_delay = len(line_paths) * theme.stagger_delay
                    delay = random.uniform(0, max_delay)
                else:
                    # Fallback to simultaneous (shouldn't happen with enum)
                    delay = 0

                existing_style = path.get("style", "")
                new_style = (
                    f"{existing_style}; "
                    f"--length: {length:.2f}; "
                    f"--glow-color: {theme.primary_color}; "
                    f"--marker-start: {marker_start}; "
                    f"--marker-end: {marker_end}; "
                    f"animation-delay: {delay}s;"
                )

                path.set("style", new_style)

                # Apply theme-specific classes
                if theme.edge_style == "neon":
                    path.set("class", "anim-edge neon-glow")
                elif theme.edge_style == "hand-drawn":
                    path.set("class", "anim-edge hand-drawn")
                else:
                    path.set("class", "anim-edge clean-edge")

                # Remove marker attributes so they start hidden
                if marker_start != "none":
                    path.attrib.pop("marker-start", None)
                if marker_end != "none":
                    path.attrib.pop("marker-end", None)

                # Enforce styling overrides for consistency
                path.set("stroke", theme.primary_color)
                path.set("fill", "none")

            except Exception as e:  # pragma: no cover
                print(f"Skipping complex line path {i}: {e}")

        # Process arrow tip paths after lines with additional delay
        for i, path in enumerate(arrow_tip_paths):
            d_string = path.get("d")
            if not d_string:
                continue

            try:
                # Calculate geometry using svgpathtools
                path_obj = parse_path(d_string)
                length = path_obj.length()

                # Calculate arrow tip delay based on order type
                if order_type == OrderType.ORDERED:
                    # Add extra delay so arrow tips appear after lines are drawn
                    base_line_delay = len(line_paths) * theme.stagger_delay
                    arrow_delay = base_line_delay + (
                        i * theme.stagger_delay * 0.2
                    )  # Faster stagger for tips
                elif order_type == OrderType.SEQUENTIAL:
                    # Sequential timing for arrow tips
                    base_line_delay = len(line_paths) * theme.stagger_delay
                    arrow_delay = base_line_delay + (i * theme.stagger_delay * 0.2)
                elif order_type == OrderType.RANDOM:
                    # Random delay for arrow tips
                    import random

                    max_delay = (
                        len(line_paths) + len(arrow_tip_paths)
                    ) * theme.stagger_delay
                    arrow_delay = random.uniform(0, max_delay)
                else:
                    # Fallback to simultaneous
                    arrow_delay = 0

                existing_style = path.get("style", "")
                new_style = (
                    f"{existing_style}; "
                    f"--length: {length:.2f}; "
                    f"--glow-color: {theme.primary_color}; "
                    f"animation-delay: {arrow_delay}s;"
                )

                path.set("style", new_style)

                # Apply theme-specific classes
                if theme.edge_style == "neon":
                    path.set("class", "anim-edge neon-glow")
                elif theme.edge_style == "hand-drawn":
                    path.set("class", "anim-edge hand-drawn")
                else:
                    path.set("class", "anim-edge clean-edge")

                # Enforce styling overrides for consistency
                path.set("stroke", theme.primary_color)
                path.set("fill", "none")

            except Exception as e:  # pragma: no cover
                print(f"Skipping complex arrow tip path {i}: {e}")

        # Process non-path arrow tip elements (circles, rects, etc.) after lines
        marker_elements = (
            self.root.findall(".//svg:marker//svg:rect", self.ns)
            + self.root.findall(".//svg:marker//svg:circle", self.ns)
            + self.root.findall(".//svg:marker//svg:ellipse", self.ns)
            + self.root.findall(".//svg:marker//svg:polygon", self.ns)
        )

        for i, element in enumerate(marker_elements):
            # Calculate marker element delay based on order type
            if order_type == OrderType.ORDERED:
                base_delay = (
                    len(line_paths) * theme.stagger_delay
                    + len(arrow_tip_paths) * theme.stagger_delay * 0.2
                )
                arrow_delay = base_delay + (
                    i * theme.stagger_delay * 0.1
                )  # Even faster stagger for non-path tips
            elif order_type == OrderType.SEQUENTIAL:
                # Sequential timing for marker elements
                base_delay = (
                    len(line_paths) * theme.stagger_delay
                    + len(arrow_tip_paths) * theme.stagger_delay * 0.2
                )
                arrow_delay = base_delay + (i * theme.stagger_delay * 0.1)
            elif order_type == OrderType.RANDOM:
                # Random delay for marker elements
                import random

                max_delay = (
                    len(line_paths) + len(arrow_tip_paths) + len(marker_elements)
                ) * theme.stagger_delay
                arrow_delay = random.uniform(0, max_delay)
            else:
                # Fallback to simultaneous
                arrow_delay = 0

            existing_style = element.get("style", "")
            new_style = f"{existing_style}; animation-delay: {arrow_delay}s;"
            element.set("style", new_style)

            # Apply theme-specific classes for arrow tips (use edge classes, not node classes)
            if theme.edge_style == "neon":
                element.set("class", "anim-edge neon-glow")
            elif theme.edge_style == "hand-drawn":
                element.set("class", "anim-edge hand-drawn")
            else:
                element.set("class", "anim-edge clean-edge")

        # 3. Process nodes (rectangles, circles, etc.) - exclude arrow tip elements inside markers
        all_rects = self.root.findall(".//svg:rect", self.ns)
        all_circles = self.root.findall(".//svg:circle", self.ns)
        all_ellipses = self.root.findall(".//svg:ellipse", self.ns)
        all_polygons = self.root.findall(".//svg:polygon", self.ns)

        # Find elements inside markers (arrow tips) to exclude from node processing
        marker_rects = self.root.findall(".//svg:marker//svg:rect", self.ns)
        marker_circles = self.root.findall(".//svg:marker//svg:circle", self.ns)
        marker_ellipses = self.root.findall(".//svg:marker//svg:ellipse", self.ns)
        marker_polygons = self.root.findall(".//svg:marker//svg:polygon", self.ns)

        marker_elements_set = set(
            marker_rects + marker_circles + marker_ellipses + marker_polygons
        )

        # Filter out marker elements from nodes
        nodes = []
        for element_list in [all_rects, all_circles, all_ellipses, all_polygons]:
            for element in element_list:
                if element not in marker_elements_set:
                    nodes.append(element)

        for i, node in enumerate(nodes):
            # Calculate node delay based on order type
            if order_type == OrderType.ORDERED:
                delay = i * theme.stagger_delay * 0.5  # Nodes appear before edges
            elif order_type == OrderType.SEQUENTIAL:
                delay = i * theme.stagger_delay * 0.5  # Sequential node timing
            elif order_type == OrderType.RANDOM:
                # Random delay for nodes
                import random

                max_delay = len(nodes) * theme.stagger_delay * 0.5
                delay = random.uniform(0, max_delay)
            else:
                # Fallback to simultaneous
                delay = 0

            # Check if node has transform that would conflict with CSS animations
            has_transform = node.get("transform") is not None

            # Skip animation for shapes with ANY transform attributes
            # CSS animations with transform properties will override existing transforms
            skip_animation = False
            if has_transform:
                # Skip ALL elements with existing transforms to prevent overriding positioning
                skip_animation = True

            if not skip_animation:
                existing_style = node.get("style", "")
                new_style = f"{existing_style}; animation-delay: {delay}s;"
                node.set("style", new_style)

            # Apply theme-specific node classes
            if skip_animation:
                # For polygons with transforms, use static classes without animation
                if theme.node_style == "glass":
                    node.set("class", "glass-node")
                elif theme.node_style == "outlined":
                    node.set("class", "outlined-node")
                else:
                    node.set("class", "solid-node")
            else:
                # For normal nodes, use animated classes
                if theme.node_style == "glass":
                    node.set("class", "anim-node glass-node")
                elif theme.node_style == "outlined":
                    node.set("class", "anim-node outlined-node")
                else:
                    node.set("class", "anim-node solid-node")

        # 4. Process node-defining paths separately (like database shapes)
        for i, path in enumerate(node_shape_paths):
            # Check if this path has transforms that would be overwritten by CSS animations
            has_transform = path.get("transform") is not None

            # Calculate node shape path delay based on order type
            if order_type == OrderType.ORDERED:
                delay = i * theme.stagger_delay * 0.5
            elif order_type == OrderType.SEQUENTIAL:
                delay = i * theme.stagger_delay * 0.5  # Sequential timing
            elif order_type == OrderType.RANDOM:
                # Random delay for node shape paths
                import random

                max_delay = len(node_shape_paths) * theme.stagger_delay * 0.5
                delay = random.uniform(0, max_delay)
            else:
                # Fallback to simultaneous
                delay = 0

            # Only apply animation styling if there's no transform conflict
            if not has_transform:
                existing_style = path.get("style", "")
                new_style = f"{existing_style}; animation-delay: {delay}s;"
                path.set("style", new_style)

            # Apply theme-specific node classes for node shape paths
            if has_transform:
                # For paths with transforms, use static classes without animation
                if theme.node_style == "glass":
                    path.set("class", "glass-node")
                elif theme.node_style == "outlined":
                    path.set("class", "outlined-node")
                else:
                    path.set("class", "solid-node")
            else:
                # For normal paths, use animated classes
                if theme.node_style == "glass":
                    path.set("class", "anim-node glass-node")
                elif theme.node_style == "outlined":
                    path.set("class", "anim-node outlined-node")
                else:
                    path.set("class", "anim-node solid-node")

        return ET.tostring(self.root, encoding="unicode")
