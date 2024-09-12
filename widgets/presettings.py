# -*- coding: utf-8 -*-
import ipywidgets as widgets
from aiida import orm
from utils import make_query
from settings import *

style = {"description_width": "initial"}
box_layout = widgets.Layout(border="solid 0.5px grey", width="100%", padding="20px")


class Presettings(widgets.VBox):
    line = widgets.HTML(
        value="<hr><br>Click on the red box below to delete the selected presetting. Reload to see the changes. "
    )
    warning_text = widgets.HTML(value="⚠️<b>WARNING:</b> this action cannot be undone!")

    def __init__(self, plugin, **kwargs):

        self.plugin = plugin

        if 'parameters' in kwargs.keys():
            self.objects = kwargs['parameters']
        else:
            self.objects = None


        self.save_settings_b = widgets.Checkbox(
            value=False,
            description="Save current settings for future calculations",
            indent=False,
        )
        self.delete_extras_b = widgets.Button(
            value=False, button_style="danger", layout={"width": "35px"}, icon="trash"
        )

        def on_click_d(b):
            qb = orm.QueryBuilder()
            qb.append(
                self.plugin,
                project=["id"],
                filters={"extras": {"has_key": self.settings.value}},
            )
            for i in qb.all():
                node = orm.load_node(i[0])
                node.base.extras.delete(self.settings.value)
                print(i[0], "--> deleted")

        self.delete_extras_b.on_click(on_click_d)

        self.name = widgets.Text(value="", description="Name", style=style)
        self.settings = widgets.ToggleButtons(
            options=make_query.get_extra_(self.plugin, name=None)+['TEST']
        )
        self.settings.observe(self.enable_settings, names="value")

        acc = widgets.Accordion(
            children=[
                widgets.VBox(
                    children=[
                        self.settings,
                        self.line,
                        widgets.HBox([self.delete_extras_b, self.warning_text]),
                    ]
                )
            ]
        )
        acc.set_title(0, "Previous settings")
        acc.selected_index = None

        self.children = [
            widgets.HBox(
                children=[self.save_settings_b]
                + [self.name] * (self.plugin != INVERSION_WORKLFOW)
            ),
            acc,
        ]

        super().__init__(children=self.children, layout=box_layout)

    def enable_settings(self, change=None):
        value = change["new"]
        if value is not "Default":
            prev_dict = make_query.get_extra_(self.plugin, value)
            if 'basic' in self.objects.keys():
                self.update_flexpart_settings(prev_dict)
            elif 'params' in self.objects.keys():
                self.update_inversion_settings(prev_dict['inv_params'])
            else:
                pass
        
    def update_inversion_settings(self, prev_dict):
        self.objects['params'].update(prev_dict)

    def update_flexpart_settings(self, prev_dict):
            # basic
            self.objects['basic'].outgrid.out_loc.value = list(prev_dict["outgrid"].keys())[0]
            if prev_dict["outgrid_nest"] == "None":
                self.objects['basic'].outgrid.out_n_loc.value = prev_dict["outgrid_nest"]
            else:
                self.objects['basic'].outgrid.out_n_loc.value = list(
                    prev_dict["outgrid_nest"].keys()
                )[0]
            for x in self.objects['basic'].locations.locations_widget.children:
                if x.description in prev_dict["locations"]:
                    x.value = True
                else:
                    x.value = False
            self.objects['basic'].release_chunk.value = prev_dict["command"]["release_chunk"]
            self.objects['basic'].offline_integration_time.value = prev_dict[
                "offline_integration_time"
            ]
            self.objects['basic'].integration_time.value = prev_dict["integration_time"]
            self.objects['basic'].model_offline.value = ",".join(prev_dict["model_offline"])
            self.objects['basic'].model.value = ",".join(prev_dict["model"])

            # advance
            self.objects['command_file'].update(prev_dict["command"])
            self.objects['input_phy'].update(prev_dict["input_phy"])
            # release-----
