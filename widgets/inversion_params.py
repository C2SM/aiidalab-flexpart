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
        self.inv_name = widgets.Text(description="name", style=style)
        self.project = widgets.Text(
            description="project", value="HFO-Europe", style=style
        )
        self.institute = widgets.Text(
            description="institute", value="Empa, Switzerland", style=style
        )
        self.chunk = widgets.IntText(description = 'chunk', style=style)
        self.chunk_w =  widgets.IntText(description = 'chunk_w', style=style)
        self.general_settings = [
                self.inv_name,
                self.project,
                self.institute,
            ]
        general = widgets.VBox(
            children=self.general_settings+[self.chunk,
                                            self.chunk_w]
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
        self.input_locations = [
                self.ftp_dir,
                self.pop_data_dir,
                self.res_dir,
                self.bot_up_file,
                self.cmask_file,
            ]
        input_loc = widgets.VBox(
            children=self.input_locations
        )
        #   INVERSION GRID
        #######################################
        self.igr_method = widgets.Dropdown(
            description="igr_method", options=["fromAverage", "load"]
        )
        self.inversion_grid = [self.igr_method]
        inv_grid = widgets.VBox(children=self.inversion_grid)

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

        self.apriori_edgar = [
                self.EDGAR_dir,
                self.edgar_version,
                self.edgar_year,
                self.rescale_EDGAR,
            ]
        edgar = widgets.VBox(
            children=self.apriori_edgar
        )

        self.apriori_dir = widgets.Text(
            description="apriori_dir",
            value="/project/s1302/shenne/PARIS/HFO_inversions/apriori/population",
        )
        self.apriori_str = widgets.Text(
            description="apriori_str", value="<para>_EUROPE_<year>.nc"
        )
        self.apriori_load = [self.apriori_dir, self.apriori_str]
        load = widgets.VBox(children=self.apriori_load)

        self.apriori_lsm = widgets.Checkbox(description="apriori_lsm", value=True)
        self.homo_by_country = widgets.Checkbox(
            description="homo_by_country", value=False
        )
        self.apriori_homo = [self.apriori_lsm, self.homo_by_country]
        homo = widgets.VBox(children=self.apriori_homo)

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

        self.x = widgets.interactive(select_option, name=["EDGAR", "load", "homo"])

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
        self.apriori_covariance = [self.u_apriori0, self.max_dist, self.tau_bg, self.u_outer]
        ap_cov = widgets.VBox(
            children=self.apriori_covariance
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
        self.plot_options = [
                self.zlim,
                self.ts_units,
                self.frmt,
                self.map_db,
                self.map_source,
                self.cities,
            ]
        plot_op = widgets.VBox(
            children=self.plot_options
        )

        #    INVERSION SETTINGS
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
        self.inversion_settings=[
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
        inv_settings = widgets.VBox(
            children=self.inversion_settings
        )
        #   MODEL-DATA-MISMATCH COVARIANCE
        ############################################
        self.contributions = widgets.TagsInput(
            description = 'contributions',
            allowed_tags=["mod", "instr", "bg", "var"],
            value = 'mod',
            allow_duplicates=False,
            style=style,
        )
        self.iterations = widgets.IntText(
            description="iterations", value=4, style=style
        )

        self.u_model = widgets.Checkbox(
            value=True, description="model_component", style=style
        )
        self.plot = widgets.Checkbox(value=True, description="plot", style=style)
        self.model_data_mismatch = [self.contributions, self.iterations, self.u_model, self.plot]
        model_mis = widgets.VBox(
            children=self.model_data_mismatch
        )

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
            "MODEL-DATA-MISMATCH COVARIANCE",
            "Apriori",
            "Apriori covariance",
            "Plot options",
        ]
        super().__init__([tab])

    def construct_dict(self):

        big_list = [*self.inversion_settings,
                    *self.general_settings,
                    *self.input_locations,
                    *self.inversion_grid,
                    *self.model_data_mismatch,
                    *self.plot_options,
                    *self.apriori_covariance
                    ]
        
        if self.x.children[0].value == "EDGAR":
                big_list+=self.apriori_edgar
        elif self.x.children[0].value == "load":
                big_list+=self.apriori_load
        elif self.x.children[0].value == "homo":
                big_list+=self.apriori_homo

        sites_dict = {'sites': sens.available_obs_list} 
        d = {x.description: x.value for x in big_list}
        d.update(sites_dict)
        return d
