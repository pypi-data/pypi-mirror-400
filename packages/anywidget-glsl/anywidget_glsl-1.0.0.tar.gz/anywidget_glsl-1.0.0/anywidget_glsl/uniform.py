from collections.abc import Callable

import numpy as np
from traitlets import TraitError, TraitType, Undefined

# traitlets.utils.sentinel.Sentinel
# Primitive data types alias (bool maps to int for GL calls)
Prim = type[float] | type[int] | type[bool]
# Valid __class_getitem__ params
Params = int | Prim | tuple[int, Prim] | tuple[int, int] | tuple[int, int, Prim]


def _parse_params(params: Params) -> tuple[tuple[int, ...], type]:
    dims: list[int] = []
    dtype: type = float
    entries = params if isinstance(params, tuple) else (params,)

    for i, arg in enumerate(entries):
        if isinstance(arg, int):
            dims.append(arg)
        elif arg in (float, int, bool):
            assert i == len(entries) - 1, "dtype must be last"
            dtype = arg
        else:
            raise TypeError(f"Invalid Uniform parameters: {params!r}")
    return tuple(dims), dtype


_registry: dict[tuple[int, ...], dict[type, type["Uniform"]]] = {}


class Uniform(TraitType):
    """
    Base for all uniform types (scalars, vectors, matrices).
    Use Uniform[...] syntax to lookup a registered type.
    """

    dims: tuple[int, ...]
    dtype: type
    # registry maps dims -> {dtype: Class}

    def validate(self, obj, value):
        if value is Undefined:
            raise TraitError(f"Value '{self.name}' must be set on initialization.")

        cls = self.__class__
        arr: np.ndarray | None = None
        try:
            arr = np.asarray(value, dtype=cls.dtype)
            # numpy will keep a view where possible.
            arr = np.reshape(arr, cls.dims)
        except TypeError as e:
            raise TraitError(
                f"Unexpected typing in casting {value.__class__} to {cls.dtype}"
            ) from e
        except ValueError as e:
            assert isinstance(arr, np.ndarray), f"Unexpected failure in casting {e}"
            raise TraitError(f"Expected shape {cls.dims}, got {arr.shape}") from e
        return arr

    def set(self, obj, value):
        # validate + store
        validated = self.validate(obj, value)
        super().set(obj, validated)
        return validated

    # Note: Uniforms do not participate in connector wiring.

    @classmethod
    def __class_getitem__(cls, params: Params) -> type["Uniform"]:
        # If subclass has fixed dims, only allow dtype override if matching original
        dtype: type = float
        if hasattr(cls, "dims"):
            if not (isinstance(params, type) and params in (float, int, bool)):
                raise TypeError(
                    f"Expected dtype (float|int|bool) for {cls.__name__}[...], got {params!r}"
                )
            # Map bool to int
            dtype = int if params is bool else params
            # Prevent changing scalar dtype if it's already specified to be an
            # int.
            if cls.dtype is int:
                raise TypeError(f"Cannot change dtype of {cls.__name__}")
            dims = cls.dims
        else:
            dims, dtype = _parse_params(params)
            # Map bool to int
        dtype = int if dtype is bool else dtype
        # Lookup registered class
        type_map = _registry.get(dims)
        if not type_map or dtype not in type_map:
            raise TypeError(
                f"No uniform type registered for dimensions {dims} and dtype {dtype.__name__}"
            )
        return type_map[dtype]

    @classmethod
    def gl_func(cls) -> str:
        if issubclass(cls, Scalar):
            return "float" if cls.dtype is float else "int"
        suffix = "" if cls.dtype is float else "i"
        # GLSL has no vec1/ivec1; map 1D vectors to scalar
        if len(cls.dims) == 1:
            return f"{suffix}vec{cls.dims[0]}"
        r, c = cls.dims
        if r == c:
            return f"{suffix}mat{r}"  # f"uniformMatrix{r}{suffix}v"
        return f"{suffix}mat{r}x{c}"  # f"uniformMatrix{r}x{c}{suffix}v"


# Decorator to register a Uniform subclass for given dims and dtype (float or int)
def register(
    *, dims: tuple[int, ...], dtype: type = float
) -> Callable[[type[Uniform]], type[Uniform]]:
    if dtype not in (float, int):
        raise TypeError("register only supports float or int dtypes; bool maps to int")

    def decorator(cls: type[Uniform]) -> type[Uniform]:
        cls.dims = dims
        cls.dtype = dtype
        _registry.setdefault(dims, {})[dtype] = cls
        return cls

    return decorator


class Blob(Uniform):
    @classmethod
    def __class_getitem__(cls, uniform: type[Uniform]) -> type["Uniform"]:
        return type(
            f"Blob[{uniform.__name__}]",
            (Blob,),
            {"dims": (-1,) + uniform.dims, "dtype": Uniform.dtype},
        )


