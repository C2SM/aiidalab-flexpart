import ipywidgets as widgets
from utils import utils
from pathlib import Path

style = {"description_width": "initial"}
path_test = Path.cwd() / "config/input_phy.yaml"


class InputPhy(widgets.VBox):
    def __init__(self):

        self.params = utils.fill(path_test)
        super().__init__(children=self.params)

    def fill_dict(self):
        return {parameter.description: parameter.value for parameter in self.params}

    def update(self, dict_):
        for param in self.params:
            if param.description in dict_:
                param.value = dict_[param.description]
