<div align="center">

  <div align="center">
    <img src="examples/outputs/viviphi_logo.svg" alt="Viviphi Logo" width="400">
  </div>

  <!-- Project Shields -->
  <p align="center">
    <a href="https://github.com/dbudaghyan/viviphi/stargazers"><img src="https://img.shields.io/github/stars/dbudaghyan/viviphi.svg?style=for-the-badge" alt="Stars"></a>
    <a href="https://github.com/dbudaghyan/viviphi/network/members"><img src="https://img.shields.io/github/forks/dbudaghyan/viviphi.svg?style=for-the-badge" alt="Forks"></a>
    <a href="https://github.com/dbudaghyan/viviphi/issues"><img src="https://img.shields.io/github/issues/dbudaghyan/viviphi.svg?style=for-the-badge" alt="Issues"></a>
    <a href="https://github.com/dbudaghyan/viviphi/graphs/contributors"><img src="https://img.shields.io/github/contributors/dbudaghyan/viviphi.svg?style=for-the-badge" alt="Contributors"></a>
    <a href="https://github.com/dbudaghyan/viviphi/blob/master/LICENSE"><img src="https://img.shields.io/github/license/dbudaghyan/viviphi?label=license&style=for-the-badge" alt="License"></a>
    <br />
    <a href="https://github.com/dbudaghyan/viviphi/actions"><img src="https://img.shields.io/github/actions/workflow/status/dbudaghyan/viviphi/coveralls.yml?style=for-the-badge&logo=python" alt="Build Status"></a>
    <a href="https://coveralls.io/github/dbudaghyan/viviphi?branch=master"><img src="https://img.shields.io/coveralls/github/dbudaghyan/viviphi/master.svg?style=for-the-badge" alt="Coverage Status"></a>
    <a href="https://github.com/dbudaghyan/viviphi/commits/master"><img src="https://img.shields.io/github/last-commit/dbudaghyan/viviphi.svg?style=for-the-badge" alt="Last Commit"></a>
    <a href="https://github.com/dbudaghyan/viviphi"><img src="https://img.shields.io/github/repo-size/dbudaghyan/viviphi.svg?style=for-the-badge" alt="Repo Size"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python" alt="Python Version"></a>
    <br />
    <a href="https://pypi.org/project/viviphi/"><img src="https://img.shields.io/pypi/v/viviphi?style=for-the-badge&logo=pypi" alt="PyPI version"></a>
    <a href="https://pepy.tech/project/viviphi"><img src="https://img.shields.io/pepy/dt/viviphi?style=for-the-badge" alt="Downloads"></a>
    <a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge" alt="PRs Welcome"></a>
  </p>
</div>

Turn static graphs into beautiful animations!

Viviphi transforms your Mermaid.js diagrams into stunning animated SVGs with customizable themes and smooth transitions. Perfect for presentations, documentation, or just making your diagrams come alive.

## ✨ Features

- 🎨 **Multiple Themes**: Cyberpunk, Corporate, and Hand-drawn styles
- ⚡ **Easy to Use**: Simple Python API with just a few lines of code
- 🎯 **Mermaid Compatible**: Works with standard Mermaid.js syntax
- 🚀 **Fast Rendering**: Powered by Playwright for reliable SVG generation
- 🎛️ **Customizable**: Adjustable animation speeds and timing

## 🚀 Quick Start

### Installation

```bash
# Install viviphi
uv add viviphi

# Install browser dependencies
uv run playwright install chromium
```

### Basic Usage

```python
from viviphi import Graph, MANIM_AQUA

# Define your Mermaid graph
mermaid_code = """
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
"""

# Create and animate
graph = Graph(mermaid_code)
animated_svg = graph.animate(theme=MANIM_AQUA, output="my_graph.svg")
```

That's it! Your animated SVG is ready.

## 🎨 Themes

Viviphi comes with three built-in themes:

### Manim Aqua 🌊
```python
from viviphi import Graph, MANIM_AQUA

graph = Graph(mermaid_code)
graph.animate(theme=MANIM_AQUA, output="manim_aqua_graph.svg")
```

<div align="center">
  <img src="examples/outputs/flowchart_manim_aqua.svg" alt="Manim Aqua Theme Example" width="300">
</div>

### Gradient Sunset 🌅
```python
from viviphi import Graph, GRADIENT_SUNSET

graph = Graph(mermaid_code)
graph.animate(theme=GRADIENT_SUNSET, output="gradient_sunset_graph.svg")
```

<div align="center">
  <img src="examples/outputs/flowchart_gradient_sunset.svg" alt="Gradient Sunset Theme Example" width="300">
</div>

### Hand Drawn ✏️
```python
from viviphi import Graph, HAND_DRAWN

graph = Graph(mermaid_code)
graph.animate(theme=HAND_DRAWN, output="hand_drawn_graph.svg")
```

