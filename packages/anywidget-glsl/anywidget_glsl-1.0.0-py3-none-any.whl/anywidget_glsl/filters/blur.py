from __future__ import annotations

from anywidget_glsl.connectors import ConnectorRef
from anywidget_glsl.widget import ToyGLSL


class Blur(ToyGLSL):
    """
    Generic, parameterized box blur filter. Use as `Blur[R]` where R is the
    integer blur radius (sample window = (2R+1)^2). Samples the previous pass
    via `iPrevPass` (place after a source in `_buffers`).

    Example:
        # Specify radius with []:
        blurred = Blur[5](source=SomeShader.frag)

        # Or use default radius=3:
        blurred = Blur(source=SomeShader.frag)

        # In multi-pass composition:
        Blur3 = Blur[3]
        class Blurred(ImageGLSL):
            _buffers = (Webcam, Blur3)
    """

    # Declare source input for connector system
    source: ConnectorRef

    def __new__(cls, *args, **kwargs):
        # If Blur() is called directly (not Blur[radius]), use default radius=3
        if cls is Blur:
            return Blur[3](*args, **kwargs)
        return super().__new__(cls)

    @classmethod
    def __class_getitem__(cls, radius: int) -> type[Blur]:
        if not isinstance(radius, int):
            raise TypeError("Blur[R]: R must be int")

        # Build GLSL body with a fixed-size sampling loop
        taps = 2 * radius + 1
        weight = 1.0 / float(taps * taps)
        # Unroll loops for determinism
        lines = [
            "vec2 texel = 1.0 / iResolution.xy;",
            "vec3 acc = vec3(0.0);",
        ]
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                lines.append(
                    f"acc += texture(iPrevPass, uv + texel * vec2({dx:.1f}, {dy:.1f})).rgb * {weight:.8f};"
                )
        lines.append("fragColor = vec4(acc, 1.0);")
        body = "\n      ".join(lines)

        # Create a concrete subclass with generated GLSL
        name = f"Blur_{radius}"
        return type(
            name,
            (Blur,),
            {
                "time": False,
                "backbuffer": False,
                "_glsl": (
                    "void mainImage(out vec4 fragColor, in vec2 fragCoord){\n"
                    "      vec2 uv = fragCoord / iResolution.xy;\n"
                    f"      {body}\n"
                    "    }"
                ),
            },
        )
