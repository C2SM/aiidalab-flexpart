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

        self._parameter_selection = ipw.Dropdown(
            options=fill_locations(),
            description="Parameter:",
            disabled=False,
            style={"description_width": "auto"},
            layout=ipw.Layout(width="350px"),
        )

        self._value = ipw.Text(
            value="0",
            description="Value:",
            disabled=False,
            style={"description_width": "auto"},
            layout=ipw.Layout(width="150px"),
        )

        super().__init__(
            children=[
                self._parameter_selection,
                self._value,
            ]
        )


class _BaseStackWidget(stack.VerticalStackWidget):
    data = tl.Dict(allow_none=True)
    options = tl.Union([tl.Dict(), tl.List()], allow_none=True)

    def add_item(self, _):
        self.items += (
            self.item_class(
                color="black",
                factor=1.0,
            ),
        )
        tl.dlink((self, "options"), (self.items[-1], "options"))
        tl.dlink((self, "data"), (self.items[-1], "data"))


class ViewerWidget(ipw.VBox):
    def __init__(self):
        self.parameters = _BaseStackWidget(
            item_class=_BaseSelectionWidget, add_button_text="Add parameter"
        )
        super().__init__([self.parameters])