<div align="center">
  <img src="examples/outputs/flowchart_hand_drawn.svg" alt="Hand Drawn Theme Example" width="300">
</div>

## ⚡ Animation Speed

Control the animation speed with the `speed` parameter:

```python
# Slow and dramatic
graph.animate(theme=MANIM_AQUA, speed="slow")

# Default speed
graph.animate(theme=MANIM_AQUA, speed="normal")

# Quick and snappy
graph.animate(theme=MANIM_AQUA, speed="fast")
```

## 📊 Supported Diagram Types

Viviphi works with all standard Mermaid diagram types:

### Flowcharts
```python
flowchart = """
graph LR
    A[User] --> B[Login]
    B --> C{Valid?}
    C -->|Yes| D[Dashboard]
    C -->|No| E[Error]
"""
```

<div align="center">
  <img src="examples/outputs/flowchart_example_manim_light.svg" alt="Flowchart Example" width="300">
</div>

### Sequence Diagrams
```python
sequence = """
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob
    B->>A: Hello Alice
"""
```

<div align="center">
  <img src="examples/outputs/sequence_manim_light.svg" alt="Sequence Diagram Example" width="300">
</div>

### Class Diagrams
```python
class_diagram = """
classDiagram
    class Vehicle {
        +String make
        +String model
        +start()
        +stop()
    }
    class Car {
        +openTrunk()
    }
    Vehicle <|-- Car
"""
```

<div align="center">
  <img src="examples/outputs/class_diagram_manim_light.svg" alt="Class Diagram Example" width="300">
</div>

### State Diagrams
```python
state_diagram = """
stateDiagram-v2
    [*] --> Idle
    Idle --> Running: start()
    Running --> Idle: stop()
    Running --> [*]: shutdown()
"""
```

<div align="center">
  <img src="examples/outputs/state_diagram_manim_light.svg" alt="State Diagram Example" width="300">
</div>

## 🔧 Advanced Usage

### Batch Processing

Process multiple diagrams at once:

```python
from pathlib import Path
from viviphi import Graph, CYBERPUNK, CORPORATE, HAND_DRAWN

def animate_all_diagrams(input_dir: Path, output_dir: Path):
    themes = {
        "cyberpunk": CYBERPUNK,
        "corporate": CORPORATE, 
        "hand_drawn": HAND_DRAWN
    }
    
    for mermaid_file in input_dir.glob("*.mmd"):
        content = mermaid_file.read_text()
        graph = Graph(content)
        
        for theme_name, theme in themes.items():
            output_file = output_dir / f"{mermaid_file.stem}_{theme_name}.svg"
            graph.animate(theme=theme, output=str(output_file))
```

### Custom Timing

Fine-tune animation timing:

```python
from viviphi import Graph, Theme

# Create a custom theme with specific timing
custom_theme = Theme(
    primary_color="#ff6b6b",
    background="#2d3748",
    edge_style="neon",
    animation_duration=2.5,  # Longer animations
    stagger_delay=0.5        # More delay between elements
)

graph = Graph(mermaid_code)
graph.animate(theme=custom_theme)
```

## 🎯 Real-World Examples

### Documentation Workflow
```python
from viviphi import Graph, GRADIENT_SUNSET

# Load your workflow diagram
workflow = """
graph TD
    A[Write Code] --> B[Create Mermaid Diagram]
    B --> C[Generate Animated SVG]
    C --> D[Include in Documentation]
    D --> E[Profit! 🎉]
"""

# Generate for docs
graph = Graph(workflow)
graph.animate(theme=GRADIENT_SUNSET, speed="normal", output="docs/workflow.svg")
```

### System Architecture
```python
from viviphi import Graph, MANIM_AQUA

architecture = """
graph TB
    subgraph "Frontend"
        UI[React App]
        API[API Client]
    end
    
    subgraph "Backend" 
        SERVER[Express Server]
        DB[(PostgreSQL)]
        CACHE[(Redis)]
    end
    
    UI --> API
    API --> SERVER
    SERVER --> DB
    SERVER --> CACHE
"""

graph = Graph(architecture)
graph.animate(theme=MANIM_AQUA, output="architecture.svg")
```

## 📁 Project Structure

```
viviphi/
├── viviphi/           # Main package
│   ├── animator.py    # SVG animation engine  
│   ├── graph.py       # Main Graph class
│   ├── mermaid.py     # Mermaid rendering
│   └── themes.py      # Theme definitions
├── examples/          # Usage examples
├── resources/         # Sample Mermaid files
└── tests/            # Test suite
```

## 🛠️ Development

```bash
# Clone the repository
git clone <repository-url>
cd viviphi

# Install dependencies
uv sync --no-install-project

# Run tests
uv run pytest

# Check code quality
ruff check
ruff format
```

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## 📄 License

This project is open source. See LICENSE file for details.

---

**Made with ❤️ by the Viviphi team**

*Transform your static diagrams into dynamic stories!*