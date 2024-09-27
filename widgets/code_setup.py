# -*- coding: utf-8 -*-
import ipywidgets as widgets
import aiidalab_widgets_base as awb
from utils import utils


class CodeSetup(widgets.VBox):
    new_code_title = widgets.HTML(
        value="""<hr><b>Create new codes</b><br>
                       Click on the button below to create and setup new codes
                       and or computers.""",
    )

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
            value=utils.fix_values("stash_address"),
            style={"description_width": "initial"},
            layout=widgets.Layout(width="40%"),
        )
        # self.codes.observe()
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
            self.new_code_title,
            widgets.HBox(
                children=[comp_res] * new_code
                + [self.codes, self.default_button, self.stash_address] * (not new_code)
            ),
        ]

        super().__init__(children=self.children)
