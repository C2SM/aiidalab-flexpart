# -*- coding: utf-8 -*-
import ipywidgets as widgets
from IPython.display import display, clear_output
from widgets import sens_query

style = {"description_width": "initial"}
sens = sens_query.SearchSens()


class InversionParams(widgets.VBox):
    def __init__(self):

        #   GENERAL
        ####################################
        self.inv_name = widgets.Text(description="run.str", style=style)
        self.project = widgets.Text(
            description="project", value="HFO-Europe", style=style
        )
        self.institute = widgets.Text(
            description="institute", value="Empa, Switzerland", style=style
        )
        self.chunk = widgets.Dropdown(
            description="chunk", options=["year", "month"], style=style
        )
        self.chunk.observe(self.change_chunk_w_options, names="value")
        self.chunk_w = widgets.Dropdown(
            description="chunk_w",
            options=["year", "3year"],
            style=style,
        )
        self.general_settings = [
            self.inv_name,
            self.project,
            self.institute,
        ]
        general = widgets.VBox(
            children=self.general_settings + [self.chunk, self.chunk_w]
        )

        #  INPUT LOCATIONS
        ########################################
        self.ftp_dir = widgets.Text(
            description="ftp.dir",
            value="tmp",
            layout=widgets.Layout(width="85%"),
        )
        self.pop_data_dir = widgets.Text(
            description="pop.data.dir",
            value="/store/empa/em05/input/GIS/population",
            layout=widgets.Layout(width="85%"),
        )
        self.bot_up_file = widgets.Text(
            description="bot.up.file",
            value="/users/shenne/progs/Rinversion/data/example.bot.up.file.csv",
            layout=widgets.Layout(width="85%"),
        )
        self.cmask_file = widgets.Text(
            description="cmask.file",
            value="/project/s1302/shenne/PARIS/CH4_inversions/Country_masks/country_EUROPE_EEZ_PARIS_gapfilled_fractional.nc",
            layout=widgets.Layout(width="85%"),
        )
        self.input_locations = [
            self.ftp_dir,
            self.pop_data_dir,
            self.bot_up_file,
            self.cmask_file,
        ]
        input_loc = widgets.VBox(children=self.input_locations)
        #   INVERSION GRID
        #######################################
        self.igr_fn = widgets.Text(
            description="igr.fn",
            value="/home/hes134/projects/inversion/GEOmon/emission_grid_brunner.txt",
            layout=widgets.Layout(width="60%"),
        )
        self.xrng = widgets.FloatRangeSlider(
            description="xrng",
            value=[-13.0, 26.4],
            min=-180,
            max=180,
            layout=widgets.Layout(width="60%"),
        )
        self.yrng = widgets.FloatRangeSlider(
            description="yrng",
            value=[36.0, 70.0],
            min=-90,
            max=90,
            layout=widgets.Layout(width="60%"),
        )
        self.nn_grid_target = widgets.IntText(description="nn.grid.target", value=700)
        self.min_tau = widgets.IntText(description="min.tau", value=86400)
        self.igr_merge = widgets.IntSlider(
            description="igr.merge", value=6, min=0, max=10
        )
        self.remove_zero_only = widgets.Checkbox(
            description="remove.zero.only", value=True
        )
        self.remove_pure_ocean = widgets.Checkbox(
            description="remove.pure.ocean", value=True
        )

        self.fromaverage = [
            self.xrng,
            self.yrng,
            self.nn_grid_target,
            self.min_tau,
            self.igr_merge,
            self.remove_zero_only,
            self.remove_pure_ocean,
        ]
        fromaverage = widgets.VBox(children=self.fromaverage)
        self.load = [self.igr_fn]
        fromload = widgets.VBox(children=self.load)

        def select_option_inv_grid(igr_method):
            if igr_method == "fromAverage":
                display(fromaverage)
                return
            elif igr_method == "load":
                display(fromload)
                return
            else:
                clear_output()

        self.igr_method = widgets.interactive(
            select_option_inv_grid, igr_method=["fromAverage", "load"]
        )

        inv_grid = widgets.VBox(children=[self.igr_method])

        #   APRIORI
        #######################################
        self.EDGAR_dir = widgets.Text(
            description="EDGAR.dir", value="/store/empa/em05/input/EDGAR"
        )
        self.edgar_version = widgets.Text(
            description="edgar.version", value="8.0_FT2022_GHG"
        )
        self.edgar_year = widgets.IntText(description="edgar.year", value=2020)
        self.rescale_EDGAR = widgets.Checkbox(description="rescale.EDGAR", value=False)

        self.apriori_edgar = [
            self.EDGAR_dir,
            self.edgar_version,
            self.edgar_year,
            self.rescale_EDGAR,
        ]
        edgar = widgets.VBox(children=self.apriori_edgar)

        self.apriori_dir = widgets.Text(
            description="apriori.dir",
            value="/project/s1302/shenne/PARIS/HFO_inversions/apriori/population",
        )
        self.apriori_str = widgets.Text(
            description="apriori.str", value="<para>_EUROPE_<year>.nc"
        )
        self.apriori_load = [self.apriori_dir, self.apriori_str]
        load = widgets.VBox(children=self.apriori_load)

        self.apriori_lsm = widgets.Checkbox(description="apriori.lsm", value=True)
        self.homo_by_country = widgets.Checkbox(
            description="homo.by.country", value=False
        )
        self.apriori_homo = [self.apriori_lsm, self.homo_by_country]
        homo = widgets.VBox(children=self.apriori_homo)

        def select_option(apriori_method):
            if apriori_method == "EDGAR":
                display(edgar)
                return
            elif apriori_method == "load" or apriori_method == "load_nc":
                display(load)
                return
            elif apriori_method == "homo":
                display(homo)
                return
            else:
                clear_output()

        self.x = widgets.interactive(
            select_option, 
            apriori_method=["EDGAR", "load", "load_nc", "homo"],
        )

        #   APRIORI COVARIANCE
        ########################################
        self.u_apriori0 = widgets.FloatText(
            description="u.apriori0",
            value=3,
        )
        self.max_dist = widgets.FloatText(
            description="max.dist",
            value=500.0,
        )
        self.tau_bg = widgets.FloatText(
            description="tau.bg",
            value=60.0,
        )
        self.u_outer = widgets.FloatText(
            description="u.outer",
            value=0.2,
        )
        self.apriori_covariance = [
            self.u_apriori0,
            self.max_dist,
            self.tau_bg,
            self.u_outer,
        ]
        ap_cov = widgets.VBox(children=self.apriori_covariance)

        #   PLOT OPTIONS
        #########################################
        self.zlim = widgets.Text(description="zlim", value="[1.0, 1.0e+04]")
        self.ts_units = widgets.Dropdown(
            description="ts.units", options=["ppt", "ppb", "ppm"]
        )
        self.frmt = widgets.Dropdown(description="frmt", options=["png16m", "eps"])
        self.map_db = widgets.Text(description="map.db", value="world.TM")

        self.map_source = widgets.Text(description="map.source", value="myRplots")

        self.cities = widgets.Checkbox(description="cities", value=False)
        self.plot_options = [
            self.zlim,
            self.ts_units,
            self.frmt,
            self.map_db,
            self.map_source,
            self.cities,
        ]
        plot_op = widgets.VBox(children=self.plot_options)

        #    INVERSION SETTINGS
        #########################################
        use_covariances = widgets.Checkbox(description="use.covariances", value=True)
        positive = widgets.Dropdown(
            description="positive",
            options=["Thacker_complete", "Stohl", "Thacker_xOnly", "none"],
        )
        maxit = widgets.IntText(description="maxit", value=100)
        neg_frac = widgets.FloatText(description="neg.frac", value=0.0005)
        unc_lt0 = widgets.FloatText(description="unc.lt0", value=0.5)
        unc_gt0 = widgets.FloatText(description="unc.gt0", value=1.01)
        use_lsm = widgets.Checkbox(description="use.lsm", value=False)
        incl_bg = widgets.Checkbox(description="incl.bg", value=True)
        bg_by = widgets.Text(description="bg.by", value="months")
        bg_type = widgets.Dropdown(
            description="bg.type",
            options=[
                "boundaries.11reg",
                "single",
                "boundaries",
            ],
        )
        bg_by_site = widgets.Checkbox(description="bg.by.site", value=False)
        bg_fac = widgets.Checkbox(description="bg.fac", value=False)
        incl_outer = widgets.Checkbox(description="incl.outer", value=True)
        self.inversion_settings = [
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
        inv_settings = widgets.VBox(children=self.inversion_settings)
        #   MODEL-DATA-MISMATCH COVARIANCE
        ############################################
        self.obs_mod_unc_contrs = widgets.SelectMultiple(
            description="obs.mod.unc.contrs",
            options=["mod", "instr", "bg", "var"],
            value=["mod", "instr", "bg", "var"],
            style=style,
        )
        self.iterations = widgets.IntText(description="it.u.obs", value=4, style=style)

        self.u_model = widgets.Checkbox(
            value=True, description="scale.u.model", style=style
        )
        self.plot = widgets.Checkbox(
            value=True, description="plot.obs.mod.unc", style=style
        )
        self.dist_adj_method = widgets.Dropdown(
            description="dist.adj.method", 
            options=["relative", "rmsOnly", "Stohl"],
            style=style
        )
        self.tau_obs = widgets.FloatText(description="tau.obs.default", style=style,value=0.2)
        # TODO inclue none value
        self.covar_nn_lag = widgets.IntSlider(
            description="covar.nn.lag",
            value=2,
            min=1,
            max=24,
        )

        self.model_data_mismatch = [
            self.obs_mod_unc_contrs,
            self.iterations,
            self.u_model,
            self.plot,
            self.dist_adj_method,
            self.tau_obs,
            self.covar_nn_lag,
        ]
        model_mis = widgets.VBox(children=self.model_data_mismatch)

        ############################################
        tab = widgets.Tab()
        tab.children = [
            general,
            input_loc,
            inv_grid,
            inv_settings,
            model_mis,
            self.x,
            ap_cov,
            plot_op,
        ]
        tab.titles = [
            "General",
            "Input locations",
            "Inversion grid",
            "Inversion settings",
            "Model-data-mismatch",
            "Apriori",
            "Apriori covariance",
            "Plot options",
        ]
        super().__init__([tab])

    def change_chunk_w_options(self, change=None):
        value = change["new"]
        if value == "year":
            self.chunk_w.options = ["year", "3year"]
        else:
            self.chunk_w.options = ["month", "3month"]

    def construct_dict(self):

        big_list = [
            *self.inversion_settings,
            *self.general_settings,
            *self.input_locations,
            *self.model_data_mismatch,
            *self.plot_options,
            *self.apriori_covariance,
        ]

        if self.x.children[0].value == "EDGAR":
            big_list += self.apriori_edgar
        elif self.x.children[0].value == "load":
            big_list += self.apriori_load
        elif self.x.children[0].value == "homo":
            big_list += self.apriori_homo

        if self.igr_method.children[0].value == "fromAverage":
            big_list += self.fromaverage
        elif self.igr_method.children[0].value == "load":
            big_list += self.load

        sites_dict = {"sites": sens.available_obs_list}
        d = {x.description: x.value for x in big_list}
        # hardcoded dictionary
        d.update(
            {
                "Interactive": False,
                "main.dir": "",
                "init.dir": "",
                "data.dir": "",
                "igr.method": self.igr_method.children[0].value,
                "apriori.method": self.x.children[0].value,
            }
        )
        d.update(sites_dict)
        return d
