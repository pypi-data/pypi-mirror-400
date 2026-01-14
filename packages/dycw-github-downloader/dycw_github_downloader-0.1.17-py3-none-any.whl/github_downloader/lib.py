from __future__ import annotations

import tarfile
from contextlib import contextmanager
from pathlib import Path
from re import IGNORECASE, search
from typing import TYPE_CHECKING, Any

from github import Github
from github.Auth import Token
from requests import get
from typed_settings import Secret
from utilities.inflect import counted_noun
from utilities.iterables import OneNonUniqueError, one
from utilities.subprocess import cp
from utilities.tempfile import TemporaryDirectory
from utilities.text import repr_str, strip_and_dedent

from github_downloader import __version__
from github_downloader.constants import MACHINE_TYPE_GROUP, SYSTEM_NAME
from github_downloader.logging import LOGGER
from github_downloader.settings import (
    DOWNLOAD_SETTINGS,
    MATCH_SETTINGS,
    PATH_BINARIES_SETTINGS,
    PERMS_SETTINGS,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from typed_settings import Secret
    from utilities.permissions import PermissionsLike
    from utilities.types import PathLike


@contextmanager
def yield_asset(
    owner: str,
    repo: str,
    /,
    *,
    token: Secret[str] | None = DOWNLOAD_SETTINGS.token,
    match_system: bool = MATCH_SETTINGS.match_system,
    match_machine: bool = MATCH_SETTINGS.match_machine,
    not_endswith: list[str] | None = MATCH_SETTINGS.not_endswith,
    timeout: int = DOWNLOAD_SETTINGS.timeout,
    chunk_size: int = DOWNLOAD_SETTINGS.chunk_size,
) -> Iterator[Path]:
    """Yield a GitHub asset."""
    gh = Github(auth=None if token is None else Token(token.get_secret_value()))
    repository = gh.get_repo(f"{owner}/{repo}")
    release = repository.get_latest_release()
    assets = list(release.get_assets())
    LOGGER.info("Got %s: %s", counted_noun(assets, "asset"), [a.name for a in assets])
    if match_system:
        assets = [a for a in assets if search(SYSTEM_NAME, a.name, flags=IGNORECASE)]
        LOGGER.info(
            "Post system name %r, got %s: %s",
            SYSTEM_NAME,
            counted_noun(assets, "asset"),
            [a.name for a in assets],
        )
    if match_machine:
        assets = [
            a
            for a in assets
            if any(search(mt, a.name, flags=IGNORECASE) for mt in MACHINE_TYPE_GROUP)
        ]
        LOGGER.info(
            "Post machine type group %s, got %s: %s",
            MACHINE_TYPE_GROUP,
            counted_noun(assets, "asset"),
            [a.name for a in assets],
        )
    if not_endswith is not None:
        assets = [
            a for a in assets if all(not a.name.endswith(e) for e in not_endswith)
        ]
        LOGGER.info(
            "Post asset name endings, got %s: %s",
            counted_noun(assets, "asset"),
            [a.name for a in assets],
        )
    try:
        asset = one(assets)
    except OneNonUniqueError as error:
        raise OneNonUniqueError(
            iterables=([a.name for a in assets],),
            first=error.first.name,
            second=error.second.name,
        ) from None
    headers: dict[str, Any] = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token.get_secret_value()}"
    with TemporaryDirectory() as temp_dir:
        with get(
            asset.browser_download_url, headers=headers, timeout=timeout, stream=True
        ) as resp:
            resp.raise_for_status()
            dest = temp_dir / asset.name
            with dest.open(mode="wb") as fh:
                fh.writelines(resp.iter_content(chunk_size=chunk_size))
        LOGGER.info("Yielding %r...", str(dest))
        yield dest


##


@contextmanager
def yield_tar_asset(
    owner: str,
    repo: str,
    /,
    *,
    token: Secret[str] | None = DOWNLOAD_SETTINGS.token,
    match_system: bool = MATCH_SETTINGS.match_system,
    match_machine: bool = MATCH_SETTINGS.match_machine,
    not_endswith: list[str] | None = MATCH_SETTINGS.not_endswith,
    timeout: int = DOWNLOAD_SETTINGS.timeout,
    chunk_size: int = DOWNLOAD_SETTINGS.chunk_size,
) -> Iterator[Path]:
    with (
        yield_asset(
            owner,
            repo,
            token=token,
            match_system=match_system,
            match_machine=match_machine,
            not_endswith=not_endswith,
            timeout=timeout,
            chunk_size=chunk_size,
        ) as temp1,
        tarfile.open(temp1, "r:gz") as tar,
        TemporaryDirectory() as temp2,
    ):
        tar.extractall(temp2, filter="data")
        yield one(temp2.iterdir())


##


