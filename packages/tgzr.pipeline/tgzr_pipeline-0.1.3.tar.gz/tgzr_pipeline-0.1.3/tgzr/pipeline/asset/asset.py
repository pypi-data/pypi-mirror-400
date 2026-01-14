from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any

from pathlib import Path
from functools import cached_property
import importlib
import dataclasses
import importlib.metadata

import rich
import pydantic
import toml


if TYPE_CHECKING:
    from ..workspace import Workspace


class AssetPublishRepo(pydantic.BaseModel):
    name: str
    path: str


class AssetPublishConfig(pydantic.BaseModel):
    publish_to: str = "review"
    repos: list[AssetPublishRepo] = []

    def to_pyproject(self):
        """Returns a dict suitable for the "tool.hatch.publish.tgzr-pipeline-asset" pyproject section."""
        return dict(
            publish_to=self.publish_to,
            repos=dict([(r.name, r.path) for r in self.repos]),
        )


class AssetPackageConfig(pydantic.BaseModel):
    inputs: list[str] = []
    publish: AssetPublishConfig


class InputPosition(pydantic.BaseModel):
    input_name: str
    x: float
    y: float


class AssetGraph(pydantic.BaseModel):
    positions: list[InputPosition] = []


class AssetData(pydantic.BaseModel):
    asset_name: str
    asset_type: str
    package: AssetPackageConfig
    tags: set[str] = set([])
    entity: str | None = None
    graph: AssetGraph

    @classmethod
    def create_default(cls, asset_name: str, asset_type: str):
        return cls(
            asset_name=asset_name,
            asset_type=asset_type,
            package=AssetPackageConfig(
                publish=AssetPublishConfig(),
            ),
            graph=AssetGraph(),
        )

    @classmethod
    def from_toml(cls, toml_path: Path):
        asset_data = toml.load(toml_path)
        return cls(**asset_data)

    def write_toml(self, toml_path: Path):
        toml_path.write_text(toml.dumps(self.model_dump()))


@dataclasses.dataclass
class AssetTypeInfo:
    category: str | None = None  # just for UIs (None = hidden category)
    type_name: str | None = None  # specify it if it's not the class name
    color: str | None = None  # html format
    icon: str | None = None  # one of the google-font or fontawesome icons


