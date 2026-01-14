from __future__ import annotations

from collections.abc import Sequence
import os
from typing import TYPE_CHECKING, Literal

from gradio.components.base import Component
from gradio.data_classes import FileData
from gradio.events import Events

if TYPE_CHECKING:
    from gradio.components import Timer
    from gradio.i18n import I18nData


class Tiff(Component):
    """
    A component for Multipage TIFF images.
    """

    EVENTS = [Events.clear, Events.change, Events.upload]
    data_model = FileData

    def __init__(
        self,
        value: str | None = None,
        *,
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        show_download_button: bool = True,
        container: bool = True,
        scale: int | None = None,
        interactive: bool | None = None,
        visible: bool | Literal["hidden"] = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
    ):        
        """
        Parameters:
            value: A path or URL to the TIFF image.
            label: the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            show_download_button: If True, shows a button to download the original TIFF file.
            container: if True, will place the component in a container - providing some extra padding around the border.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            interactive: if True, will allow users to upload and edit an image; if False, can only be used to display images. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden. If "hidden", component will be visually hidden and not take up space in the layout but still exist in the DOM
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.show_download_button = show_download_button
        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )

    def preprocess(self, payload: FileData | None) -> str | None:
        """
        Extracts the file path for the Python function.
        """
        if payload is None:
            return None
        return payload.path

    def postprocess(self, value: str | None) -> FileData | None:
        """
        Accepts a file path or URL and packages it for the frontend.

        Ensures that a valid URL is generated for local files so the frontend can fetch them via the Gradio server.
        """
        if not value:
            return None

        # Check if the value is already a remote URL (e.g. for examples)
        if value.lower().startswith(("http://", "https://")):
            return FileData(path=value, url=value)

        # For local files, we must construct a URL that Gradio can serve via /file=
        try:
            filename = os.path.basename(value)
        except Exception:
            filename = "image.tiff"

        return FileData(path=value, url=f"/file={value}", orig_name=filename)

    def example_payload(self):
        return {
            "path": "https://raw.githubusercontent.com/NiklasvonM/Gradio-TIFF/main/demo/data/sample.tiff",
            "orig_name": "sample.tiff",
        }

    def example_value(self):
        return "https://raw.githubusercontent.com/NiklasvonM/Gradio-TIFF/main/demo/data/sample.tiff"
