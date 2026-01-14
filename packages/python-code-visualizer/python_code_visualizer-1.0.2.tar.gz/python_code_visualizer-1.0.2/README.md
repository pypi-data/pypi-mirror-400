<p align="center">
  <img src="https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/python.svg" width="80" height="80" alt="Python Logo">
</p>

<h1 align="center">🐍 Python Code Visualizer</h1>

<p align="center">
  <strong>An interactive step-by-step Python code execution visualizer</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#api-reference">API</a> •
  <a href="#examples">Examples</a> •
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="MIT License">
  <img src="https://img.shields.io/badge/status-production--ready-brightgreen.svg?style=flat-square" alt="Production Ready">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome">
</p>

---

## ✨ Overview

**Python Code Visualizer** is a powerful library that helps developers and educators understand Python code execution by generating interactive, step-by-step visualizations. Watch your code come alive as you trace through variables, function calls, and control flow.

<p align="center">
  <img src="https://github.com/jayachandranpm/python-code-visualizer/blob/main/assets/demo-preview.webp" alt="Demo Preview" width="800">
</p>



---

## 🎯 Features

<table>
<tr>
<td width="50%">

### 🔍 **Execution Tracing**
- Line-by-line code execution
- Variable state tracking
- Function call/return visualization
- Exception handling display

</td>
<td width="50%">

### 📊 **Visual Analytics**
- Execution heatmap (hot loops)
- Timeline event markers
- Call stack visualization
- Scope separation (locals/globals)

</td>
</tr>
<tr>
<td width="50%">

### 🛡️ **Safety & Robustness**
- Timeout protection (default: 10s)
- Step limit (default: 10,000)
- HTML escaping (XSS prevention)
- Empty code validation

</td>
<td width="50%">

### 🎨 **Rich UI**
- VS Code-inspired dark theme
- Syntax highlighting (highlight.js)
- Keyboard navigation
- Playback controls

</td>
</tr>
</table>

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install via pip

```bash
# Clone the repository
git clone https://github.com/jayachandranpm/python-code-visualizer.git
cd python-code-visualizer

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `jinja2` | ≥3.0.0 | HTML template rendering |

---

## 🚀 Quick Start

### Basic Usage

```python
from PythonVisualizer import CodeVisualizer

code = """
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
total = sum(squares)
print(f"Sum of squares: {total}")
"""

# Create visualizer
viz = CodeVisualizer(code)

# Execute and capture trace
viz.execute()

# Generate HTML visualization
viz.render(output_file='visualization.html')
```

Then open `visualization.html` in your browser! 🎉

---

## 📖 API Reference

### `CodeVisualizer`

The main entry point for the library.

```python
CodeVisualizer(
    code: str,                    # Python code to visualize
    inputs: list = None,          # Mock inputs for input() calls
    timeout: float = 10.0,        # Execution timeout in seconds
    max_steps: int = 10000        # Maximum trace steps
)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `execute()` | Runs the code and captures trace | `dict` with `steps`, `counts`, `limit_reached` |
| `render(format='web', output_file='visualization.html')` | Generates visualization | File path or HTML string |

---

## 💡 Examples

### Example 1: Recursive Function

```python
from PythonVisualizer import CodeVisualizer

code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"5! = {result}")
"""

viz = CodeVisualizer(code)
viz.execute()
viz.render(output_file='factorial.html')
```

**What you'll see:**
- 🟢 Green markers for each recursive call
- 🟠 Orange markers for each return
- 📚 Deep call stack during recursion

---

### Example 2: User Input Handling

```python
from PythonVisualizer import CodeVisualizer

code = """
name = input("What's your name? ")
age = input("How old are you? ")
print(f"Hello {name}, you are {age} years old!")
"""

# Provide mock inputs
viz = CodeVisualizer(code, inputs=["Alice", "25"])
viz.execute()
viz.render(output_file='input_demo.html')
```

**What you'll see:**
- 💬 Terminal shows the conversation
- 📝 Variables update with input values

---

### Example 3: Exception Visualization

```python
from PythonVisualizer import CodeVisualizer

code = """
def divide(a, b):
    return a / b

result = divide(10, 0)  # This will crash!
"""

viz = CodeVisualizer(code)
viz.execute()
viz.render(output_file='exception.html')
```

**What you'll see:**
- 🔴 Red highlighted crash line
- ⚠️ Error banner with exception details
- 🔴 Red marker on timeline

---

## 🎮 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `←` | Step backward |
| `→` | Step forward |
| `Space` | Play / Pause |

---

## 🏗️ Project Structure

```
PythonVisualizer/
├── __init__.py              # Package exports
├── api.py                   # CodeVisualizer class
├── core/
│   ├── __init__.py
│   ├── parser.py            # AST validation
│   ├── tracer.py            # sys.settrace logic
│   └── executor.py          # Code execution engine
├── visualization/
│   ├── __init__.py
│   ├── web_renderer.py      # HTML generation
│   └── templates/
│       └── view.html.j2     # Jinja2 template
└── utils/
    ├── __init__.py
    └── serializer.py        # Object serialization
```

---

## 🔒 Security

Python Code Visualizer includes multiple security measures:

| Feature | Description |
|---------|-------------|
| **Timeout** | Prevents infinite loops (configurable) |
| **Step Limit** | Prevents memory exhaustion |
| **HTML Escaping** | Prevents XSS attacks in output |
| **Sandboxed Execution** | Code runs with limited globals |

> ⚠️ **Warning**: This library executes arbitrary Python code. Only visualize code you trust.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Highlight.js](https://highlightjs.org/) for syntax highlighting
- [Jinja2](https://jinja.palletsprojects.com/) for templating
- VS Code for UI inspiration

---

<p align="center">
  Made with ❤️ by developers, for developers
</p>

<p align="center">
  <a href="https://github.com/jayachandranpm/python-code-visualizer">
    <img src="https://img.shields.io/github/stars/jayachandranpm/python-code-visualizer?style=social" alt="GitHub Stars">
  </a>
</p>
