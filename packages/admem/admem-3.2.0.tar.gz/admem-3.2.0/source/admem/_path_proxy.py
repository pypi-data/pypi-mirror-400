# Copyright (c) 2022-2026 Mario S. Könz; License: MIT
import io
import os
import typing as tp  # pylint: disable=reimported
from pathlib import Path
from pathlib import PosixPath
from pathlib import WindowsPath

from django.core.files.storage import storages

# import tempfile

# 2023-Q1: sphinx has a bug regarding adjusting the signature for attributes,
# hence I need fully qualified imports for typing and django.db

__all__ = ["DjangoPath"]


class _NonClosingBinIOWrapper(io.TextIOWrapper):
    """Proxy for binary handles that suppresses close while delegating ops."""

    def __init__(self, raw: tp.IO[tp.Any]):
        self._raw = raw

    def __getattr__(self, name: str) -> tp.Any:  # pragma: no cover - delegation
        return getattr(self._raw, name)

    def __iter__(self):  # type: ignore
        return iter(self._raw)

    @property
    def closed(self) -> bool:
        return getattr(self._raw, "closed", False)

    def close(self) -> None:
        return None

    def __enter__(self) -> "_NonClosingBinIOWrapper":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore
        return None


class _NonClosingTextIOWrapper(io.TextIOWrapper):

    def close(self) -> None:
        # we are not calling super().close() intentionally here
        if self.closed is True:
            return
        try:
            self.flush()
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        io.TextIOBase.close(self)


class DjangoPath(Path):
    if os.name == "nt":
        _flavour = WindowsPath._flavour  # type: ignore[attr-defined] # pylint: disable=protected-access
    else:

        _flavour = PosixPath._flavour  # type: ignore[attr-defined] # pylint: disable=protected-access
    __slots__ = ("_prefix", "_in_mem_file")

    def __new__(  # pylint: disable=arguments-differ
        cls, *args: str, prefix: str | None = None
    ) -> "DjangoPath":
        # pylint: disable=no-member,self-cls-assignment
        cls = DjangoPosixPath
        if os.name == "nt":
            cls = DjangoWindowsPath
        res = super().__new__(cls, *args)
        res._prefix = prefix  # type: ignore
        return res

    def name_wo_prefix(self) -> str:
        name = self.as_posix()
        # pylint: disable=no-member

        if self._prefix:  # type: ignore
            name = name.split(self._prefix + "/", 1)[1]  # type: ignore
        return name

    def __copy__(self) -> "DjangoPath":
        # pylint: disable=no-member
        return self.__class__(self, prefix=self._prefix)  # type: ignore

    def __deepcopy__(self, memo: dict[str, tp.Any]) -> "DjangoPath":
        # pylint: disable=no-member
        return self.__class__(self, prefix=self._prefix)  # type: ignore

    def open(  # type: ignore # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> tp.IO[tp.Any]:
        # assert encoding is None
        assert errors is None
        assert newline is None
        assert buffering == -1
        try:
            # try:
            media_storage = storages["default"]
            return media_storage.open(self.as_posix(), mode=mode)
        except FileNotFoundError as err:
            if not hasattr(self, "_in_mem_file"):
                raise err
            if "a" in mode:
                raise NotImplementedError(
                    "append currently not supported in transient files"
                ) from err
            if "w" in mode:
                # f = tempfile.SpooledTemporaryFile(mode="wb", max_size=5_000_000)
                f = io.BytesIO()
                self._in_mem_file.file = f  # pylint: disable=no-member
            elif "r" in mode:
                f = self._in_mem_file.file  # pylint: disable=no-member
                f.seek(0)

            if "b" in mode:
                return _NonClosingBinIOWrapper(f)

            return _NonClosingTextIOWrapper(
                f,
                encoding=encoding,
                errors=errors,
                newline=newline,
            )

    def iterdir(self) -> tp.Generator["DjangoPath", None, None]:
        media_storage = storages["default"]
        dirs, files = media_storage.listdir(self.as_posix())
        for path in dirs + files:
            yield self / path

    def is_dir(self) -> bool:
        try:
            with self.open():
                return False
        except IsADirectoryError:
            return True


class DjangoPosixPath(PosixPath, DjangoPath):  # pylint: disable=abstract-method
    pass


class DjangoWindowsPath(WindowsPath, DjangoPath):  # pylint: disable=abstract-method
    pass
