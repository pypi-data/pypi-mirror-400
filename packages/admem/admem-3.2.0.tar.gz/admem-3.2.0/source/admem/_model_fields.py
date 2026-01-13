# Copyright (c) 2022-2026 Mario S. Könz; License: MIT
from __future__ import annotations

import dataclasses as dc
import typing as tp

__all__ = [
    "ModelFieldInfo",
    "iter_model_fields",
    "is_pydantic_model",
    "require_pydantic",
]


@dc.dataclass(frozen=True)
class ModelFieldInfo:
    name: str
    annotation: tp.Any
    metadata: tp.Mapping[str, tp.Any]
    default: tp.Any = dc.MISSING
    constraints: dict[str, tp.Any] = dc.field(default_factory=dict)


def is_pydantic_model(obj: tp.Any) -> bool:
    cls = obj if isinstance(obj, type) else type(obj)
    try:
        import pydantic as pyd  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError:
        return False
    return isinstance(cls, type) and issubclass(cls, pyd.BaseModel)


def iter_model_fields(model: tp.Any) -> tp.Iterator[ModelFieldInfo]:
    cls = model if isinstance(model, type) else type(model)
    if dc.is_dataclass(cls):
        yield from _iter_dataclass_fields(cls)
        return
    if is_pydantic_model(cls):
        yield from _iter_pydantic_fields(cls)
        return
    raise TypeError(f"{cls!r} must be a dataclass or a Pydantic BaseModel subclass")


def _iter_dataclass_fields(cls: type) -> tp.Iterator[ModelFieldInfo]:
    for field in dc.fields(cls):
        metadata = dict(field.metadata)
        constraints = _constraints_from_annotation(field.type)
        default = _dataclass_default(field)
        yield ModelFieldInfo(
            name=field.name,
            annotation=field.type,
            metadata=metadata,
            default=default,
            constraints=constraints,
        )


def _dataclass_default(field: dc.Field[tp.Any]) -> tp.Any:
    if field.default is not dc.MISSING:
        assert field.default_factory is dc.MISSING
        return field.default
    if field.default_factory is not dc.MISSING:
        assert field.default is dc.MISSING
        return field.default_factory
    return dc.MISSING


def _iter_pydantic_fields(cls: type) -> tp.Iterator[ModelFieldInfo]:
    pyd = require_pydantic("to translate BaseModel subclasses")
    assert issubclass(cls, pyd.BaseModel)
    for name, info in cls.model_fields.items():  # type: ignore
        extras = info.json_schema_extra
        if callable(extras):
            extras = {}
        default = _pydantic_default(info)
        constraints: dict[str, tp.Any] = {}
        _extend_constraints_from_iterable(constraints, info.metadata)
        yield ModelFieldInfo(
            name=name,
            annotation=info.annotation,
            metadata=extras or {},
            default=default,
            constraints=constraints,
        )


def _pydantic_default(field_info: tp.Any) -> tp.Any:
    default_factory = getattr(field_info, "default_factory", None)
    if default_factory is not None:
        return default_factory
    if field_info.is_required():
        return dc.MISSING
    return field_info.default


def require_pydantic(action: str) -> tp.Any:
    try:
        import pydantic as pyd  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as exc:  # pragma: no cover - guarded by callers
        raise RuntimeError(f"pydantic is required {action}") from exc
    return pyd


def _constraints_from_annotation(annotation: tp.Any) -> dict[str, tp.Any]:
    constraints: dict[str, tp.Any] = {}
    origin = tp.get_origin(annotation)
    if origin is tp.Annotated:
        args = tp.get_args(annotation)
        for extra in args[1:]:
            if hasattr(extra, "metadata"):
                _extend_constraints_from_iterable(constraints, extra.metadata)
            else:
                _extend_constraints_from_iterable(constraints, (extra,))
    return constraints


def _extend_constraints_from_iterable(
    constraints: dict[str, tp.Any], iterable: tp.Iterable[tp.Any]
) -> None:
    for meta in iterable:
        for attr in (
            "ge",
            "gt",
            "le",
            "lt",
            "min_length",
            "max_length",
            "pattern",
            "multiple_of",
        ):
            if hasattr(meta, attr):
                value = getattr(meta, attr)
                if value is not None:
                    constraints[attr] = value
