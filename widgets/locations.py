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

    groups_title = widgets.HTML(value="<hr><b>GROUPS</b>")
    ind_title = widgets.HTML(value="<b>ALL LOCATIONS</b>")
    hr = widgets.HTML(value="<hr>")

    def __init__(self):
        utils.initialize_group(locations_yaml_path, group_name="locations")
        with open(locations_groups_yaml_path) as finp:
            self.group_dict = yaml.safe_load(finp)
        self.locations_g_w = [
            widgets.Checkbox(description=g) for g in self.group_dict.keys()
        ]
        for group in self.locations_g_w:
            group.observe(self.enable_locations_in_group, names="value")

        self.locations_w = utils.generate_locations(locations_yaml_path)

        add_locations = add_location.AddLocation()
        add_locations.update_b.observe(self.update_locations)

        acc = widgets.Accordion(
            children=[
                add_locations,
            ],
        )
        acc.set_title(0, "Add a new location")
        acc.selected_index = None

        self.children = [
            self.ind_title,
            widgets.GridBox(self.locations_w, layout=layout),
            self.groups_title,
            widgets.GridBox(self.locations_g_w, layout=layout),
            self.hr,
            acc,
        ]
        super().__init__(children=self.children)

    def enable_locations_in_group(self, change=None):
        value = change["new"]
        group_name = change["owner"].description
        list_of_locations = set(self.group_dict[group_name])
        for location in self.locations_w:
            if location.description in list_of_locations:
                location.value = value

    def update_locations(self, change=None):
        self.locations_w += utils.generate_locations(locations_yaml_path)

    def fill(self):
        return [x.description for x in self.locations_w if x.value == True]
