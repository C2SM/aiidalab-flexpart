import ipywidgets as widgets
import yaml
import pathlib
import datetime
import static
from aiida import orm
from importlib import resources

style = {'description_width': 'initial'}
style_calendar = resources.read_text(static, "style.css")

def read_yaml_data(data_filename: str, names=None) -> dict:
    """Read in a YAML data file as a dictionary"""
    data_path = pathlib.Path(data_filename)
    with data_path.open('r', encoding='utf-8') as fp:
        yaml_data = yaml.safe_load(fp)

    return {key: value
            for key, value in yaml_data.items()
            if key in names} if names else yaml_data

"""def make_locations_list(list_locations: list) -> list:
    list_locations_ = read_yaml_data('/home/jovyan/work/aiida-flexpart/examples/inputs/location_groups.yaml',names=list_locations)
    list_=[]
    if list_locations_:
        for i,j in list_locations_.items():
            list_+=j
    return sorted(set(list_locations+list_))"""

def simulation_dates_parser(date_list: list) -> list:
    """
    Parse a range of dates and returns a list of date strings.

    Examples:
        2021-01-02--2021-01-10 -> [2021-01-02 00:00:00, 2021-01-02 00:00:00, ..., 2021-01-10 00:00:00]
        2021-01-02, 2021-01-10 -> [2021-01-02 00:00:00, 2021-01-10 00:00:00]
        2021-01-02 -> [2021-01-02 00:00:00,]
    """
    dates = []
    for date_string in date_list:
        if ',' in date_string:
            dates += [
                date.strip() + ' 00:00:00' for date in date_string.split(',')
            ]
        elif '--' in date_string:
            date_start, date_end = list(
                map(lambda date: datetime.datetime.strptime(date, '%Y-%m-%d'),
                    date_string.split('--')))
            dates += [
                date.strftime('%Y-%m-%d 00:00:00') for date in [
                    date_start + datetime.timedelta(days=x)
                    for x in range(0, (date_end - date_start).days + 1)
                ]
            ]
        else:
            dates += [date_string.strip() + ' 00:00:00']

    return orm.List(list=dates)

def fill_locations(path_loc:str):
        return list(read_yaml_data(path_loc).keys())

def read_description(path_loc:str, 
                     key_:str)->str:
    if key_=='None':
        return ''
    dict_ = read_yaml_data(path_loc,names=[key_])
    string=''
    if type(dict_[key_]) == list:
        string = '\n'.join(dict_[key_])
    else:
        for k,v in dict_[key_].items():
            string+=k+' : '+str(v)+'\n'
    return string

def reformat_locations(dict_, model):
    """reformat locations"""
    for key in dict_.keys():
        if 'longitude' in dict_[key]:
            dict_[key]['longitude_of_lower_left_corner'] = dict_[key][
                'longitude']
            dict_[key]['longitude_of_upper_right_corner'] = dict_[key][
                'longitude']
            dict_[key]['latitude_of_lower_left_corner'] = dict_[key][
                'latitude']
            dict_[key]['latitude_of_upper_right_corner'] = dict_[key][
                'latitude']

            if model in dict_[key]['level']:
                dict_[key]['lower_z_level'] = dict_[key]['level'][model]
                dict_[key]['upper_z_level'] = dict_[key]['level'][model]
            elif 'default' in dict_[key]['level']:
                dict_[key]['lower_z_level'] = dict_[key]['level']['default']
                dict_[key]['upper_z_level'] = dict_[key]['level']['default']
            else:
                dict_[key]['lower_z_level'] = 10
                dict_[key]['upper_z_level'] = 10

            if model in dict_[key]['level']:
                dict_[key]['level_type'] = dict_[key]['level_type'][model]
            else:
                dict_[key]['level_type']= 2

            dict_[key].pop('longitude')
            dict_[key].pop('latitude')
            dict_[key].pop('level')
    return dict_

def generate_locations(path_yaml:str)->list:
    list_widgets_loc = []
    list_locations = fill_locations(path_yaml)
    for loc in list_locations:
        list_widgets_loc.append(
                            widgets.ToggleButton(
                                    value = False,
                                    description=loc,
                                    disabled=False,
                                    button_style='', 
                                    tooltip = read_description(path_yaml, 
                                                               loc)
                                    )
                                )
    return list_widgets_loc

def generate_outgrid(path_yaml:str, outgrid_nest:bool)->list:
    list_locations = fill_locations(path_yaml)
    if outgrid_nest:
        list_locations.append('None')
        list_widgets_loc = widgets.ToggleButtons(options = list_locations, value  ='None',
                          tooltips=[read_description(path_yaml, loc) for loc in list_locations])
    else:
        list_widgets_loc = widgets.ToggleButtons(options = list_locations,
                          tooltips=[read_description(path_yaml, loc) for loc in list_locations])                                              
    return list_widgets_loc

