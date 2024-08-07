# -*- coding: utf-8 -*-
import ipywidgets as widgets
import re
from IPython.display import clear_output

from aiida.orm import QueryBuilder

from utils import utils
from settings import NETCDF

style = {"description_width": "initial"}


def parse_dict(d_):
    html = ""
    for k, v in d_.items():
        html += f"<b>{k}: </b>{v}<br>"
    return html


def search_locations(a_obs: list) -> list:
    # Search for observations that match the available
    # observations names.
    available_locations = []
    qb = QueryBuilder()
    qb.append(
        NETCDF,
        filters={
            "attributes.filename": {"or": [{"like": f"{l}%"} for l in a_obs]},
        },
        project="attributes.filename",
    )
    for i in qb.all():
        s = re.split("_|-", i[0])
        available_locations.append(s[0] + "-" + s[1])
    return list(set(available_locations))


def search_species():
    available_species = []
    qb = QueryBuilder()
    qb.append(NETCDF, project="attributes.global_attributes.species")
    for i in qb.all():
        if i[0]:
            values = i[0].split(";")
            if len(values) > 1:
                for j in range(len(values)):
                    available_species.append(re.sub("'", "", values[j]))
            else:
                available_species.append(re.sub("'", "", values[0]))
    s = set(available_species)
    if 'Inert' in s:
        s.remove("Inert")
    elif 'inert' in s:
        s.remove("inert")
    return list(s)


