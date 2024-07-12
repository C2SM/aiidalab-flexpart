# -*- coding: utf-8 -*-
import ipywidgets as widgets
from widgets import add_location
from utils import utils
from pathlib import Path
import yaml

style = {"description_width": "initial"}
layout = widgets.Layout(grid_template_columns="repeat(4, 25%)")

locations_yaml_path = Path.cwd() / "config" / "locations.yaml"
locations_groups_yaml_path = Path.cwd() / "config" / "location_groups.yaml"


class Locations(widgets.VBox):
    def __init__(self):

        # Creates the locations group and stores the default locations
        utils.initialize_group(locations_yaml_path, group_name="locations")

        with open(locations_groups_yaml_path) as finp:
            self.group_dict = yaml.safe_load(finp)
        self.locations_g_w = [
            widgets.Checkbox(description=g) for g in self.group_dict.keys()
        ]

        for group in self.locations_g_w:
            group.observe(self.enable_locations_in_group, names="value")

        self.locations_widget = widgets.GridBox(
            utils.generate_locations(), layout=layout
        )

        # Adds accordion for adding new location
        add_locations = add_location.AddLocation()
        add_locations.update_b.on_click(self.update_locations)
        acc = widgets.Accordion(
            children=[
                add_locations,
            ],
        )
        acc.set_title(0, "Add a new location")
        acc.selected_index = None

        self.children = [
            widgets.HTML(value="<b>ALL LOCATIONS</b>"),
            self.locations_widget,
            widgets.HTML(value="<hr><b>GROUPS</b>"),
            widgets.GridBox(self.locations_g_w, layout=layout),
            widgets.HTML(value="<hr>"),
            acc,
        ]
        super().__init__(children=self.children)

    def enable_locations_in_group(self, change=None):
        value = change["new"]
        group_name = change["owner"].description
        list_of_locations = set(self.group_dict[group_name])
        for location in self.locations_widget.children:
            if location.description in list_of_locations:
                location.value = value

    def update_locations(self, change=None):
        self.locations_widget.children = utils.generate_locations()

    def fill(self):
        return [x.description for x in self.locations_widget.children if x.value == True]
