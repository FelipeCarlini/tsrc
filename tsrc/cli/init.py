""" Entry point for `tsrc init`. """
from typing import List, Optional
import os

from argh import arg
import cli_ui as ui
from path import Path

import tsrc
from tsrc.cli import repos_from_config, workspace_arg, groups_arg
from tsrc.workspace import Workspace
from tsrc.workspace.config import WorkspaceConfig

remote_help = "only use this remote when cloning repositories"


@workspace_arg  # type: ignore
@groups_arg  # type: ignore
@arg("-r", "--singular-remote", help=remote_help)  # type: ignore
def init(
    url: str,
    workspace_path: Optional[Path] = None,
    groups: Optional[List[str]] = None,
    branch: str = "master",
    clone_all_repos: bool = False,
    shallow: bool = False,
    singular_remote: Optional[str] = None,
) -> None:
    """ initialize a new workspace"""
    path_as_str = workspace_path or os.getcwd()
    workspace_path = Path(path_as_str)
    cfg_path = workspace_path / ".tsrc" / "config.yml"

    if cfg_path.exists():
        raise tsrc.Error("Workspace already configured with file " + cfg_path)

    ui.info_1("Configuring workspace in", ui.bold, workspace_path)

    workspace_config = WorkspaceConfig(
        manifest_url=url,
        manifest_branch=branch,
        clone_all_repos=clone_all_repos,
        repo_groups=groups or [],
        shallow_clones=shallow,
        singular_remote=singular_remote,
    )

    workspace_config.save_to_file(cfg_path)

    workspace = Workspace(workspace_path)
    workspace.update_manifest()
    manifest = workspace.get_manifest()
    workspace.repos = repos_from_config(manifest, workspace_config)
    workspace.clone_missing()
    workspace.set_remotes()
    workspace.perform_filesystem_operations()
    ui.info_2("Workspace initialized")
    ui.info_2("Configuration written in", ui.bold, workspace.cfg_path)
