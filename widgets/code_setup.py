# -*- coding: utf-8 -*-
import ipywidgets as widgets
import aiidalab_widgets_base as awb
from utils import utils
import pathlib
path_to_default_codes = pathlib.Path.cwd() /'utils'/ "default_codes.yaml"

class CodeSetup(widgets.VBox):

    def __init__(self, plugin_name: str, new_code=False):

        comp_res = awb.ComputationalResourcesWidget()
        self.codes = widgets.Dropdown(
            description="code",
            options=utils.codes_list() + ["None"],
            value=utils.fix_values(plugin_name),
            style={"description_width": "initial"},
        )
        self.stash_address = widgets.Text(
            description="Stash Address",
            value=utils.read_yaml_data(path_to_default_codes, names=['stash_address'])['stash_address'],
            style={"description_width": "initial"},
            layout=widgets.Layout(width="40%"),
        )
        self.account = widgets.Text(
            description="account",
            value = 'em05',
            style = {"description_width": "initial"},
        )
        self.wall_time = widgets.IntText(
            description="wall time",
            value = 1800,
            style = {"description_width": "initial"},
        )
        self.default_button = widgets.Button(
            description="Save as default", button_style="info"
        )

        if new_code:
            comp_res.code_select_dropdown.layout.visibility = "hidden"

        def on_click(b):
            utils.update_codes(
                {
                    plugin_name: self.codes.value,
                    "stash_address": self.stash_address.value,
                }
            )

        self.default_button.on_click(on_click)

        self.children = [
            widgets.VBox(
                children=[comp_res] * new_code
                + [widgets.HBox(children=[self.codes,self.stash_address,self.default_button]*(not new_code) )]
                + [widgets.HBox(children=[self.account,self.wall_time]*(not new_code) )]
            ),
        ]

        super().__init__(children=self.children)
