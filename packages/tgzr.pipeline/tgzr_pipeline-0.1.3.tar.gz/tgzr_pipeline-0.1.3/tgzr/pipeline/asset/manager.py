from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Type, Any

from pathlib import Path
import subprocess
from packaging.requirements import Requirement

import toml
import rich

from .asset import AssetData, AssetTypeInfo, Asset, ToolAsset, AssetPublishRepo
from .asset import ToolAsset
from .asset_plugins.workscene import Workscene
from .asset_plugins.builder import Builder
from .asset_plugins.creator import ShotCreator
from .asset_plugins.casting import Casting


class AssetManager:
    def __init__(
        self,
        hatch_path: str,
        uv_path: str,
        python_path: str,
    ):
        self._hatch_path = hatch_path
        self._uv_path = uv_path
        self._python_path = python_path

        # TODO: we should be able to detect that:
        # if the current code in running in editable mode, we
        # should use that editable mode path.
        # Maybe pkg_resources tell use if we're editable ?
        # self.USE_DEV_HATCH_HOOKS = True
        self.USE_DEV_HATCH_HOOKS = False

        self._asset_types: list[Type[Asset]] = [
            Asset,
            ToolAsset,
            Workscene,
            Builder,
            ShotCreator,
            Casting,
        ]

    def get_asset_types(self) -> list[Type[Asset]]:
        return self._asset_types

    def get_asset_type(self, asset_type_name: str) -> Type[Asset]:
        for T in self.get_asset_types():
            if T.__name__ == asset_type_name:
                if T.ASSET_TYPE_INFO.type_name is None:
                    T.ASSET_TYPE_INFO.type_name = T.__name__
                return T
        raise KeyError(f"No Asset type named {asset_type_name!r}")

    def get_asset_type_info(self, asset_type_name: str) -> AssetTypeInfo:
        AssetType = self.get_asset_type(asset_type_name)
        return AssetType.ASSET_TYPE_INFO

    def get_asset_from_toml(self, toml_path) -> Asset:
        asset_data = AssetData.from_toml(toml_path)
        asset_type_name = asset_data.asset_type
        AssetType = self.get_asset_type(asset_type_name)
        dinit = toml_path.parent / "__init__.py"
        return AssetType(dinit)

    def create_asset(
        self,
        asset_folder: Path,
        asset_name: str,
        default_repo: str | None,
        asset_data: AssetData | None,
        version: str | None,
        asset_type_name: str,
        **asset_repos: str,
    ):
        """
        Returns the name of the created pacakge.
        """
        AssetType = self.get_asset_type(asset_type_name)

        asset_data = asset_data or AssetData.create_default(
            asset_name=asset_name,
            asset_type=asset_type_name,
        )
        version = version or "0.1.0"
        package_name = asset_name.lower().replace("-", "_").replace(" ", "_")
        if not package_name.replace(".", "").replace("-", "").isidentifier():
            raise ValueError(
                f"Invalid name for package ({asset_name}->{package_name}-> not valid indentifier)"
            )

        if asset_repos is not None:
            asset_data.package.publish.repos.clear()
            for repo_name, repo_path in asset_repos.items():
                asset_data.package.publish.repos.append(
                    AssetPublishRepo(name=repo_name, path=repo_path)
                )
        if default_repo is not None:
            asset_data.package.publish.publish_to = default_repo

        repo_names = [r.name for r in asset_data.package.publish.repos]
        if asset_data.package.publish.publish_to not in repo_names:
            raise ValueError(
                f"Cannot set default repo to {default_repo}: "
                f"not in provided repos: {sorted(repo_names)}"
            )

        asset_path = asset_folder / package_name
        rich.print("Creating Asset", asset_path)
        rich.print(asset_data)

        asset_path.mkdir(exist_ok=True)

        src = (
            asset_path / "src" / package_name
        )  # FIXME: support . here (package namespaces)
        src.mkdir(parents=True, exist_ok=True)

        asset_toml = src / "asset.toml"
        asset_data.write_toml(asset_toml)

        dinit = src / "__init__.py"
        dinit_content = AssetType.default_dinit_content()
        dinit.write_text(dinit_content)

        dversion = src / "__version__.py"
        dversion_content = f'__version__ = "{version}"'
        dversion.write_text(dversion_content)

        readme = asset_path / "README.md"
        readme_content = f"# TGZR Asset: {asset_name}\n"
        readme.write_text(readme_content)

        asset = AssetType(dinit)

        pyproject = asset_path / "pyproject.toml"
        dev_hatch_hooks_location = ""
        if self.USE_DEV_HATCH_HOOKS:
            dev_hatch_hooks_location = (
                " @ file:///home/dee/DEV/_OPEN-TGZR_/tgzr.pipeline"
            )
        asset.write_pyproject(pyproject, hatch_hooks_location=dev_hatch_hooks_location)
        return package_name

    def _edit_asset_data(
        self,
        asset_folder: Path,
        asset_name: str,
        modifier: Callable[[AssetData], AssetData | None],
        rebuild_pyproject: bool,
        bump: str | None = "patch,a",
    ):
        asset_path = asset_folder / asset_name
        if not asset_path.exists():
            raise ValueError(
                f"Cannot edit asset data for {asset_name!r}: it was not found in {asset_folder})."
            )

        toml_path = asset_path / "src" / asset_name / "asset.toml"
        asset = self.get_asset_from_toml(toml_path)
        asset_data = asset.read_asset_data()

        asset_data = modifier(asset_data)

        if asset_data is None:
            print("Nothing to save.")
            return

        # rich.print(asset_data)

        asset_data = asset.write_asset_data(asset_data)

        if rebuild_pyproject:
            pyproject = asset_path / "pyproject.toml"
            dev_hatch_hooks_location = ""
            if self.USE_DEV_HATCH_HOOKS:
                dev_hatch_hooks_location = (
                    " @ file:///home/dee/DEV/_OPEN-TGZR_/tgzr.pipeline"
                )
            asset.write_pyproject(
                pyproject, hatch_hooks_location=dev_hatch_hooks_location
            )

        if bump is not None:
            self.bump_asset(asset_folder, asset_name, "patch,a")

    def rebuild_pyproject(self, asset_folder: Path, asset_name: str):
        asset_path = asset_folder / asset_name
        if not asset_path.exists():
            raise ValueError(
                f"Cannot rebuild pyproject for {asset_name!r}: it was not found in {asset_folder})."
            )

        toml_path = asset_path / "src" / asset_name / "asset.toml"
        asset = self.get_asset_from_toml(toml_path)
        pyproject = asset_path / "pyproject.toml"
        dev_hatch_hooks_location = ""
        if self.USE_DEV_HATCH_HOOKS:
            dev_hatch_hooks_location = (
                " @ file:///home/dee/DEV/_OPEN-TGZR_/tgzr.pipeline"
            )
        asset.write_pyproject(pyproject, hatch_hooks_location=dev_hatch_hooks_location)

    def add_tags(self, asset_folder: Path, asset_name: str, tags: set[str]):

        def add_tags(asset_data: AssetData) -> AssetData | None:
            rich.print(f"Adding tags {tags!r} to {asset_name!r}.")
            old_tags = asset_data.tags.copy()
            asset_data.tags.update(tags)
            if asset_data.tags == old_tags:
                print("No change in tags.")
                return
            return asset_data

        self._edit_asset_data(
            asset_folder,
            asset_name,
            add_tags,
            rebuild_pyproject=True,
            bump="patch,a",
        )

    def add_inputs(self, asset_folder: Path, asset_name: str, *input_requirements: str):
        rich.print(f"Adding inputs {input_requirements!r} to {asset_name!r}.")

        def add_inputs(asset_data: AssetData) -> AssetData | None:
            existing_requirements = [Requirement(i) for i in asset_data.package.inputs]
            existing_named_requirements = dict(
                [(req.name, req) for req in existing_requirements]
            )
            reqs_to_remove = []
            reqs_to_add = []
            for input_requirement in input_requirements:
                input_req = Requirement(input_requirement)
                if input_req.name in existing_named_requirements:
                    existing_req = existing_named_requirements[input_req.name]
                    if input_req == existing_req:
                        # this requirement is already there
                        pass
                    else:
                        reqs_to_remove.append(existing_req)
                        reqs_to_add.append(input_req)
                else:
                    reqs_to_add.append(input_req)

            new_dependencies = []
            for req in existing_requirements:
                if req in reqs_to_remove:
                    continue
                new_dependencies.append(str(req))

            new_dependencies += [str(req) for req in reqs_to_add]
            if asset_data.package.inputs == new_dependencies:
                return None

            asset_data.package.inputs = new_dependencies
            return asset_data

        self._edit_asset_data(
            asset_folder,
            asset_name,
            add_inputs,
            rebuild_pyproject=True,
            bump="patch,a",
        )

    def bump_asset(
        self,
        asset_folder: Path,
        asset_name: str,
        bump: str = "minor",
    ):
        asset_path = asset_folder / asset_name
        subprocess.call(
            [self._hatch_path, "version", bump],
            cwd=asset_path,
        )

    def build_asset(
        self,
        asset_folder: Path,
        asset_name: str,
        dist_folder: Path,
    ):

        asset_path = asset_folder / asset_name
        dist_path = dist_folder / asset_name

        if self.USE_DEV_HATCH_HOOKS:
            rich.print("❗Pruning hatch envs, this should ony be used by devs.")
            subprocess.call(
                [self._hatch_path, "env", "prune"],
                cwd=asset_path,
            )

        subprocess.call(
            [self._hatch_path, "build", "-t", "sdist", dist_path],
            cwd=asset_path,
        )

    def publish_asset(
        self, asset_folder: Path, asset_name: str, dist_folder: Path, **options: str
    ):
        """
        Provided options like:
            option_name='option_value', target='bob'
        will be passed to the publisher plugin like:
            -o option_name=option_value -o default_target=blessed

        """
        asset_path = asset_folder / asset_name

        if self.USE_DEV_HATCH_HOOKS:
            rich.print("❗Pruning hatch envs, this should ony be used by devs.")
            subprocess.call(
                [self._hatch_path, "env", "prune"],
                cwd=asset_path,
            )

        dist_path = dist_folder / asset_name
        hatch_options = sum([["-o", f"{k}={v}"] for k, v in options.items()], [])
        cmd = [
            self._hatch_path,
            "publish",
            "--publisher",
            "tgzr-pipeline-asset",
            *hatch_options,
            *dist_path.iterdir(),
        ]
        # print("--->", cmd)
        subprocess.call(
            cmd,
            cwd=asset_path,
        )

    def install_editable(
        self, asset_folder: Path, asset_name: str, *extra_find_links: str
    ):
        print("AM Install Editable", asset_name)
        find_links = []
        find_links.extend(sum([["-f", i] for i in extra_find_links], []))
        asset_path = asset_folder / asset_name
        cmd = [
            self._uv_path,
            "pip",
            "install",
            "--python",
            self._python_path,  # needed to install in the target venv
            "--no-build-isolation",
            "--no-index",
            *find_links,
            "--editable",
            str(asset_path),
        ]
        print(f"AM: Installing {asset_name} in editable mode:", cmd)
        ret = subprocess.call(cmd)
        print("AM: return code:", ret)

    def install(self, repo_path: str, extra_find_link: str, *requirements: str):
        find_links = []
        if extra_find_link:
            find_links = ["-f", extra_find_link]

        cmd = [
            self._uv_path,
            "pip",
            "install",
            "--python",
            self._python_path,  # needed to install in the target venv
            "--no-build-isolation",
            "--no-index",
            *find_links,
            "-U",
            "-f",
            str(repo_path),
            *requirements,
        ]
        print(cmd)
        subprocess.call(cmd)

    def run_asset_method(
        self, asset_folder: Path, asset_name: str, method_name: str, *args, **kwargs
    ) -> Any:
        asset_path = asset_folder / asset_name
        if not asset_path.exists():
            raise ValueError(
                f"Cannot run method {method_name} from {asset_name!r}: it was not found in {asset_folder})."
            )
        toml_path = asset_path / "src" / asset_name / "asset.toml"
        asset = self.get_asset_from_toml(toml_path)

        try:
            method = getattr(asset, method_name)
        except Exception as err:
            raise AttributeError(
                f"Cannot get method {method_name} from {asset_name!r}: {err}."
            )

        return method(*args, **kwargs)
