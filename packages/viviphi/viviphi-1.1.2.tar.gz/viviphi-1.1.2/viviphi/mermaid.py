"""Mermaid.js integration using headless browser for layout generation."""

from playwright.sync_api import sync_playwright


class MermaidRenderer:
    """Renders Mermaid definitions to static SVG using headless browser."""

    def __init__(self, headless: bool = True) -> None:
        """Initialize the renderer.

        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless

    def render_to_svg(self, mermaid_definition: str) -> str:
        """Render a Mermaid definition to static SVG.

        Args:
            mermaid_definition: Mermaid.js syntax string

        Returns:
            Static SVG content as string

        Raises:
            RuntimeError: If rendering fails
        """
        html_template = self._create_html_template(mermaid_definition)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            try:
                # Capture console messages to detect Mermaid errors
                console_messages = []
                page.on(
                    "console",
                    lambda msg: console_messages.append(f"{msg.type}: {msg.text}"),
                )

                # Load the HTML with Mermaid
                page.set_content(html_template)

                # Wait for either success or error state with increased timeout
                try:
                    # Check if SVG was rendered successfully
                    page.wait_for_selector("#mermaid-output svg", timeout=15000)
                except Exception:
                    # If SVG didn't render, check for error state
                    try:
                        page.wait_for_selector("#mermaid-error", timeout=2000)
                        error_msg = page.evaluate(
                            "document.querySelector('#mermaid-error').textContent"
                        )
                        raise RuntimeError(f"Mermaid rendering failed: {error_msg}")
                    except Exception:  # pragma: no cover
                        # Check console for errors
                        error_logs = [
                            msg for msg in console_messages if "error" in msg.lower()
                        ]
                        if error_logs:  # pragma: no cover
                            raise RuntimeError(
                                f"Mermaid rendering failed with errors: {'; '.join(error_logs)}"
                            )
                        else:
                            raise RuntimeError(
                                "Mermaid rendering timed out without clear error indication"
                            )

                # Extract the SVG content
                svg_content = page.evaluate("""() => {
                    const svg = document.querySelector('#mermaid-output svg');
                    return svg ? svg.outerHTML : null;
                }""")

                if not svg_content:
                    raise RuntimeError("Failed to generate SVG from Mermaid definition")

                return svg_content

            finally:
                browser.close()

    def _create_html_template(self, mermaid_definition: str) -> str:
        """Create HTML template with Mermaid.js and the definition.

        Args:
            mermaid_definition: Mermaid syntax string

        Returns:
            Complete HTML page content
        """
        # Don't escape - let Mermaid handle the content directly but use a safer approach
        # with JavaScript to set the content to avoid injection
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mermaid Renderer</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
        </head>
        <body>
            <div id="mermaid-output"></div>
            <div id="mermaid-error" style="display: none; color: red;"></div>
            
            <script>
                const mermaidDefinition = {repr(mermaid_definition)};
                
                try {{
                    mermaid.initialize({{
                        startOnLoad: false,
                        theme: 'base',
                        themeVariables: {{
                            primaryColor: '#ffffff',
                            primaryTextColor: '#000000',
                            primaryBorderColor: '#000000',
                            lineColor: '#000000',
                            secondaryColor: '#ffffff',
                            tertiaryColor: '#ffffff'
                        }},
                        // Better Unicode and special character support
                        securityLevel: 'loose',
                        htmlLabels: true,
                        fontFamily: 'Arial, sans-serif'
                    }});
                    
                    // Render the diagram
                    mermaid.run({{
                        querySelector: '.mermaid'
                    }});
                    
                    // Set the content after initialization
                    const outputDiv = document.getElementById('mermaid-output');
                    const preElement = document.createElement('pre');
                    preElement.className = 'mermaid';
                    preElement.textContent = mermaidDefinition;
                    outputDiv.appendChild(preElement);
                    
                    // Re-run mermaid on the new content
                    mermaid.run();
                    
                }} catch(error) {{
                    console.error('Mermaid error:', error);
                    const errorDiv = document.getElementById('mermaid-error');
                    errorDiv.style.display = 'block';
                    errorDiv.textContent = 'Error: ' + error.toString();
                }}
            </script>
        </body>
        </html>
        """
