from typing import Any, TYPE_CHECKING
import uuid

import solara

console_width = solara.reactive(80)


@solara.component_vue("getsize.vue")
def GetSize(ref_id=None, console_width=None, on_console_width=None, children=[], style={}):
    ...


if TYPE_CHECKING:
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model


@solara.component
def ShowHtml(obj: 'Dataset | Model', element_id: str, console_width: int, method_name: str, **kwargs: Any):
    obj.config.display.terminal.width = console_width
    obj.config.display.terminal.height = 400

    html_string = getattr(obj, method_name)(**kwargs)

    solara.HTML(tag='div', unsafe_innerHTML=f'<div id="{element_id}">{html_string}</div>')


@solara.component
def Page(obj: 'Dataset | Model', method_name: str, **kwargs: Any):
    element_id = f"html-size-{uuid.uuid4().hex}"

    ShowHtml(
        obj,
        element_id=element_id,
        console_width=console_width.value,
        method_name=method_name,
        **kwargs,
    )

    GetSize(
        ref_id=element_id,
        console_width=console_width.value,
        on_console_width=console_width.set,
    )

    solara.Markdown(f'The column size is: {console_width.value}')


# Page(dataset, view=True)
