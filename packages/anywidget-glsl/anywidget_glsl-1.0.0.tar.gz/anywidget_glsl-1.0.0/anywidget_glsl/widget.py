from importlib.resources import files as _pkg_files

import anywidget
import traitlets

import anywidget_glsl.uniform as uniform
from anywidget_glsl.connectors import ConnectorRef, Output


class GLSLWidget(anywidget.AnyWidget):
    """
    Base widget for GLSL-backed rendering in anywidget-glsl.

    Pipeline and Toy (image) widgets should subclass this base.
    """

    # Load widget front-end JavaScript from installed package data
    _esm = _pkg_files("anywidget_glsl").joinpath("src/glsl.js").read_text(encoding="utf-8")

    def __init__(self, **kwargs):
        # Accept ergonomic width/height and map to internal traits if present
        w = kwargs.pop("width", None)
        h = kwargs.pop("height", None)
        if w is not None:
            kwargs["_width"] = int(w)
        if h is not None:
            kwargs["_height"] = int(h)
        super().__init__(**kwargs)

    def destroy(self) -> None:
        """Request the frontend to destroy GL resources and detach the canvas."""
        # Toggle a synced trait to signal disposal
        try:
            self._destroy = True  # type: ignore[attr-defined]
        except Exception:
            pass

    def __del__(self) -> None:  # pragma: no cover
        """Best-effort backend cleanup trigger.

        Note: __del__ is not guaranteed to run in all environments (e.g.,
        interpreter shutdown). This is a safety net to try to signal the
        frontend to release GL resources if the widget is GC'ed without an
        explicit destroy() call.
        """
        try:
            if not getattr(self, "_destroy", False):
                # Swallow any errors — finalizers must not raise.
                self.destroy()
        except Exception:
            pass


