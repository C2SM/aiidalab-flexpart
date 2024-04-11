import ipywidgets as widgets
import aiidalab_widgets_base as awb
from aiida import orm
from utils import utils
from pathlib import Path
import yaml

style = {'description_width': 'initial'}
path_to_default_codes = Path.cwd() / 'utils' / 'default_codes.yaml'

def codes_list():
    return [awb.ComputationalResourcesWidget._full_code_label(c[0]) 
 for c in orm.QueryBuilder()
 .append(orm.Code).all() 
]

def fix_values(name):
    return utils.read_yaml_data(path_to_default_codes,
                                 names =[name])[name]
    
class Misc(widgets.VBox):
    def __init__(self):

        self.prepend_text = widgets.Textarea(
            value = 'export OMP_NUM_THREADS=36\n',
            description='Prepend text:',
            ensure_option=True,
            disabled=False,style=style
        )
        self.wall_time_cosmo = widgets.IntText(
            value=1800,
            description='Wall time cosmo:',
            disabled=False,style=style
        )
        self.wall_time_ifs = widgets.IntText(
            value=1800,
            description='Wall time ifs:',
            disabled=False,style=style
        )
        comp_res = awb.ComputationalResourcesWidget()
        comp_res.code_select_dropdown.layout.visibility = "hidden"

        self.f_cosmo_code = widgets.Dropdown(description = 'cosmo',
                                      options = codes_list(),
                                      value = fix_values('cosmo'),
                                      style = style
                                      )
        self.f_ifs_code = widgets.Dropdown(description = 'ifs',
                                      options = codes_list(),
                                      value = fix_values('ifs'),
                                      style = style
                                      )
        self.f_post_code = widgets.Dropdown(description = 'post',
                                       options = codes_list(),
                                       value = fix_values('post'),
                                       style=style) 
        self.ifs_m_code = widgets.Dropdown(description = 'ifs_meteo',
                                       options = codes_list(),
                                       value = fix_values('ifs_meteo'),
                                       style=style)
        self.cosmo_m_code = widgets.Dropdown(description = 'cosmo_meteo',
                                       options = codes_list(),
                                       value = fix_values('cosmo_meteo'),
                                       style=style)
        self.collect_sens_code = widgets.Dropdown(description = 'collect_sens',
                                       options = codes_list(),
                                       value = fix_values('collect_sens'),
                                       style=style)
              
        button = widgets.Button(description="Make default",button_style="info")

        def on_click(b):
            d = {self.f_ifs_code.description: self.f_ifs_code.value,
                 self.f_post_code.description: self.f_post_code.value,
                 self.cosmo_m_code.description: self.cosmo_m_code.value,
                 self.ifs_m_code.description: self.ifs_m_code.value,
                 self.f_cosmo_code.description: self.f_cosmo_code.value,
                 self.collect_sens_code.description: self.collect_sens_code.value,
                 } 
            with open(path_to_default_codes, 'w') as f:
                yaml.dump(d, f) 

        button.on_click(on_click)

        self.codes_title = widgets.HTML(
            value = "<hr><b>Code selection</b>",
        )
        self.new_code_title = widgets.HTML(
            value = """<hr><b>Create new codes</b><br>
                       Click on the button below to create and setup new codes
                       and or computers.""",
        )

        self.children = [
                         self.wall_time_cosmo,
                         self.wall_time_ifs,
                         self.prepend_text,

                         self.codes_title,
                         self.f_cosmo_code,
                         self.cosmo_m_code,
                         self.f_ifs_code,
                         self.ifs_m_code,
                         self.f_post_code,
                         self.collect_sens_code,
                         button,

                         self.new_code_title,
                         comp_res
                    ]

        super().__init__(children = self.children)