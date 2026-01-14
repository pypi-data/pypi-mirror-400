from __future__ import annotations

import time
from re import MULTILINE, search
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Literal, overload

from pydantic import TypeAdapter
from utilities.iterables import one
from utilities.subprocess import cp, run
from utilities.tempfile import TemporaryDirectory
from whenever import TimeDelta

from restic.logging import LOGGER
from restic.models import Snapshot
from restic.repo import yield_repo_env
from restic.settings import SETTINGS
from restic.utilities import (
    expand_bool,
    expand_dry_run,
    expand_exclude,
    expand_exclude_i,
    expand_group_by,
    expand_include,
    expand_include_i,
    expand_keep,
    expand_keep_within,
    expand_read_concurrency,
    expand_tag,
    expand_target,
    yield_password,
)

if TYPE_CHECKING:
    from utilities.types import PathLike

    from restic.repo import Repo
    from restic.types import PasswordLike


def backup(
    path: PathLike,
    repo: Repo,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    dry_run: bool = SETTINGS.dry_run,
    exclude: list[str] | None = SETTINGS.exclude_backup,
    exclude_i: list[str] | None = SETTINGS.exclude_i_backup,
    read_concurrency: int = SETTINGS.read_concurrency,
    tag_backup: list[str] | None = SETTINGS.tag_backup,
    run_forget: bool = SETTINGS.run_forget,
    keep_last: int | None = SETTINGS.keep_last,
    keep_hourly: int | None = SETTINGS.keep_hourly,
    keep_daily: int | None = SETTINGS.keep_daily,
    keep_weekly: int | None = SETTINGS.keep_weekly,
    keep_monthly: int | None = SETTINGS.keep_monthly,
    keep_yearly: int | None = SETTINGS.keep_yearly,
    keep_within: str | None = SETTINGS.keep_within,
    keep_within_hourly: str | None = SETTINGS.keep_within_hourly,
    keep_within_daily: str | None = SETTINGS.keep_within_daily,
    keep_within_weekly: str | None = SETTINGS.keep_within_weekly,
    keep_within_monthly: str | None = SETTINGS.keep_within_monthly,
    keep_within_yearly: str | None = SETTINGS.keep_within_yearly,
    group_by: list[str] | None = SETTINGS.group_by,
    prune: bool = SETTINGS.prune,
    repack_cacheable_only: bool = SETTINGS.repack_cacheable_only,
    repack_small: bool = SETTINGS.repack_small,
    repack_uncompressed: bool = SETTINGS.repack_uncompressed,
    tag_forget: list[str] | None = SETTINGS.tag_forget,
    sleep: int | None = SETTINGS.sleep,
) -> None:
    LOGGER.info("Backing up '%s' to '%s'...", path, repo)
    try:
        _backup_core(
            path,
            repo,
            password=password,
            dry_run=dry_run,
            exclude=exclude,
            exclude_i=exclude_i,
            read_concurrency=read_concurrency,
            tag=tag_backup,
        )
    except CalledProcessError as error:
        if search(
            "Is there a repository at the following location?",
            error.stderr,
            flags=MULTILINE,
        ):
            LOGGER.info("Auto-initializing repo...")
            init(repo, password=password)
            _backup_core(
                path,
                repo,
                password=password,
                dry_run=dry_run,
                exclude=exclude,
                exclude_i=exclude_i,
                read_concurrency=read_concurrency,
                tag=tag_backup,
            )
        else:
            raise
    if run_forget and (
        (keep_last is not None)
        or (keep_hourly is not None)
        or (keep_daily is not None)
        or (keep_weekly is not None)
        or (keep_monthly is not None)
        or (keep_yearly is not None)
        or (keep_within is not None)
        or (keep_within_hourly is not None)
        or (keep_within_daily is not None)
        or (keep_within_weekly is not None)
        or (keep_within_monthly is not None)
        or (keep_within_yearly is not None)
    ):
        forget(
            repo,
            password=password,
            keep_last=keep_last,
            keep_hourly=keep_hourly,
            keep_daily=keep_daily,
            keep_weekly=keep_weekly,
            keep_monthly=keep_monthly,
            keep_yearly=keep_yearly,
            keep_within=keep_within,
            keep_within_hourly=keep_within_hourly,
            keep_within_daily=keep_within_daily,
            keep_within_weekly=keep_within_weekly,
            keep_within_monthly=keep_within_monthly,
            keep_within_yearly=keep_within_yearly,
            group_by=group_by,
            prune=prune,
            repack_cacheable_only=repack_cacheable_only,
            repack_small=repack_small,
            repack_uncompressed=repack_uncompressed,
            tag=tag_forget,
        )
    if sleep is None:
        LOGGER.info("Finished backing up '%s' to '%s'", path, repo)
    else:
        delta = TimeDelta(seconds=sleep)
        LOGGER.info(
            "Finished backing up '%s' to '%s'; sleeping for %s...", path, repo, delta
        )
        time.sleep(sleep)
        LOGGER.info("Finishing sleeping for %s", delta)


