# -*- coding: utf-8 -*-
from aiida import plugins

# Workflows
WORKFLOW = plugins.WorkflowFactory("flexpart.multi_workflow")  # multi_dates
INSPECT = plugins.WorkflowFactory("inspect.workflow")

# Calculations
COSMO = plugins.CalculationFactory("flexpart.cosmo")
IFS = plugins.CalculationFactory("flexpart.ifs")
POST = plugins.CalculationFactory("flexpart.post")
COLLECT_SENS = plugins.CalculationFactory("collect.sensitivities")
INVERSION = plugins.CalculationFactory("inversion.calc")

# Data
NETCDF = plugins.DataFactory("netcdf.data")
