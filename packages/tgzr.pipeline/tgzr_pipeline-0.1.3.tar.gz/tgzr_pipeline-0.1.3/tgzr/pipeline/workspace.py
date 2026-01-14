from __future__ import annotations
from typing import Any

from pathlib import Path
import subprocess
import platform
from importlib.metadata import Distribution
import dataclasses
from ast import literal_eval
import os

import uv as external_uv
import pydantic

from .asset.manager import AssetManager, AssetTypeInfo


class WorkspaceSettings(pydantic.BaseModel):
    main_entity: str | None = (
        None  # optional main entity FIXME: should be auto installed
    )


@dataclasses.dataclass
class AssetInfo:
    pass


@dataclasses.dataclass
class ToolInfo:
    pass


@dataclasses.dataclass
class DistInfo:
    """
    Pipeline related information extracted from
    a `importlib.metadata.Distribution()`.

    These are created by Workspace.get_dist_info
    """

    dist: Distribution
    is_asset: bool
    asset_name: str
    asset_type: str | None
    tags: set[str]
    is_editable: bool
    nice_panel_names: list[str]


class Workspace:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._name = self.path.name

        bin = "bin"
        if platform.system() != "Linux":
            bin = "Scripts"
        self._venv_name = "inputs"
        self._venv_path = self.path / self._venv_name
        self._venv_bin_path = self._venv_path / bin
        self._external_packages_path = self.path / "external_packages"
        self._output_path = self.path / "outputs"
        self._build_path = self._path / "build"

        self._asset_manager = AssetManager(
            hatch_path=str(self._venv_bin_path / "hatch"),
            uv_path=str(self._venv_bin_path / "uv"),
            python_path=str(self._venv_bin_path / "python"),
        )

        # TODO: make these configurable?
        self._default_repo_name = "review"
        self._blessed_repo_name = "blessed"

        self._default_repos: dict[str, str] = {}

    @property
    def path(self) -> Path:
        """The path of the Workspace, including its name."""
        return self._path

    @property
    def name(self) -> str:
        """The name of the Workspace, deducted from its path."""
        return self._name

    @property
    def venv_path(self) -> Path:
        """The path to the Workspace's venv."""
        return self._venv_path

    @property
    def exists(self) -> bool:
        return self._venv_bin_path.exists()

    @property
    def asset_manager(self) -> AssetManager:
        return self._asset_manager

    def get_asset_types_info(self) -> dict[str, AssetTypeInfo]:
        asset_types = self.asset_manager.get_asset_types()
        ret = dict()
        for AssetType in asset_types:
            asset_type_info = AssetType.ASSET_TYPE_INFO
            # set default type_name if needed:
            if asset_type_info.type_name is None:
                asset_type_info.type_name = AssetType.__name__
            ret[asset_type_info.type_name] = asset_type_info
        return ret

    def add_repo(
        self,
        repo_name: str,
        repo_path: str,
        make_blessed: bool = False,
        make_default: bool = True,
    ):
        """
        Add a repo to the workspace.
        All asset created after this will be configured with this repo.
        """
        # TODO: store these in a confif file in the workspace?
        repo_abs_path = (self.path / repo_path).resolve()
        self._default_repos[repo_name] = str(repo_abs_path)
        print(f"Adding repo {repo_name}: {repo_abs_path}")
        repo_abs_path.mkdir(parents=True, exist_ok=True)
        if make_blessed:
            self._blessed_repo_name = repo_name
        if make_default:
            self._default_repo_name = repo_name

    def repo_names(self) -> list[str]:
        return list(self._default_repos.keys())

    def ensure_exists(self, force_build: bool = False):
        if not force_build and self.exists:
            return
        self._path.mkdir(parents=True, exist_ok=True)
        self._external_packages_path.mkdir(parents=True, exist_ok=True)
        self._output_path.mkdir(parents=True, exist_ok=True)
        self._build_path.mkdir(parents=True, exist_ok=True)

        self._recreate_venv()

    def _recreate_venv(self):
        # Create the venv:
        venv_path = self.path / self._venv_name
        uv = external_uv.find_uv_bin()
        cmd = [
            uv,
            "venv",
            "--allow-existing",
            "--prompt",
            f"WS: {self.name}",
            str(venv_path),
        ]
        print(cmd)
        subprocess.call(cmd)

        # Seed with our build system dependencies
        # (Installing assets do not have access to pypi, for security reasons.)
        dependencies = [
            "uv",
            "hatch",
            "hatchling",
            "editables",
            "tgzr.pipeline",  # TODO: we should specify the current runing version, and support editable install
        ]
        self.install_external_packages(*dependencies)

        # Install all needed/allowed dependencies:
        # (Installing assets do not have access to pypi, for security reasons.)
        allowlist = []
        self.add_extenal_packages(*allowlist)

    def install_external_packages(self, *requirements):
        """
        Install the given requirements in the workspace venv
        so that they are available if an asset has them as
        dependency.
        """
        if not requirements:
            return
        uv = external_uv.find_uv_bin()
        python = self._venv_bin_path / "python"
        cmd = [
            uv,
            "pip",
            "install",
            "--python",
            python,
            *requirements,
        ]
        print(cmd)
        subprocess.call(cmd)

    def add_extenal_packages(self, *requirements):
        """
        Install the given requirement in the external_packages
        folder. This folder is always use as --find-links so
        this will make theses pacakages available if an asset
        has them as dependency.
        """
        if not requirements:
            return
        uv = external_uv.find_uv_bin()
        cmd = [
            uv,
            "pip",
            "install",
            "--target",
            self._external_packages_path,
            *requirements,
        ]
        print(cmd)
        subprocess.call(cmd)

    def create_asset(
        self,
        asset_type_name: str,
        asset_name: str,
        default_repo: str | None = None,
        **extra_repos: str,
    ):
        """
        Create an output asset in this workspace.
        """
        default_repo = default_repo or self._default_repo_name
        extra_repos.update(self._default_repos)
        package_name = self.asset_manager.create_asset(
            self._output_path,
            asset_name,
            default_repo=default_repo,
            asset_data=None,
            version=None,
            asset_type_name=asset_type_name,
            **extra_repos,
        )
        self._install_editable(package_name)

    def rebuid_pyproject(self, asset_name: str):
        """
        Rebuild the pyproject.toml file, bump and install (editable)
        Usefull when the content of the pyproject file need to be updated/conformed
        """
        self.asset_manager.rebuild_pyproject(self._output_path, asset_name)
        self.bump_asset(asset_name, "micro")

    def get_output_project_names(self):
        names = []
        for path in self._output_path.iterdir():
            if (path / "pyproject.toml").exists:
                names.append(path.name)
        return sorted(names)

    def _install_editable(self, asset_name: str):
        print("WS Install editable", asset_name)

        find_links = []
        blessed = self._default_repos.get(self._blessed_repo_name)
        if blessed:
            find_links.append(blessed)
        default = self._default_repos.get(self._default_repo_name)
        if default:
            find_links.append(default)

        self.asset_manager.install_editable(
            self._output_path,
            asset_name,
            str(self._external_packages_path),
            *find_links,
        )

    def tag_asset(self, asset_name: str, *tags: str):
        self.asset_manager.add_tags(self._output_path, asset_name, set(tags))
        self._install_editable(asset_name)

    def add_inputs(self, asset_name: str, *input_requirements: str):
        """
        Make this asset dependent of the input_requirements.
        Each input_requirement can be like:
            - asset-name
            - asset-name==1.2.3
            - asset-anme>=2.3.4
            - asset-name>=3.4.5<4.0
            etc...
        """
        if not self.has_editable_asset(asset_name):
            raise ValueError(f"Cannot add inputs to non-editable asset {asset_name!r}")
        self.asset_manager.add_inputs(
            self._output_path, asset_name, *input_requirements
        )
        self._install_editable(asset_name)

    def bump_asset(self, asset_name: str, bump: str = "minor"):
        """
        Bumpt the part of the version specified with bump, like:"
            major
            minor
            micro / patch / fix
            a / alpha
            b / alpha
            c / rc / pre / preview
            r / rev / post
            dev

        or a combination like:
            minor,rc
            patch,a
            major,alpha,dev

        Defaults is to bump minor."
        """
        self.asset_manager.bump_asset(self._output_path, asset_name, bump=bump)
        self._install_editable(asset_name)

    def build_asset(self, asset_name: str, bump: str = "minor"):
        self.asset_manager.bump_asset(self._output_path, asset_name, bump=bump)
        self.asset_manager.build_asset(self._output_path, asset_name, self._build_path)

    def publish_asset(self, asset_name: str, repo_name: str | None = None):
        options = {}
        if repo_name is not None:
            options["publish_to"] = repo_name
        self.asset_manager.publish_asset(
            self._output_path,
            asset_name,
            self._build_path,
            **options,
        )

    def install_asset(
        self,
        repo_name: str,
        requirement,
    ):
        try:
            repo_path = self._default_repos[repo_name]
        except KeyError:
            raise ValueError(
                f"The repo {repo_name!r} in not defined "
                f"(got: {sorted(list(self._default_repos.keys()))}"
            )
        self.asset_manager.install(
            repo_path, str(self._external_packages_path), requirement
        )

    def has_editable_asset(self, asset_name: str):
        return (self._output_path / asset_name).exists()

    def turn_asset_editable(self, asset_name: str, force: bool = False):
        """
        Turn an input asset into a output asset.
        The asset must already be installed in the inputs
        """
        if self.has_editable_asset(asset_name):
            if not force:
                raise ValueError(
                    f"The asset {asset_name} is already an editable in workspace {self.path}."
                )

        uv = self._venv_bin_path / "uv"
        python = self._venv_bin_path / "python"
        cmd = [
            str(uv),
            "run",
            "--python",
            str(python),
            "--directory",
            str(self._venv_bin_path),
            "python",
            "-c",
            f"import {asset_name} as package; package.asset.create_editable(workspace_path='{self.path}', force={force})",
        ]
        # print(cmd)
        err_code = subprocess.call(cmd)
        if err_code:
            print(f"Oops, return code is error: {err_code}.")
        else:
            self.asset_manager.bump_asset(self._output_path, asset_name, bump="micro")
            self._install_editable(asset_name)

    def get_dist_info(self, dist: Distribution) -> DistInfo:
        is_editable = False
        if (
            dist.origin is not None
            and hasattr(dist.origin, "dir_info")
            and dist.origin.dir_info.editable
        ):
            # TODO: verify if the editable path in in our output dir?
            is_editable = True

        dist_info = DistInfo(
            dist=dist,
            asset_name=dist.name,
            asset_type=None,
            is_editable=is_editable,
            is_asset="tgzr.pipeline.asset_info_trick" in dist.entry_points.groups,
            tags=set(),
            nice_panel_names=[],
        )
        if dist_info.is_asset:
            for ep in dist.entry_points.select(group="tgzr.pipeline.asset_info_trick"):
                if ep.name == "asset_name":
                    dist_info.asset_name = ep.value
                elif ep.name == "asset_type":
                    dist_info.asset_type = ep.value
                elif ep.name == "tags":
                    dist_info.tags = literal_eval(ep.value)

            for ep in dist.entry_points.select(group="tgzr.pipeline.asset.nice_panel"):
                dist_info.nice_panel_names.append(ep.name)

        return dist_info

    def run(self, console_script_name: str):
        uv = self._venv_bin_path / "uv"
        python = self._venv_bin_path / "python"
        cmd = [
            str(uv),
            "run",
            "--python",
            str(python),
            "--directory",
            str(self._venv_bin_path),
            console_script_name,
        ]
        # print(cmd)
        env = os.environ.copy()
        env["tgzr.pipeline.current_workspace.path"] = str(self.path)
        # print(env)
        err_code = subprocess.call(cmd, env=env)
        if err_code:
            print(
                f"Oops, 'uv run {console_script_name}' returned error code: {err_code}."
            )

    def run_asset_method(
        self, asset_name: str, method_name: str, *args, **kwargs
    ) -> Any:
        """
        Execute that asset's method in the current thread.

        This is probably dangerous. Doing things like modifying the
        asset in that method would be quite a bad ides I guess...
        """
        return self.asset_manager.run_asset_method(
            self._output_path, asset_name, method_name, *args, **kwargs
        )

    def render_nice_panel(self, asset_name: str, panel_name: str) -> Any:
        """
        Assets can implement GUI panels (see Asset.nice_panel_names())
        When they do so, their DistInfo.nice_panel_names contains the
        name of the panel they can render.
        You can call this method under a nicegui.ui element context
        to render the asset's panel.
        """
        return self.run_asset_method(
            asset_name=asset_name, method_name=panel_name, workspace=self
        )