def _backup_core(
    path: PathLike,
    repo: Repo,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    dry_run: bool = SETTINGS.dry_run,
    exclude: list[str] | None = SETTINGS.exclude_backup,
    exclude_i: list[str] | None = SETTINGS.exclude_i_backup,
    read_concurrency: int = SETTINGS.read_concurrency,
    tag: list[str] | None = SETTINGS.tag_backup,
) -> None:
    with yield_repo_env(repo), yield_password(password=password):
        run(
            "restic",
            "backup",
            *expand_dry_run(dry_run=dry_run),
            *expand_exclude(exclude=exclude),
            *expand_exclude_i(exclude_i=exclude_i),
            *expand_read_concurrency(read_concurrency),
            *expand_tag(tag=tag),
            str(path),
            print=True,
        )


def copy(
    src: Repo,
    dest: Repo,
    /,
    *,
    src_password: PasswordLike = SETTINGS.password,
    dest_password: PasswordLike = SETTINGS.password,
    tag: list[str] | None = SETTINGS.tag_copy,
    sleep: int | None = SETTINGS.sleep,
) -> None:
    LOGGER.info("Copying snapshots from '%s' to '%s'...", src, dest)
    with (
        yield_repo_env(src, env_var="RESTIC_FROM_REPOSITORY"),
        yield_repo_env(dest),
        yield_password(password=src_password, env_var="RESTIC_FROM_PASSWORD_FILE"),
        yield_password(password=dest_password),
    ):
        run("restic", "copy", *expand_tag(tag=tag), print=True)
    if sleep is None:
        LOGGER.info("Finished copying snapshots from '%s' to '%s'", src, dest)
    else:
        delta = TimeDelta(seconds=sleep)
        LOGGER.info(
            "Finished copying snapshots from '%s' to '%s'; sleeping for %s...", delta
        )
        time.sleep(sleep)
        LOGGER.info("Finishing sleeping for %s", delta)


def forget(
    repo: Repo,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    dry_run: bool = SETTINGS.dry_run,
    keep_last: int | None = SETTINGS.keep_last,
    keep_hourly: int | None = SETTINGS.keep_hourly,
    keep_daily: int | None = SETTINGS.keep_daily,
    keep_weekly: int | None = SETTINGS.keep_weekly,
    keep_monthly: int | None = SETTINGS.keep_monthly,
    keep_yearly: int | None = SETTINGS.keep_yearly,
    keep_within: str | None = SETTINGS.keep_within,
    keep_within_hourly: str | None = SETTINGS.keep_within_hourly,
    keep_within_daily: str | None = SETTINGS.keep_within_daily,
    keep_within_weekly: str | None = SETTINGS.keep_within_weekly,
    keep_within_monthly: str | None = SETTINGS.keep_within_monthly,
    keep_within_yearly: str | None = SETTINGS.keep_within_yearly,
    group_by: list[str] | None = SETTINGS.group_by,
    prune: bool = SETTINGS.prune,
    repack_cacheable_only: bool = SETTINGS.repack_cacheable_only,
    repack_small: bool = SETTINGS.repack_small,
    repack_uncompressed: bool = SETTINGS.repack_uncompressed,
    tag: list[str] | None = SETTINGS.tag_forget,
) -> None:
    LOGGER.info("Forgetting snapshots in '%s'...", repo)
    with yield_repo_env(repo), yield_password(password=password):
        run(
            "restic",
            "forget",
            *expand_dry_run(dry_run=dry_run),
            *expand_keep("last", n=keep_last),
            *expand_keep("hourly", n=keep_hourly),
            *expand_keep("daily", n=keep_daily),
            *expand_keep("weekly", n=keep_weekly),
            *expand_keep("monthly", n=keep_monthly),
            *expand_keep("yearly", n=keep_yearly),
            *expand_keep_within("within", duration=keep_within),
            *expand_keep_within("within-hourly", duration=keep_within_hourly),
            *expand_keep_within("within-daily", duration=keep_within_daily),
            *expand_keep_within("within-weekly", duration=keep_within_weekly),
            *expand_keep_within("within-monthly", duration=keep_within_monthly),
            *expand_keep_within("within-yearly", duration=keep_within_yearly),
            *expand_group_by(group_by=group_by),
            *expand_bool("prune", bool_=prune),
            *expand_bool("repack-cacheable-only", bool_=repack_cacheable_only),
            *expand_bool("repack-small", bool_=repack_small),
            *expand_bool("repack-uncompressed", bool_=repack_uncompressed),
            *expand_tag(tag=tag),
            print=True,
        )
    LOGGER.info("Finished forgetting snapshots in '%s'", repo)


