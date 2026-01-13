from typing import Any, Type


def setattrs(
    obj: Any,
    exclude_none: bool = False,
    exclude_type: Type[Any] | None = None,
    **kwargs
) -> None:
    for key, value in kwargs.items():
        if (exclude_none and value is None) or (
            exclude_type is not None and isinstance(value, exclude_type)
        ):
            continue
        setattr(obj, key, value)
