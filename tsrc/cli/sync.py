""" Entry point for `tsrc sync` """

from typing import List, Optional
import cli_ui as ui
from argh import arg
from path import Path

from tsrc.cli import (
    get_workspace,
    repos_arg,
    resolve_repos,
)

file_help = "use manifest from a file instead of a git repository"


@repos_arg
@arg("-f", "--file", help=file_help, action="store_true")  # type: ignore
def sync(
    workspace_path: Optional[Path] = None,
    groups: Optional[List[str]] = None,
    all_cloned: bool = False,
    force: bool = False,
    file: Optional[bool] = None,
) -> None:
    """ synchronize the current workspace with the manifest """
    workspace = get_workspace(workspace_path, local_file=file)
    if not file:
        ui.info_2("Updating manifest")
        workspace.update_manifest()

    workspace.repos = resolve_repos(workspace, groups=groups, all_cloned=all_cloned)
    workspace.clone_missing()
    workspace.set_remotes()
    workspace.sync(force=force)
    workspace.perform_filesystem_operations()
    ui.info("Done", ui.check)
