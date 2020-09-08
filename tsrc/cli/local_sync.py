""" Entry point for `tsrc sync` """

from typing import List, Optional
import cli_ui as ui
from argh import arg
from path import Path
import shutil
import os

from tsrc.cli import (
    get_workspace,
    repos_arg,
    resolve_repos,
)


@repos_arg
def local_sync(
    workspace_path: Optional[Path] = None,
    groups: Optional[List[str]] = None,
    all_cloned: bool = False,
    force: bool = False,
) -> None:
    """ synchronize the current workspace with the manifest """
    workspace = get_workspace(workspace_path, local_file=True)
    update_manifest_local()

    workspace.repos = resolve_repos(workspace, groups=groups, all_cloned=all_cloned)
    workspace.clone_missing()
    workspace.set_remotes()
    workspace.sync(force=force)
    workspace.perform_filesystem_operations()
    ui.info("Done", ui.check)


def update_manifest_local():
    ui.info_2("Updating manifest")
    if not os.path.exists('.tsrc/manifest'):
        os.mkdir('.tsrc/manifest')
    shutil.copy('manifest.yml', '.tsrc/manifest')
