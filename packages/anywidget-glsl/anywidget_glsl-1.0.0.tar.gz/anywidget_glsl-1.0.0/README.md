# anywidget-glsl

[![PyPI](https://img.shields.io/pypi/v/anywidget-glsl.svg)](https://pypi.org/project/anywidget-glsl/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/pypi/pyversions/anywidget-glsl.svg)](https://pypi.org/project/anywidget-glsl/)

Write GPU-accelerated GLSL shaders in [marimo](https://github.com/marimo-team/marimo) notebooks with a Shadertoy-like API built on [AnyWidget](https://github.com/manzt/anywidget).

## Features

- 🎨 **Shadertoy-compatible API** - Familiar `mainImage()` signature with built-in uniforms
- 🔗 **String-free wiring** - Connect shader passes using class attributes instead of string names
- 🎬 **Multi-pass rendering** - Compose complex effects with feedback buffers
- 🎮 **Interactive inputs** - Built-in support for mouse, keyboard, webcam, and time
- 🔧 **Full Pipeline API** - Explicit vertex+fragment shader control for advanced use cases
- 📊 **Type-safe uniforms** - Python↔GLSL binding with numpy arrays and textures
- 🐛 **Clear error messages** - Source wrapped with `#line` directives for precise GLSL debugging

## Installation

```bash
uv add anywidget-glsl
```

### Development Installation

```bash
git clone https://github.com/dmadisetti/anywidget-glsl.git
cd anywidget-glsl
pip install -e ".[dev]"
```

## Quick Start

### Simple Animated Shader

```python
from anywidget_glsl import ToyGLSL

class Rainbow(ToyGLSL):
    time = True  # Enable iTime uniform

    _glsl = r"""
    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec2 uv = fragCoord / iResolution.xy;
        vec3 color = 0.5 + 0.5 * cos(iTime + uv.xyx + vec3(0, 2, 4));
        fragColor = vec4(color, 1.0);
    }
    """

Rainbow()  # Display in notebook
```

### Interactive with Mouse

```python
class Interactive(ToyGLSL):
    time = True
    mouse = True  # Enable iMouse uniform

    _glsl = r"""
    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec2 uv = fragCoord / iResolution.xy;
        vec2 mouse = iMouse.xy / iResolution.xy;
        float dist = length(uv - mouse);
        vec3 color = vec3(1.0 - smoothstep(0.0, 0.3, dist));
        fragColor = vec4(color, 1.0);
    }
    """

Interactive()
```

## ToyGLSL API (Image Shaders)

The `ToyGLSL` API is inspired by Shadertoy and focuses on fragment shaders with automatic uniform management.

### Built-in Uniforms

Enable uniforms by setting class attributes:

```python
class MyShader(ToyGLSL):
    time = True       # → uniform float iTime
    mouse = True      # → uniform vec4 iMouse (xy = pos, zw = click state)
    webcam = True     # → uniform sampler2D iWebcam
    keyboard = True   # → uniform sampler2D iKeyboard (256×1 texture)
```

Always available:
- `uniform vec3 iResolution` - Canvas size (width, height, 1.0)
- `uniform float iTimeDelta` - Time since last frame
- `uniform float iFrame` - Frame counter
- `uniform float iFrameRate` - Frames per second
- `uniform vec4 iDate` - (year, month, day, time in seconds)

### Multi-Pass Composition

Create complex effects by chaining shader passes:

```python
class BlurPass(ToyGLSL):
    _glsl = r"""
    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec2 uv = fragCoord / iResolution.xy;
        vec4 sum = vec4(0.0);
        for(int i = -2; i <= 2; i++) {
            for(int j = -2; j <= 2; j++) {
                vec2 offset = vec2(i, j) / iResolution.xy;
                sum += texture(iPrevPass, uv + offset);
            }
        }
        fragColor = sum / 25.0;
    }
    """

class Final(ToyGLSL):
    time = True
    _buffers = (BlurPass,)  # BlurPass runs first

    _glsl = r"""
    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec2 uv = fragCoord / iResolution.xy;
        vec3 blurred = texture(iPrevPass, uv).rgb;
        vec3 color = blurred * (0.5 + 0.5 * sin(iTime));
        fragColor = vec4(color, 1.0);
    }
    """

Final()
```

### Feedback Buffers

Use `backbuffer=True` to access the previous frame for trail effects:

```python
class Trail(ToyGLSL):
    time = True
    mouse = True
    backbuffer = True  # → uniform sampler2D iBackbuffer

    _glsl = r"""
    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec2 uv = fragCoord / iResolution.xy;
        vec2 mouse = iMouse.xy / iResolution.xy;

        // Read previous frame
        vec4 prev = texture(iBackbuffer, uv);

        // Add new content near mouse
        float dist = length(uv - mouse);
        vec3 add = vec3(1.0 - smoothstep(0.0, 0.1, dist));

        // Fade and accumulate
        fragColor = vec4(prev.rgb * 0.95 + add, 1.0);
    }
    """

Trail()
```

### String-Free Connectors

Wire shader passes without string names using class attribute references:

```python
class PassA(ToyGLSL):
    time = True
    _glsl = r"""
    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec2 uv = fragCoord / iResolution.xy;
        fragColor = vec4(uv, sin(iTime) * 0.5 + 0.5, 1.0);
    }
    """

class PassB(ToyGLSL):
    time = True
    source_a = PassA.frag  # Reference PassA's output (no strings!)

    _glsl = r"""
    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec2 uv = fragCoord / iResolution.xy;
        vec3 a = texture(source_a, uv).rgb;
        fragColor = vec4(1.0 - a, 1.0);  // Invert colors
    }
    """

PassB()  # PassA runs automatically as a dependency
```

## Pipeline API (Vertex + Fragment)

For advanced use cases requiring full control over the vertex and fragment pipeline:

```python
from anywidget_glsl import uniform
from anywidget_glsl.pipeline import (
    VertexProgram, FragmentProgram, In, Out, Color, PipelineFactory
)

class MyVertex(VertexProgram):
    # Declare vertex attributes
    position = In[uniform.Vec2](loc=0).tag(sync=True)
    color = In[uniform.Vec3](loc=1).tag(sync=True)

    # Declare varyings
    v_color = Out[uniform.Vec3]()
    gl_Position = Out[uniform.Vec4]()

    _glsl = """
    void main() {
        v_color = color;
        gl_Position = vec4(position, 0.0, 1.0);
    }
    """

class MyFragment(FragmentProgram):
    # Receive varyings from vertex shader
    v_color = MyVertex.v_color

    # Declare color output
    color0 = Color[uniform.Vec4](loc=0)

    _glsl = """
    void main() {
        color0 = vec4(v_color, 1.0);
    }
    """

# Create widget from pipeline
MyPipeline = PipelineFactory(MyFragment.color0)

# Use in notebook
import numpy as np
positions = np.array([[-0.5, -0.5], [0.5, -0.5], [0.0, 0.5]], dtype=np.float32)
colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)

widget = MyPipeline(position=positions, color=colors)
widget
```

## Examples

Check out the `examples/` directory for more demos:

- `basic_shader.py` - Simple animated shaders
- `interactive_uniforms.py` - Mouse and time interactions
- `multipass_feedback.py` - Multi-pass rendering with backbuffers
- `pipeline_demo.py` - Vertex+fragment pipeline examples
- `filters_demo.py` - Built-in filter effects

## API Reference

### ToyGLSL Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `time` | `bool` | Enable `iTime` uniform |
| `mouse` | `bool` | Enable `iMouse` uniform (vec4) |
| `webcam` | `bool` | Enable `iWebcam` texture |
| `keyboard` | `bool` | Enable `iKeyboard` texture (256×1) |
| `backbuffer` | `bool` | Enable `iBackbuffer` (previous frame) |
| `_glsl` | `str` | Fragment shader source with `mainImage()` |
| `_buffers` | `tuple` | Tuple of ToyGLSL classes for multi-pass |

### Uniform Types

From `anywidget_glsl.uniform`:

- `Vec2`, `Vec3`, `Vec4` - Vector uniforms
- `Mat2`, `Mat3`, `Mat4` - Matrix uniforms
- `Float`, `Int` - Scalar uniforms
- `Texture2D` - Image textures

All uniform types are traitlets and must be tagged with `.tag(sync=True)` for Python↔JavaScript synchronization.

## Built-in Filters

```python
from anywidget_glsl.filters import Blur, Trail

# Apply Gaussian blur
blurred = Blur(source=MyShader.frag, radius=5.0)

# Apply trail effect
trails = Trail(source=MyShader.frag, decay=0.95)
```

## Requirements

- Python ≥ 3.13
- anywidget ≥ 0.9.0
- numpy ≥ 2.3.4
- marimo ≥ 0.17.2 (for notebook environments)

## Browser Compatibility

Requires WebGL 2.0 support. Compatible with:
- Chrome/Edge 56+
- Firefox 51+
- Safari 15+

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built on [AnyWidget](https://github.com/manzt/anywidget) by Trevor Manz.

Inspired by [Shadertoy](https://www.shadertoy.com/) by Iñigo Quilez and Pol Jeremias.
