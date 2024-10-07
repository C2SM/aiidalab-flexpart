# -*- coding: utf-8 -*-
import ipywidgets as widgets
from IPython.display import clear_output
import pandas as pd
from datetime import datetime
from pathlib import Path
from settings import *

from utils import utils, make_query
from widgets import filter

style = {"description_width": "initial"}
path_to_out = Path.cwd() / "config" / "outgrid.yaml"
models_path = Path.cwd() / "config" / "models.yaml"
ad_q = filter.ViewerWidget(mode="params")


class SearchCalculations(widgets.VBox):
    def __init__(self):
        self.date_range = widgets.Text(
            value="2020-10-01--2020-12-31",
            description="Dates",
            description_tooltip="range of dates to query",
            style=style,
        )
        self.presettings = widgets.Dropdown(
            options=make_query.get_extra_(WORKFLOW, name=None),
            description="Presettings",
            description_tooltip="Query for a specific presetting",
            style=style,
        )
        self.location = widgets.SelectMultiple(
            options=utils.get_names_in_group("locations"),
            description="Locations",
            description_tooltip='Multiple values can be selected with "Shift" and/or "ctrl"(or "command")',
            rows=12,
            style=style,
        )
        self.model = widgets.Dropdown(
            options=utils.read_yaml_data(models_path)["models"],
            description="Model",
            ensure_option=True,
            style=style,
        )
        self.model_offline = widgets.Dropdown(
            options=utils.read_yaml_data(models_path)["models_offline"],
            description="Model offline",
            ensure_option=True,
            style=style,
        )
        self.outgrid = widgets.Dropdown(
            options=utils.get_names_in_group("outgrid"),
            description="Outgrid",
            ensure_option=True,
            style=style,
        )
        self.outgrid_nest = widgets.Dropdown(
            options=utils.get_names_in_group("outgrid") + ["None"],
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
        self.download_link = widgets.HTML()
        self.w_check_all = widgets.Checkbox(description="Check all", style=style, value=False)
        self.w_check_all.observe(self.check_all_boxes, names="value")

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
        self.button = widgets.Button(description="Search", button_style="info")
        self.results = widgets.HTML()
        self.info_out = widgets.Output()
        self.remotes = pd.DataFrame()
        self.full_remotes = pd.DataFrame()

        def on_click(b):
            with self.info_out:
                clear_output()
                self.search()
                self.items_checkboxes.children = (
                    [self.w_check_all] + self.w_checkboxes + [self.download_link]
                )                

        self.button.on_click(on_click)

        tabs = widgets.Tab(
            children=[
                widgets.HBox([self.date_range, self.presettings]),
                search_crit,
            ]
        )
        tabs.set_title(0, "Basic")
        tabs.set_title(1, "Advance")
        self.bar = widgets.HTML("<hr>")

        super().__init__(
            [tabs, self.button, self.results, self.info_out, 
             self.bar, self.items_checkboxes]
        )

    def check_all_boxes(self, change=None):
        value = change["new"]
        for i in self.w_checkboxes:
            i.value = value
        
        if value:
            self.fill_model_output_df()
        else:
            self.download_link.value = ""

    def fill_model_output_df(self, change=None):
        """ Reformat and filter q.remotes
            to create q.full_remotes dataframe
            containing the selected results only
        """
        self.full_remotes = pd.DataFrame()
        for i in self.w_checkboxes:
            if i.value == True:
                group_name = i.description
                self.full_remotes = pd.concat([self.full_remotes, self.remotes.loc[self.remotes['w_hash'] == group_name]],
                ignore_index = True)
        if self.full_remotes.empty:
            self.download_link.value = ""
            return 
        
        self.full_remotes['date'] = self.full_remotes['date'].str[:10]
        self.full_remotes['id'] = \
                    self.full_remotes['date'].replace('-','_', regex=True) + \
                    self.full_remotes['location'].replace('-','_', regex=True) 
            
        self.full_remotes['date'] = pd.to_datetime(self.full_remotes['date'])
        self.full_remotes.sort_values(by='date', inplace = True)
        self.full_remotes['label']=self.presettings.value
        self.full_remotes['stash_address_post']=[i.target_basepath for i in self.full_remotes.stash_post]
        self.full_remotes['stash_address_main']=[i.target_basepath for i in self.full_remotes.stash_main]

        columns_raw  = ['date', 'label', 'location', 'stash_address_main']
        if 'stash_offline' in self.full_remotes.columns:
            self.full_remotes['stash_address_offline']=[i.target_basepath for i in self.full_remotes.stash_offline]            
            columns_raw += ['stash_address_offline']
        columns_post = ['date', 'label', 'location', 'stash_address_post']

        self.download_link.value = utils.download_button('flexpart_raw_results.csv',
                    self.full_remotes[columns_raw],
                        'Download .csv table of flexpart raw result locations' )
        self.download_link.value += '<br>'
        self.download_link.value += utils.download_button('postprocessed_results.csv',
                    self.full_remotes[columns_post],
                        'Download .csv table of post-processed result locations' )


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
            dict_from_extra = make_query.get_extra_(WORKFLOW, self.presettings.value)
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
            if "IFS" in model:
                input_phy_dict = "None"
            release_dict = make_query.make_dict_for_query(dict_from_extra["release"])

        # fill the dataframe with the values returned by the query
        df = make_query.all_in_query(
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
        columns_df = ["w_hash", "stash_post", "date", "location", "model", "outgrid", "stash_main"]
        if self.model_offline.value != 'None':
            columns_df += ["stash_offline"]

        self.remotes = df[columns_df]
            
        self.w_options = df["w_hash"].unique()
        self.w_checkboxes = [
            widgets.Checkbox(description=f"{i}", style=style, value=False) for i in self.w_options
        ]
        for w_checkbox in self.w_checkboxes: 
            w_checkbox.observe(self.fill_model_output_df, names='value')

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
