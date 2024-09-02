# -*- coding: utf-8 -*-
import ipywidgets as widgets
from utils import utils
from pathlib import Path
from widgets import add_outgrid

style = {"description_width": "initial"}
path_to_out = Path.cwd() / "config" / "outgrid.yaml"


class Outgrid(widgets.VBox):
    def __init__(self):
        # Create outgrid group and store default outgrids
        utils.initialize_group(path_to_out, group_name="outgrid")

        # Generate list of outgrid & outgrid_nest widgets
        self.out_loc = utils.generate_outgrids_buttons(outgrid_nest=False)
        self.out_n_loc = utils.generate_outgrids_buttons(outgrid_nest=True)

        # Add outgrid tab
        add_outgrids = add_outgrid.AddOutgrid()
        add_outgrids.update_button.on_click(self.update_outgrids)
        acc_out = widgets.Accordion(children=[add_outgrids])
        acc_out.set_title(0, "Add a new outgrid")
        acc_out.selected_index = None

        self.children = [
            widgets.HTML(value="<b>Outgrid</b>"),
            self.out_loc,
            widgets.HTML(value="<b>Outgrid nest</b>"),
            self.out_n_loc,
            widgets.HTML(value="<br>"),
            acc_out,
        ]
        super().__init__(children=self.children)

    def selected_outgrid(self):
        return self.out_loc.value

    def selected_outgrid_nest(self):
        return self.out_n_loc.value

    # TODO tooltips missing
    def update_outgrids(self, change=None):
        self.out_loc.options = utils.generate_outgrids_buttons(
            outgrid_nest=False
        ).options
        self.out_n_loc.options = utils.generate_outgrids_buttons(
            outgrid_nest=True
        ).options