def init(repo: Repo, /, *, password: PasswordLike = SETTINGS.password) -> None:
    LOGGER.info("Initializing '%s'", repo)
    with yield_repo_env(repo), yield_password(password=password):
        run("restic", "init", print=True)
    LOGGER.info("Finished initializing '%s'", repo)


def unlock(
    repo: Repo,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    remove_all: bool = SETTINGS.remove_all,
) -> None:
    LOGGER.info("Unlocking '%s'", repo)
    with yield_repo_env(repo), yield_password(password=password):
        run(
            "restic", "unlock", *expand_bool("remove-all", bool_=remove_all), print=True
        )
    LOGGER.info("Finished unlocking '%s'", repo)


def restore(
    repo: Repo,
    target: PathLike,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    delete: bool = SETTINGS.delete,
    dry_run: bool = SETTINGS.dry_run,
    exclude: list[str] | None = SETTINGS.exclude_restore,
    exclude_i: list[str] | None = SETTINGS.exclude_i_restore,
    include: list[str] | None = SETTINGS.include_restore,
    include_i: list[str] | None = SETTINGS.include_i_restore,
    tag: list[str] | None = SETTINGS.tag_restore,
    snapshot: str = SETTINGS.snapshot,
) -> None:
    LOGGER.info("Restoring snapshot '%s' of '%s' to '%s'...", snapshot, repo, target)
    with (
        yield_repo_env(repo),
        yield_password(password=password),
        TemporaryDirectory() as temp,
    ):
        run(
            "restic",
            "restore",
            *expand_bool("delete", bool_=delete),
            *expand_dry_run(dry_run=dry_run),
            *expand_exclude(exclude=exclude),
            *expand_exclude_i(exclude_i=exclude_i),
            *expand_include(include=include),
            *expand_include_i(include_i=include_i),
            *expand_tag(tag=tag),
            *expand_target(temp),
            "--verify",
            snapshot,
            print=True,
        )
        snaps = snapshots(repo, password=password, return_=True)
        path = one(snaps[-1].paths)
        src = temp / path.relative_to(path.anchor)
        cp(src, target)
    LOGGER.info(
        "Finished restoring snapshot '%s' of '%s' to '%s'", snapshot, repo, target
    )


@overload
def snapshots(
    repo: Repo,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    return_: Literal[True],
    print: bool = False,
) -> list[Snapshot]: ...
@overload
def snapshots(
    repo: Repo,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    return_: Literal[False] = False,
    print: bool = False,
) -> None: ...
@overload
def snapshots(
    repo: Repo,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    return_: bool = False,
    print: bool = False,
) -> list[Snapshot] | None: ...
def snapshots(
    repo: Repo,
    /,
    *,
    password: PasswordLike = SETTINGS.password,
    return_: bool = False,
    print: bool = False,  # noqa: A002
) -> list[Snapshot] | None:
    LOGGER.info("Listing snapshots in '%s'...", repo)
    args: list[str] = ["restic", "snapshots"]
    if return_:
        args.append("--json")
    with yield_repo_env(repo), yield_password(password=password):
        result = run(*args, print=print, return_=return_)
    LOGGER.info("Finished listing snapshots in '%s'", repo)
    return None if result is None else TypeAdapter(list[Snapshot]).validate_json(result)


__all__ = ["backup", "copy", "forget", "init", "restore", "snapshots", "unlock"]
