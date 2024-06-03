import ipywidgets as widgets
from utils import utils
from pathlib import Path

style = {"description_width": "initial"}
path_to_out = Path.cwd() / "config" / "outgrid.yaml"


class Outgrid(widgets.VBox):
    def __init__(self):
        utils.initialize_group(path_to_out, group_name="outgrid")
        self.out_loc = utils.generate_outgrids_buttons(outgrid_nest=False)
        self.children = [self.out_loc]
        super().__init__(children=self.children)

    def selected_outgrid(self):
        selected = self.children[0].value
        return selected