class Asset:
    ASSET_TYPE_INFO = AssetTypeInfo(
        category="asset",
        color="#00bc7d",
        icon="diamond",
    )

    def __init__(self, init_file: Path | str):
        self._init_file = Path(init_file)
        # self._data_path = self._init_file / ".." / "DATA"
        self.name = self._init_file.parent.name
        self.asset_toml = (self._init_file / ".." / "asset.toml").resolve()

    def hello(self):
        print(f"Hello from asset {self.name} ({self.is_editable=})")
        rich.print(AssetData.from_toml(self.asset_toml))

    @cached_property
    def is_editable(self) -> bool:
        for parent in self._init_file.parents:
            if (parent / "pyproject.toml").exists():
                return True
        return False

    def get_version(self) -> str:
        version_module = importlib.import_module(self.name + ".__version__")
        return version_module.__version__

    def read_asset_data(self) -> AssetData:
        asset_data = AssetData.from_toml(self.asset_toml)
        return asset_data

    def write_asset_data(self, asset_data: AssetData):
        asset_data.write_toml(self.asset_toml)

    # @property
    # def data_dir(self) -> str:
    #     return str(self._data_path)

    # def pull_data(self):
    #     raise NotImplementedError()
    #     repo = dvc.repo.Repo(self.data_dir)
    #     repo.pull()

    @classmethod
    def default_dinit_content(cls) -> str:
        return """
from tgzr.pipeline.asset import Asset

asset = Asset(__file__)

def main() -> None:
    asset.hello()

    """

    def _get_pyproject_data(self, hatch_hooks_location: str = "") -> dict[str, Any]:
        asset_data = self.read_asset_data()
        name = self.name
        data = {
            "project": {
                "name": name,
                "dynamic": ["version"],
                "description": f"{name!r} - A TGZR Pipeline Asset created by tgzr.pipeline.asset.manager",
                "readme": "README.md",
                "dependencies": ["tgzr.pipeline"] + asset_data.package.inputs,
                "scripts": {name: f"{name}:main"},
                "entry-points": {
                    "tgzr.pipeline.asset": {"asset": f"{name}:asset"},
                    "tgzr.pipeline.asset_info_trick": {
                        f"asset_name": asset_data.asset_name,
                        f"asset_type": asset_data.asset_type,
                        f"tags": repr(asset_data.tags),
                    },
                },
            },
            "build-system": {
                "requires": [
                    "hatchling",
                    f"tgzr.pipeline{hatch_hooks_location}",
                ],
                "build-backend": "hatchling.build",
            },
            "tool": {
                "hatch": {
                    "envs": {"default": {"installer": "uv"}},
                    "version": {"path": f"src/{name}/__version__.py"},
                    "publish": {
                        "tgzr-pipeline-asset": asset_data.package.publish.to_pyproject()
                    },
                }
            },
        }

        panel_names = self.nice_panel_names()
        if panel_names:
            try:
                nice_panels_ep = data["project"]["entry-points"][
                    "tgzr.pipeline.asset.nice_panel"
                ]
            except KeyError:
                nice_panels_ep = {}
                data["project"]["entry-points"][
                    "tgzr.pipeline.asset.nice_panel"
                ] = nice_panels_ep

        for panel_name in panel_names:
            nice_panels_ep[panel_name] = f"{self.name}:asset.{panel_name}"

        return data

    def write_pyproject(self, pyproject_path: Path, hatch_hooks_location: str = ""):
        pyproject_data = self._get_pyproject_data(hatch_hooks_location)
        print("Saving pyproject:", pyproject_path)
        pyproject_path.write_text(toml.dumps(pyproject_data))

    def create_editable(self, workspace_path: Path | str, force: bool = False):
        if self.is_editable:
            raise ValueError(
                f"Are you sure you want to create an editable version of {self.name}? \n"
                f"(it is already editable linked to {self._init_file})."
            )
        from ..workspace import Workspace

        workspace_path = Path(workspace_path)
        ws = Workspace(workspace_path)
        if ws.has_editable_asset(self.name):
            if not force:
                raise ValueError(
                    f"The asset {self.name} is already an editable in workspace {workspace_path}."
                )

        print(f"Creating editable asset for {self.name} in workspace {workspace_path}")

        version = self.get_version()
        asset_data = self.read_asset_data()

        ws.asset_manager.create_asset(
            ws._output_path,
            self.name,
            default_repo=None,  # = dont override it in asset_data
            asset_data=asset_data,
            version=version,
            asset_type_name=self.__class__.__name__,
        )

    def nice_panel_names(self) -> list[str]:
        """
        Asset subclasses implementing nice panel guis
        must override this method to return the name of the method
        implementing each panel.

        NB: You panel method will **NOT** be executed in the asset
        virtual env. That means you cant do things like execute them
        or even import the input asset with `self.get_input_assets()`.
        But you can access the asset data with `self.read_asset_data()`
        and save them with `self.write_asset_data(data)`.
        If you **really** want to affect the asset, you need to do so
        using the Workspace provided with the `workspace` arguemnt.

        NB: GUIs will show your panels by alphabetic order, but you
        can preprend the panel names with some "_" to bring them first.

        Example:

        from tgzr.pipeline.workspace import Workspace

        class MyAsset(Asset):
            def nice_panel_name(self)->list[str]:
                return ['preview_panel', 'options_panel']

            def preview_panel(self, workspace:Workspace)->None:
                ui.label('This is the preview panel.')

            def options_panel(self, workspace:Workspace)->None:
                ui.label('This is the option panel.')

        """
        return []

    def get_input_assets(self, group: str | None = None) -> dict[str, Asset]:
        """
        Returns a dict like {asset_name:Asset}
        """
        assets = {}
        asset_data = self.read_asset_data()
        for package_name in asset_data.package.inputs:
            module = importlib.import_module(package_name)
            try:
                asset: Asset = module.asset
            except AttributeError:
                pass
            else:
                assets[package_name] = module.asset
        return assets

    def get_outputs(self) -> list[Any]:
        return [self]


class ToolAsset(Asset):
    """
    An asset that is made of code.
    It can load plugin (and should advertise it in pyproject if it does.)
    """

    ASSET_TYPE_INFO = AssetTypeInfo(
        category="tool",
        color="#79716b",
        icon="handyman",
    )

    @classmethod
    def default_dinit_content(cls) -> str:
        # TODO: this could totally be done in the Asset class !!!!!
        cls_module = cls.__module__
        cls_name = cls.__name__

        return f"""
from {cls_module} import {cls_name}

asset = {cls_name}(__file__)
    
def main() -> None:
    asset.hello()

    """

    def _get_pyproject_data(self, hatch_hooks_location: str = "") -> dict[str, Any]:

        # TODO: this could totally be done in the Asset class !!!!!

        data = super()._get_pyproject_data(hatch_hooks_location)
        # we register the tools in a different entry point:
        eps = data["project"]["entry-points"]
        value = eps.pop("tgzr.pipeline.asset")
        eps[f"tgzr.pipeline.{self.__class__.__name__}"] = value

        return data

    def get_plugins(
        self, plugin_group: str = "tgzr.pipeline.asset.plugin_name"
    ) -> tuple[list[Any], list[tuple[importlib.metadata.EntryPoint, Exception]]]:

        all_entry_points = importlib.metadata.entry_points(group=plugin_group)

        plugins = []
        errs = []
        for ep in all_entry_points:
            # print(f"Loading {entry_point_group} plugin:", ep.name)
            try:
                loaded = ep.load()
            except Exception as err:
                errs.append((ep, err))
                continue

            if not isinstance(loaded, list):
                errs.append(
                    (ep, ValueError(f"EntryPoint loaded value is not a list: {loaded}"))
                )
                continue
            plugins.extend(loaded)
        return plugins, errs