class SearchSens(widgets.VBox):
    species_title = widgets.HTML(value="""<b>1. Observations</b><br>Species """)
    locations_title = widgets.HTML(
        value="""<b>2. Locations</b><br>Choose from the list of locations where observations are available."""
    )
    info = widgets.HTML(value='<p style="color:green;">Available: ')

    def __init__(self):

        self.date_range = widgets.Text(
            value="2020-01-01--2020-12-31",
            description="Range_dates",
            style=style,
        )
        self.location = widgets.TagsInput(
            allowed_tags=["LUT"],  # search_locations(["JFJ"]),
            allow_duplicates=False,
            style=style,
        )
        self.domain = widgets.Dropdown(
            options=["EUROPE"],
            description="Domain",
            style=style,
        )
        self.time_step = widgets.Dropdown(
            options=["3hourly", "4hourly", "6hourly", "12hourly", "24hourly"],
            description="Time steps",
            style=style,
        )
        self.model = widgets.Dropdown(
            options=["NAME", "FLEXPART"],
            description="Model",
            style=style,
        )
        self.model_version = widgets.Dropdown(
            options=["NAME III (version 7.2)", "FLEXPART IFS (version 9.1_Empa)"],
            description="Model version",
            style=style,
        )
        self.species = widgets.TagsInput(
            allowed_tags=search_species(),
            allow_duplicates=False,
            style=style,
        )

        self.time_step.observe(self.available_observations, names="value")
        self.species.observe(self.available_observations, names="value")
        self.available_obs_list = {}
        self.selected_obs = {}
        self.list_remotes = {}
        self.list_info_obs = []
        self.site_extras = {}

        search_crit = widgets.VBox(
            [
                widgets.VBox(
                    [self.species_title, self.species, self.time_step, self.domain],
                ),
                self.info,
                widgets.HTML(value="""<hr>"""),
                self.locations_title,
                self.location,
                widgets.HTML(value="""<hr>"""),
                widgets.GridBox(
                    [
                        self.date_range,
                        self.model,
                        self.model_version,
                    ],
                    layout=widgets.Layout(grid_template_columns="repeat(2, 50%)"),
                ),
            ]
        )
        button = widgets.Button(description="Search")
        self.info_out = widgets.Output()

        self.acc = widgets.Accordion()
        self.accordion_sites = widgets.Accordion()

        def on_click(b):
            with self.info_out:
                clear_output()
                self.accordions()
                self.filter_observations()
                self.accordions_sites()

        button.on_click(on_click)

        super().__init__(
            [
                search_crit,
                widgets.HTML(value="""<hr>"""),
                button,
                widgets.HTML(value="<hr> <b>Sensitivites</b>"),
                self.acc,
                widgets.HTML(value="<hr> <b>Observations</b>"),
                self.accordion_sites,
                self.info_out,
                widgets.HTML(value="""<hr>"""),
            ]
        )

    def filter_observations(self):
        self.selected_obs = {}
        for i in [re.split("_|-", x)[0] for x in self.location.value]:
            if i in self.available_obs_list.keys():
                self.selected_obs[i] = self.available_obs_list[i]

    def available_observations(self, change=None):
        self.info.value = '<p style="color:green;">Available: '
        qb = QueryBuilder()
        qb.append(
            NETCDF,
            filters={
                "attributes.filename": {"ilike": f"%{self.time_step.value}%"},
                "attributes.global_attributes.species": {
                    "or": [{"like": f"'%{s}%'"} for s in self.species.value]
                },
            },
            project=["attributes.filename", "*"],
        )
        for i in qb.all():
            self.available_obs_list[re.split("_|-", i[0])[0]] = i[1]
        self.info.value += ", ".join(list(self.available_obs_list.keys()))
        self.info.value += "</p>"
        self.location.allowed_tags = search_locations(
            list(self.available_obs_list.keys())
        )

    def accordions_sites(self):
        self.list_info_obs = []
        for k, v in self.selected_obs.items():
            filename = v.attributes["filename"].split("_")
            x = v.attributes["global_attributes"]
            d_ = {
                "name": k,
                "id": k,
                "flex.id": filename[0] + "_" + filename[1],
                "rel.com": filename[0] + "_" + filename[1],
                "ft.type": "ncdf_monthly",
                "site.obs.fn": v.attributes["remote_path"],
                "val.ts": False,
                "x": float(x["station_longitude"]),
                "y": float(x["station_latitude"]),
                "ex.hours": '~',
                "sig.srr": ".na",
                "sig.min": ".na",
            }
            self.list_info_obs.append(d_)

        for i in self.list_info_obs:
            self.site_extras[i['name']] =  [
                        widgets.IntText(description="pch",value = 4),
                        widgets.IntText(description="col",value = 1),
                        widgets.IntText(description="lwd",value = 1),
                        widgets.IntText(description="cex",value = 1),
                        widgets.IntText(description="pos",value = 3)
                    ]
        self.accordion_sites.children = [
            widgets.HBox(
                children=[
                    widgets.HTML(value=parse_dict(i)),
                    widgets.VBox(children = self.site_extras[i['name']])
                ]
            )
            for i in self.list_info_obs
        ]
     
        for i,k in enumerate(self.selected_obs.keys()):
            self.accordion_sites.set_title(i, k)
          

    def accordions(self):
        icons = {True: "  ✅", False: "  ❌"}
        list_locations = {}
        for i in self.location.value:
            html, is_complete = self.search(i)
            children = [html]
            if is_complete:
                children.append(
                    widgets.Button(
                        description="Run missing",
                        button_style="info",
                    )
                )
            list_locations[widgets.VBox(children=children)] = (is_complete, i)
        self.acc.children = list(list_locations.keys())
        i = 0
        for _, v in list_locations.items():
            self.acc.set_title(i, f"{v[1]}" + icons[not v[0]])
            i += 1

    def search(self, n_location):
        missing_dates = []
        dates_list = utils.simulation_dates_parser([self.date_range.value])
        reformated_dates = sorted(list(set([i[:4] + i[5:7] for i in dates_list])))
        qb = QueryBuilder()
        qb.append(
            NETCDF,
            project=[
                "attributes.filename",
                "attributes.global_attributes.created",
                "id",
                "attributes.remote_path",
                "*",
            ],
            filters={
                "attributes.filename": {
                    "and": [
                        {"or": [{"like": f"{n_location}%"}]},
                        # {"or": [{"like": f"%{l}%"} for l in reformated_dates]},
                    ]
                },
                # "attributes.global_attributes.domain": {"==": f"'{self.domain.value}'"},
                "attributes.global_attributes.model": {"==": f"'{self.model.value}'"},
                # "attributes.global_attributes.model_version": {"ilike": f"'{self.model_version.value}'"},
                # "attributes.global_attributes.species": {
                #    "ilike": f"{self.species.value}"
                # },
            },
        )

        html = """<style>
        table, th, td {
            border: 1px solid;
            text-align: center;
            padding: 5px}</style>
        <table>
                <tr>
                    <th>Id</th>
                    <th>Date</th>
                    <th>Name</th>
                    <th>Created</th>
                </tr>"""

        dict_ = {}
        for i in qb.all():
            dict_[i[0][-9:-3]] = i
        for m in reformated_dates:
            if m in dict_.keys():
                html += f"""<tr>
                        <td>
                            <a href=http://127.0.0.1:8888/apps/apps/FLEXPART_AiiDAlab/ncdump.ipynb?id={dict_[m][2]}
                                                        target="_blanm">
                                {dict_[m][2]}
                            </a>
                        </td>
                        <td>{m}</td>
                        <td>{dict_[m][0]}</td>
                        <td>{dict_[m][1]}</td>
                        </tr>"""
                self.list_remotes[dict_[m][0]] = dict_[m][4]
            else:
                html += f"""<tr>
                        <td><mark style='color: red;'>Missing</mark></td>
                        <td>{m}</td>
                        <td><mark style='color: red;'>Missing</mark></td>
                        <td><mark style='color: red;'>Missing</mark></td>
                        </tr>"""
                missing_dates.append(m)
        html += "</table>"

        return widgets.HTML(html), missing_dates
