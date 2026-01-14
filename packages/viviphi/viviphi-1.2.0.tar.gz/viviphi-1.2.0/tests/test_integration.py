"""Integration tests without browser dependencies."""

import unittest
from unittest.mock import Mock, patch
from viviphi import Graph, CYBERPUNK, OrderType


class TestGraphIntegration(unittest.TestCase):
    """Integration tests for Graph class."""
    
    @patch('viviphi.graph.MermaidRenderer')
    def test_graph_animate_workflow(self, mock_renderer_class):
        """Test the complete animation workflow without browser."""
        # Mock the renderer
        mock_renderer = Mock()
        mock_svg = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
            <rect x="40" y="140" width="20" height="20" fill="white"/>
        </svg>
        """
        mock_renderer.render_to_svg.return_value = mock_svg
        mock_renderer_class.return_value = mock_renderer
        
        # Test the workflow
        graph = Graph("graph TD; A --> B")
        result = graph.animate(theme=CYBERPUNK, speed="normal")
        
        # Verify renderer was called
        mock_renderer.render_to_svg.assert_called_once_with("graph TD; A --> B")
        
        # Verify animation was applied
        assert "<style>" in result
        assert "neon-glow" in result
        assert CYBERPUNK.primary_color in result
        assert "@keyframes" in result
    
    @patch('viviphi.graph.MermaidRenderer')
    def test_graph_speed_adjustment(self, mock_renderer_class):
        """Test that speed setting affects animation timing."""
        mock_renderer = Mock()
        mock_svg = """
        <svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
            <path d="M 10 50 L 190 50" stroke="black" fill="none"/>
        </svg>
        """
        mock_renderer.render_to_svg.return_value = mock_svg
        mock_renderer_class.return_value = mock_renderer
        
        graph = Graph("graph LR; A --> B")
        
        # Test different speeds
        slow_result = graph.animate(speed="slow")
        fast_result = graph.animate(speed="fast")
        
        # Speeds should affect the CSS timing values
        # (We can't easily test exact values without parsing CSS, 
        # but we can ensure different outputs)
        assert slow_result != fast_result
    
    @patch('viviphi.graph.MermaidRenderer')
    def test_order_type_parameter(self, mock_renderer_class):
        """Test that the order_type parameter controls animation timing."""
        mock_renderer = Mock()
        mock_svg = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 200 150" stroke="black" fill="none" data-animation-order="1"/>
            <path d="M 200 150 L 350 150" stroke="black" fill="none" data-animation-order="2"/>
        </svg>
        """
        mock_renderer.render_to_svg.return_value = mock_svg
        mock_renderer_class.return_value = mock_renderer
        
        graph = Graph("graph LR; A --> B --> C")
        
        # Test OrderType.ORDERED (semantic order)
        ordered_result = graph.animate(order_type=OrderType.ORDERED)
        
        # Test OrderType.SEQUENTIAL (index-based sequential)
        sequential_result = graph.animate(order_type=OrderType.SEQUENTIAL)
        
        # Test OrderType.RANDOM (random delays)
        random_result = graph.animate(order_type=OrderType.RANDOM)
        
        # All three should produce different results
        assert ordered_result != sequential_result
        assert sequential_result != random_result
        assert ordered_result != random_result
    
    def test_graph_initialization(self):
        """Test Graph initialization."""
        mermaid_def = "graph TD; A[Start] --> B[End]"
        graph = Graph(mermaid_def)
        assert graph.mermaid_definition == mermaid_def

    @patch('viviphi.graph.MermaidRenderer')
    def test_graph_file_output(self, mock_renderer_class):
        """Test that Graph can save output to a file."""
        import tempfile
        import os
        
        mock_renderer = Mock()
        mock_svg = """<svg><path d="M 10 10 L 100 100"/></svg>"""
        mock_renderer.render_to_svg.return_value = mock_svg
        mock_renderer_class.return_value = mock_renderer
        
        graph = Graph("graph TD; A --> B")
        
        # Test file output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            output_path = f.name
        
        try:
            result = graph.animate(output=output_path)
            
            # Verify file was created and contains expected content
            assert os.path.exists(output_path)
            with open(output_path, 'r') as f:
                file_content = f.read()
            assert "<style>" in file_content
            assert result == file_content
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)

    @patch('viviphi.graph.MermaidRenderer') 
    def test_graph_preview_method(self, mock_renderer_class):
        """Test the preview method."""
        mock_renderer = Mock()
        mock_svg = """<svg><path d="M 10 10 L 100 100"/></svg>"""
        mock_renderer.render_to_svg.return_value = mock_svg
        mock_renderer_class.return_value = mock_renderer
        
        graph = Graph("graph TD; A --> B")
        result = graph.preview()
        
        # Preview should generate animated SVG with default settings
        assert "<style>" in result
        assert CYBERPUNK.primary_color in result
        assert "neon-glow" in result