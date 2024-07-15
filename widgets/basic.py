# -*- coding: utf-8 -*-
import ipywidgets as widgets
from widgets import locations, outgrid
from pathlib import Path
from utils import utils

style = {"description_width": "initial"}
box_layout = widgets.Layout(box_layout="padding 200px")
models_path = Path.cwd() / "config" / "models.yaml"


class Basic(widgets.VBox):
    def __init__(self):

        self.simulation_dates = widgets.Text(
            value="2020-10-01",
            description="Simulation dates",
            tooltip ='Format for one day: YYYY-MM-DD, for a range of dates use "--" and for a list of dates ",". Example: 2021-01-02--2021-01-10.',
            style=style,
        )
        self.model = widgets.Dropdown(
            options=utils.read_yaml_data(models_path)["models"],
            description="Model",
            ensure_option=True,
            style=style,
        )
        self.model_offline = widgets.Dropdown(
            options=utils.read_yaml_data(models_path)["models_offline"],
            description="Model offline",
            ensure_option=True,
            style=style,
        )
        self.model_offline.observe(self.change_to_zero_off_time, names="value")
        self.integration_time = widgets.IntText(
            value=24,
            description="Integration time",
            description_tooltip="Hours",
            style=style,
        )
        self.offline_integration_time = widgets.IntText(
            value=48,
            description="Offline integration time",
            description_tooltip="Hours. Zero if model offline is none.",
            style=style,
        )
        self.release_chunk = widgets.IntText(
            value=10800,
            description="Release chunk",
            description_tooltip="Seconds",
            style=style,
        )
        self.locations = locations.Locations()
        self.outgrid = outgrid.Outgrid()

        acc_loc = widgets.Accordion(children=[self.locations])
        acc_loc.set_title(0, "Locations")
        acc_loc.selected_index = 0

        self.children = [
            widgets.VBox(
                children=[
                    self.simulation_dates,
                    widgets.HTML(value="<hr>"),
                    widgets.HBox(
                        children=[
                            widgets.VBox(children=[self.model, self.integration_time]),
                            widgets.VBox(
                                children=[
                                    self.model_offline,
                                    self.offline_integration_time,
                                ]
                            ),
                            widgets.VBox(
                                children=[
                                    self.release_chunk,
                                ]
                            ),
                        ]
                    ),
                    widgets.HTML(value="<hr>"),
                ]
            ),
            widgets.VBox(
                children=[
                    acc_loc,
                    self.outgrid,
                ],
                layout=box_layout,
            ),
        ]

        super().__init__(children=self.children, layout=box_layout)

    def change_to_zero_off_time(self, change=None):
        if change["new"] == "None":
            self.offline_integration_time.value = 0
