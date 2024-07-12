# -*- coding: utf-8 -*-
import ipywidgets as widgets
from IPython.display import display, clear_output

style = {"description_width": "initial"}


class InversionParams(widgets.VBox):
    def __init__(self):

        #   GENERAL
        ####################################
        self.inv_name = widgets.Text(description="Inversion name", style=style)
        self.project = widgets.Text(
            description="Project", value="HFO-Europe", style=style
        )
        self.institute = widgets.Text(
            description="Institute", value="Empa, Switzerland", style=style
        )

        general = widgets.VBox(
            children=[
                self.project,
                self.institute,
                self.inv_name,
            ]
        )

        #  INPUT LOCATIONS
        ########################################
        self.ftp_dir = widgets.Text(
            description="ftp_dir", value="/scratch/snx3000/shenne/tmp"
        )
        self.pop_data_dir = widgets.Text(
            description="pop_data_dir", value="/store/empa/em05/input/GIS/population"
        )
        self.res_dir = widgets.Text(
            description="res_dir",
            value="/scratch/snx3000/shenne/HFO_inversions/results_202406/",
        )
        self.bot_up_file = widgets.Text(
            description="bot_up_file",
            value="/project/s1302/shenne/PARIS/HFO_inversions/code/invSettings/bot.up.uniform.csv",
        )
        self.cmask_file = widgets.Text(
            description="cmask_file",
            value="/project/s1302/shenne/PARIS/CH4_inversions/Country_masks/country_EUROPE_EEZ_PARIS_gapfilled_fractional.nc",
        )
        input_loc = widgets.VBox(
            children=[
                self.ftp_dir,
                self.pop_data_dir,
                self.res_dir,
                self.bot_up_file,
                self.cmask_file,
            ]
        )

        #   SITES
        #######################################
        #   INVERSION GRID
        #######################################
        self.igr_method = widgets.Dropdown(
            description="igr_method", options=["fromAverage", "load"]
        )
        inv_grid = widgets.VBox(children=[self.igr_method])

        #   APRIORI
        #######################################
        self.EDGAR_dir = widgets.Text(
            description="EDGAR_dir", value="/store/empa/em05/input/EDGAR"
        )
        self.edgar_version = widgets.Text(
            description="edgar_version", value="8.0_FT2022_GHG"
        )
        self.edgar_year = widgets.IntText(description="edgar_year", value=2020)
        self.rescale_EDGAR = widgets.Checkbox(description="rescale_EDGAR", value=False)

        edgar = widgets.VBox(
            children=[
                self.EDGAR_dir,
                self.edgar_version,
                self.edgar_year,
                self.rescale_EDGAR,
            ]
        )

        self.apriori_dir = widgets.Text(
            description="apriori_dir",
            value="/project/s1302/shenne/PARIS/HFO_inversions/apriori/population",
        )
        self.apriori_str = widgets.Text(
            description="apriori_str", value="<para>_EUROPE_<year>.nc"
        )
        load = widgets.VBox(children=[self.apriori_dir, self.apriori_str])

        self.apriori_lsm = widgets.Checkbox(description="apriori_lsm", value=True)
        self.homo_by_country = widgets.Checkbox(
            description="homo_by_country", value=False
        )

        homo = widgets.VBox(children=[self.apriori_lsm, self.homo_by_country])

        def select_option(name):
            if name == "EDGAR":
                display(edgar)
                return
            elif name == "load":
                display(load)
                return
            elif name == "homo":
                display(homo)
                return
            else:
                clear_output()

        x = widgets.interactive(select_option, name=["EDGAR", "load", "homo"])

        #   APRIORI COVARIANCE
        ########################################
        self.u_apriori0 = widgets.FloatText(
            description="u_apriori0",
            value=3,
        )
        self.max_dist = widgets.FloatText(
            description="max_dist",
            value=500.0,
        )
        self.tau_bg = widgets.FloatText(
            description="tau_bg",
            value=60.0,
        )
        self.u_outer = widgets.FloatText(
            description="tau_bg",
            value=0.2,
        )
        ap_cov = widgets.VBox(
            children=[self.u_apriori0, self.max_dist, self.tau_bg, self.u_outer]
        )

        #   PLOT OPTIONS
        #########################################
        self.zlim = widgets.Text(description="map_db", value="1.0, 1.0e+04")
        self.ts_units = widgets.Dropdown(
            description="ts_units", options=["ppt", "ppb", "ppm"]
        )
        self.frmt = widgets.Dropdown(description="frmt", options=["png16m", "eps"])
        self.map_db = widgets.Text(description="map_db", value="world.TM")

        self.map_source = widgets.Text(description="map_source", value="myRplots")

        self.cities = widgets.Checkbox(description="cities", value=False)
        plot_op = widgets.VBox(
            children=[
                self.zlim,
                self.ts_units,
                self.frmt,
                self.map_db,
                self.map_source,
                self.cities,
            ]
        )

        #       INVERSION SETTINGS
        #########################################
        use_covariances = widgets.Checkbox(description="use_covariances", value=True)
        positive = widgets.Text(description="positive", value="Thacker_complete")
        maxit = widgets.IntText(description="maxit", value=100)
        neg_frac = widgets.FloatText(description="neg_frac", value=0.0005)
        unc_lt0 = widgets.FloatText(description="unc_lt0", value=0.5)
        unc_gt0 = widgets.FloatText(description="unc_gt0", value=1.01)
        use_lsm = widgets.Checkbox(description="use_lsm", value=False)
        incl_bg = widgets.Checkbox(description="incl_bg", value=True)
        bg_by = widgets.Text(description="bg_by", value="months")
        bg_type = widgets.Text(description="bg_type", value="boundaries.11reg")
        bg_by_site = widgets.Checkbox(description="bg_by_site", value=False)
        bg_fac = widgets.Checkbox(description="bg_fac", value=False)
        incl_outer = widgets.Checkbox(description="incl_outer", value=True)

        inv_settings = widgets.VBox(
            children=[
                use_covariances,
                positive,
                maxit,
                neg_frac,
                unc_lt0,
                unc_gt0,
                use_lsm,
                incl_bg,
                bg_by,
                bg_type,
                bg_by_site,
                bg_fac,
                incl_outer,
            ]
        )
        #   MODEL-DATA-MISMATCH COVARIANCE
        ############################################
        self.contributions = widgets.TagsInput(
            allowed_tags=["mod", "instr", "bg", "var"],
            allow_duplicates=False,
            style=style,
        )
        self.iterations = widgets.IntText(
            description="Iterations", value=4, style=style
        )

        self.u_model = widgets.Checkbox(
            value=True, description="Model component", style=style
        )
        self.plot = widgets.Checkbox(value=True, description="Plot", style=style)
        model_mis = widgets.VBox(
            children=[self.contributions, self.iterations, self.u_model, self.plot]
        )

        ############################################
        tab = widgets.Tab()
        tab.children = [
            general,
            input_loc,
            general,
            inv_grid,
            inv_settings,
            model_mis,
            x,
            ap_cov,
            plot_op,
        ]
        tab.titles = [
            "General",
            "Input locations",
            "Sites",
            "Inversion grid",
            "Inversion settings",
            "MODEL-DATA-MISMATCH COVARIANCE",
            "Apriori",
            "Apriori covariance",
            "Plot options",
        ]
        super().__init__([tab])
