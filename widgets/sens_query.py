import ipywidgets as widgets
from IPython.display import clear_output

from aiida.orm import QueryBuilder
from aiida import plugins

from utils import utils
from pathlib import Path

coll_sens = plugins.CalculationFactory("collect.sens")
NetCDF = plugins.DataFactory("netcdf.data")
style = {"description_width": "initial"}


class SearchSens(widgets.VBox):
    def __init__(self):

        self.date_range = widgets.Text(
            value="2020-09-01--2020-12-31",
            description="Range_dates",
            style=style,
        )
        self.location = widgets.SelectMultiple(
            options=utils.fill_locations(Path.cwd() / "config" / "locations.yaml"),
            description="Locations",
            description_tooltip='Multiple values can be selected with "Shift" and/or "ctrl"(or "command")',
            value=["JFJ_5magl"],
            rows=12,
            style=style,
        )
        self.domain = widgets.Dropdown(
            options=["EUROPE"],
            description="Domain",
            ensure_option=True,
            style=style,
        )
        self.model = widgets.Dropdown(
            options=["NAME", "FLEXPART"],
            description="Model",
            ensure_option=True,
            style=style,
        )
        self.model_version = widgets.Dropdown(
            options=["NAME III (version 7.2)", "FLEXPART IFS (version 9.1_Empa)"],
            description="Model version",
            ensure_option=True,
            style=style,
        )
        self.species = widgets.Dropdown(
            options=[
                "inert",
            ],
            description="Species",
            ensure_option=True,
            style=style,
        )

        self.ind_title = widgets.HTML(
            value="""<hr>
            """
        )
        search_crit = widgets.HBox(
            [
                self.location,
                widgets.GridBox(
                    [
                        self.date_range,
                        self.domain,
                        self.model,
                        self.model_version,
                        self.species,
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
            NetCDF,
            project=[
                "attributes.filename",
                "attributes.global_attributes.created",
                "id",
            ],
            filters={
                "attributes.filename": {
                    "and": [
                        {"or": [{"like": f"{n_location}%"}]},
                        {"or": [{"like": f"%{l}%"} for l in reformated_dates]},
                    ]
                },
                # "attributes.global_attributes.domain": {"==": f"'{self.domain.value}'"},
                "attributes.global_attributes.model": {"==": f"'{self.model.value}'"},
                # "attributes.global_attributes.model_version": {"ilike": f"'{self.model_version.value}'"},
                "attributes.global_attributes.species": {
                    "ilike": f"'{self.species.value}'"
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