def setup_asset(
    asset_owner: str,
    asset_repo: str,
    path: PathLike,
    /,
    *,
    token: Secret[str] | None = DOWNLOAD_SETTINGS.token,
    match_system: bool = MATCH_SETTINGS.match_system,
    match_machine: bool = MATCH_SETTINGS.match_machine,
    not_endswith: list[str] | None = MATCH_SETTINGS.not_endswith,
    timeout: int = DOWNLOAD_SETTINGS.timeout,
    chunk_size: int = DOWNLOAD_SETTINGS.chunk_size,
    sudo: bool = PERMS_SETTINGS.sudo,
    perms: PermissionsLike | None = PERMS_SETTINGS.perms,
    owner: str | int | None = PERMS_SETTINGS.owner,
    group: str | int | None = PERMS_SETTINGS.group,
) -> None:
    """Setup a GitHub asset."""
    LOGGER.info(
        strip_and_dedent("""
            Running '%s' (version %s) with settings:
             - asset_owner   = %s
             - asset_repo    = %s
             - path          = %s
             - token         = %s
             - match_system  = %s
             - match_machine = %s
             - not_endswith  = %s
             - timeout       = %d
             - chunk_size    = %d
             - sudo          = %s
             - perms         = %s
             - owner         = %s
             - group         = %s
        """),
        setup_asset.__name__,
        __version__,
        asset_owner,
        asset_repo,
        path,
        token,
        match_system,
        match_machine,
        not_endswith,
        timeout,
        chunk_size,
        sudo,
        perms,
        owner,
        group,
    )
    with yield_asset(
        asset_owner,
        asset_repo,
        token=token,
        match_system=match_system,
        match_machine=match_machine,
        not_endswith=not_endswith,
        timeout=timeout,
        chunk_size=chunk_size,
    ) as src:
        cp(src, path, sudo=sudo, perms=perms, owner=owner, group=group)
        LOGGER.info("Downloaded to %r", str(path))


##


def setup_age(
    *,
    token: Secret[str] | None = DOWNLOAD_SETTINGS.token,
    timeout: int = DOWNLOAD_SETTINGS.timeout,
    path_binaries: PathLike = PATH_BINARIES_SETTINGS.path_binaries,
    chunk_size: int = DOWNLOAD_SETTINGS.chunk_size,
    sudo: bool = PERMS_SETTINGS.sudo,
    perms: PermissionsLike | None = PERMS_SETTINGS.perms,
    owner: str | int | None = PERMS_SETTINGS.owner,
    group: str | int | None = PERMS_SETTINGS.group,
) -> None:
    """Setup 'age'."""
    with yield_tar_asset(
        "FiloSottile",
        "age",
        token=token,
        match_system=True,
        match_machine=True,
        not_endswith=["proof"],
        timeout=timeout,
        chunk_size=chunk_size,
    ) as temp:
        downloads: list[Path] = []
        for src in temp.iterdir():
            if src.name.startswith("age"):
                dest = Path(path_binaries, src.name)
                cp(src, dest, sudo=sudo, perms=perms, owner=owner, group=group)
                downloads.append(dest)
        LOGGER.info("Downloaded to %s", ", ".join(map(repr_str, downloads)))


##


def setup_ripgrep(
    *,
    token: Secret[str] | None = DOWNLOAD_SETTINGS.token,
    timeout: int = DOWNLOAD_SETTINGS.timeout,
    path_binaries: PathLike = PATH_BINARIES_SETTINGS.path_binaries,
    chunk_size: int = DOWNLOAD_SETTINGS.chunk_size,
    sudo: bool = PERMS_SETTINGS.sudo,
    perms: PermissionsLike | None = PERMS_SETTINGS.perms,
    owner: str | int | None = PERMS_SETTINGS.owner,
    group: str | int | None = PERMS_SETTINGS.group,
) -> None:
    """Setup 'ripgrep'."""
    with yield_tar_asset(
        "burntsushi",
        "ripgrep",
        token=token,
        match_system=True,
        match_machine=True,
        not_endswith=["sha256"],
        timeout=timeout,
        chunk_size=chunk_size,
    ) as temp:
        src = temp / "rg"
        dest = Path(path_binaries, src.name)
        cp(src, dest, sudo=sudo, perms=perms, owner=owner, group=group)
    LOGGER.info("Downloaded to %r", str(dest))


##


def setup_sops(
    *,
    token: Secret[str] | None = DOWNLOAD_SETTINGS.token,
    timeout: int = DOWNLOAD_SETTINGS.timeout,
    path_binaries: PathLike = PATH_BINARIES_SETTINGS.path_binaries,
    chunk_size: int = DOWNLOAD_SETTINGS.chunk_size,
    sudo: bool = PERMS_SETTINGS.sudo,
    perms: PermissionsLike | None = PERMS_SETTINGS.perms,
    owner: str | int | None = PERMS_SETTINGS.owner,
    group: str | int | None = PERMS_SETTINGS.group,
) -> None:
    """Setup 'sops'."""
    dest = Path(path_binaries, "sops")
    setup_asset(
        "getsops",
        "sops",
        dest,
        token=token,
        match_system=True,
        match_machine=True,
        not_endswith=["json"],
        timeout=timeout,
        chunk_size=chunk_size,
        sudo=sudo,
        perms=perms,
        owner=owner,
        group=group,
    )
    LOGGER.info("Downloaded to %r", str(dest))


__all__ = [
    "setup_age",
    "setup_asset",
    "setup_ripgrep",
    "setup_sops",
    "yield_asset",
    "yield_tar_asset",
]
