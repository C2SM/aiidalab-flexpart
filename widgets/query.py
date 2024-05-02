import ipywidgets as widgets
from IPython.display import clear_output
import pandas as pd
from datetime import datetime
from pathlib import Path

from aiida import plugins
from utils import utils, make_query
from widgets import filter

flexpart_cosmo = plugins.CalculationFactory("flexpart.cosmo")
flexpart_ifs = plugins.CalculationFactory("flexpart.ifs")
flexpart_post = plugins.CalculationFactory("flexpart.post")
workflow = plugins.WorkflowFactory("flexpart.multi_dates")

style = {"description_width": "initial"}
path_to_out = Path.cwd() / "config" / "outgrid.yaml"
ad_q = filter.ViewerWidget()


class SearchCalculations(widgets.VBox):
    def __init__(self):
        self.date_range = widgets.Text(
            value="2020-09-01--2020-12-31",
            description="Dates",
            description_tooltip="range of dates to query",
            style=style,
        )
        self.presettings = widgets.Dropdown(
            options=make_query.get_extra_(None),
            description="Presettings",
            description_tooltip="Query for a specific presetting",
            style=style,
        )
        self.workflow_p = widgets.Dropdown(
            options=plugins.entry_point.get_entry_point_names("aiida.workflows"),
            description="Workflow",
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
        self.model = widgets.Dropdown(
            options=[
                "cosmo7",
                "cosmo2",
                "cosmo1",
                "kenda1",
                "cosmo7,cosmo1",
                "cosmo7,cosmo2",
                "cosmo7,kenda1",
                "IFS_GL_1",
                "IFS_GL_05",
                "IFS_EU_02",
                "IFS_EU_01",
                "IFS_GL_1,IFS_EU_02",
                "IFS_GL_05,IFS_EU_01",
            ],
            description="Model",
            ensure_option=True,
            style=style,
        )
        self.model_offline = widgets.Dropdown(
            options=[
                "IFS_GL_1",
                "IFS_GL_05",
                "IFS_EU_02",
                "IFS_EU_01",
                "IFS_GL_1,IFS_EU_02",
                "IFS_GL_05,IFS_EU_01",
                "None",
            ],
            description="Model offline",
            ensure_option=True,
            style=style,
        )
        self.outgrid = widgets.Dropdown(
            options=utils.fill_locations(path_to_out),
            description="Outgrid",
            ensure_option=True,
            style=style,
        )
        self.outgrid_nest = widgets.Dropdown(
            options=utils.fill_locations(path_to_out) + ["None"],
            description="Outgrid nest",
            value="None",
            ensure_option=True,
            style=style,
        )
        self.w_options_buttons = widgets.RadioButtons(
            options=[],
            description="Workflow options",
            continuous_update=True,
            style=style,
            layout={"width": "max-content"},
        )

        self.w_options = []
        self.w_checkboxes = []
        self.items_checkboxes = widgets.VBox()
        self.check_all = widgets.Checkbox(description="Check all", style=style)

        search_crit = widgets.HBox(
            [
                self.location,
                widgets.VBox(
                    [
                        widgets.HBox([self.model, self.model_offline]),
                        widgets.HBox([self.outgrid, self.outgrid_nest]),
                        ad_q,
                    ]
                ),
            ]
        )
        button = widgets.Button(description="Search", button_style="info")
        self.results = widgets.HTML()
        self.info_out = widgets.Output()
        self.remotes = pd.DataFrame()
        self.full_remotes = pd.DataFrame()

        def on_click(b):
            with self.info_out:
                clear_output()
                self.search()
                self.items_checkboxes.children = [self.check_all] + self.w_checkboxes
                self.check_all.observe(self.check_all_boxes, names="value")

        button.on_click(on_click)

        tabs = widgets.Tab(
            children=[
                widgets.HBox([self.date_range, self.presettings, self.workflow_p]),
                search_crit,
            ]
        )
        tabs.set_title(0, "Basic")
        tabs.set_title(1, "Advance")
        self.bar = widgets.HTML("<hr>")

        super().__init__(
            [tabs, button, self.results, self.info_out, self.bar, self.items_checkboxes]
        )

    def check_all_boxes(self, change=None):
        value = change["new"]
        for i in self.w_checkboxes:
            i.value = value

    def search(self):
        self.results.value = "searching..."

        # Create the query dict with the additional parameters
        query_dict = make_query.make_dict_for_query(ad_q.parameters.items)

        # List of dates
        date_range_p = utils.simulation_dates_parser([self.date_range.value])
        input_phy_dict = {}
        release_dict = {}
        # create the df
        if self.presettings.value != "Default":
            dict_from_extra = make_query.get_extra_(self.presettings.value)
            model = ",".join(dict_from_extra["model"])
            model_offline = ",".join(dict_from_extra["model_offline"])

            self.location.value = list(dict_from_extra["locations"].keys())
            self.model.value = model
            self.model_offline.value = model_offline
            self.outgrid.value = list(dict_from_extra["outgrid"].keys())[0]
            self.outgrid_nest.value = "None"
            if dict_from_extra["outgrid_nest"] != "None":
                self.outgrid_nest.value = list(dict_from_extra["outgrid_nest"].keys())[
                    0
                ]

            query_dict = make_query.make_dict_for_query(dict_from_extra["command"])
            input_phy_dict = make_query.make_dict_for_query(
                dict_from_extra["input_phy"]
            )
            release_dict = make_query.make_dict_for_query(dict_from_extra["release"])

        # fill the dataframe with the values returned by the query
        df = make_query.all_in_query(
            w=self.workflow_p.value,
            model=self.model.value,
            model_offline=self.model_offline.value,
            locations=self.location.value,
            outgrid=self.outgrid.value,
            outgrid_nest=self.outgrid_nest.value,
            dates=date_range_p,
            command=query_dict,
            input_phy=input_phy_dict,
            release=release_dict,
        )
        # make remotes
        self.remotes = df[
            ["w_hash", "RemoteStash", "date", "location", "model", "outgrid"]
        ]
        self.w_options = df["w_hash"].unique()
        self.w_checkboxes = [
            widgets.Checkbox(description=f"{i}", style=style) for i in self.w_options
        ]
        # <mark style="background-color: #{i[:6]};">{i[:6]}</mark>

        # make calendar
        df_for_calendar = df[["date", "FolderData_PK", "w_hash"]]
        df_for_calendar["pairs"] = list(zip(df.FolderData_PK, df.w_hash))
        df_for_calendar = df_for_calendar.groupby(["date"]).agg({"pairs": list})
        df_for_calendar.index = df_for_calendar.index.map(
            lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        )

        range_date = pd.date_range(
            start=date_range_p[0], end=date_range_p[-1], freq="D"
        )
        self.results.value = utils.generate_html_calendar(range_date, df_for_calendar)
