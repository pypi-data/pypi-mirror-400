# Copyright (c) 2022-2026 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp

__all__ = ["InspectDataclass", "MetaInfo"]


class MetaInfo(tp.NamedTuple):
    primary_key: str | None = None
    unique_together: list[str] | None = None
    extra: dict[str, dict[str, tp.Any]] | None = None
    ordering: list[str] | None = None
    app_label: str | None = None
    db_table: str | None = None
    validate_on_save: bool = False
    validate_on_clean: bool = True
    polymorphic: bool = False
    mirror_inheritance: bool = True


@dc.dataclass(frozen=True)
class InspectDataclass:
    dataclass: type

    # these fields can only be gathered on this.Meta, not
    # any parent.Meta
    fields_on_this: tp.ClassVar[list[str]] = [
        "primary_key",
        "unique_together",
        "extra",
        "ordering",
        "polymorphic",
    ]
    # used at runtime, do not ingest, but also dont raise
    runtime_keys: tp.ClassVar[list[str]] = ["weak_ref"]

    def extract_meta(self) -> MetaInfo:
        valid_types = tp.get_type_hints(MetaInfo)

        kwgs = {}

        if hasattr(self.dataclass, "Meta"):
            kwgs = {
                k: v
                for k, v in getattr(self.dataclass, "Meta").__dict__.items()
                if not (k.startswith("_") or k in self.runtime_keys)
            }

        for name, val in kwgs.items():  # poor mans pydantic validation
            if name not in valid_types:
                raise AttributeError(
                    f"{name} is not a valid field for Meta, use {list(valid_types)}"
                )
            # type check, first strip optional and then...
            type_ = valid_types[name]
            if tp.get_args(type_):
                type_ = tp.get_args(type_)[0]
            type_ = tp.get_origin(type_) or type_  # ...remove parametrized generic
            if not isinstance(val, type_):
                raise RuntimeError(f"{name} must be a {type_}, please fix!")

        return MetaInfo(**kwgs)

    def adjust_meta(self, base_dc: type, meta: MetaInfo) -> MetaInfo:
        # remove fields that came from the base_dc
        kwgs = {k: getattr(meta, k) for k in tp.get_type_hints(MetaInfo)}

        if hasattr(base_dc, "Meta"):
            if base_dc.Meta == self.dataclass.Meta:  # type: ignore
                for k in self.fields_on_this:
                    kwgs.pop(k)

        return MetaInfo(**kwgs)

    def get_identifying_parameter(self) -> set[str]:
        meta = self.extract_meta()
        primary_key = meta.primary_key
        unique_together = meta.unique_together
        res = set()
        if primary_key is not None:
            res.add(primary_key)
        if unique_together is not None:
            res.update(unique_together)
        return res