class ToyGLSL(GLSLWidget):
    """
    Shadertoy-compatible Image Shader widget with optional backbuffer and
    multi-pass support via `_buffers`.

    Usage:
        class My(ToyGLSL):
            time = True
            mouse = True
            _glsl = \"""void mainImage(out vec4 fragColor, in vec2 fragCoord){ ... }\"""
    """

    # Class-level output handle for typed connectors
    frag = Output("sampler2D")

    def __init__(self, **kwargs):
        # Bridge Python attributes into traitlets used by the frontend
        self._form = self.form()

        # Enable instance-time connector wiring (e.g., Blur(source=SomeShader.frag))
        # Extract ConnectorRef instances from kwargs and temporarily assign as class attrs
        connector_kwargs = {}
        for key, value in list(kwargs.items()):
            if isinstance(value, (ConnectorRef, Output)):
                connector_kwargs[key] = value
                kwargs.pop(key)

        # Temporarily add connectors to class for dependency resolution
        if connector_kwargs:
            # Find the defining class in MRO - the original class that has _glsl defined
            # Skip the first (dynamic subclass) and find the next one with _glsl
            target_cls = self.__class__
            for cls in self.__class__.__mro__:
                if cls is not self.__class__ and "_glsl" in vars(cls):
                    target_cls = cls
                    break

            for key, value in connector_kwargs.items():
                setattr(target_cls, key, value)

        # Expect subclasses to define `_glsl` (shader source) and toggles
        if hasattr(self, "_glsl"):
            self.glsl = self._glsl

        # Booleans toggles on the top-level widget
        if hasattr(self, "mouse"):
            self._mouse = bool(self.mouse)
        if hasattr(self, "time"):
            self._time = bool(self.time)
        if hasattr(self, "webcam"):
            self._webcam = bool(self.webcam)
        if hasattr(self, "keyboard"):
            self._keyboard = bool(self.keyboard)
        if hasattr(self, "backbuffer"):
            self._backbuffer = bool(self.backbuffer)

        # Collect declared uniforms (Uniform/Texture traits on the class)
        uniforms = {
            k: v.gl_func()
            for k, v in self.__class__._traits.items()
            if isinstance(v, (uniform.Uniform, uniform.Texture2D))
            and getattr(v, "metadata", {}).get("sync", False) is True
        }

        # Ensure values are validated or set from kwargs
        for k in uniforms:
            if k not in self._trait_values:
                if k in kwargs:
                    setattr(self, k, kwargs.pop(k))
                else:
                    self.__class__._traits[k].validate(self, traitlets.Undefined)

        self._uniforms = uniforms

        # Assemble multi-pass descriptors from `_buffers` if present on class
        passes = []
        buffers = getattr(self.__class__, "_buffers", None)

        def collect_deps(cls: type, acc: list[type], seen: set[type]):
            if cls in seen:
                return
            # Gather providers from connectors on cls
            providers: list[type] = []
            for _, val in vars(cls).items():
                if isinstance(val, ConnectorRef):
                    providers.append(val.owner)
            for p in providers:
                collect_deps(p, acc, seen)
            if cls not in acc:
                acc.append(cls)
            seen.add(cls)

        if buffers:
            # Expand declared buffers with any implicit providers via connectors
            order: list[type] = []
            seen: set[type] = set()
            for B in buffers:
                collect_deps(B, order, seen)
            for idx, B in enumerate(order):
                # Resolve toggles with per-buffer override, else use top-level
                # Merge flags from entire dependency chain for uniform consistency
                def get(name, B=B, idx=idx):
                    # Check if ANY pass in the dependency chain up to B has this flag
                    flag_value = getattr(self, name, False)  # Start with top-level
                    for dep_cls in order[: idx + 1]:
                        if getattr(dep_cls, name, False):
                            flag_value = True
                            break
                    return bool(flag_value)

                glsl_src = getattr(B, "_glsl", None)
                if not isinstance(glsl_src, str) or len(glsl_src.strip()) == 0:
                    raise ValueError(f"Buffer {B.__name__} must define non-empty _glsl string")
                # Determine output name (single MRT for Image pass)
                out_names = [
                    k
                    for k, t in getattr(B, "_traits", {}).items()
                    if isinstance(t, uniform.Texture2D)
                    and not getattr(t, "metadata", {}).get("sync", False)
                ]
                if len(out_names) > 1:
                    raise ValueError(
                        f"{B.__name__} declares multiple outputs {out_names}; multiple render targets not supported yet"
                    )
                out_name = out_names[0] if out_names else "fragColor"
                # Scan inputs: any class attr that is a ConnectorRef to an earlier pass
                inputs = []
                for attr_name, val in vars(B).items():
                    if isinstance(val, ConnectorRef):
                        try:
                            from_idx = order.index(val.owner)
                        except ValueError:
                            raise ValueError(
                                f"Connector '{attr_name}' in {B.__name__} references provider {val.owner.__name__} not present in _buffers"
                            ) from None
                        if from_idx < idx:
                            inputs.append(
                                {
                                    "name": attr_name,
                                    "from": from_idx,
                                    "type": val.glsl_type,
                                    "source_attr": val.attr,
                                }
                            )
                passes.append(
                    {
                        "name": B.__name__,
                        "glsl": glsl_src,
                        "time": get("time"),
                        "mouse": get("mouse"),
                        "webcam": get("webcam"),
                        "keyboard": get("keyboard"),
                        "backbuffer": get("backbuffer"),
                        "out": out_name,
                        "inputs": inputs,
                    }
                )
        else:
            # Implicit pass graph from connectors on this class
            if hasattr(self, "_glsl") and isinstance(self._glsl, str):
                order: list[type] = []
                seen: set[type] = set()
                collect_deps(self.__class__, order, seen)
                for idx, B in enumerate(order):
                    # Merge flags from entire dependency chain for uniform consistency
                    def get(name, B=B, idx=idx):
                        # Check if ANY pass in the dependency chain up to B has this flag
                        flag_value = getattr(self, name, False)  # Start with top-level
                        for dep_cls in order[: idx + 1]:
                            if getattr(dep_cls, name, False):
                                flag_value = True
                                break
                        return bool(flag_value)

                    glsl_src = getattr(B, "_glsl", None)
                    if not isinstance(glsl_src, str) or len(glsl_src.strip()) == 0:
                        raise ValueError(f"Buffer {B.__name__} must define non-empty _glsl string")
                    # Determine output name
                    out_names = [
                        k
                        for k, t in getattr(B, "_traits", {}).items()
                        if isinstance(t, uniform.Texture2D)
                        and not getattr(t, "metadata", {}).get("sync", False)
                    ]
                    if len(out_names) > 1:
                        raise ValueError(
                            f"{B.__name__} declares multiple outputs {out_names}; multiple render targets not supported yet"
                        )
                    out_name = out_names[0] if out_names else "fragColor"
                    # Scan inputs for this pass
                    inputs = []
                    for attr_name, val in vars(B).items():
                        if isinstance(val, ConnectorRef):
                            try:
                                from_idx = order.index(val.owner)
                            except ValueError:
                                raise ValueError(
                                    f"Connector '{attr_name}' in {B.__name__} references provider {val.owner.__name__} not present"
                                ) from None
                            if from_idx >= idx:
                                raise ValueError(
                                    f"Connector '{attr_name}' in {B.__name__} must reference a provider that precedes it"
                                )
                            inputs.append(
                                {
                                    "name": attr_name,
                                    "from": from_idx,
                                    "type": val.glsl_type,
                                    "source_attr": val.attr,
                                }
                            )
                    passes.append(
                        {
                            "name": B.__name__,
                            "glsl": glsl_src,
                            "time": get("time"),
                            "mouse": get("mouse"),
                            "webcam": get("webcam"),
                            "keyboard": get("keyboard"),
                            "backbuffer": get("backbuffer"),
                            "out": out_name,
                            "inputs": inputs,
                        }
                    )

        self._passes = passes
        super().__init__(**kwargs)

    def form(self):
        return None

    # Stateful properties synced to the front-end
    _glsl: str
    glsl = traitlets.Unicode("").tag(sync=True)
    _width = traitlets.Int(640).tag(sync=True)
    _height = traitlets.Int(240).tag(sync=True)
    _time = traitlets.Bool(False).tag(sync=True)
    _mouse = traitlets.Bool(True).tag(sync=True)
    _webcam = traitlets.Bool(False).tag(sync=True)
    _keyboard = traitlets.Bool(False).tag(sync=True)
    _backbuffer = traitlets.Bool(False).tag(sync=True)
    _passes = traitlets.List(traitlets.Dict()).tag(sync=True)
    _uniforms = traitlets.Dict(key_trait=traitlets.Unicode(), value_trait=traitlets.Unicode()).tag(
        sync=True
    )
    # Disposal signal
    _destroy = traitlets.Bool(False).tag(sync=True)
