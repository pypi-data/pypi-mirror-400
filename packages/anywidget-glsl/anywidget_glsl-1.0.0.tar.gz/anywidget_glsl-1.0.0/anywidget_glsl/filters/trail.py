from __future__ import annotations

from anywidget_glsl.connectors import ConnectorRef
from anywidget_glsl.widget import ToyGLSL


class Trail(ToyGLSL):
    """
    Accumulative trail filter that blends the previous pass output (`iPrevPass`)
    with the last frame of this pass (`iBackbuffer`).

    Place Trail after any source pass in `_buffers`, e.g. `(WebcamBuf, Trail)`.
    Or use instance-time wiring: Trail(source=SomeShader.frag, decay=0.95)
    """

    # Declare source input for connector system
    source: ConnectorRef

    time = True
    backbuffer = True

    _glsl = r"""
    void mainImage(out vec4 fragColor, in vec2 fragCoord){
      vec2 uv = fragCoord / iResolution.xy;
      vec3 base = texture(iPrevPass, uv).rgb;    // output of previous pass
      vec3 prev = texture(iBackbuffer, uv).rgb;  // previous frame of Trail
      // simple decay + injection for visible trails
      vec3 ink = vec3(0.3, 0.6, 1.0) * 0.02;
      vec3 mixed = mix(prev, base + ink, 0.08);
      fragColor = vec4(mixed, 1.0);
    }
    """
