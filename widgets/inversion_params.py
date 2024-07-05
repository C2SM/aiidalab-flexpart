import ipywidgets as widgets
from IPython.display import display,clear_output

style = {"description_width": "initial"}

class InversionParams(widgets.VBox):

    def __init__(self):
        self.inv_name = widgets.Text(description = 'Inversion name',
                                     style=style)
        self.project = widgets.Text(description = 'Project',
                                    value = "HFO-Europe",
                                     style=style)
        self.institute = widgets.Text(description = 'Institute',
                                      value = 'Empa, Switzerland',
                                     style=style)
        self.iterations = widgets.IntText(description = 'Iterations',
                                      value = 4,
                                      style=style)
        self.contributions = widgets.TagsInput(
            allowed_tags=["mod", "instr", "bg", "var"],
            allow_duplicates=False,
            style=style,
        )
        self.u_model = widgets.Checkbox( value=True,
                                        description='Model component',
                                        style=style)
        self.plot = widgets.Checkbox( value=True,
                                        description='Plot',
                                        style=style)
        
        basic = widgets.VBox(children = [self.project,
                                        self.institute,
                                        self.inv_name,
                                        self.iterations,
                                        self.contributions,
                                        self.u_model,
                                        self.plot])
        
        self.EDGAR_dir = widgets.Text(description = 'EDGAR_dir',
                                 value = "/store/empa/em05/input/EDGAR" )
        self.edgar_version =  widgets.Text(description = 'edgar_version',
                                      value ="8.0_FT2022_GHG")
        self.edgar_year =  widgets.IntText(description ='edgar_year', 
                                      value = 2020)
        self.rescale_EDGAR = widgets.Checkbox(description = 'rescale_EDGAR',
                                         value=False)
        
        edgar = widgets.VBox(children = [
                                         self.EDGAR_dir,
                                         self.edgar_version,
                                         self.edgar_year,
                                         self.rescale_EDGAR
                                         ])
        
        self.apriori_dir = widgets.Text(description = 'apriori_dir',
                                  value = "/project/s1302/shenne/PARIS/HFO_inversions/apriori/population")
        self.apriori_str = widgets.Text(description = 'apriori_str',
                                   value = "<para>_EUROPE_<year>.nc")
        load = widgets.VBox(children = [
            self.apriori_dir,
            self.apriori_str
        ])

        self.apriori_lsm = widgets.Checkbox(description = 'apriori_lsm',
                                       value = True)
        self.homo_by_country= widgets.Checkbox(description = 'homo_by_country',
                                          value = False)
        
        homo = widgets.VBox(children = [
            self.apriori_lsm,
            self.homo_by_country
        ])

        def select_option(name):
            if name == 'EDGAR':
                display(edgar)
                return
            elif name == 'load':
                display(load)
                return
            elif name == 'homo':
                display(homo)
                return
            else:
                clear_output()
        x = widgets.interactive(select_option,name = ['EDGAR', 'load', 'homo'])

        sites_info = None

        use_covariances = widgets.Checkbox(description = 'use_covariances',
                                          value= True) 
        positive = widgets.Text(description ='positive',
                                   value= "Thacker_complete")  
        maxit =  widgets.IntText(description ='maxit',  
                                 value = 100)       
        neg_frac =  widgets.FloatText(description ='neg_frac',
                                      value = 0.0005)
        unc_lt0 = widgets.FloatText(description ='unc_lt0',
                                     value = 0.5)   
        unc_gt0 = widgets.FloatText(description ='unc_gt0',
                                     value =1.01)  
        use_lsm = widgets.Checkbox(description ='use_lsm',
                                   value = False)  
        incl_bg = widgets.Checkbox(description = 'incl_bg',
                                   value = True)  
        bg_by= widgets.Text(description ='bg_by',
                            value = "months")   
        bg_type= widgets.Text(description ='bg_type',
                              value = "boundaries.11reg")
        bg_by_site = widgets.Checkbox(description = 'bg_by_site',
                                      value = False)
        bg_fac = widgets.Checkbox(description = 'bg_fac',
                                  value = False)

        inv_settings = widgets.VBox(children = [use_covariances,
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
                                                x])
        inv_grid = None
        plot_opt = None

        tab = widgets.Tab()
        tab.children = [basic,
                        basic,
                        inv_settings,
                        basic,
                        basic,
                        basic,
                        x,
                        basic,
                        basic
                        ]
        tab.titles=['General',
                    'Input locations',
                    'Sites',
                    'Inversion grid',
                    'Inversion settings',
                    'MODEL-DATA-MISMATCH COVARIANCE',
                    'Apriori',
                    'Apriori covariance',
                    'Plot options']

        super().__init__([tab])