class Array(Uniform):
    """
    Fixed-size uniform arrays for scalars, vectors, or matrices.
    Usage: Array[uniform.Vec3, 10]() or Array[uniform.Mat3, 4]()
    """

    @classmethod
    def __class_getitem__(cls, params: tuple[type["Uniform"], int]) -> type["Uniform"]:
        try:
            element, length = params  # type: ignore[misc]
        except Exception as e:
            raise TypeError("Array[...] expects (UniformSubclass, length)") from e
        if not isinstance(length, int) or length <= 0:
            raise TypeError("Array length must be a positive integer")
        if not (isinstance(element, type) and issubclass(element, Uniform)):
            raise TypeError("First parameter to Array[...] must be a Uniform subclass")

        dims = (length,) + element.dims
        dtype = element.dtype

        # Build a concrete subclass capturing element + length
        return type(
            f"Array[{element.__name__},{length}]",
            (Array,),
            {
                "dims": dims,
                "dtype": dtype,
                "_element": element,
                "_length": length,
                "gl_func": classmethod(lambda cls: f"{element.gl_func()}[{length}]"),
            },
        )


# Fairly easy to just enumerate all of them and have a test
# to double check.
# as this plays more nicely with LSPs.


# Namespaces
class Vec(Uniform): ...


class Mat(Uniform): ...


class Scalar(Uniform): ...


# Scalar uniforms
@register(dims=(1,), dtype=float)
class Float(Scalar): ...


@register(dims=(1,), dtype=int)
class Int(Scalar): ...


# Vector uniforms (bool maps to Int)
@register(dims=(1,), dtype=float)
class Vec1(Vec): ...


@register(dims=(1,), dtype=int)
class Vec1Int(Vec): ...


@register(dims=(2,), dtype=float)
class Vec2(Vec): ...


@register(dims=(2,), dtype=int)
class Vec2Int(Vec): ...


@register(dims=(3,), dtype=float)
class Vec3(Vec): ...


@register(dims=(3,), dtype=int)
class Vec3Int(Vec): ...


@register(dims=(4,), dtype=float)
class Vec4(Vec): ...


@register(dims=(4,), dtype=int)
class Vec4Int(Vec): ...


# Matrix uniforms (explicit enumeration)
@register(dims=(2, 2), dtype=float)
class Mat2x2(Mat): ...


@register(dims=(2, 2), dtype=int)
class Mat2x2Int(Mat): ...


@register(dims=(2, 3), dtype=float)
class Mat2x3(Mat): ...


@register(dims=(2, 3), dtype=int)
class Mat2x3Int(Mat): ...


@register(dims=(2, 4), dtype=float)
class Mat2x4(Mat): ...


@register(dims=(2, 4), dtype=int)
class Mat2x4Int(Mat): ...


@register(dims=(3, 2), dtype=float)
class Mat3x2(Mat): ...


@register(dims=(3, 2), dtype=int)
class Mat3x2Int(Mat): ...


@register(dims=(3, 3), dtype=float)
class Mat3x3(Mat): ...


@register(dims=(3, 3), dtype=int)
class Mat3x3Int(Mat): ...


@register(dims=(3, 4), dtype=float)
class Mat3x4(Mat): ...


@register(dims=(3, 4), dtype=int)
class Mat3x4Int(Mat): ...


@register(dims=(4, 2), dtype=float)
class Mat4x2(Mat): ...


@register(dims=(4, 2), dtype=int)
class Mat4x2Int(Mat): ...


@register(dims=(4, 3), dtype=float)
class Mat4x3(Mat): ...


@register(dims=(4, 3), dtype=int)
class Mat4x3Int(Mat): ...


@register(dims=(4, 4), dtype=float)
class Mat4x4(Mat): ...


@register(dims=(4, 4), dtype=int)
class Mat4x4Int(Mat): ...


# Aliases for common types
Bool = Int

# Aliases for square matrices (float)
Mat2 = Mat2x2
Mat3 = Mat3x3
Mat4 = Mat4x4
Mat2Int = Mat2x2Int
Mat3Int = Mat3x3Int
Mat4Int = Mat4x4Int


# Texture uniforms for sampler2D
class Texture2D(TraitType):
    """
    Texture uniform for 2D image data.
    Expects numpy array with shape (H, W, C) where C is 3 (RGB) or 4 (RGBA).
    Data should be uint8 (0-255) or float (0.0-1.0).
    """

    def validate(self, obj, value):
        if value is Undefined:
            raise TraitError(f"Texture '{self.name}' must be set on initialization.")

        try:
            arr = np.asarray(value)
        except Exception as e:
            raise TraitError(f"Could not convert value to numpy array: {e}") from e

        # Validate shape (H, W, C) where C is 3 or 4
        if arr.ndim != 3:
            raise TraitError(
                f"Texture must be 3D array with shape (H, W, C), got shape {arr.shape}"
            )

        height, width, channels = arr.shape
        if channels not in (3, 4):
            raise TraitError(f"Texture must have 3 (RGB) or 4 (RGBA) channels, got {channels}")

        # Validate dtype and normalize to 0-255 uint8
        if arr.dtype in (np.float32, np.float64):
            # Float data should be in range [0, 1], convert to uint8
            arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
        elif arr.dtype == np.uint8:
            # Already in correct format
            pass
        else:
            raise TraitError(f"Texture dtype must be float or uint8, got {arr.dtype}")

        # Ensure C-contiguous for efficient transfer to JavaScript
        if not arr.flags["C_CONTIGUOUS"]:
            arr = np.ascontiguousarray(arr)

        return arr

    def set(self, obj, value):
        validated = self.validate(obj, value)
        super().set(obj, validated)
        return validated

    @classmethod
    def gl_func(cls) -> str:
        return "sampler2D"

    # Texture2D uniforms are Python-provided inputs only (sync=True). Outputs
    # are exposed via the ImageGLSL.frag handle.
