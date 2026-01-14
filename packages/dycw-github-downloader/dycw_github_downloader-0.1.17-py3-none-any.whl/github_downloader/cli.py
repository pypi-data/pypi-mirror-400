from __future__ import annotations

from click import argument, group
from rich.pretty import pretty_repr
from typed_settings import click_options
from utilities.click import CONTEXT_SETTINGS
from utilities.logging import basic_config
from utilities.os import is_pytest
from utilities.text import strip_and_dedent

from github_downloader import __version__
from github_downloader.lib import setup_age, setup_asset, setup_ripgrep, setup_sops
from github_downloader.logging import LOGGER
from github_downloader.settings import (
    LOADER,
    DownloadSettings,
    MatchSettings,
    PathBinariesSettings,
    PermsSettings,
)


@group(**CONTEXT_SETTINGS)
def _main() -> None: ...


@_main.command(name="run", **CONTEXT_SETTINGS)
@argument("asset-owner", type=str)
@argument("asset-repo", type=str)
@argument("binary-name", type=str)
@click_options(MatchSettings, [LOADER], show_envvars_in_help=True, argname="common")
@click_options(
    DownloadSettings, [LOADER], show_envvars_in_help=True, argname="download"
)
@click_options(PermsSettings, [LOADER], show_envvars_in_help=True, argname="perms")
def run_sub_cmd(
    *,
    asset_owner: str,
    asset_repo: str,
    binary_name: str,
    common: MatchSettings,
    download: DownloadSettings,
    perms: PermsSettings,
) -> None:
    if is_pytest():
        return
    basic_config(obj=LOGGER)
    LOGGER.info(
        strip_and_dedent("""
            Running '%s' (version %s) with settings:
            %s
            %s
            %s
        """),
        setup_asset.__name__,
        __version__,
        pretty_repr(common),
        pretty_repr(download),
        pretty_repr(perms),
    )
    setup_asset(
        asset_owner,
        asset_repo,
        binary_name,
        token=download.token,
        match_system=common.match_system,
        match_machine=common.match_machine,
        not_endswith=common.not_endswith,
        timeout=download.timeout,
        chunk_size=download.chunk_size,
        sudo=perms.sudo,
        perms=perms.perms,
        owner=perms.owner,
        group=perms.group,
    )


@_main.command(name="age", **CONTEXT_SETTINGS)
@click_options(
    DownloadSettings, [LOADER], show_envvars_in_help=True, argname="download"
)
@click_options(
    PathBinariesSettings, [LOADER], show_envvars_in_help=True, argname="path_binaries"
)
@click_options(PermsSettings, [LOADER], show_envvars_in_help=True, argname="perms")
def age_sub_cmd(
    *,
    download: DownloadSettings,
    path_binaries: PathBinariesSettings,
    perms: PermsSettings,
) -> None:
    if is_pytest():
        return
    basic_config(obj=LOGGER)
    LOGGER.info(
        strip_and_dedent("""
            Running '%s' (version %s) with settings:
            %s
            %s
            %s
        """),
        setup_age.__name__,
        __version__,
        pretty_repr(download),
        pretty_repr(path_binaries),
        pretty_repr(perms),
    )
    setup_age(
        token=download.token,
        timeout=download.timeout,
        path_binaries=path_binaries.path_binaries,
        chunk_size=download.chunk_size,
        sudo=perms.sudo,
        perms=perms.perms,
        owner=perms.owner,
        group=perms.group,
    )


@_main.command(name="ripgrep", **CONTEXT_SETTINGS)
@click_options(
    DownloadSettings, [LOADER], show_envvars_in_help=True, argname="download"
)
@click_options(
    PathBinariesSettings, [LOADER], show_envvars_in_help=True, argname="path_binaries"
)
@click_options(PermsSettings, [LOADER], show_envvars_in_help=True, argname="perms")
def ripgrep_sub_cmd(
    *,
    download: DownloadSettings,
    path_binaries: PathBinariesSettings,
    perms: PermsSettings,
) -> None:
    if is_pytest():
        return
    basic_config(obj=LOGGER)
    LOGGER.info(
        strip_and_dedent("""
            Running '%s' (version %s) with settings:
            %s
            %s
            %s
        """),
        setup_ripgrep.__name__,
        __version__,
        pretty_repr(download),
        pretty_repr(path_binaries),
        pretty_repr(perms),
    )
    setup_ripgrep(
        token=download.token,
        timeout=download.timeout,
        path_binaries=path_binaries.path_binaries,
        chunk_size=download.chunk_size,
        sudo=perms.sudo,
        perms=perms.perms,
        owner=perms.owner,
        group=perms.group,
    )


@_main.command(name="sops", **CONTEXT_SETTINGS)
@click_options(
    DownloadSettings, [LOADER], show_envvars_in_help=True, argname="download"
)
@click_options(
    PathBinariesSettings, [LOADER], show_envvars_in_help=True, argname="path_binaries"
)
@click_options(PermsSettings, [LOADER], show_envvars_in_help=True, argname="perms")
def sops_sub_cmd(
    *,
    download: DownloadSettings,
    path_binaries: PathBinariesSettings,
    perms: PermsSettings,
) -> None:
    if is_pytest():
        return
    basic_config(obj=LOGGER)
    LOGGER.info(
        strip_and_dedent("""
            Running '%s' (version %s) with settings:
            %s
            %s
            %s
        """),
        setup_sops.__name__,
        __version__,
        pretty_repr(download),
        pretty_repr(path_binaries),
        pretty_repr(perms),
    )
    setup_sops(
        token=download.token,
        timeout=download.timeout,
        path_binaries=path_binaries.path_binaries,
        chunk_size=download.chunk_size,
        sudo=perms.sudo,
        perms=perms.perms,
        owner=perms.owner,
        group=perms.group,
    )


if __name__ == "__main__":
    _main()
