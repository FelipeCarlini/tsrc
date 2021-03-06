import abc
import os

import attr
import cli_ui as ui
from path import Path

import tsrc


class FileSystemOperation(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def perform(self, workspace_path: Path) -> None:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass


@attr.s(frozen=True)
class Copy(FileSystemOperation):
    repo = attr.ib()  # type: str
    src = attr.ib()  # type: str
    dest = attr.ib()  # type: str

    def perform(self, workspace_path: Path) -> None:
        src_path = workspace_path / self.repo / self.src
        dest_path = workspace_path / self.dest
        src_path.copy(dest_path)

    def __str__(self) -> str:
        return f"copy from '{self.repo}/{self.src}' to '{self.dest}'"


@attr.s(frozen=True)
class Link(FileSystemOperation):
    repo = attr.ib()  # type: str
    source = attr.ib()  # type: str
    target = attr.ib()  # type: str

    def perform(self, workspace_path: Path) -> None:
        source = workspace_path / self.source
        target = Path(self.target)
        safe_link(source=source, target=target)

    def __str__(self) -> str:
        return f"link from '{self.source}' to '{self.target}'"


def safe_link(*, source: Path, target: Path) -> None:
    """ Safely create a link in 'source' pointing to 'target'. """
    # Not: we need to call both islink() and exist() to safely ensure
    # that the link exists:
    #
    #    islink()  exists()    Description
    #    ----------------------------------------------------------
    #    False     False       source doesn't currently exist : OK
    #    False     True        source corresponds to a file or dir : Error!
    #    True      False       broken symlink, need to remove
    #    True      True        symlink points to a valid target, check target
    #    ----------------------------------------------------------
    make_link = check_link(source=source, target=target)
    if make_link:
        ui.info_3("Creating link", source, "->", target)
        os.symlink(
            target.normpath(), source.normpath(), target_is_directory=target.isdir()
        )


def check_link(*, source: Path, target: Path) -> bool:
    remove_link = False
    if source.exists() and not source.islink():
        raise tsrc.Error("Specified symlink source exists but is not a link")
        return False
    if source.islink():
        if source.exists():
            # symlink exists and points to some target
            current_target = source.readlink()
            if current_target.realpath() == target.realpath():
                ui.info_3("Leaving existing link")
                return False
            else:
                ui.info_3("Replacing existing link")
                remove_link = True
        else:
            # symlink exists, but points to a non-existent target
            ui.info_3("Replacing broken link")
            remove_link = True
    if remove_link:
        os.unlink(source)
    return True
