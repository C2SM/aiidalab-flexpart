import ipywidgets as widgets
import aiidalab_widgets_base as awb


class CodeSetup(widgets.VBox):
    new_code_title = widgets.HTML(
        value="""<hr><b>Create new codes</b><br>
                       Click on the button below to create and setup new codes
                       and or computers.""",
    )

    def __init__(self):
        # ComputationalResourcesDatabaseWidget(database_source = 
        #"https://aiidateam.github.io/aiida-resource-registry/database.json"  <-- change?
        #)
        comp_res = awb.ComputationalResourcesWidget()
        comp_res.code_select_dropdown.layout.visibility = "hidden"

        self.children = [
            self.new_code_title,
            comp_res,
        ]

        super().__init__(children=self.children)
