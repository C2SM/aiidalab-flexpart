# -*- coding: utf-8 -*-
import ipywidgets as widgets
import re
from IPython.display import clear_output

from aiida.orm import QueryBuilder

from utils import utils
from settings import NETCDF
from widgets import filter

style = {"description_width": "initial"}


def parse_dict(d_):
    html = ""
    for k, v in d_.items():
        html += f"<b>{k}: </b>{v}<br>"
    return html


def search_import_labels():
    qb = QueryBuilder().append(
        NETCDF,
        project="attributes.time_label",
    )
    return list({i[0] for i in qb.all()})


def range_inlet(inlet_height: str, rang: int) -> list:
    number = int(inlet_height[:-4])
    return [str(i) + "magl" for i in range(number - rang, number + rang + 1)]


def search_locations(a_obs: list) -> list:
    # Search for observations that match the available
    # observations names.
    complete_obs = []
    for i in a_obs:
        complete_obs += [
            re.split("-", i)[0] + "-" + x for x in range_inlet(re.split("-", i)[1], 15)
        ]

    available_locations = []
    qb = QueryBuilder()
    qb.append(
        NETCDF,
        filters={
            "attributes.filename": {"or": [{"like": f"{l}%"} for l in complete_obs]},
        },
        project="attributes.filename",
    )
    for i in qb.all():
        s = re.split("_|-", i[0])
        available_locations.append(s[0] + "-" + s[1])
    return list(set(available_locations))


