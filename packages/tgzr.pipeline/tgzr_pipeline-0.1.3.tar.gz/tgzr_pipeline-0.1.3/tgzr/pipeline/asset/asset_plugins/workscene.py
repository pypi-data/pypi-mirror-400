from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from ..asset import Asset, AssetTypeInfo


class Workscene(Asset):
    ASSET_TYPE_INFO = AssetTypeInfo(
        category="file",
        color="#fd9a00",
        icon="palette",
    )

    @classmethod
    def default_dinit_content(cls) -> str:
        cls_module = cls.__module__
        cls_name = cls.__name__
        return f"""
from typing import Callable
from {cls_module} import {cls_name}

asset = {cls_name}(__file__)

def get_builders() -> list[Callable[[], None]]:
    return [asset.workscene_builder]
    
def main() -> None:
    asset.hello()

    """

    def _get_pyproject_data(self, hatch_hooks_location: str = ""):

        data = super()._get_pyproject_data(hatch_hooks_location)
        # we declare our build plugin:
        eps = data["project"]["entry-points"]
        eps[f"tgzr.pipeline.asset.builder"] = {"buildes": f"{self.name}:get_builders"}

        return data

    def workscene_builder(self) -> Callable[[], None]:
        raise Exception("Builder not implemented on abstract Workscene!")
