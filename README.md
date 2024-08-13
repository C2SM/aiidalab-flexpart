# Aiida FLEXPART plugin
An [AiiDA](http://aiida-core.readthedocs.io/) plugin for FLEXPART cosmo and ifs simulations, and inversions.

This plugin contains 5 types of calculations:

- `flexpart.cosmo`
- `flexpart.ifs`
- `flexpart.post`
- `collect.sensitivities`
- `inversion.calc`

A data plugin:

- `netcdf.data`

and 2 workflows:

- `flexpart.multi_workflow`: A workflow that can be used to submit flexpart calculations for multiple days.
- `inspect.workflow`


- [AiiDA FLEXPART plugin](#aiida-flexpart-plugin)
  - [Installation](#installation)
    - [Computers setup](#computers-setup)
    - [Codes Setup](#codes-setup)
    - [Enable caching](#enable-caching)
  - [Workflow](#workflow)
    - [Structure](#structure)
    - [Running the workflow launcher](#workflow-launcher)
    - [Monitoring the workflow](#monitoring-the-workflow)
  - [Flexpart Aiidalab app](#flexpart-aiidalab-app)
    - [Running the workflow](#running-the-workflow)
    - [Quering](#quering)
  - [Development guide](#development-guide)



## Installation
Install the plugins with:
```hs
pip install -e .
```
Install [Aiida shell](https://aiida-shell.readthedocs.io/en/latest/):
```
pip install aiida-shell
```
Additional packages for Aiidalab:

```hs
pip install aiidalab-widgets-base
```
(it can also be installed through Aiidalab web)

### Computers setup
It is necessary to setup two different configurations of Daint. The configuration files are in `/config` by the names of `computer-daint.yaml` and `computer-daint-direct.yaml`. To set up the computers:

```hs
verdi computer setup --config NAME.yaml
```
followed by:

```hs
verdi computer configure core.ssh COMPUTER-NAME
```
refer to the `daint-configure.yaml` for answering the questions asked by Aiida after runnign the above line.

Finally, test the computer with:
```hs
verdi computer test COMPUTER-NAME
```

After the setup of both computers, daint and daint-direct, you can check the configuration of each by:
```hs
verdi computer list
```
Should display:
```
Report: List of configured computers
Report: Use 'verdi computer show COMPUTERLABEL' to display more detailed information
* daint
* daint-direct-106
* localhost
```
### Codes setup
Use the following line with all the <i>.yaml</i> files in `/config` that start with <i>code_</i>
```hs
verdi code create core.code.installed --config NAME.yaml
```
Similarly as with the computers, one can check the list of all the installed codes by:
```hs
verdi code list
```
Should display:
```
Full label                           Pk  Entry point
---------------------------------  ----  -------------------
flexpart_cosmo@daint                  1  core.code.installed
flexpart_ifs@daint                    2  core.code.installed
post-processing@daint                 3  core.code.installed
check-cosmo-data@daint-direct-106     4  core.code.installed
check-ifs-data@daint-direct-106       5  core.code.installed
```
<b>Note</b> that the pk numbers may differ.

### Enable caching
Make sure caching is enabled by typing:<br>

```
verdi config list caching
```
if False, enable it with:

```hs
verdi config set caching.default_enabled True
```

## Workflow

### Structure

The following is the workflow structure. It will loop over all the given dates. If model offline is not none, integration_time_offline should be greater than zero. The available models for cosmo are: <i>cosmo7, cosmo1</i> and <i>kenda1</i>. And the ECMWF models: <i>IFS_GL_05, IFS_GL_1, IFS_EU_02</i> and <i>IFS_EU_01</i>. Both, model and model offline can be set as a list of the previous.

```mermaid
   graph TD;
      id1{MODEL}--cosmo models-->PREPARE_COSMO_METEO_FILES;
      id1{MODEL}--ecmwf models-->PREPARE_IFS_METEO_FILES;

      subgraph  -
      PREPARE_COSMO_METEO_FILES-->RUN_FLEXPART_COSMO;
      end
      subgraph IFS
      PREPARE_IFS_METEO_FILES-->RUN_FLEXPART_IFS;
      end

      RUN_FLEXPART_COSMO-->id2{MODEL_OFFLINE};
      id2{MODEL_OFFLINE}--ecmwf models-->PREPARE_IFS_METEO_FILES;
      id2{MODEL_OFFLINE}--none -->POST-PROCESSING;
      RUN_FLEXPART_IFS-->POST-PROCESSING;
```

The second step deals withthe various results of the post-processings produced previously.

```mermaid
   graph TD;

      POST-PROCESSING_1 -->COLLECT_SENSITIVITIES;
      POST-PROCESSING_2 -->COLLECT_SENSITIVITIES;
      POST-PROCESSING_3 -->COLLECT_SENSITIVITIES;
      POST-PROCESSING_4 -->COLLECT_SENSITIVITIES;

      COLLECT_SENSITIVITIES --> RESULTS(NetCFD);
```

Next:

```mermaid
   graph TD;

      NetCFD_1-- external --> INVERSION;
      NetCFD_2-- observations --> INVERSION;
      NetCFD_3-- FLEXPART --> INVERSION;

      INVERSION --> RESULTS;

```

#### Storage
Results will be stashed in `/store/empa/em05/{username}/aiida_stash` directory, and will include the following:

- `header*`
- `partposit_inst*`
- `grid_time_*.nc`
- `aiida.out`
- `boundary_sensitivity_*.nc` (post-processsing only)

And from the collect sensitivities calcjob:

- `<LOCATION>_<DOMAIN>_<YYYYMM>.nc`
- `aiida.out`

### Running the workflow with the launcher

The workflow can be triggered directly through a verdi command that launchs the script `example_workflow_combi.py`. The calculation inputs are
in several yaml files in `/example/inputs/`. The script reads directly from the yaml files. Some parameters, however, need to be
settled from the launcher script, e.g., simulation_dates, model, model_offline, etc.

```hs
cd aiida-flexpart/examples
verdi run example_workflow_combi.py --code flexpart-cosmo@daint
```
### Monitoring the workflow

The worflow can be monitored using

```hs
verdi process list
```
 or
```hs
verdi process status PK
```
To check the status of terminated jobs use:
```hs
verdi process list -a
```

## Flexpart Aiidalab app

Check [Aiidalab user guide](https://aiidalab.readthedocs.io/en/latest/usage/index.html) for details on how to use and configure Aiida lab.

```hs
docker run -p 8888:8888 aiidalab/full-stack
```
> [!NOTE]<br>
> NOTE

## Development guide
