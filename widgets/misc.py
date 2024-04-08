import ipywidgets as widgets
import aiidalab_widgets_base as awb

style = {'description_width': 'initial'}

class Misc(widgets.VBox):
    def __init__(self):

        self.prepend_text = widgets.Textarea(
            value = '#SBATCH --constraint=mc\n'+\
                    'export OMP_NUM_THREADS=36\n'+\
                    'source $MODULESHOME/init/bash\n'+\
                    'ulimit -s unlimited',
            description='Prepend text:',
            ensure_option=True,
            disabled=False,style=style
        )
        self.account = widgets.Text(
            value='em05',
            description='Account:',
            ensure_option=True,
            disabled=False,style=style
        )
        self.queue_name = widgets.Text(
            value='',
            description='Queue name:',
            disabled=False,style=style
        )
        self.wall_time_cosmo = widgets.IntText(
            value=1800,
            description='Wall time cosmo:',
            disabled=False,style=style
        )
        self.wall_time_ifs = widgets.IntText(
            value=1800,
            description='Wall time ifs:',
            disabled=False,style=style
        )
        comp_res = awb.ComputationalResourcesWidget(enable_quick_setup = False,
                                                    enable_detailed_setup = True)
                                  
        self.children = [
                         self.wall_time_cosmo,
                         self.wall_time_ifs,
                         self.prepend_text,
                         self.account,
                         self.queue_name,
                         comp_res
                    ]

        super().__init__(children = self.children)