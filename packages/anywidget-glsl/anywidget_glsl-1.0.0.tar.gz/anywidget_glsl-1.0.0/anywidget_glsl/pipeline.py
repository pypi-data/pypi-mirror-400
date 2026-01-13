from __future__ import annotations

# ruff: noqa: E402
"""
Pipeline authoring primitives (pre-declared vertex attributes, typed varyings,
and color attachments) with a class-first, string-free API.

This module provides descriptors and traitlets for defining explicit pipelines
without a Vao container. Example:

    from anywidget_glsl import uniform
    from anywidget_glsl.pipeline import VertexProgram, ShaderProgram, In, Out, Color

    class Vert(VertexProgram):
        pos = In[uniform.Vec2](loc=0).tag(sync=True)
        uv = In[uniform.Vec2](loc=1).tag(sync=True)
        v_uv = Out[uniform.Vec2]()
        gl_Position = Out[uniform.Vec4]()
        _glsl = \"""
        void main(){
          v_uv = uv;                // name-bound attributes inferred from class
          gl_Position = vec4(pos, 0.0, 1.0);
        }
        \"""

    class Frag(ShaderProgram):
        v_uv = Vert.v_uv
        color0 = Color[uniform.Vec4](loc=0)
        _glsl = \"""
        void main(){ color0 = vec4(vec3(v_uv, 0.0), 1.0); }
        \"""

Note: Runtime execution and JS codegen are added in later iterations. This file
establishes the Python surface and metadata for connectors and attributes.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import traitlets as _tl

from anywidget_glsl import uniform
from anywidget_glsl.connectors import ConnectorRef
from anywidget_glsl.widget import GLSLWidget

# -----------------------------------------
# Vertex attribute trait (pre-declared, no Vao)
# -----------------------------------------


class _VertexAttr(_tl.TraitType):
    """
    Vertex attribute traitlet.

    Validates numpy arrays shaped (N, D) where D is inferred from the
    associated uniform type (e.g., Vec2 → D=2). Dtype must be float32.
    """

    def __init__(self, *, elem: type[uniform.Uniform], loc: int | None = None):
        super().__init__()
        self._elem = elem
        self._loc = loc
        # Extract dims from uniform type (e.g., Vec2 → (2,))
        self._dims = getattr(elem, "dims", None)
        if not isinstance(self._dims, tuple) or len(self._dims) != 1:
            raise TypeError(
                "Vertex attribute element must be a vector Uniform type (e.g., Vec2/Vec3/Vec4)"
            )
        if self._dims[0] not in (1, 2, 3, 4):
            raise TypeError("Unsupported attribute size; expected 1-4 components")

    @property
    def size(self) -> int:
        return int(self._dims[0])

    @property
    def loc(self) -> int | None:
        return self._loc

    @property
    def glsl_type(self) -> str:
        return self._elem.gl_func()

    def validate(self, obj, value):
        if value is _tl.Undefined:
            raise _tl.TraitError(f"Vertex attribute '{self.name}' must be set on initialization.")
        try:
            arr = np.asarray(value)
        except Exception as e:
            raise _tl.TraitError(
                f"Could not convert attribute '{self.name}' to numpy array: {e}"
            ) from e

        # Auto-reshape 1D arrays to (N, 1) for scalar attributes
        if self.size == 1 and arr.ndim == 1:
            arr = arr.reshape(-1, 1)

        if arr.ndim != 2 or arr.shape[1] != self.size:
            raise _tl.TraitError(
                f"Attribute '{self.name}' must have shape (N, {self.size}), got {arr.shape}"
            )
        if arr.dtype != np.float32:
            try:
                arr = arr.astype(np.float32, copy=False)
            except Exception as e:
                raise _tl.TraitError(
                    f"Attribute '{self.name}' must be float32-compatible, got {arr.dtype}"
                ) from e
        # Ensure C-contiguous for upload
        if not arr.flags["C_CONTIGUOUS"]:
            arr = np.ascontiguousarray(arr)
        return arr


class In:
    """
    Factory for vertex attributes.

    Usage: `pos = In[uniform.Vec2](loc=0).tag(sync=True)`
    """

    @classmethod
    def __class_getitem__(cls, elem: type[uniform.Uniform]) -> Callable[..., _VertexAttr]:
        if not (isinstance(elem, type) and issubclass(elem, uniform.Uniform)):
            raise TypeError("In[...] expects a Uniform subclass, e.g., In[uniform.Vec2]")

        def _ctor(*, loc: int | None = None) -> _VertexAttr:
            return _VertexAttr(elem=elem, loc=loc)

        return _ctor


# -----------------------------------------
# Index buffer trait
# -----------------------------------------


class IndexBuffer(_tl.TraitType):
    """
    Index buffer for indexed draws. Expects 1D array of uint16 or uint32.
    """

    def validate(self, obj, value):
        if value is _tl.Undefined:
            raise _tl.TraitError("Index buffer must be set on initialization.")
        try:
            arr = np.asarray(value)
        except Exception as e:
            raise _tl.TraitError(f"Could not convert index buffer to numpy array: {e}") from e
        if arr.ndim != 1:
            raise _tl.TraitError(f"Index buffer must be 1D array, got shape {arr.shape}")
        if arr.dtype not in (np.uint16, np.uint32):
            try:
                # default to uint32 for safety in WebGL2
                arr = arr.astype(np.uint32, copy=False)
            except Exception as e:
                raise _tl.TraitError(
                    f"Index buffer dtype must be uint16 or uint32, got {arr.dtype}"
                ) from e
        if not arr.flags["C_CONTIGUOUS"]:
            arr = np.ascontiguousarray(arr)
        return arr


# -----------------------------------------
# Varying and color connectors (string-free)
# -----------------------------------------


@dataclass(frozen=True)
class _DescriptorSpec:
    glsl_type: str
    loc: int | None = None


class Out:
    """
    Varying output descriptor for vertex stage.

    Usage: `v_uv = Out[uniform.Vec2]()`
    """

    def __init__(self, glsl_type: str):
        self._spec = _DescriptorSpec(glsl_type=glsl_type)
        self._name: str | None = None

    @classmethod
    def __class_getitem__(cls, elem: type[uniform.Uniform]) -> Out:
        if not (isinstance(elem, type) and issubclass(elem, uniform.Uniform)):
            raise TypeError("Out[...] expects a Uniform subclass, e.g., Out[uniform.Vec2]")
        return cls(glsl_type=elem.gl_func())

    def __call__(self) -> Out:
        return self

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def __get__(self, instance, owner: type) -> ConnectorRef:
        name = self._name or "varying"
        return ConnectorRef(owner=owner, attr=name, glsl_type=self._spec.glsl_type)


class _ColorDescriptor:
    def __init__(self, *, glsl_type: str, loc: int = 0) -> None:
        self._spec = _DescriptorSpec(glsl_type=glsl_type, loc=loc)
        self._name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name

    def __get__(self, instance, owner: type) -> ConnectorRef:
        name = self._name or "color0"
        return ConnectorRef(owner=owner, attr=name, glsl_type=self._spec.glsl_type)

    @property
    def loc(self) -> int:
        return int(self._spec.loc or 0)

    @property
    def glsl_type(self) -> str:
        return self._spec.glsl_type


class Color:
    """
    Fragment color attachment descriptor.

    Usage: `color0 = Color[uniform.Vec4](loc=0)`
    """

    @classmethod
    def __class_getitem__(cls, elem: type[uniform.Uniform]) -> Callable[..., _ColorDescriptor]:
        if not (isinstance(elem, type) and issubclass(elem, uniform.Uniform)):
            raise TypeError("Color[...] expects a Uniform subclass, e.g., Color[uniform.Vec4]")

        def _ctor(*, loc: int = 0) -> _ColorDescriptor:
            return _ColorDescriptor(glsl_type=elem.gl_func(), loc=loc)

        return _ctor


# -----------------------------------------
# Program bases and factory (skeleton)
# -----------------------------------------


class VertexProgram:
    """Base class for vertex stage authoring (metadata only)."""

    _glsl: str


class FragmentProgram:
    """Base class for fragment stage authoring (metadata only)."""

    _glsl: str


def PipelineFactory(final: ConnectorRef) -> type[GLSLWidget]:
    """
    Create a GLSLWidget subclass that represents the pipeline ending at `final`.

    - `final` should be a ConnectorRef to a Color[...] on a FragmentProgram.
    - Currently supports a single vertex+fragment pass.
    """

    # Validate final output owner
    frag_cls = final.owner
    if not isinstance(frag_cls, type) or not issubclass(frag_cls, FragmentProgram):  # type: ignore[arg-type]
        raise TypeError("PipelineFactory expects a FragmentProgram color output handle")

    # Discover varyings from fragment → vertex (final vertex stage referenced)
    varyings: list[dict[str, str]] = []
    vertex_end: type | None = None
    for name, val in vars(frag_cls).items():
        if (
            isinstance(val, ConnectorRef)
            and isinstance(val.owner, type)
            and issubclass(val.owner, VertexProgram)
        ):
            if vertex_end is None:
                vertex_end = val.owner
            elif vertex_end is not val.owner:
                raise ValueError("Multiple VertexProgram providers not supported in v1")
            varyings.append({"name": name, "type": val.glsl_type})

    if vertex_end is None:
        raise ValueError("FragmentProgram must consume at least one varying from a VertexProgram")

    # Optional upstream vertex chain: ... -> vertex_end
    vertex_chain: list[type] = []
    cur = vertex_end
    while True:
        vertex_chain.append(cur)
        upstream: type | None = None
        for _n, _v in vars(cur).items():
            if (
                isinstance(_v, ConnectorRef)
                and isinstance(_v.owner, type)
                and issubclass(_v.owner, VertexProgram)
            ):
                if upstream is not None and upstream is not _v.owner:
                    raise ValueError("Multiple upstream VertexProgram providers not supported yet")
                upstream = _v.owner
        if upstream is None:
            break
        cur = upstream
    vertex_chain.reverse()

    # Uniforms from both stages (sync=True only)
    def collect_uniforms(cls: type) -> dict[str, _tl.TraitType]:
        out: dict[str, _tl.TraitType] = {}
        for k, v in vars(cls).items():
            if (
                isinstance(v, (uniform.Uniform, uniform.Texture2D))
                and getattr(v, "metadata", {}).get("sync", False) is True
            ):
                out[k] = v
        return out

    # Build multi-pass spec: discover fragment classes in topo order
    order: list[type] = []
    seen_frag: set[type] = set()

    def collect(fcls: type) -> None:
        if fcls in seen_frag:
            return
        for _, val in vars(fcls).items():
            if (
                isinstance(val, ConnectorRef)
                and isinstance(val.owner, type)
                and issubclass(val.owner, FragmentProgram)
            ):
                collect(val.owner)
        order.append(fcls)
        seen_frag.add(fcls)

    collect(frag_cls)

    frag_to_index: dict[type, int] = {f: i for i, f in enumerate(order)}
    passes_spec: list[dict[str, Any]] = []
    vertex_traits: dict[str, _VertexAttr] = {}
    index_names: set[str] = set()
    uniforms_map: dict[str, _tl.TraitType] = {}

    for fcls in order:
        # Vertex stage for this fragment
        varyings: list[dict[str, str]] = []
        vertex_cls: type | None = None
        for name, val in vars(fcls).items():
            if (
                isinstance(val, ConnectorRef)
                and isinstance(val.owner, type)
                and issubclass(val.owner, VertexProgram)
            ):
                if vertex_cls is None:
                    vertex_cls = val.owner
                elif vertex_cls is not val.owner:
                    raise ValueError(
                        "A FragmentProgram must reference a single VertexProgram for varyings"
                    )
                varyings.append({"name": name, "type": val.glsl_type})
        if vertex_cls is None:
            raise ValueError(f"{fcls.__name__} must reference a VertexProgram varying")

        # Attributes and index for this pass
        attributes: list[dict[str, int | str | None]] = []
        index_name: str | None = None
        for attr_name, trait in vars(vertex_cls).items():
            if isinstance(trait, _VertexAttr):
                vertex_traits[attr_name] = trait
                attributes.append(
                    {
                        "name": attr_name,
                        "size": trait.size,
                        "type": trait.glsl_type,
                        "loc": trait.loc,
                    }
                )
            elif isinstance(trait, IndexBuffer):
                index_name = attr_name
                index_names.add(attr_name)

        # Uniforms
        uniforms_map.update(collect_uniforms(vertex_cls))
        uniforms_map.update(collect_uniforms(fcls))

        # Inputs from prior fragment passes
        inputs: list[dict[str, Any]] = []
        for name, val in vars(fcls).items():
            if (
                isinstance(val, ConnectorRef)
                and isinstance(val.owner, type)
                and issubclass(val.owner, FragmentProgram)
            ):
                inputs.append(
                    {
                        "name": name,
                        "from": frag_to_index[val.owner],
                        "type": "sampler2D",
                        "source_attr": val.attr,
                    }
                )

        passes_spec.append(
            {
                "name": f"{vertex_cls.__name__}+{fcls.__name__}",
                "vert": getattr(vertex_cls, "_glsl", ""),
                "frag": getattr(fcls, "_glsl", ""),
                "time": bool(getattr(vertex_cls, "time", False) or getattr(fcls, "time", False)),
                "mouse": bool(getattr(vertex_cls, "mouse", False) or getattr(fcls, "mouse", False)),
                "webcam": bool(
                    getattr(vertex_cls, "webcam", False) or getattr(fcls, "webcam", False)
                ),
                "keyboard": bool(
                    getattr(vertex_cls, "keyboard", False) or getattr(fcls, "keyboard", False)
                ),
                "varyings": varyings,
                "attributes": attributes,
                "colors": [{"name": "color0", "type": "vec4", "loc": 0}],
                "primitive": getattr(vertex_cls, "primitive", "points"),
                "index": index_name,
                "inputs": inputs,
                "overlay": bool(
                    getattr(vertex_cls, "overlay", False) or getattr(fcls, "overlay", False)
                ),
            }
        )

    # Create dynamic widget subclass and copy traitlets for attrs + uniforms
    class _Pipeline(GLSLWidget):
        # stateful traitlets synced to frontend
        glsl = _tl.Unicode("").tag(sync=True)
        _width = _tl.Int(640).tag(sync=True)
        _height = _tl.Int(360).tag(sync=True)
        _time = _tl.Bool(False).tag(sync=True)
        _mouse = _tl.Bool(False).tag(sync=True)
        _webcam = _tl.Bool(False).tag(sync=True)
        _keyboard = _tl.Bool(False).tag(sync=True)
        _backbuffer = _tl.Bool(False).tag(sync=True)
        _passes = _tl.List(_tl.Dict()).tag(sync=True)
        _uniforms = _tl.Dict(key_trait=_tl.Unicode(), value_trait=_tl.Unicode()).tag(sync=True)

        def __init__(self, **kwargs: Any) -> None:
            # Set toggles based on stages
            def _get(stage: type, name: str, default: bool = False) -> bool:
                return bool(getattr(stage, name, default))

            # Validate pass sources
            for p in passes_spec:
                if not isinstance(p["vert"], str) or not p["vert"].strip():
                    raise ValueError(
                        f"Vertex program for pass {p['name']} must define non-empty _glsl string"
                    )
                if not isinstance(p["frag"], str) or not p["frag"].strip():
                    raise ValueError(
                        f"Fragment program for pass {p['name']} must define non-empty _glsl string"
                    )

            uniforms_types: dict[str, str] = {k: v.gl_func() for k, v in uniforms_map.items()}

            # Initialize required attributes/uniforms/index from kwargs
            for p in passes_spec:
                for a in p["attributes"]:
                    name = a["name"]
                    if name not in self._trait_values:
                        if name in kwargs:
                            setattr(self, name, kwargs.pop(name))
                        else:
                            getattr(self.__class__, name).validate(self, _tl.Undefined)
                if p.get("index"):
                    n = p["index"]
                    if n not in self._trait_values:
                        if n in kwargs:
                            setattr(self, n, kwargs.pop(n))
                        else:
                            getattr(self.__class__, n).validate(self, _tl.Undefined)
            for k in uniforms_types:
                if k not in self._trait_values:
                    if k in kwargs:
                        setattr(self, k, kwargs.pop(k))
                    else:
                        getattr(self.__class__, k).validate(self, _tl.Undefined)

            self._passes = passes_spec
            self._uniforms = uniforms_types
            super().__init__(**kwargs)

    # Attach traitlets for attributes/uniforms/index across all passes
    attached_attrs: set[str] = set()
    for p in passes_spec:
        for a in p["attributes"]:
            name = str(a["name"])  # type: ignore[index]
            if name in attached_attrs:
                continue
            t = vertex_traits[name]
            new_trait = _VertexAttr(elem=t._elem, loc=t._loc).tag(sync=True)
            try:
                new_trait.name = name  # type: ignore[attr-defined]
            except Exception:
                pass
            setattr(_Pipeline, name, new_trait)
            attached_attrs.add(name)
        if p.get("index"):
            n = str(p["index"])  # type: ignore[index]
            if not hasattr(_Pipeline, n):
                trait = IndexBuffer().tag(sync=True)
                try:
                    trait.name = n  # type: ignore[attr-defined]
                except Exception:
                    pass
                setattr(_Pipeline, n, trait)

    for k, v in uniforms_map.items():
        # create a fresh trait instance of the same type and tag for sync
        trait = v.__class__().tag(sync=True)  # type: ignore[call-arg]
        try:
            trait.name = k  # type: ignore[attr-defined]
        except Exception:
            pass
        setattr(_Pipeline, k, trait)

    _Pipeline.__name__ = f"Pipeline[{frag_cls.__name__}.{final.attr}]"
    return _Pipeline
