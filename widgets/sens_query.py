import ipywidgets as widgets
import re
from IPython.display import clear_output, display

from aiida.orm import QueryBuilder

from utils import utils
from settings import NETCDF

style = {"description_width": "initial"}


def search_locations(a_obs):
    available_locations = []
    qb = QueryBuilder()
    qb.append(
        NETCDF,
        filters={
            "attributes.filename": {"or": [{"like": f"{l}%"} for l in a_obs]},
            #'attributes.global_attributes.model': {'==': 'NAME'}
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
    return list(set(available_species))


class SearchSens(widgets.VBox):
    ind_title = widgets.HTML(value="""<hr>""")
    species_title = widgets.HTML(value="""<b>1. Observations</b><br>Species """)
    locations_title = widgets.HTML(
        value="""<b>2. Locations</b><br>Choose from the list of locations where observations are available."""
    )
    info = widgets.HTML(value='<p style="color:green;">Available: ')

    def __init__(self):

        self.date_range = widgets.Text(
            value="2020-09-01--2020-12-31",
            description="Range_dates",
            style=style,
        )
        self.location = widgets.TagsInput(
            allowed_tags=search_locations(["JFJ"]),
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
        self.available_obs_list = {"names": [], "remotes": []}
        self.list_remotes = []

        search_crit = widgets.VBox(
            [
                widgets.VBox(
                    [self.species_title, self.species, self.time_step, self.domain],
                ),
                self.info,
                self.ind_title,
                self.locations_title,
                self.location,
                self.ind_title,
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

        def on_click(b):
            with self.info_out:
                clear_output()
                self.accordions()

        button.on_click(on_click)

        super().__init__(
            [
                search_crit,
                self.ind_title,
                button,
                self.acc,
                self.info_out,
                self.ind_title,
            ]
        )

    def available_observations(self, change=None):
        self.info.value = '<p style="color:green;">Available: '
        available_locations = []
        qb = QueryBuilder()
        qb.append(
            NETCDF,
            filters={
                "attributes.filename": {"ilike": f"%{self.time_step.value}%"},
                "attributes.global_attributes.species": {
                    "or": [{"like": f"'%{s}%'"} for s in self.species.value]
                },
            },
            project=["attributes.filename", "attributes.remote_path"],
        )
        for i in qb.all():
            s = re.split("_|-", i[0])
            available_locations.append(s[0])
            self.available_obs_list["remotes"].append(i[1])
        self.info.value += ", ".join(available_locations)
        self.info.value += "</p>"
        self.available_obs_list["names"] = available_locations
        self.location.allowed_tags = search_locations(self.available_obs_list["names"])

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
        reformated_dates = list(set([i[:4] + i[5:7] for i in dates_list]))
        qb = QueryBuilder()
        qb.append(
            NETCDF,
            project=[
                "attributes.filename",
                "attributes.global_attributes.created",
                "id",
                "attributes.remote_path",
            ],
            filters={
                "attributes.filename": {
                    "and": [
                        {"or": [{"like": f"{n_location}%"}]},
                        # {"or": [{"like": f"%{l}%"} for l in reformated_dates]},
                    ]
                },
                # "attributes.global_attributes.domain": {"==": f"'{self.domain.value}'"},
                # "attributes.global_attributes.model": {"==": f"'{self.model.value}'"},
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
                self.list_remotes.append(dict_[m][3] + "/" + dict_[m][0])
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
