import ipywidgets as widgets
from utils import utils
from pathlib import Path
import yaml

style = {'description_width': 'initial'}
locations_yaml_path = Path.cwd() / 'config' / 'locations.yaml'

def update_locations(new_loc):
    with open(locations_yaml_path, 'r') as f:
        d = yaml.safe_load(f)
        d.update(new_loc)

    with open(locations_yaml_path, 'w') as f:
        yaml.dump(d, f)

def str_to_dict(s):
    d  = {}
    for i in s.split(','):
        d[i.split(' ')[0]] = float(i.split(' ')[1])
    return d

class AddLocation(widgets.HBox):
    def __init__(self):
        self.name = widgets.Text(
            description='Name',
            style=style 
        ) 
        self.longitude =  widgets.FloatText(description='Longitude',style=style)
        self.latitude = widgets.FloatText(description='Latitude',style=style)
        self.level =widgets.Textarea(
            description='Level',
            style=style,
            tooltip = """Example format: 
                         cosmo1 1,cosmo7 2"""
        ) 
        self.level_type =  widgets.Textarea(
            description='Level type',
            style=style 
        ) 
        self.update_b = widgets.Button(
            value=False,
            description='Add',
            button_style="info",
            )
        
        def on_click(b):
            #{v:k for v,k in }
            new_loc = {self.name.value:
                        {'longitude':self.longitude.value,
                         'latitude':self.latitude.value,
                         'level':str_to_dict(self.level.value),
                         'level_type':str_to_dict(self.level_type.value)
                         }
                        }
            update_locations(new_loc)

        self.update_b.on_click(on_click)

        text_info = widgets.HTML(""" To <b>delete or modify</b> an existing location,<br>
                                     Click on File Manager (in the home page) and navigate to:<br>
                                     <i>apps/flexpart_aiidalab/config/locations.yaml </i><br><br>
                                     Format example for level and level type:<br>
                                     cosmo1 2,cosmo7 2
                                                
                                 """)
        super().__init__(children = [
                                     widgets.VBox(children=[self.name,
                                                  self.longitude,
                                                  self.latitude,
                                                  self.level,
                                                  self.level_type,
                                                  self.update_b
                                                  ]),
                                     text_info
        ])