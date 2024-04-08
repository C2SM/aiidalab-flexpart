import ipywidgets as widgets
from IPython.display import clear_output

from aiida.orm import QueryBuilder, RemoteStashFolderData, FolderData, load_node
from aiida import plugins
from utils import utils
from widgets import filter


coll_sens = plugins.CalculationFactory('collect.sens')
NetCDF = plugins.DataFactory('netcdf.data')

style = {'description_width': 'initial'}
ad_q = filter.ViewerWidget()

class SearchSens(widgets.VBox):
    def __init__(self):

        self.date_range = widgets.Text(
            value='2020-09-01--2020-12-31',
            description='Range_dates',
            disabled=False,
            style=style 
        ) 
        self.location = widgets.SelectMultiple(
            options=utils.fill_locations('/home/jovyan/apps/flexpart_aiidalab/config/locations.yaml'),
            description='Locations',
            description_tooltip = 'Multiple values can be selected with "Shift" and/or "ctrl"(or "command")',
            value=['JFJ_5magl'],
            rows = 12,
            style=style
        )
        self.domain = widgets.Dropdown(
            options=[
                     'EUROPE'
                     ],
            description='Domain:',
            ensure_option=True, 
            disabled=False, style=style
        )
        
        self.ind_title = widgets.HTML(
            value = """<hr>     
            """
        )
        search_crit = widgets.HBox([self.location,
                                    self.date_range,
                                    self.domain
                                    ])
        button = widgets.Button(description="Search")
        self.results = widgets.HTML()
        self.info_out = widgets.Output()

        def on_click(b):
            with self.info_out:
                clear_output()
                self.search() 
        button.on_click(on_click)
        
        
        super().__init__([
                          search_crit,  
                          self.ind_title,
                          ad_q,
                          button,
                          self.results, 
                          self.info_out,
                          self.ind_title,
                          ])
        
    def search(self):
        self.results.value = "searching..."
      
        qb = QueryBuilder()
        qb.append(NetCDF, 
          project=["attributes.filename", 
                   'id'],
          filters = {'attributes.global_attributes.domain' : "'EUROPE'"}
          )
       
        html = """<style>
        table, th, td {
            border: 1px solid;
            text-align: center;
            padding: 5px}</style>
        <table>
                <tr>
                    <th>id</th>
                    <th>Name</th>
                </tr>"""
        
        for i in qb.all():
            html += f'<tr><td>{i[1]}</td><td>{i[0]}</td></tr>'
        html+='</table>'
        
        self.results.value = html
   