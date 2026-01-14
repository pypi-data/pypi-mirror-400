"""Comprehensive test of ALL sample Mermaid graphs."""

import pytest
import unittest
from pathlib import Path
from viviphi import Graph, CYBERPUNK
from viviphi.mermaid import MermaidRenderer


class TestAllSampleGraphs:
    """Test every single sample graph without exceptions."""
    
    @pytest.fixture
    def samples_dir(self):
        """Get the samples directory path."""
        return Path(__file__).parent.parent / "resources" / "mermaid_graphs"
    
    @pytest.fixture(autouse=True)
    def cleanup_test_artifacts(self):
        """Clean up any test artifacts from previous runs or current test."""
        # Clean up before test
        project_root = Path.cwd()
        for test_file in project_root.glob("test_output_*.svg"):
            test_file.unlink(missing_ok=True)
        
        yield  # Run the test
        
        # Clean up after test
        for test_file in project_root.glob("test_output_*.svg"):
            test_file.unlink(missing_ok=True)
    
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
    def test_individual_graph_rendering(self, samples_dir, tmp_path, mmd_file):
        """Test each graph individually - no skipping, capture all failures."""
        file_path = samples_dir / mmd_file
        
        # Verify file exists first
        assert file_path.exists(), f"File not found: {mmd_file}"
        
        # Read content
        mermaid_content = file_path.read_text(encoding='utf-8')
        print(f"\n--- Testing {mmd_file} ---")
        print(f"Content preview: {mermaid_content[:100]}...")
        
        # Test 1: Mermaid rendering to static SVG
        renderer = MermaidRenderer(headless=True)
        try:
            static_svg = renderer.render_to_svg(mermaid_content)
            print("✅ Static SVG generation: SUCCESS")
            static_success = True
            
            # Basic SVG validation
            assert static_svg is not None
            assert len(static_svg) > 0
            assert "<svg" in static_svg
            assert "</svg>" in static_svg
            
        except Exception as e:
            print(f"❌ Static SVG generation: FAILED - {e}")
            static_success = False
            static_svg = None
        
        # Test 2: Animation processing (only if static SVG worked)
        if static_success and static_svg:
            try:
                graph = Graph(mermaid_content)
                animated_svg = graph.animate(theme=CYBERPUNK)
                print("✅ Animation processing: SUCCESS")
                
                # Validate animated SVG
                assert animated_svg is not None
                assert len(animated_svg) > 0
                assert "<style>" in animated_svg
                assert "@keyframes" in animated_svg
                
                # Save for inspection in temporary directory
                output_file = tmp_path / f"test_output_{mmd_file.replace('.mmd', '.svg')}"
                output_file.write_text(animated_svg)
                print(f"📁 Saved output to: {output_file}")
                
            except Exception as e:
                print(f"❌ Animation processing: FAILED - {e}")
                # Don't fail the test here, just record the failure
                pytest.fail(f"Animation failed for {mmd_file}: {e}")
        
        else:
            # If static SVG failed, the whole test should fail
            pytest.fail(f"Static SVG rendering failed for {mmd_file}")
    
    def test_comprehensive_batch_report(self, samples_dir):
        """Generate a comprehensive report of all graphs."""
        all_files = list(samples_dir.glob("*.mmd"))
        results = {}
        
        print("\n" + "="*80)
        print("COMPREHENSIVE MERMAID GRAPH TEST REPORT")
        print("="*80)
        
        for mmd_file in sorted(all_files):
            filename = mmd_file.name
            print(f"\n📄 Testing: {filename}")
            
            try:
                # Read content
                mermaid_content = mmd_file.read_text(encoding='utf-8')
                print(f"   📝 Content length: {len(mermaid_content)} characters")
                
                # Test static rendering
                renderer = MermaidRenderer(headless=True)
                static_svg = renderer.render_to_svg(mermaid_content)
                print(f"   ✅ Static SVG: SUCCESS ({len(static_svg)} chars)")
                
                # Test animation
                graph = Graph(mermaid_content)
                animated_svg = graph.animate(theme=CYBERPUNK)
                print(f"   ✅ Animation: SUCCESS ({len(animated_svg)} chars)")
                
                results[filename] = "FULL SUCCESS"
                
            except Exception as e:
                print(f"   ❌ ERROR: {type(e).__name__}: {e}")
                results[filename] = f"FAILED: {e}"
        
        # Summary report
        print("\n" + "="*80)
        print("FINAL SUMMARY:")
        print("="*80)
        
        successes = []
        failures = []
        
        for filename, result in sorted(results.items()):
            status = "✅" if result == "FULL SUCCESS" else "❌"
            print(f"{status} {filename}: {result}")
            
            if result == "FULL SUCCESS":
                successes.append(filename)
            else:
                failures.append(filename)
        
        print("\n📊 STATISTICS:")
        print(f"   Total files: {len(results)}")
        print(f"   Successes: {len(successes)}")
        print(f"   Failures: {len(failures)}")
        print(f"   Success rate: {len(successes)/len(results)*100:.1f}%")
        
        if failures:
            print("\n🔍 FAILED FILES:")
            for filename in failures:
                print(f"   - {filename}")
        
        # Store results for later analysis
        self._test_results = results


class TestSampleGraphsUnitTest(unittest.TestCase):
    """Simplified unittest-compatible version of sample graph tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.samples_dir = Path(__file__).parent.parent / "resources" / "mermaid_graphs"
    
    def test_unicode_characters_rendering(self):
        """Test specific case that was failing - Unicode characters."""
        file_path = self.samples_dir / "04_special_characters_unicode.mmd"
        if not file_path.exists():
            self.skipTest("Sample file not found")
            
        mermaid_content = file_path.read_text(encoding='utf-8')
        
        # Test static SVG generation
        renderer = MermaidRenderer(headless=True)
        static_svg = renderer.render_to_svg(mermaid_content)
        
        self.assertIsNotNone(static_svg)
        self.assertIn("<svg", static_svg)
        self.assertIn("</svg>", static_svg)
        
        # Test animation
        graph = Graph(mermaid_content)
        animated_svg = graph.animate(theme=CYBERPUNK)
        
        self.assertIsNotNone(animated_svg)
        self.assertIn("<style>", animated_svg)
        self.assertIn("@keyframes", animated_svg)
    
    def test_basic_flowchart_rendering(self):
        """Test basic flowchart rendering."""
        file_path = self.samples_dir / "01_kitchen_sink_flowchart.mmd"
        if not file_path.exists():
            self.skipTest("Sample file not found")
            
        mermaid_content = file_path.read_text(encoding='utf-8')
        
        # Test both static and animated rendering
        renderer = MermaidRenderer(headless=True)
        static_svg = renderer.render_to_svg(mermaid_content)
        self.assertIsNotNone(static_svg)
        
        graph = Graph(mermaid_content)
        animated_svg = graph.animate(theme=CYBERPUNK)
        self.assertIsNotNone(animated_svg)
        self.assertIn("@keyframes", animated_svg)
    
    def test_all_sample_files_exist(self):
        """Test that all expected sample files exist."""
        expected_files = [
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
        ]
        
        missing_files = []
        for filename in expected_files:
            if not (self.samples_dir / filename).exists():
                missing_files.append(filename)
        
        self.assertEqual(missing_files, [], f"Missing sample files: {missing_files}")