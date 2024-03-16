from aiida import plugins, orm
import pandas as pd

# Plugins
workflow = plugins.WorkflowFactory("flexpart.multi_dates")
flexpart_cosmo = plugins.CalculationFactory("flexpart.cosmo")
flexpart_ifs = plugins.CalculationFactory("flexpart.ifs")
flexpart_post = plugins.CalculationFactory("flexpart.post")


def make_dict_for_query(dict_):
    query_dict = {}
    if type(dict_) == tuple:
        for item in dict_:
            query_dict['attributes.'+item.children[0].value] = eval(item.children[1].value)
    else:
        for k,v in dict_.items():
            query_dict['attributes.'+k] = v

    return query_dict


def get_extra_(name):
    """
    Convenient function to return extra information.

    Parameters
    ----------
    name: str
        Name of the extra dictionary.

    Return
    ------
        If name is set to None, it will return the available
        names. Otherwise it returns the dictionary of the
        given name.
    """
    qb = orm.QueryBuilder()
    if name:
        qb.append(
            workflow,
            project=["extras." + name],
            filters={"attributes.exit_status": 0, "extras": {"has_key": name}},
        )
        return qb.all()[0][0]
    qb.append(workflow, project=["extras"], filters={"attributes.exit_status": 0})
    name_list = []
    for dict_ in qb.all():
        for n in dict_[0].keys():
            if n not in name_list and n != "_aiida_hash":
                name_list.append(n)
    return ["Default"] + name_list


def all_in_query(
    model, 
    model_offline, 
    locations, 
    outgrid, 
    outgrid_nest, 
    dates, 
    command,
    input_phy
) -> pd.DataFrame:
    """
    function that constructs the query and returns a dataframe with the
    query information.

    Parameters
    ----------
    model: str
    modle_offline: str
    locations: list
    outgrid: str
    outgrid_nest: str
    dates: list
    command: dict

    Return
    ------
        Pandas dataframe with the query results.
    """
    columns = ["w_hash", "outgrid",'location', "model", "date", "RemoteStash", "FolderData_PK"]

    # Append calcjobs and workflow
    qb = orm.QueryBuilder()
    qb.append(workflow, tag="w", project=["*"], filters={"attributes.exit_status": 0})
    qb.append(
        [flexpart_cosmo, flexpart_ifs],
        with_incoming="w",
        tag="calcs",
        filters={"attributes.exit_status": 0},
    )
    qb.append(flexpart_post, with_ancestors="calcs", tag="post")

    # Outgrid and Outgrid Nest
    qb.append(
        orm.Dict,
        with_outgoing="w",
        edge_filters={"label": {"like": "outgrid"}},
        filters={"attributes": {"has_key": outgrid}},
        project="attributes",
    )
    
    # Locations
    qb.append(
        orm.Dict,
        with_outgoing="w",
        edge_filters={"label": {"like": "locations"}},
        filters={"attributes": {"or": [{"has_key": l} for l in locations]}},
        project='attributes'
    )

    # Models
    qb.append(
        orm.List,
        with_outgoing="w",
        edge_filters={"label": {"like": "model"}},
        filters={
            "attributes.list": {"and": [{"contains": [i]} for i in model.split(",")]}
        },
        project="attributes.list",
    )
    if model_offline !='None':
        qb.append(
            orm.List,
            with_outgoing="w",
            edge_filters={"label": {"like": "model_offline"}},
            filters={
                "attributes.list": {
                    "and": [{"contains": [i]} for i in model_offline.split(",")]
                }
            },
            project="attributes.list",
        )

    # Command, Release and Input_phy
    filter_commad_dict = {
        "attributes.simulation_date": {"or": [{"==": i} for i in dates]}
    }
    filter_commad_dict.update(command)
   
    qb.append(
        orm.Dict,
        with_outgoing="calcs",
        edge_filters={"label": {"like": "model_settings__command"}},
        filters=filter_commad_dict,
        project="attributes.simulation_date",
    )
    qb.append(
        orm.Dict,
        with_outgoing="calcs",
        edge_filters={"label": {"like": "model_settings__input_phy"}},
        filters=input_phy,
    )
    """qb.append(
        orm.Dict,
        with_outgoing="calcs",
        edge_filters={"label": {"like": "model_settings__release_settings"}},
        filters=filter_commad_dict,
    )"""

    # Post-processing data
    qb.append(orm.RemoteStashFolderData, with_incoming="post", project="*")
    qb.append(orm.FolderData, with_incoming="post", project="id")

    if outgrid_nest!='None':
        qb.append(
            orm.Dict,
            with_outgoing="w",
            edge_filters={"label": {"like": "outgrid_nest"}},
            filters={"attributes": {"has_key": outgrid_nest}},
            project="attributes",
        )
        columns += ["outgrid_n"]

    # Dataframe construct
    df = pd.DataFrame(qb.all(), columns=columns)
    df['location'] = df['location'].map(lambda x: list(x.keys())[0])
    df['outgrid'] = df['outgrid'].map(lambda x: list(x.keys())[0])
    df['model'] = df['model'].map(lambda x: ','.join(x))
    if 'outgrid_n' in df.columns:
            df['outgrid_n'] = df['outgrid_n'].map(lambda x: list(x.keys())[0])
    df['w_hash'] = df['w_hash'].map(lambda x: x.get_hash())
    df = df.drop_duplicates(subset=['w_hash', 'date','location'])

    return df
