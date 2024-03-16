import ipywidgets as widgets
from IPython.display import clear_output

from aiida.orm import QueryBuilder, RemoteStashFolderData, FolderData, load_node
from aiida import plugins
from utils import utils
from widgets import filter


coll_sens = plugins.CalculationFactory('collect.sens')

style = {'description_width': 'initial'}
ad_q = filter.ViewerWidget()

class SearchSens(widgets.VBox):
    def __init__(self):

        self.date_range = widgets.Text(
            value='2020-09-01--2020-12-31',
            placeholder='range_dates',
            description='range_dates',
            disabled=False,
            style=style 
        ) 
        self.location = widgets.Dropdown(
            placeholder='Choose location',
            options=utils.fill_locations('/home/jovyan/apps/flexpart_aiidalab/config/locations.yaml'),
            description='location:',
            value='JFJ_5magl',
            disabled=False,
            style=style
        )
        self.model = widgets.Dropdown(
            placeholder='model',
            options=[
                     'cosmo7',
                     'cosmo1',
                     'kenda1',
                     'IFS_GL_1',
                     'IFS_GL_05',
                     'IFS_EU_02',
                     'IFS_EU_01',
                     ],
            description='model:',
            ensure_option=True, 
            disabled=False,style=style
        )
        
        self.ind_title = widgets.HTML(
            value = """<hr>     
            """
        )
        search_crit = widgets.HBox([self.date_range,
                                    self.location, 
                                    self.model
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

        #list of dates
        list_dates=[]
        date_range_p = utils.simulation_dates_parser([self.date_range.value])
        for i in date_range_p:
             list_dates.append({'like':'remote__'+i[:10].replace('-','_')+self.location.value})
      
        qb = QueryBuilder()
        qb.append(coll_sens, tag='sens',filters={'attributes.exit_status': 0}, project= ['id'])
        qb.append(RemoteStashFolderData, with_outgoing='sens',    
                  edge_filters={'label':{'or':list_dates}},
                 )
        qb.append(FolderData, with_incoming='sens', project='id')
       
        html = """<style>
        table, th, td {
            border: 1px solid;
            text-align: center;}</style>
        <table>
                <tr>
                    <th>id</th>
                    <th>Folder Data</th>
                    <th>Output</th>

                </tr>"""
        
        for i in qb.all():
            node = load_node(i[1])
            list_ = node.list_object_names()
            html += f'<tr><td>{i[0]}</td><td>{i[1]}</td><td>{list_[0]}</td></tr>'
        html+='</table>'
        
        self.results.value = html
   