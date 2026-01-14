from pathlib import Path
import os
from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.version.core import VersionFile

import packaging.version

"""
NB: you need to do:
hatch env prune
in the project using this plugin
each time you modify it !
(See README in the same folder)
"""


def save_default_version_file(root: str, relative_path: str):
    default_version = "0"
    path = os.path.normpath(os.path.join(root, relative_path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(f'__version__ = "{default_version}"')
    return default_version


class TGZRAssetMetadataHook(MetadataHookInterface):

    PLUGIN_NAME = "tgzr-pipeline-asset"

    def do_bump(self, version: packaging.version.Version) -> str | None:
        bump_mode = os.environ.get("TGZR_ASSET_BUMP_MODE")
        if not bump_mode:
            print("TGZR_ASSET_BUMP_MODE env var not set")
            # print("Not bumping")
            # return None
            print("Bumping patch")
            bump_mode = "patch"
        elif bump_mode not in ["auto", "major", "minor", "patch"]:
            print(f'Invalid value in env TGZR_ASSET_BUMP_MODE: "{bump_mode}"')
            print('please use "major", "minor" or "patch"')
            print("Bumping patch")
            bump_mode = "auto"

        major = version.major
        minor = version.minor
        patch = version.micro

        if bump_mode == "auto":
            print("Auto bump on", version.release)
            release_len = len(version.release)
            if release_len > 2:
                patch += 1
            elif release_len > 1:
                minor += 1
            else:
                major += 1

        elif bump_mode == "major":
            print("Major bump")
            major += 1
            minor = 0
            patch = 0

        elif bump_mode == "minor":
            print("Minor bump")
            minor += 1
            patch = 0

        elif bump_mode == "patch":
            print("Patch bump")
            patch += 1

        _version = list(version._version)
        release = (major, minor, patch)
        _version[1] = release
        version._version = packaging.version._Version(
            *_version  # pyright: ignore[reportArgumentType]
        )
        return str(packaging.version._TrimmedRelease(str(version)))

    def update_version(self, metadata: dict) -> None:
        name = metadata["name"]
        name = name.replace("-", "_")

        version_file_relative_path = self.config.get("version_file", None)
        if version_file_relative_path is None:
            default = f"src/{name}/__version__.py"
            print(f"version_file not specified. Using default: {default}")
            # raise ValueError(
            #     "You need to add something like this in your pyproject.toml:\n\n"
            #     f"[tools.hatch.metadata.hooks.{self.PLUGIN_NAME}]\n"
            #     f'version_file="src/{name}/__version__.py"\n'
            # )
            version_file_relative_path = default
        print("Using version file:", version_file_relative_path)
        version_file = VersionFile(self.root, version_file_relative_path)
        try:
            current_version_str = version_file.read(pattern=True)
        except OSError:
            current_version_str = save_default_version_file(
                self.root, version_file_relative_path
            )
        current_version = packaging.version.parse(current_version_str)
        print(">>> Version:", current_version)
        new_version = self.do_bump(current_version)
        if new_version is not None:
            print(">>> New version:", new_version)
            version_file.set_version(new_version)
            metadata["version"] = str(new_version)

    def declare_scripts(self, metadata: dict) -> None:
        metadata["scripts"] = {metadata["name"]: metadata["name"] + ":main"}

    def excludes_dvc_data(self, metadata: dict) -> None:
        pass

    def update(self, metadata: dict) -> None:
        print("???? THIS SHOULD NOT BUMP UNLESS EDITABLE")
        name = metadata["name"]

        # try to bump the version only if installed in editable:
        pyproject = Path(self.root) / "pyproject.toml"
        if pyproject.exists():
            print("!!!!!!!!!!! PYPROJECT EXISTS", pyproject)
            if pyproject.parent.name == name:
                print("!!!!!!!!!!! Parent is project name:", pyproject.parent.name)
                self.update_version(metadata)
            else:
                print("!!!!!!!!!!! Parent is not project name:", pyproject.parent.name)
                print("     Chances are we are currently installing the package.")

        self.declare_scripts(metadata)
        # self.excludes_dvc_data(metadata)

        import rich

        rich.print(metadata)
