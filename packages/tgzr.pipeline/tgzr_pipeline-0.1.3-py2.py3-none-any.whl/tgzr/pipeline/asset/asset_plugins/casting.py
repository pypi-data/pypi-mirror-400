from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..asset import ToolAsset, AssetTypeInfo

if TYPE_CHECKING:
    from tgzr.pipeline.workspace import Workspace


class Casting(ToolAsset):
    ASSET_TYPE_INFO = AssetTypeInfo(
        category="tool",
        color="#79716b",
        icon="build",
    )

    def get_outputs(self) -> list[Any]:
        print("????")
        casted_assets = []
        for name, asset in self.get_input_assets().items():
            casted_assets.extend(asset.get_outputs())
        return casted_assets

    def nice_panel_names(self) -> list[str]:
        return ["summary_panel"]

    def summary_panel(self, workspace: Workspace):
        from nicegui import ui

        nodes = [
            dict(
                label="Assets",
                children=[
                    dict(
                        label="Chars",
                        value=2,
                        children=[
                            dict(label="Alice", value="==1.2.3", children=[]),
                            dict(label="Bob", value=None, children=[]),
                        ],
                    ),
                    dict(
                        label="Sets",
                        children=[
                            dict(label="Kitchen", children=[]),
                        ],
                    ),
                ],
            ),
            dict(
                label="Data",
                children=[
                    dict(label="has_hair", value=True, children=[]),
                    dict(label="uv_set_name", value="default", children=[]),
                    dict(label="force_blessed", value=False, children=[]),
                ],
            ),
        ]

        # with ui.column().classes("p-4 gap-0"):
        header = ui.row(align_items="center").classes("gap-0 w-full")
        tree = ui.tree(nodes, node_key="label").classes("w-full")
        tree.add_slot(
            "default-header",
            """
            <span :props="props">{{ props.node.label }} : {{ props.node.value }}</span>
            """,
        )

        with header:
            ui.label("✨ Casting Summary ✨")
            ui.space()
            ui.button(icon="sym_o_expand_content", on_click=tree.expand).tooltip(
                "Expand"
            ).props("dense flat")
            ui.button(icon="sym_o_collapse_content", on_click=tree.collapse).tooltip(
                "Expand"
            ).props("dense flat")
