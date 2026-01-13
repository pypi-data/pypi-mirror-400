from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorRef:
    """
    Typed reference to an output defined on a class.

    Produced by accessing a class-level Output descriptor, e.g. `Provider.frag`.
    """

    owner: type
    attr: str
    glsl_type: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"ConnectorRef(owner={self.owner.__name__}, attr={self.attr}, type={self.glsl_type})"


class Output:
    """
    Class-level descriptor representing a typed output handle produced by a pass.

    Accessing `Owner.attr` returns a `ConnectorRef(owner=Owner, attr, type)`.
    """

    def __init__(self, glsl_type: str = "sampler2D") -> None:
        self._glsl_type = glsl_type
        self._attr_name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr_name = name

    def __get__(self, instance, owner: type) -> ConnectorRef:
        # When accessed on the class, return a typed connector for wiring.
        # Find the defining class in MRO (skip dynamic subclasses created by anywidget)
        defining_class = owner
        for cls in owner.__mro__:
            if cls is not owner and "_glsl" in vars(cls):
                defining_class = cls
                break

        attr = self._attr_name or "frag"
        return ConnectorRef(owner=defining_class, attr=attr, glsl_type=self._glsl_type)
