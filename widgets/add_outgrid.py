# -*- coding: utf-8 -*-
import ipywidgets as widgets
from utils import utils

style = {"description_width": "initial"}


class AddOutgrid(widgets.HBox):

    text_info = widgets.HTML(
        """<ul>
               <li><b>output_grid_type</b>: 1 for coos provided in rotated system 0 for geographical.</li>
               <li><b>longitude_of_output_grid</b>: Longitude of lower left corner of output grid <br>(left boundary of the first grid cell - not its centre).</li>
               <li><b>latitude_of_output_grid</b>: Latitude of lower left corner of output grid  <br>(lower boundary of the first grid cell - not its centre).</li>
               <li><b>number_of_grid_points_x</b>: Number of grid points in x direction (= # of cells + 1).</li>
               <li><b>number_of_grid_points_y</b>: Number of grid points in y direction (= # of cells + 1).</li>
               <li><b>grid_distance_x</b>: Grid distance in x direction.</li>
               <li><b>grid_distance_y</b>: Grid distance in y direction.</li>
               <li><b>heights_of_levels</b>: List of heights of leves (upper boundary).</li>
            </ul>"""
    )

    def __init__(self):

        self.name = widgets.Text(description="Name", style=style)
        self.output_grid_type = widgets.Dropdown(
            description="Output grid type", options=[0, 1], value=0, style=style
        )
        self.longitude_of_output_grid = widgets.FloatText(
            description="Longitude", style=style
        )
        self.latitude_of_output_grid = widgets.FloatText(
            description="Latitude", style=style
        )
        self.number_of_grid_points_x = widgets.IntText(
            description="Number of grid points x", style=style
        )
        self.number_of_grid_points_y = widgets.IntText(
            description="Number of grid points y", style=style
        )
        self.grid_distance_x = widgets.FloatText(
            description="Grid distance x", style=style
        )
        self.grid_distance_y = widgets.FloatText(
            description="Grid distance y", style=style
        )
        self.heights_of_levels = widgets.Text(
            description="Heights of levels", placeholder="(upper boundary)", style=style
        )

        self.update_b = widgets.Button(
            description="Add",
            button_style="info",
        )

        def on_click(b):
            new_outgrid = {
                self.name.value: {
                    "output_grid_type": self.output_grid_type.value,
                    "longitude_of_output_grid": self.longitude_of_output_grid.value,
                    "latitude_of_output_grid": self.latitude_of_output_grid.value,
                    "number_of_grid_points_x": self.number_of_grid_points_x.value,
                    "number_of_grid_points_y": self.number_of_grid_points_y.value,
                    "grid_distance_x": self.heights_of_levels.value,
                    "grid_distance_y": self.heights_of_levels.value,
                    "heights_of_levels": self.heights_of_levels.value,
                }
            }
            utils.store_dictionary(new_outgrid, "outgrid")

        self.update_b.on_click(on_click)

        super().__init__(
            children=[
                widgets.VBox(
                    children=[
                        self.name,
                        self.output_grid_type,
                        self.longitude_of_output_grid,
                        self.latitude_of_output_grid,
                        self.number_of_grid_points_x,
                        self.number_of_grid_points_y,
                        self.grid_distance_x,
                        self.grid_distance_y,
                        self.heights_of_levels,
                        self.update_b,
                    ]
                ),
                self.text_info,
            ]
        ),
