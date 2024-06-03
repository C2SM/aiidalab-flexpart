import ipywidgets as widgets
from utils import utils
from pathlib import Path

style = {"description_width": "initial"}
path_to_out = Path.cwd() / "config" / "outgrid.yaml"


class OutgridNest(widgets.VBox):
    def __init__(self):
        self.out_loc = utils.generate_outgrids_buttons(outgrid_nest=True)
        self.children = [self.out_loc]
        super().__init__(children=self.children)

    def selected_outgrid_nest(self):
        selected = self.children[0].value
        return selected
