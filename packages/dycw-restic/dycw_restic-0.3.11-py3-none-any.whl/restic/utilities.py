from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, assert_never, override

from typed_settings import Secret
from utilities.os import temp_environ
from utilities.tempfile import TemporaryFile
from utilities.text import repr_str

from restic.settings import SETTINGS

if TYPE_CHECKING:
    from collections.abc import Iterator

    from utilities.types import PathLike

    from restic.types import PasswordLike


def expand_bool(flag: str, /, *, bool_: bool = False) -> list[str]:
    return [f"--{flag}"] if bool_ else []


def expand_dry_run(*, dry_run: bool = False) -> list[str]:
    return expand_bool("dry-run", bool_=dry_run)


def expand_exclude(*, exclude: list[str] | None = None) -> list[str]:
    return _expand_list("exclude", arg=exclude)


def expand_exclude_i(*, exclude_i: list[str] | None = None) -> list[str]:
    return _expand_list("iexclude", arg=exclude_i)


def expand_group_by(*, group_by: list[str] | None = None) -> list[str]:
    return [] if group_by is None else ["--group-by", ",".join(group_by)]


def expand_include(*, include: list[str] | None = None) -> list[str]:
    return _expand_list("include", arg=include)


def expand_include_i(*, include_i: list[str] | None = None) -> list[str]:
    return _expand_list("iinclude", arg=include_i)


def expand_keep(freq: str, /, *, n: int | None = None) -> list[str]:
    return [] if n is None else [f"--keep-{freq}", str(n)]


def expand_keep_within(freq: str, /, *, duration: str | None = None) -> list[str]:
    return [] if duration is None else [f"--keep-{freq}", duration]


def expand_read_concurrency(n: int, /) -> list[str]:
    return ["--read-concurrency", str(n)]


def expand_tag(*, tag: list[str] | None = None) -> list[str]:
    return _expand_list("tag", arg=tag)


def expand_target(target: PathLike, /) -> list[str]:
    return ["--target", str(target)]


##


@contextmanager
def yield_password(
    *, password: PasswordLike = SETTINGS.password, env_var: str = "RESTIC_PASSWORD_FILE"
) -> Iterator[None]:
    match password:
        case Secret():
            value = password.get_secret_value()
        case Path() | str() as value:
            ...
        case never:
            assert_never(never)
    match value:
        case Path():
            if value.is_file():
                with temp_environ({env_var: str(value)}):
                    yield
            else:
                raise YieldPasswordError(path=value)
        case str():
            if Path(value).is_file():
                with temp_environ({env_var: value}):
                    yield
            else:
                with TemporaryFile() as temp, temp_environ({env_var: str(temp)}):
                    _ = temp.write_text(value)
                    yield
        case never:
            assert_never(never)


@dataclass(order=True, unsafe_hash=True, kw_only=True, slots=True)
class YieldPasswordError(Exception):
    path: Path

    @override
    def __str__(self) -> str:
        return f"Password file not found: {repr_str(self.path)}"


##


def _expand_list(flag: str, /, *, arg: list[str] | None = None) -> list[str]:
    return (
        [] if arg is None else list(chain.from_iterable([f"--{flag}", a] for a in arg))
    )


__all__ = [
    "YieldPasswordError",
    "expand_bool",
    "expand_dry_run",
    "expand_exclude",
    "expand_exclude_i",
    "expand_group_by",
    "expand_include",
    "expand_include_i",
    "expand_keep",
    "expand_keep_within",
    "expand_read_concurrency",
    "expand_tag",
    "expand_target",
    "yield_password",
]
