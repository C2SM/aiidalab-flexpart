# -*- coding: utf-8 -*-
import ipywidgets as widgets
import pandas as pd
import yaml
import pathlib
import datetime
import static
import base64
import re
from aiida import orm
from importlib import resources
from settings import NETCDF
from aiida.orm import QueryBuilder, Group, Dict
import aiidalab_widgets_base as awb

style = {"description_width": "initial"}
style_calendar = resources.read_text(static, "style.css")
path_to_default_codes = pathlib.Path.cwd() /'utils'/ "default_codes.yaml"


def get_global_attribute_family(attribute: str) -> list:
    # returns a list of all different values stored for a given global attribute
    qb = QueryBuilder().append(
        NETCDF, project="attributes.global_attributes." + attribute
    )
    return list({i[0] for i in qb.all() if i[0] != None})

def update_codes(d:dict)->None:
    with open(path_to_default_codes, 'r') as f:
        current_dict = yaml.safe_load(f)
    if current_dict:
        current_dict.update(d)
    else:
        current_dict = d
    with open(path_to_default_codes, 'w') as f:
        yaml.dump(current_dict, f)

def get_dictionary_of_group_element(group_name: str, name: str) -> dict:
    qb = QueryBuilder()
    qb.append(Group, filters={"label": group_name}, tag="g")
    qb.append(Dict, project=["attributes"], with_group="g")
    for i in qb.all():
        if next(iter(i[0])) == name:
            return i[0][name]


def read_yaml_data(data_filename: str, names=None) -> dict:
    # Read in a YAML data file as a dictionary
    data_path = pathlib.Path(data_filename)
    with data_path.open("r", encoding="utf-8") as fp:
        yaml_data = yaml.safe_load(fp)

    return (
        {key: value for key, value in yaml_data.items() if key in names}
        if names
        else yaml_data
    )


def store_dictionary(dict_: dict, group_label: str) -> None:
    # Stores a dictionary under a given group.
    d = orm.Dict(dict_)
    d.store()
    group = orm.Group.get(label=group_label)
    group.add_nodes(d)


def initialize_group(path_to_yaml: str, group_name: str) -> None:
    # Creates a group (if it does not exist) and stores the dictionaries from
    # the given yaml file.
    q = orm.QueryBuilder().append(orm.Group, filters={"label": group_name})
    if not q.all():
        group = orm.Group(label=group_name)
        group.store()
        d = read_yaml_data(path_to_yaml)
        for k in d.keys():
            store_dictionary({k: d[k]}, group_name)


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
        if "," in date_string:
            dates += [date.strip() + " 00:00:00" for date in date_string.split(",")]
        elif "--" in date_string:
            date_start, date_end = list(
                map(
                    lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"),
                    date_string.split("--"),
                )
            )
            dates += [
                date.strftime("%Y-%m-%d 00:00:00")
                for date in [
                    date_start + datetime.timedelta(days=x)
                    for x in range(0, (date_end - date_start).days + 1)
                ]
            ]
        else:
            dates += [date_string.strip() + " 00:00:00"]

    return orm.List(list=dates)


def read_description(path_loc: str, key_: str) -> str:
    if key_ == "None":
        return ""
    dict_ = read_yaml_data(path_loc, names=[key_])
    string = ""
    if type(dict_[key_]) == list:
        string = "\n".join(dict_[key_])
    else:
        for k, v in dict_[key_].items():
            string += k + " : " + str(v) + "\n"
    return string


def validate_dates(date: str) -> bool:
    # True if date is in the right format
    # False otherwise
    dates = re.split(",|--", date)
    if not all(
        re.search(r"^([0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01]))$", i)
        for i in dates
    ):
        return True
    return False


def parse_description(dict_: dict) -> str:
    key_ = next(iter(dict_))
    if key_ == "None":
        return ""
    string = ""
    if type(dict_[key_]) == list:
        string = "\n".join(dict_[key_])
    else:
        for k, v in dict_[key_].items():
            string += k + " : " + str(v) + "\n"
    return string


def reformat_locations(dict_: dict, model: str) -> dict:
    for key in dict_.keys():
        if "longitude" in dict_[key]:
            dict_[key]["longitude_of_lower_left_corner"] = dict_[key]["longitude"]
            dict_[key]["longitude_of_upper_right_corner"] = dict_[key]["longitude"]
            dict_[key]["latitude_of_lower_left_corner"] = dict_[key]["latitude"]
            dict_[key]["latitude_of_upper_right_corner"] = dict_[key]["latitude"]

            if model in dict_[key]["level"]:
                dict_[key]["lower_z_level"] = dict_[key]["level"][model]
                dict_[key]["upper_z_level"] = dict_[key]["level"][model]
            elif "default" in dict_[key]["level"]:
                dict_[key]["lower_z_level"] = dict_[key]["level"]["default"]
                dict_[key]["upper_z_level"] = dict_[key]["level"]["default"]
            else:
                dict_[key]["lower_z_level"] = 10
                dict_[key]["upper_z_level"] = 10

            if model in dict_[key]["level"]:
                dict_[key]["level_type"] = dict_[key]["level_type"][model]
            else:
                dict_[key]["level_type"] = 2

            dict_[key].pop("longitude")
            dict_[key].pop("latitude")
            dict_[key].pop("level")
    return dict_


