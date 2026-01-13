from functools import update_wrapper
from typing import Any, Type, TypeVar, cast

import attr

_JSON_IGNORE = "__pe_json_ignore"


T = TypeVar("T")


def hex_repr(cls: Type[T]) -> Type[T]:
    """
    Prints ints in both hex and dec in __repr__
    :param cls:
    :return:
    """
    if not hasattr(cls, "__attrs_attrs__"):
        raise TypeError(f"Class {cls} needs to be annotated with @attr.s")

    def _repr(self: Any) -> str:
        parts = []
        for field in cls.__attrs_attrs__:  # type: ignore
            if not field.repr:
                continue
            field_name = field.name
            field_value = getattr(self, field.name)

            # Python 3.12 is stricter about hex formatting; coerce to int before using :x
            if isinstance(field.repr, int) and field_value is not None:
                try:
                    field_value_int = int(field_value)
                except (TypeError, ValueError):
                    field_value_int = None
                else:
                    field_value = f"{field_value_int} | 0x{field_value_int:x}"

            # Note: This doesn't handle tuples and lists.  We could add this if necessary.

            parts.append(f"{field_name}={field_value}")
        return f"{self.__class__.__name__}({', '.join(parts)})"

    cls.__repr__ = update_wrapper(_repr, cls.__repr__)  # type: ignore
    return cls


def is_json_ignored(at: attr.Attribute) -> bool:
    return cast(bool, at.metadata.get(_JSON_IGNORE, False))


def json_ignore_ib(**kwargs: Any) -> Any:
    metadata = kwargs.setdefault("metadata", {})
    metadata[_JSON_IGNORE] = True
    return attr.ib(**kwargs)