def fill(path_file:str):
    list_widgets = []
    dict_ = read_yaml_data(path_file)
 
    for k in dict_.keys():
        if type(dict_[k]['value']) == int and 'options' not in dict_[k]:
            list_widgets.append(widgets.IntText(
                                    value = dict_[k]['value'],
                                    description = k,
                                    description_tooltip = dict_[k]['tooltip'],
                                    disabled=False,style=style
                                )
                            )
        if type(dict_[k]['value']) == float and 'options' not in dict_[k]:
            list_widgets.append(widgets.FloatText(
                                    value = dict_[k]['value'],
                                    description = k,
                                    description_tooltip = dict_[k]['tooltip'],
                                    disabled=False,style=style
                                )
                            )
        if type(dict_[k]['value']) == bool and 'options' not in dict_[k]:
            list_widgets.append(widgets.Checkbox(
                                    value = dict_[k]['value'],
                                    description = k,
                                    description_tooltip = dict_[k]['tooltip'],
                                    disabled=False,style=style
                                )
                            )
        if 'options' in dict_[k]:
            list_widgets.append(widgets.Dropdown(options=dict_[k]['options'],
                                    value=dict_[k]['value'],
                                    description=k,
                                    description_tooltip = dict_[k]['tooltip'],
                                    disabled=False,style=style))
    return list_widgets

def generate_html_calendar(range_date, a_dates):
    months = {1:'January',
                  2:'February',
                  3:'March',
                  4:'April',
                  5:'May',
                  6:'June',
                  7:'July',
                  8:'August',
                  9:'September',
                  10:'October',
                  11:'November',
                  12:'December'}
    
    html = '<style>'+style_calendar+'</style>'+"<div class='grid-container'>"
    b_table = """
        <div class="grid-item">
        <table>
                <tr>
                    <th>Mo</th>
                    <th>Tu</th>
                    <th>We</th>
                    <th>Th</th>
                    <th>Fr</th>
                    <th>Sa</th>
                    <th>Su</th>
                </tr>"""
    e_table = "</table></div>"

    dates=[]
    for i in range(len(range_date)):
            if(dates==[]):
                dates.append([range_date[i]])
            elif(range_date[i].month==dates[-1][0].month):
                dates[-1].append(range_date[i])
            else:
                dates.append([range_date[i]])

    for m in dates:
             html +=b_table+f"<caption><b>{months[m[0].month]} {m[0].year}</b></caption>"
             k=0
             first_day = m[0].day_of_week
             for w in [0,7,14,21,28]:
                  html +="<tr>"
                  for i in range(1,8):
                        list_ = [d.day+first_day for d in m]
                        if i+w in list_ and m[k] not in a_dates.index:
                            html +=f"<td>{m[k].day}<div class='block_box'></div></td>"
                            k+=1
                        elif i+w in list_ and m[k] in a_dates.index:
                            pk_list = a_dates.loc[m[k]][0]
                            multiple_w_list ='<div class = "shwtext">'
                            if len (pk_list)>1:
                                for i in pk_list[1:]:   
                                    multiple_w_list+= f"""
                                                      <a href=http://127.0.0.1:8888/apps/apps/flexpart_aiidalab/plot.ipynb?id={i[0]}
                                                      target="_blank">
                                                      <mark style="background-color: #{i[1][:6]}; color:#ffffff">{i[1][:6]}</mark>
                                                      </a>
                                                      """
                                html +=f"""<td>
                                        {m[k].day}<br><div class='block_box'>
                                        <a href=http://127.0.0.1:8888/apps/apps/flexpart_aiidalab/plot.ipynb?id={pk_list[0][0]}
                                                      target="_blank">
                                        <mark style="background-color: #{pk_list[0][1][:6]}; color:#ffffff">{pk_list[0][1][:6]}</mark>
                                        </a>
                                        <div class = 'tltip'>
                                                <mark style="background-color: #000000; color:#ffffff">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+&nbsp;&nbsp;&nbsp;&nbsp;</mark>
                                                {multiple_w_list}
                                                </div>
                                        </div></div>
                                       </td>"""
                            else: 
                                html +=f"""<td>
                                        {m[k].day}<br><div class='block_box'>
                                        <a href=http://127.0.0.1:8888/apps/apps/flexpart_aiidalab/plot.ipynb?id={pk_list[0][0]}
                                                      target="_blank">
                                        <mark style="background-color: #{pk_list[0][1][:6]}; color:#ffffff">{pk_list[0][1][:6]}</mark>
                                        </a></div></td>"""
                            k+=1
                        else:
                            html +="<td> </td>"
                  html +="</tr>"
             html +=e_table
    html+="</div>"
    return html