def generate_locations() -> list:
    # returns a list of Togglebuttons for each location in
    # locations group
    list_widgets_loc = []
    d = get_dicts_in_group("locations")
    names = get_names_in_group("locations")
    s_d = {next(iter(i)): i[next(iter(i))] for i in d}

    for loc in names:
        list_widgets_loc.append(
            widgets.ToggleButton(
                value=False,
                description=loc,
                button_style="",
                tooltip=str(s_d[loc]),
            )
        )
    return list_widgets_loc


def generate_outgrids_buttons(outgrid_nest: bool) -> list:
    # generates list of widgets for outgrids
    d = get_dicts_in_group("outgrid")
    names = [next(iter(x)) for x in d]
    if outgrid_nest:
        names.append("None")
        list_widgets = widgets.ToggleButtons(
            options=names,
            value="None",
            tooltips=[parse_description(i) for i in d],
        )
    else:
        list_widgets = widgets.ToggleButtons(
            options=names,
            tooltips=[parse_description(i) for i in d],
        )
    return list_widgets


def get_element_dict_by_group(group: str, list_: list) -> list:
    q = orm.QueryBuilder()
    q.append(orm.Group, filters={"label": group}, tag="g")
    q.append(
        orm.Dict,
        filters={"attributes": {"or": [{"has_key": l} for l in list_]}},
        project=["attributes"],
        with_group="g",
    )
    return [x[0] for x in q.all()]


def get_dicts_in_group(group_name: str) -> list:
    # Returns dictionarie of an element in a given group
    q = orm.QueryBuilder()
    q.append(orm.Group, filters={"label": group_name}, tag="g")
    q.append(orm.Dict, project=["attributes"], with_group="g")
    return [x[0] for x in q.all()]


def get_names_in_group(group_name: str) -> list:
    return [next(iter(x)) for x in get_dicts_in_group(group_name)]


def fill(path_file: str) -> list:
    list_widgets = []
    dict_ = read_yaml_data(path_file)
    d = {
        int: widgets.IntText,
        float: widgets.FloatText,
        bool: widgets.Checkbox,
    }
    for k in dict_.keys():
        if "options" in dict_[k]:
            list_widgets.append(
                widgets.Dropdown(
                    options=dict_[k]["options"],
                    value=dict_[k]["value"],
                    description=k,
                    tooltip=dict_[k]["tooltip"],
                    style=style,
                )
            )
        else:
            list_widgets.append(
                d[type(dict_[k]["value"])](
                    value=dict_[k]["value"],
                    description=k,
                    style=style,
                    tooltip=dict_[k]["tooltip"],
                )
            )
    return list_widgets

def codes_list():
    return [
        awb.ComputationalResourcesWidget._full_code_label(c[0])
        for c in orm.QueryBuilder().append(orm.Code).all()
    ]

def fix_values(name):
    try:
        d = read_yaml_data(path_to_default_codes, names=[name])[name]
    except:
        return "None"
    return d if d in codes_list() else "None"

def download_button(fname: str, data: pd.DataFrame, button_text:str) -> str:
    payload = base64.b64encode(data.to_csv(index=False).encode()).decode()
    return f"""<a download="{fname}"
                  href="data:text/csv;base64,{payload}"
                  target="_blank">
                        {button_text}
                </a>"""

def generate_html_calendar(range_date, a_dates):
    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    html = "<style>" + style_calendar + "</style>" + "<div class='grid-container'>"
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

    dates = []
    for i in range(len(range_date)):
        if dates == []:
            dates.append([range_date[i]])
        elif range_date[i].month == dates[-1][0].month:
            dates[-1].append(range_date[i])
        else:
            dates.append([range_date[i]])

    for m in dates:
        html += b_table + f"<caption><b>{months[m[0].month]} {m[0].year}</b></caption>"
        k = 0
        first_day = m[0].day_of_week
        for w in [0, 7, 14, 21, 28]:
            html += "<tr>"
            for i in range(1, 8):
                list_ = [d.day + first_day for d in m]
                if i + w in list_ and m[k] not in a_dates.index:
                    html += f"<td>{m[k].day}<div class='block_box'></div></td>"
                    k += 1
                elif i + w in list_ and m[k] in a_dates.index:
                    pk_list = a_dates.loc[m[k]][0]
                    multiple_w_list = '<div class = "shwtext">'
                    if len(pk_list) > 1:
                        for i in pk_list[1:]:
                            multiple_w_list += f"""
                                                      <a href=./plot.ipynb?id={i[0]}
                                                      target="_blank">
                                                      <mark style="background-color: #{i[1][:6]}; color:#ffffff">{i[1][:6]}</mark>
                                                      </a>
                                                      """
                        html += f"""<td>
                                        {m[k].day}<br><div class='block_box'>
                                        <a href=./plot.ipynb?id={pk_list[0][0]}
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
                        html += f"""<td>
                                        {m[k].day}<br><div class='block_box'>
                                        <a href=./plot.ipynb?id={pk_list[0][0]}
                                                      target="_blank">
                                        <mark style="background-color: #{pk_list[0][1][:6]}; color:#ffffff">{pk_list[0][1][:6]}</mark>
                                        </a></div></td>"""
                    k += 1
                else:
                    html += "<td> </td>"
            html += "</tr>"
        html += e_table
    html += "</div>"
    return html
