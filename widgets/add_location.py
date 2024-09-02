# -*- coding: utf-8 -*-
import ipywidgets as widgets
from utils import utils
import re

style = {"description_width": "initial"}


def str_to_dict(s: str) -> dict:
    if s:
        return {i.split(" ")[0]: float(i.split(" ")[1]) for i in s.split(",")}
    return


output2 = widgets.Output()


class AddLocation(widgets.HBox):

    text_info = widgets.HTML(
        """<ul>
               <li><b>Release height</b>: in meters with respect to chosen release coordinate.<br>
               Different values for different input meteorologies can be given as a comma separated list<br>
              (e.g.: cosmo1 100,cosmo7 50)</li>
               <li><b>Release coordinate</b>:1 for meters above ground, 2 for meters above sea level.<br>
                                    Different values for different input meteorologies can be given as a comma separated list<br>
                                    (e.g.: cosmo1 2,cosmo7 1)</li>
            </ul>"""
    )
    warning_message = widgets.HTML("")

    def __init__(self):
        self.name = widgets.Text(description="Name", style=style)
        self.longitude = widgets.FloatText(description="Longitude", style=style)
        self.latitude = widgets.FloatText(description="Latitude", style=style)
        self.level = widgets.Text(
            description="Release height",
            style=style,
        )
        self.level_type = widgets.Text(description="Release coordinate", style=style)
        self.update_button = widgets.Button(
            description="Add",
            button_style="info",
        )

        def on_click(b):
            if (
                self.name.value in utils.get_names_in_group("locations")
                or self.name.value == ""
            ):
                self.warning_message.value = (
                    '<p style="color:red;">Name is empty or already exists</p>'
                )
            elif not re.search("\w+\s\d+", self.level.value) or not re.search(
                "\w+\s\d+", self.level_type.value
            ):
                self.warning_message.value = (
                    '<p style="color:red;">Releases not in the right format</p>'
                )

            else:
                new_loc = {
                    self.name.value: {
                        "longitude": self.longitude.value,
                        "latitude": self.latitude.value,
                        "level": str_to_dict(self.level.value),
                        "level_type": str_to_dict(self.level_type.value),
                    }
                }
                utils.store_dictionary(new_loc, group_label="locations")
                self.warning_message.value = ""

        self.update_button.on_click(on_click)

        super().__init__(
            children=[
                widgets.VBox(
                    children=[
                        self.name,
                        self.longitude,
                        self.latitude,
                        self.level,
                        self.level_type,
                        self.update_button,
                        self.warning_message,
                    ]
                ),
                self.text_info,
            ]
        ),
