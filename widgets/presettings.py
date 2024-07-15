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

    def __init__(self, command_file, input_phy, release, basic):

        self.command_file = command_file
        self.basic = basic
        self.input_phy = input_phy
        self.release = release

        self.save_settings_b = widgets.Checkbox(
            value=False,
            description="Save current settings for future calculations",
            disabled=False,
            indent=False,
        )
        self.delete_extras_b = widgets.Button(
            value=False,
            description="x",
            button_style="danger",
            layout={"width": "30px"},
        )

        def on_click_d(b):
            qb = orm.QueryBuilder()
            qb.append(
                WORKFLOW,
                project=["id"],
                filters={"extras": {"has_key": self.settings.value}},
            )
            for i in qb.all():
                node = orm.load_node(i[0])
                node.base.extras.delete(self.settings.value)
                print(i[0], "--> deleted")

        self.delete_extras_b.on_click(on_click_d)

        self.name = widgets.Text(
            value="", placeholder="", description="Name", disabled=False, style=style
        )
        self.settings = widgets.ToggleButtons(
            options=make_query.get_extra_(name=None),
            description="",
            button_style="",
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
            widgets.HBox(children=[self.save_settings_b, self.name]),
            acc,
        ]

        super().__init__(children=self.children, layout=box_layout)

    def enable_settings(self, change=None):
        # dict load
        value = change["new"]
        if value is not "Default":
            prev_dict = make_query.get_extra_(value)

            # basic
            self.basic.outgrid.out_loc.value = list(prev_dict["outgrid"].keys())[0]
            if prev_dict["outgrid_nest"] == "None":
                self.basic.outgrid.out_n_loc.value = prev_dict["outgrid_nest"]
            else:
                self.basic.outgrid.out_n_loc.value = list(
                    prev_dict["outgrid_nest"].keys()
                )[0]
            for x in self.basic.locations.locations_widget.children:
                if x.description in prev_dict["locations"]:
                    x.value = True
                else:
                    x.value = False
            self.basic.release_chunk.value = prev_dict["command"]["release_chunk"]
            self.basic.offline_integration_time.value = prev_dict[
                "offline_integration_time"
            ]
            self.basic.integration_time.value = prev_dict["integration_time"]
            self.basic.model_offline.value = ",".join(prev_dict["model_offline"])
            self.basic.model.value = ",".join(prev_dict["model"])

            # advance
            self.command_file.update(prev_dict["command"])
            self.input_phy.update(prev_dict["input_phy"])
            # release-----
