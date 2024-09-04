# -*- coding: utf-8 -*-
import ipywidgets as widgets
import aiidalab_widgets_base as awb

from aiida import orm

from settings import *

style = {"description_width": "initial"}


def computer_list():
    return [
        c[0].label
        for c in orm.QueryBuilder().append(orm.Computer).all()
        if c[0].label != "localhost"
    ]


class Import(widgets.VBox):

    info_text = widgets.HTML(
        value="""Find for nc lise in stash folder of previous
            Collect sensitivities calclations.
            """
    )
    warning_msg = widgets.HTML(value="")

    def __init__(self):

        self.address = widgets.Text(
            placeholder="Address to files",
            description="Remote address",
            style=style,
        )
        self.time_label = widgets.Text(
            description="Import label",
            style=style,
        )
        self.computer = widgets.Dropdown(
            description="Computer", options=computer_list(), style=style
        )

        btn_submit_1 = awb.SubmitButtonWidget(
            INSPECT,
            inputs_generator=self.prepare_inspect,
            disable_after_submit=False,
            append_output=True,
        )
        btn_submit_1.btn_submit.button_style = "info"
        btn_submit_1.btn_submit.description = "Launch import"

        btn_submit_2 = awb.SubmitButtonWidget(
            INSPECT,
            inputs_generator=self.prepare_inspect_cs,
            disable_after_submit=False,
            append_output=True,
        )
        btn_submit_2.btn_submit.button_style = "success"
        btn_submit_2.btn_submit.description = "Launch CS import"

        acc = widgets.Accordion(
            children=[
                widgets.VBox(
                    children=[
                        widgets.HBox(
                            children=[
                                widgets.VBox(
                                    children=[
                                        self.address,
                                        self.computer,
                                    ]
                                ),
                                widgets.VBox(
                                    children=[
                                        self.time_label,
                                    ]
                                ),
                            ]
                        ),
                        btn_submit_1,
                        self.warning_msg,
                        widgets.HTML(value="<hr>"),
                        self.info_text,
                        btn_submit_2,
                    ]
                )
            ],
        )
        acc.set_title(0, "Import")
        acc.selected_index = None

        self.children = [acc]
        super().__init__(children=self.children)

    def prepare_inspect(self):
        if not self.address.value:
            self.warning_msg.value = "<p style='color:red;'>Empty address</p>"
            return
        computer = orm.load_computer(self.computer.value)
        remote_path = orm.RemoteData(remote_path=self.address.value, computer=computer)
        builder = INSPECT.get_builder()
        builder.time_label = orm.Str(self.time_label.value)
        builder.remotes = {
            "a": remote_path,
        }
        #'b':remote_path_2}
        return builder

    def prepare_inspect_cs(self):
        qb = orm.QueryBuilder()
        qb.append(COLLECT_SENS, tag="cs", filters={"attributes.exit_status": 0})
        qb.append(orm.RemoteStashFolderData, with_incoming="cs", project="*")
        builder = INSPECT.get_builder()
        directories_ = {f"test_{j}": i[0] for j, i in enumerate(qb.all())}
        if directories_:
            builder.remotes_cs = directories_
            return builder
        else:
            print("No files found")
