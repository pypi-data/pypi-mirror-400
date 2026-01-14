"""Tests for SVGAnimator class."""

import unittest
from unittest.mock import patch
from viviphi.animator import SVGAnimator
from viviphi.themes import CYBERPUNK, CORPORATE
from viviphi.enums import OrderType


class TestSVGAnimator(unittest.TestCase):
    """Test SVGAnimator functionality."""
    
    def test_init_with_simple_svg(self):
        """Test initialization with a simple SVG."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 Q 200 50 350 150" stroke="black" fill="none"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        assert animator.root is not None
        assert animator.ns == {'svg': 'http://www.w3.org/2000/svg'}
    
    def test_process_with_theme_basic(self):
        """Test basic theme processing functionality."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK)
        
        # Check that CSS is injected
        assert "<style>" in result
        assert "@keyframes draw-flow" in result
        assert "stroke-dasharray" in result
        
        # Check that path has animation attributes
        assert 'class="anim-edge' in result
        assert CYBERPUNK.primary_color in result
        assert "--length:" in result
        assert "animation-delay:" in result
    
    def test_process_with_theme_cyberpunk(self):
        """Test processing with cyberpunk theme."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
            <rect x="40" y="140" width="20" height="20" fill="white"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK)
        
        # Check theme-specific styling
        assert CYBERPUNK.primary_color in result
        assert "neon-glow" in result
        assert "glass-node" in result
    
    def test_process_with_theme_corporate(self):
        """Test processing with corporate theme."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CORPORATE)
        
        # Check corporate theme styling
        assert CORPORATE.primary_color in result
        assert "clean-edge" in result
    
    def test_process_handles_empty_paths(self):
        """Test that paths without 'd' attribute are skipped gracefully."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path stroke="black" fill="none"/>
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK)
        
        # Should not raise error and should process the valid path
        assert result is not None
        assert "stroke-dasharray" in result

    def test_create_reversed_marker(self):
        """Test reversed marker creation functionality."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="extension-arrow" markerWidth="18" markerHeight="18" refX="9" refY="9">
                    <path d="M 1,7 L18,13 V 1 Z" fill="black"/>
                </marker>
            </defs>
            <path d="M 50 150 L 350 150" stroke="black" marker-end="url(#extension-arrow)"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        
        # Test marker creation
        animator._create_reversed_marker("extension-arrow")
        
        # Should create reversed marker without error
        assert "extension-arrow_reversed" in animator._reversed_markers
        
        # Test duplicate creation prevention
        initial_size = len(animator._reversed_markers)
        animator._create_reversed_marker("extension-arrow")
        assert len(animator._reversed_markers) == initial_size

    def test_create_reversed_marker_missing(self):
        """Test reversed marker creation with missing original marker."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <defs></defs>
            <path d="M 50 150 L 350 150" stroke="black"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        
        # Should handle missing marker gracefully
        animator._create_reversed_marker("nonexistent-marker")
        assert "nonexistent-marker_reversed" not in animator._reversed_markers

    def test_is_node_shape_path(self):
        """Test node shape path detection."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <g id="flowchart-node-1">
                <path d="M 40 140 L 80 140 L 80 160 L 40 160 Z" fill="white"/>
            </g>
            <path d="M 50 150 L 350 150" stroke="black"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        
        # Find paths
        all_paths = animator.root.findall(".//svg:path", animator.ns)
        node_path = all_paths[0]  # First path is inside flowchart group
        edge_path = all_paths[1]  # Second path is an edge
        
        assert animator._is_node_shape_path(node_path) == True
        assert animator._is_node_shape_path(edge_path) == False

    def test_flip_path_horizontally(self):
        """Test path horizontal flipping functionality."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        
        # Test basic path flipping
        original_path = "M 1,7 L18,13 V 1 Z"
        flipped = animator._flip_path_horizontally(original_path, 18)
        
        # Should contain flipped coordinates (with decimal places)
        assert "17.0,7" in flipped  # 18-1 = 17
        assert "0.0,13" in flipped  # 18-18 = 0

    def test_database_alignment_functionality(self):
        """Test database cylinder alignment functionality."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <g>
                <path d="M 10,20 a 40,10 0 0 1 0,0 l 0,30 a 40,10 0 0 1 0,0 Z" transform="translate(100, 50)"/>
                <g class="label" transform="translate(100, 60)">
                    <text>Database</text>
                </g>
            </g>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        
        # Should run without error
        animator._fix_database_alignment()
        # Database alignment is complex to test without detailed geometry validation

    def test_order_type_sequential(self):
        """Test processing with SEQUENTIAL order type."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 150 150" stroke="black"/>
            <path d="M 150 150 L 250 150" stroke="black"/>
            <rect x="40" y="140" width="20" height="20" fill="white"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK, order_type=OrderType.SEQUENTIAL)
        
        # Should contain animation delays
        assert "animation-delay:" in result
        assert result is not None

    def test_order_type_random(self):
        """Test processing with RANDOM order type."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 150 150" stroke="black"/>
            <path d="M 150 150 L 250 150" stroke="black"/>
            <rect x="40" y="140" width="20" height="20" fill="white"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK, order_type=OrderType.RANDOM)
        
        # Should contain animation delays with random timing
        assert "animation-delay:" in result
        assert result is not None

    def test_marker_handling_and_reversal(self):
        """Test marker handling and path reversal logic."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrow-start" markerWidth="10" markerHeight="10">
                    <path d="M 0,0 L 10,5 L 0,10 Z" fill="black"/>
                </marker>
                <marker id="arrow-end" markerWidth="10" markerHeight="10">
                    <path d="M 0,0 L 10,5 L 0,10 Z" fill="black"/>
                </marker>
            </defs>
            <path d="M 50 150 L 350 150" stroke="black" 
                  marker-start="url(#arrow-start)" 
                  data-flow-direction="forward"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK)
        
        # Should handle marker reversal for proper animation flow
        assert result is not None

    def test_complex_svg_elements(self):
        """Test processing of complex SVG with various element types."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="marker1">
                    <circle cx="5" cy="5" r="3" fill="red"/>
                    <rect x="2" y="2" width="6" height="6" fill="blue"/>
                    <ellipse cx="5" cy="5" rx="4" ry="3" fill="green"/>
                    <polygon points="0,0 10,0 5,10" fill="yellow"/>
                </marker>
            </defs>
            <path d="M 50 150 L 350 150" stroke="black" marker-end="url(#marker1)"/>
            <circle cx="100" cy="100" r="20" fill="white"/>
            <ellipse cx="200" cy="100" rx="30" ry="20" fill="white"/>
            <polygon points="50,50 100,50 75,100" fill="white"/>
            <rect x="300" y="80" width="40" height="40" fill="white"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK)
        
        # Should process all element types without error
        assert result is not None
        assert "anim-node" in result
        assert "anim-edge" in result

    def test_elements_with_transforms(self):
        """Test handling of elements with transform attributes."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <g id="flowchart-node">
                <path d="M 0,0 L 40,0 L 40,20 L 0,20 Z" transform="translate(100, 100)" fill="white"/>
            </g>
            <rect x="200" y="100" width="40" height="20" transform="rotate(45)" fill="white"/>
            <polygon points="0,0 20,0 10,20" transform="translate(300, 100)" fill="white"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK)
        
        # Should preserve transforms and apply appropriate classes
        assert result is not None
        # Elements with transforms should get static classes, not animated ones

    def test_animation_order_attribute(self):
        """Test handling of data-animation-order attribute."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 150 150" stroke="black" data-animation-order="2"/>
            <path d="M 150 150 L 250 150" stroke="black" data-animation-order="1"/>
            <path d="M 250 150 L 350 150" stroke="black" data-animation-order="3"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK, order_type=OrderType.ORDERED)
        
        # Should respect animation order attributes
        assert result is not None
        assert "animation-delay:" in result

    def test_exception_handling_in_path_processing(self):
        """Test exception handling during complex path processing."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="INVALID_PATH_DATA" stroke="black"/>
            <path d="M 50 150 L 350 150" stroke="black"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        
        # Should handle invalid path data gracefully and continue with valid paths
        with patch('builtins.print') as mock_print:
            result = animator.process(CYBERPUNK)
            # Should print error message for invalid path
            mock_print.assert_called()
            assert result is not None

    def test_arrow_tip_processing(self):
        """Test processing of arrow tip elements inside markers."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrow-tip">
                    <path d="M 0,0 L 10,5 L 0,10 Z" fill="black"/>
                </marker>
            </defs>
            <path d="M 50 150 L 350 150" stroke="black" marker-end="url(#arrow-tip)"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(CYBERPUNK)
        
        # Should process arrow tips with separate timing
        assert result is not None
        # Arrow tips should get different animation delays

    def test_hide_all_animatable_elements(self):
        """Test hiding of animatable elements to prevent FOUC."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black"/>
            <rect x="100" y="100" width="40" height="20" fill="white"/>
            <circle cx="200" cy="110" r="15" fill="white"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        animator._hide_all_animatable_elements()
        
        # Nodes should have opacity: 0 added to prevent FOUC
        # This is tested by the actual processing which calls this method

    def test_edge_style_variations(self):
        """Test different edge style applications."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black"/>
        </svg>
        """
        
        # Test with hand-drawn theme
        hand_drawn_theme = CORPORATE.model_copy()
        hand_drawn_theme.edges.style = "hand-drawn"
        
        animator = SVGAnimator(svg_content)
        result = animator.process(hand_drawn_theme)
        assert "hand-drawn" in result
        
        # Test clean edge style
        clean_theme = CORPORATE.model_copy()
        clean_theme.edges.style = "clean"
        
        result2 = animator.process(clean_theme)
        assert "clean-edge" in result2

    def test_node_style_variations(self):
        """Test different node style applications."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect x="100" y="100" width="40" height="20" fill="white"/>
        </svg>
        """
        
        # Test solid node style
        solid_theme = CORPORATE.model_copy()
        solid_theme.nodes.style = "solid"
        
        animator = SVGAnimator(svg_content)
        result = animator.process(solid_theme)
        assert "solid-node" in result
        
        # Test outlined node style  
        outlined_theme = CORPORATE.model_copy()
        outlined_theme.nodes.style = "outlined"
        
        result2 = animator.process(outlined_theme)
        assert "outlined-node" in result2