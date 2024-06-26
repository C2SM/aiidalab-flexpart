import ipywidgets as widgets
from utils import utils

style = {"description_width": "initial"}


def str_to_dict(s: str) -> dict:
    if s:
        d = {}
        for i in s.split(","):
            d[i.split(" ")[0]] = float(i.split(" ")[1])
        return d
    return None


class AddLocation(widgets.VBox):

    rel_h_info = widgets.HTML(
        """Release height in meters with respect to chosen release coordinate.<br>
              Different values for different input meteorologies can be given as a comma separated list <br>
              (e.g.: cosmo1 100, cosmo7 50)
                """
    )

    rel_coor_info = widgets.HTML(
        """1 for meters above ground, 2 for meters above sea level.<br>
                                    Different values for different input meteorologies can be given as a comma separated list<br>
                                    (e.g.: cosmo1 2, cosmo7 1)"""
    )

    def __init__(self):
        self.name = widgets.Text(description="Name", style=style)
        self.longitude = widgets.FloatText(description="Longitude", style=style)
        self.latitude = widgets.FloatText(description="Latitude", style=style)
        self.level = widgets.Text(
            description="Release height",
            style=style,
        )
        self.level_type = widgets.Text(description="Release coordinate", style=style)
        self.update_b = widgets.Button(
            description="Add",
            button_style="info",
        )

        def on_click(b):
            new_loc = {
                self.name.value: {
                    "longitude": self.longitude.value,
                    "latitude": self.latitude.value,
                    "level": str_to_dict(self.level.value),
                    "level_type": str_to_dict(self.level_type.value),
                }
            }
            utils.store_dictionary(new_loc, group_label="locations")

        self.update_b.on_click(on_click)

        super().__init__(
            children=[
                self.name,
                self.longitude,
                self.latitude,
                self.rel_h_info,
                self.level,
                self.rel_coor_info,
                self.level_type,
                self.update_b,
            ]
        ),
