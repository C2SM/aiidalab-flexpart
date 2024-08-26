# -*- coding: utf-8 -*-
from . import stack
import traitlets as tl
import ipywidgets as ipw
from utils import utils
from pathlib import Path

command_yaml_path = Path.cwd() / "config" / "command.yaml"
input_yaml_path = Path.cwd() / "config" / "input_phy.yaml"
release_yaml_path = Path.cwd() / "config" / "release.yaml"


def fill_locations():
    command = list(utils.read_yaml_data(command_yaml_path).keys())
    input_phy = list(utils.read_yaml_data(input_yaml_path).keys())
    release = list(utils.read_yaml_data(release_yaml_path).keys())
    return command + input_phy + release


def make_query(list_parameters: list) -> list:
    return ["attributes." + i for i in list_parameters]


class _BaseSelectionWidget(stack.HorizontalItemWidget):
    data = tl.Dict(allow_none=True)
    options = tl.Union([tl.Dict(), tl.List()], allow_none=True)

    def __init__(self, **kwargs):
        self.mode = kwargs.get("mode")
        self._parameter_selection = ipw.Dropdown(
            options=fill_locations(),
            description="Parameter:",
            style={"description_width": "auto"},
            layout=ipw.Layout(width="350px"),
        )

        self.filter_selection = ipw.Dropdown(
            options=["TT", "PP", "WS", "WD", "PBLH", "hour"],
            description="column",
            style={"description_width": "auto"},
            layout=ipw.Layout(width="100px"),
        )

        self._value = ipw.Text(
            value="0",
            description="Value:",
            disabled=False,
            style={"description_width": "auto"},
            layout=ipw.Layout(width="150px"),
        )

        self.min = ipw.IntText(
            description="min",
            value=0,
        )
        self.max = ipw.IntText(description="max", value=0)
        self.vals = ipw.Text(description="vals", value="[]")

        params_conf = [
            self._parameter_selection,
            self._value,
        ]

        filter_conf = [self.filter_selection, self.min, self.max, self.vals]

        if self.mode == "filter":
            children = filter_conf
        else:
            children = params_conf
        super().__init__(children=children)


class _BaseStackWidget(stack.VerticalStackWidget):
    data = tl.Dict(allow_none=True)
    options = tl.Union([tl.Dict(), tl.List()], allow_none=True)

    def add_item(self, _):
        self.items += (self.item_class(color="black", factor=1.0, mode=self.mode),)
        tl.dlink((self, "options"), (self.items[-1], "options"))
        tl.dlink((self, "data"), (self.items[-1], "data"))


class ViewerWidget(ipw.VBox):
    def __init__(self, mode):
        self.mode = mode
        if self.mode == "params":
            self.parameters = _BaseStackWidget(
                item_class=_BaseSelectionWidget,
                add_button_text="Add parameter",
                mode="params",
            )
        else:
            self.parameters = _BaseStackWidget(
                item_class=_BaseSelectionWidget,
                add_button_text="Add filter",
                mode="filter",
            )
        super().__init__([self.parameters])
