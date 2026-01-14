"""Browser-based SVG validation tests to catch actual syntax errors."""

import pytest
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
from viviphi import Graph, CYBERPUNK


class TestBrowserSVGValidation:
    """Test SVG validity by loading them in actual browsers."""
    
    @pytest.fixture
    def samples_dir(self):
        """Get the samples directory path."""
        return Path(__file__).parent.parent / "resources" / "mermaid_graphs"
    
    @pytest.mark.parametrize("mmd_file", [
        "01_kitchen_sink_flowchart.mmd",
        "02_nested_subgraphs_direction.mmd", 
        "03_styling_and_classes.mmd",
        "04_special_characters_unicode.mmd",
        "05_sequence_diagram.mmd",
        "06_class_diagram.mmd",
        "07_state_diagram.mmd",
        "08_entity_relationship_diagram.mmd",
        "09_gantt_chart.mmd",
        "10_stress_test.mmd",
        "11_interaction_click_events.mmd"
    ])
    def test_svg_loads_in_browser_without_errors(self, samples_dir, mmd_file):
        """Test that generated SVG loads in browser without console errors."""
        # Generate SVG from sample
        file_path = samples_dir / mmd_file
        mermaid_content = file_path.read_text(encoding='utf-8')
        
        graph = Graph(mermaid_content)
        animated_svg = graph.animate(theme=CYBERPUNK)
        
        # Create HTML page with the SVG
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>SVG Validation Test</title>
        </head>
        <body>
            <h1>Testing {mmd_file}</h1>
            <div id="svg-container">
                {animated_svg}
            </div>
            <script>
                // Check for any parsing errors
                window.svgErrors = [];
                window.addEventListener('error', function(e) {{
                    window.svgErrors.push({{
                        message: e.message,
                        filename: e.filename,
                        line: e.lineno,
                        col: e.colno
                    }});
                }});
                
                // Validate SVG is properly loaded
                document.addEventListener('DOMContentLoaded', function() {{
                    const svgElement = document.querySelector('svg');
                    if (!svgElement) {{
                        window.svgErrors.push({{message: 'No SVG element found'}});
                    }} else {{
                        // Check if SVG has proper dimensions
                        const bbox = svgElement.getBoundingClientRect();
                        if (bbox.width === 0 || bbox.height === 0) {{
                            window.svgErrors.push({{message: 'SVG has zero dimensions'}});
                        }}
                    }}
                    
                    window.validationComplete = true;
                }});
            </script>
        </body>
        </html>
        '''
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Capture console messages
            console_messages = []
            page.on("console", lambda msg: console_messages.append({
                "type": msg.type,
                "text": msg.text
            }))
            
            try:
                # Load the HTML with SVG
                page.set_content(html_content)
                
                # Wait for validation to complete (reduced timeout for speed)
                page.wait_for_function("window.validationComplete === true", timeout=5000)
                
                # Check for JavaScript errors
                svg_errors = page.evaluate("window.svgErrors")
                
                # Check for console errors
                error_messages = [msg for msg in console_messages if msg["type"] == "error"]
                
                # Verify SVG is visible and properly rendered
                svg_element = page.query_selector("svg")
                assert svg_element is not None, f"No SVG element found for {mmd_file}"
                
                # Check SVG dimensions
                bbox = svg_element.bounding_box()
                assert bbox is not None and bbox["width"] > 0 and bbox["height"] > 0, f"SVG has invalid dimensions for {mmd_file}"
                
                # Report any errors found
                if svg_errors:
                    pytest.fail(f"SVG validation errors for {mmd_file}: {svg_errors}")
                
                if error_messages:
                    pytest.fail(f"Console errors for {mmd_file}: {error_messages}")
                
                print(f"✅ {mmd_file}: Browser validation passed")
                
            finally:
                browser.close()
    
    
    def _check_svg_syntax(self, svg_content: str) -> list:
        """Check SVG for common syntax issues."""
        issues = []
        
        # Check for unclosed tags
        if svg_content.count('<svg') != svg_content.count('</svg>'):
            issues.append("Mismatched svg tags")
        
        # Check for problematic HTML elements that should have been cleaned
        if 'html:' in svg_content:
            issues.append("Contains HTML namespace elements")
        
        if '<html:div' in svg_content or '<html:span' in svg_content:
            issues.append("Contains HTML elements")
        
        if 'foreignObject' in svg_content:
            issues.append("Contains foreignObject elements")
        
        # Check for invalid characters in text content
        if 'textmermaid' in svg_content:
            issues.append("Contains 'textmermaid' artifacts")
        
        # Check for malformed style attributes
        if 'style=""' in svg_content:
            issues.append("Contains empty style attributes")
        
        return issues
    
    def _validate_in_browser_with_page(self, page, svg_content: str, filename: str) -> dict:
        """Validate SVG in browser using existing page and return result."""
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Validation</title></head>
        <body>
            {svg_content}
            <script>
                window.errors = [];
                window.addEventListener('error', e => window.errors.push(e.message));
                setTimeout(() => window.done = true, 500);
            </script>
        </body>
        </html>
        '''
        
        console_errors = []
        page.on("console", lambda msg: 
            console_errors.append(msg.text) if msg.type == "error" else None)
        
        try:
            page.set_content(html_content)
            page.wait_for_function("window.done === true", timeout=3000)
            
            js_errors = page.evaluate("window.errors")
            svg_element = page.query_selector("svg")
            
            all_errors = js_errors + console_errors
            success = len(all_errors) == 0 and svg_element is not None
            
            return {
                "success": success,
                "errors": all_errors,
                "has_svg": svg_element is not None
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Browser test failed: {e}"],
                "has_svg": False
            }
    
    def _validate_in_browser(self, svg_content: str, filename: str) -> dict:
        """Legacy method - validate SVG in browser with own browser instance."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                return self._validate_in_browser_with_page(page, svg_content, filename)
            finally:
                browser.close()


class TestBrowserSVGValidationUnitTest(unittest.TestCase):
    """Simplified unittest-compatible version of browser validation tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.samples_dir = Path(__file__).parent.parent / "resources" / "mermaid_graphs"
    
    def test_unicode_svg_browser_validation(self):
        """Test Unicode SVG loads properly in browser."""
        file_path = self.samples_dir / "04_special_characters_unicode.mmd"
        if not file_path.exists():
            self.skipTest("Sample file not found")
            
        mermaid_content = file_path.read_text(encoding='utf-8')
        graph = Graph(mermaid_content)
        animated_svg = graph.animate(theme=CYBERPUNK)
        
        # Basic SVG structure check
        self.assertIn("<svg", animated_svg)
        self.assertIn("</svg>", animated_svg)
        self.assertIn("<style>", animated_svg)
        
        # Quick browser validation - simplified
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>{animated_svg}</body>
        </html>
        '''
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.set_content(html_content)
                svg_element = page.query_selector("svg")
                self.assertIsNotNone(svg_element, "SVG element should be present")
            finally:
                browser.close()
    
    def test_basic_svg_syntax_validation(self):
        """Test basic SVG syntax validation."""
        # Test with a simple mermaid diagram
        mermaid_content = 'graph TD; A["Start"] --> B["End"]'
        graph = Graph(mermaid_content)
        animated_svg = graph.animate(theme=CYBERPUNK)
        
        # Check basic SVG structure
        self.assertIn("<svg", animated_svg)
        self.assertIn("</svg>", animated_svg)
        self.assertIn("@keyframes", animated_svg)
        
        # Check for common syntax issues
        svg_open_count = animated_svg.count('<svg')
        svg_close_count = animated_svg.count('</svg>')
        self.assertEqual(svg_open_count, svg_close_count, "Mismatched SVG tags")
        
        # Should not contain problematic elements that would break rendering
        # Note: 'html:' namespace is normal in Mermaid SVG output, but check for problematic patterns
        self.assertNotIn('<html:script', animated_svg)  # Scripts would be problematic
        self.assertNotIn('javascript:', animated_svg)   # Inline JavaScript