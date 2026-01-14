from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from ..asset import Asset, AssetTypeInfo


class Creator(Asset):
    ASSET_TYPE_INFO = AssetTypeInfo(
        category="creator",
        color="#79716b",
        icon="plumbing",
    )

    @classmethod
    def default_dinit_content(cls) -> str:
        # TODO: this could totally be done in the Asset class !!!!!
        cls_module = cls.__module__
        cls_name = cls.__name__
        return f"""
from {cls_module} import {cls_name}

asset = {cls_name}(__file__)

def create():
    asset.create()

def main() -> None:
    asset.hello()

    """

    def _get_pyproject_data(self, hatch_hooks_location: str = ""):

        data = super()._get_pyproject_data(hatch_hooks_location)
        # we register our build plugin:
        eps = data["project"]["scripts"]
        eps[f"tgzr.pipeline.asset.create"] = f"{self.name}:create"

        return data

    def create(self) -> Callable[[], None]:
        raise Exception("Create not implemented on abstract Creator!")


class ShotCreator(Creator):

    def create(self) -> None:
        from tgzr.shell.session import get_default_session
        import rich

        rich.print("\n\nLook at me Mom, I'm creating stuff ! ✨🤗✨")

        session = get_default_session()
        if session is None:
            print("No Session !?!")
            return
        rich.print("Session Context:", session.context)

        from tgzr.pipeline.workspace import Workspace

        project = session.get_selected_project()
        if project is None:
            print("No Project !?!")
            return

        import os

        workspace_path = os.environ.get("tgzr.pipeline.current_workspace.path")
        if workspace_path is None:
            print("No current workspace path !?!")
            return

        workspace = Workspace(workspace_path)
        rich.print("Workspace:", workspace)

        inputs = self.get_input_assets()
        print("Inputs:")
        for name, asset in inputs.items():
            rich.print(name, ":", asset.get_outputs())