def search_species():
    available_species = []
    for i in utils.get_global_attribute_family("species"):
        values = i.split(";")
        if len(values) > 1:
            for j in range(len(values)):
                available_species.append(re.sub("'", "", values[j]))
        else:
            available_species.append(re.sub("'", "", values[0]))
    s = set(available_species)
    if "Inert" in s:
        s.remove("Inert")
    elif "inert" in s:
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
            value="2020-01-01--2021-01-01",
            description="Range_dates",
            style=style,
        )
        self.location = widgets.TagsInput(
            allowed_tags=["LUT"],
            allow_duplicates=False,
            style=style,
        )
        self.domain = widgets.Dropdown(
            options=utils.get_global_attribute_family("domain"),
            description="Domain",
            style=style,
        )
        self.time_step = widgets.Dropdown(
            options=["3hourly", "4hourly", "6hourly", "12hourly", "24hourly"],
            description="Time steps",
            style=style,
        )
        self.time_label = widgets.Dropdown(
            description="Import label",
            options=['None']+search_import_labels(),
            style=style)
        self.import_label_sensitivities = widgets.Dropdown(
            description="Import label",
            options=['None']+search_import_labels(),
            style=style)

        self.model = widgets.Dropdown(
            options=utils.get_global_attribute_family("model"),
            description="Model",
            style=style,
        )
        self.model_version = widgets.Dropdown(
            options=utils.get_global_attribute_family("model_version"),
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
        self.time_label.observe(self.available_observations, names="value")
        self.available_obs_list = {}
        self.selected_obs = {}
        self.list_remotes = {}
        self.list_info_obs = []
        self.site_extras = {}
        self.site_filter = {}

        search_crit = widgets.VBox(
            [
                widgets.VBox(
                    [self.species_title, self.species, 
                     widgets.HBox(
                         children = [self.time_step, self.time_label]
                                  )
                                  ],
                ),
                self.info,
                widgets.HTML(value="""<hr>"""),
                self.locations_title,
                self.location,
                widgets.HTML(value="""<hr>"""),
                widgets.GridBox(
                    [self.date_range, self.model, self.model_version, self.domain,
                     self.import_label_sensitivities],
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
        for i in self.location.value:
            if i in self.available_obs_list.keys():
                self.selected_obs[i] = self.available_obs_list[i]

    def available_observations(self, change=None):
        self.info.value = '<p style="color:green;">Available: '
        filter_dict = {
                "attributes.filename": {"ilike": f"%\\_{self.time_step.value}%"},
                "attributes.global_attributes.species": {
                    "or": [{"like": f"'%{s}%'"} for s in self.species.value]
                }}
        #if self.time_label.value!='None':
        filter_dict.update({"attributes.time_label":self.time_label.value})
        qb = QueryBuilder()
        qb.append(
            NETCDF,
            filters = filter_dict,
            project=["attributes.filename", "*"],
        )
        for i in qb.all():
            name = re.split("_|-", i[0])
            self.available_obs_list[name[0]+'-'+name[1]] = i[1]
        self.info.value += ", ".join(list(self.available_obs_list.keys()))
        self.info.value += "</p>"
        self.location.allowed_tags = search_locations(
            list(self.available_obs_list.keys())
        )

    def accordions_sites(self):
        self.list_info_obs = []
        for k, v in self.selected_obs.items():
            x = v.attributes["global_attributes"]
            d_ = {
                "name": k.split("-")[0],
                "id": k.split("-")[0],
                "flex.id": k,
                "ft.type": "ncdf_monthly",
                "site.obs.fn": v.attributes["remote_path"],
                "lon": float(x["station_longitude"]),
                "lat": float(x["station_latitude"]),
            }
            self.list_info_obs.append(d_)

        for i in self.list_info_obs:
            self.site_extras[i["name"]] = [
                widgets.IntText(description="pch", value=4, style=style),
                widgets.IntText(description="col", value=1, style=style),
                widgets.IntText(description="lwd", value=1, style=style),
                widgets.IntText(description="cex", value=1, style=style),
                widgets.IntText(description="pos", value=3, style=style),
                widgets.Text(description="sig.srr", value=".na", style=style),
                widgets.Text(description="sig.min", value=".na", style=style),
                widgets.Checkbox(description="val.ts", value=False, style=style),
            ]
            self.site_filter[i["name"]] = filter.ViewerWidget(mode="filter")

        self.accordion_sites.children = [
            widgets.VBox(
                children=[
                    widgets.HBox(
                        children=[
                            widgets.HTML(value=parse_dict(i)),
                            widgets.VBox(
                                children=[widgets.HTML("<b>Plot options</b>")]
                                + self.site_extras[i["name"]][:5]
                                + [widgets.HTML("<hr>")]
                                + self.site_extras[i["name"]][5:]
                            ),
                        ]
                    ),
                    widgets.HTML("<hr>"),
                    self.site_filter[i["name"]],
                ]
            )
            for i in self.list_info_obs
        ]

        for i, k in enumerate(self.selected_obs.keys()):
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
                    ]
                },
                "attributes.time_label":self.import_label_sensitivities.value,
                "attributes.global_attributes.domain": {"==": f"{self.domain.value}"},
                "attributes.global_attributes.model": {"==": f"{self.model.value}"},
                "attributes.global_attributes.model_version": {
                    "ilike": f"{self.model_version.value}"
                },
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
                    <th>Address</th>
                </tr>"""

        dict_ = {}
        for i in qb.all():
            dict_[i[0][-9:-3]] = i
        for m in reformated_dates:
            if m in dict_.keys():
                html += f"""<tr>
                        <td>
                            <a href=./ncdump.ipynb?id={dict_[m][2]}
                                                        target="_blanm">
                                {dict_[m][2]}
                            </a>
                        </td>
                        <td>{m}</td>
                        <td>{dict_[m][0]}</td>
                        <td>{dict_[m][1]}</td>
                        <td>{dict_[m][3].replace(dict_[m][0],'')}</td>
                        </tr>"""
                self.list_remotes[dict_[m][0]] = dict_[m][4]
            else:
                html += f"""<tr>
                        <td><mark style='color: red;'>Missing</mark></td>
                        <td>{m}</td>
                        <td><mark style='color: red;'>Missing</mark></td>
                        <td><mark style='color: red;'>Missing</mark></td>
                        <td><mark style='color: red;'>Missing</mark></td>
                        </tr>"""
                missing_dates.append(m)
        html += "</table>"

        return widgets.HTML(html), missing_dates
