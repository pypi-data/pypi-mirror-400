from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any, Iterable

from ..asset import ToolAsset, AssetTypeInfo

if TYPE_CHECKING:
    from tgzr.pipeline.workspace import Workspace


class Builder(ToolAsset):
    ASSET_TYPE_INFO = AssetTypeInfo(
        category="builder",
        color="#79716b",
        icon="build",
    )
    PLUGIN_GROUP = "tgzr.pipeline.asset.builder"

    @classmethod
    def default_dinit_content(cls) -> str:
        # TODO: this could totally be done in the Asset class !!!!!
        cls_module = cls.__module__
        cls_name = cls.__name__

        return f"""
from {cls_module} import {cls_name}

asset = {cls_name}(__file__)

def build()->None:
    asset.build()
    
def main() -> None:
    asset.hello()

    """

    def _get_pyproject_data(self, hatch_hooks_location: str = ""):

        data = super()._get_pyproject_data(hatch_hooks_location)
        # we declare the plugins we consume:
        eps = data["project"]["entry-points"]
        eps[f"tgzr.pipeline.plugin_groups"] = {"builder": self.PLUGIN_GROUP}
        scripts = data["project"]["scripts"]
        scripts["tgzr.pipeline.asset.build"] = f"{self.name}:build"

        return data

    def build(self) -> Callable[[], None]:
        plugins, error = self.get_plugins(self.PLUGIN_GROUP)
        raise Exception(
            f"Builder not implemented on abstract Workscene! (found plugins though: {plugins}, {error})"
        )

    def nice_panel_names(self) -> list[str]:
        return ["_options_panel", "help_panel"]

    def _options_panel(self, workspace: Workspace):
        from nicegui import ui

        class ValueField:
            _ALL: list[ValueField] = []

            @classmethod
            def all(cls) -> Iterable[tuple[str, ValueField]]:
                return [(f.name, f) for f in cls._ALL]

            def __init__(self, name: str, value, editable: bool) -> None:
                self._ALL.append(self)
                self.name = name
                self.value = value
                self.editable = editable
                self._input = None
                self._box = ui.row().classes("w-full")
                self.render()

            def save(self):
                print("   SAVING", self.name, self.value)
                self.value = self._input.value

            def toggle(self):
                if self.editable:
                    self.save()
                    self.editable = False
                else:
                    self.editable = True
                self.refresh()

            def refresh(self):
                self._box.clear()
                self.render()

            def render(self):
                with self._box:
                    if self.editable:
                        self._input = (
                            ui.number(
                                value=self.value,
                                min=1,
                                max=100,
                            )
                            .classes("w-full")
                            .props("dense rounded standout")
                            .on(
                                "mousedown",
                                js_handler="(e)=>{console.log(e); e.stopPropagation()}",
                            )
                        )
                    else:
                        self._input = None
                        ui.label(self.value)

        def toggle():
            editable = None
            for name, field in ValueField.all():
                field.toggle()
                editable = field.editable
            if editable:
                btn.set_icon("sym_o_save")
            else:
                btn.set_icon("sym_o_edit")

        data = self.read_asset_data()
        with ui.grid(columns="auto 1fr"):
            for i, name in enumerate(data.package.inputs):
                with ui.row(align_items="center").classes("w-full min-w-[2em]"):
                    with ui.column(align_items="end").classes("w-full"):
                        ui.label(name + ":")
                ValueField(name, i, editable=False)

        if workspace.has_editable_asset(self.name):
            with ui.column(align_items="end").classes("w-full"):
                btn = ui.button(icon="sym_o_edit", on_click=toggle).props(
                    "flat dense outlined"
                )

    def help_panel(self, workspace: Workspace):
        from nicegui import ui

        # NB: You need too space at the end of a line to have a line break in the markdown!
        ui.markdown(
            """
            ### Builder
            They build your Workscenes.

            Connect `Assets` and/or `Castings` to the `Builder`.  
            Connect the **Builder** to a `Workscene`.  
            Click the "Edit" button on the `Workscene`  
            - ➡️ The scene will be built by the Builder if it does not exists ✨

            ```mermaid
            ---
            config:
                theme: 'dark'
            ---
            flowchart LR;
                BOB@{ shape: stadium, label: "Char_Bob..." } --> MP@{ shape: stadium, label: "MainPack..." };
                ALICE@{ shape: stadium, label: "Char_Alice..." } --> MP;
                MP-->B@{ shape: stadium, label: "Builder..." };
                KITCHER@{ shape: stadium, label: "Set_Kitchen..." }-->B;
                GLASS@{ shape: stadium, label: "Props_Glass..." }-->B;
                B-->ANIM@{ shape: stadium, label: "Anim_Workscene....." };
            ```

            > Notes:  
            > Some Builders may support updating the scene too.  
            > In this case, the scene will be updated when a new  
            > version of an upstream asset was installed.  


            """,
            extras=["mermaid"],
        )  # .classes("text-xs")
