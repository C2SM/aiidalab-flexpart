import ipywidgets as widgets
from widgets import (locations, 
                     outgrid, 
                     outgrid_nest
                     )

style = {'description_width': 'initial'}
box_layout = widgets.Layout(box_layout = 'padding 200px')

class Basic(widgets.VBox):
    def __init__(self):

        self.line = widgets.HTML(
            value="<hr>"
        )
        self.out_title = widgets.HTML(
            value="<b>Outgrid</b>"
        )
        self.out_n_title = widgets.HTML(
            value="<b>Outgrid nest</b>"
        )
        self.simulation_dates = widgets.Text(
            value='2020-10-01',
            description='Simulation dates',
            description_tooltip = 'Format for one day: YYYY-MM-DD, for a range of dates use "--" and for a list of dates ",". Example: 2021-01-02--2021-01-10.',
            disabled=False,style=style 
        ) 
        self.model = widgets.Dropdown(
            options=[
                     'cosmo7',
                     'cosmo2',
                     'cosmo1',
                     'kenda1',
                     'cosmo7,cosmo1',
                     'cosmo7,cosmo2',
                     'cosmo7,kenda1',
                     'IFS_GL_1',
                     'IFS_GL_05',
                     'IFS_EU_02',
                     'IFS_EU_01',
                     'IFS_GL_1,IFS_EU_02',
                     'IFS_GL_05,IFS_EU_01'
                     ],
            description='Model',
            ensure_option=True,
            disabled=False,style=style
        )
        self.model_offline = widgets.Dropdown(
            options=[
                     'IFS_GL_1',
                     'IFS_GL_05',
                     'IFS_EU_02',
                     'IFS_EU_01',
                     'IFS_GL_1,IFS_EU_02',
                     'IFS_GL_05,IFS_EU_01',
                     'None'
                     ],
            description='Model offline',
            ensure_option=True,
            disabled=False,style=style
        )
        self.model_offline.observe(self.change_to_zero_off_time,names = 'value')
        self.integration_time = widgets.IntText(
            value=24,
            description='Integration time',
            description_tooltip = 'Hours',
            disabled=False,style=style
        )
        self.offline_integration_time = widgets.IntText(
            value=48,
            description='Offline integration time',
            description_tooltip = 'Hours. Zero if model offline is none.',
            disabled=False,style=style
        )
        self.release_chunk = widgets.IntText(
            value=10800,
            description='Release chunk',
            description_tooltip = 'Seconds',
            disabled=False,style=style
        )
        self.locations = locations.Locations()
        self.outgrid = outgrid.Outgrid()
        self.outgrid_nest = outgrid_nest.OutgridNest()

        acc = widgets.Accordion(children=[self.locations,
                                        ], 
                               )
        acc.set_title(0,'Locations')
        acc.selected_index = None
                                  
        self.children = [
                    widgets.VBox(children=[
                                  self.simulation_dates,
                                  self.line,

                                  widgets.HBox(children=[
            
                                        widgets.VBox(children=[
                                                        self.model,
                                                        self.integration_time
                                                        ]
                                             ),
                                        widgets.VBox(children=[
                                                       self.model_offline,
                                                       self.offline_integration_time,
                                                        ]
                                             ),
                                        widgets.VBox(children=[
                                                        self.release_chunk,
                                                        ]
                                             ),
                                                ]
                                        ),
                                    self.line,
                        ]),
                    widgets.VBox(children=[
                                   acc,
                                   self.out_title,
                                   self.outgrid,
                                   self.out_n_title,
                                   self.outgrid_nest

                        ],
                         layout = box_layout)
                    ]

        super().__init__(children = self.children,
                         layout = box_layout
                         )
    def change_to_zero_off_time(self, change=None):
        if change["new"] == 'None':
            self.offline_integration_time.value = 0