# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
"""
Usage of the discretisation error verification tool
===================================================

Check discretisation error of the Abaqus cantilever beam model using the
'DiscretizationSolutionVerification' tool.
"""

from __future__ import annotations

import logging

from gemseo.utils.directory_creator import DirectoryNamingMethod
from numpy import array
from numpy import atleast_1d
from vims import EXAMPLE_RUNS_DIR_NAME

from vimseo.api import activate_logger
from vimseo.api import create_model
from vimseo.core.base_integrated_model import IntegratedModelSettings
from vimseo.tools.verification.solution_verification import (
    DiscretizationSolutionVerification,
)

# %%
# First we define the logger level and the directory under which results are written:
activate_logger(level=logging.INFO)

# %%
# Then the tool that check convergence and discretisation error is instantiated:
verificator = DiscretizationSolutionVerification(
    directory_naming_method=DirectoryNamingMethod.NUMBERED,
    working_directory="DiscretizationSolutionVerification_results",
)

# %%
# The model to verify is the following:
model_name = "BendingTestFem"
load_case = "Cantilever"
model = create_model(
    model_name,
    load_case,
    model_options=IntegratedModelSettings(
        directory_archive_root=f"../../../{EXAMPLE_RUNS_DIR_NAME}/archive/solution_verification",
        directory_scratch_root=f"../../../{EXAMPLE_RUNS_DIR_NAME}/scratch/solution_verification",
        cache_file_path=f"../../../{EXAMPLE_RUNS_DIR_NAME}/caches/solution_verification/{model_name}_{load_case}_cache.hdf",
    ),
)

# %%
# Then we define the mesh sizes to explore
NOMINAL_ELEMENT_SIZE = 4.32
RATIO = 1.2
mesh_sizes = array([
    NOMINAL_ELEMENT_SIZE * RATIO,
    NOMINAL_ELEMENT_SIZE,
    NOMINAL_ELEMENT_SIZE / RATIO,
    NOMINAL_ELEMENT_SIZE / RATIO**2,
])
print("Mesh sizes to evaluate: ", mesh_sizes)
print("Outputs", model.get_output_data_names())

model.default_input_data["element_integration"] = array(["QUADRATIC"])

verificator.execute(
    model=model,
    element_size_variable_name="element_size",
    element_size_values=mesh_sizes,
    output_name="reaction_forces",
)
print(verificator.result)

# %%
# The results can be saved on disk:
verificator.save_results()

# %%
# The saved results can be loaded in a dedicated dashboard to be explored.
# The dashboard is opened by typing ``dashboard_verification`` in a terminal,
# and selecting the tab ``Convergence case``.

# %%
# Alternatively, the results can be plotted from a Python script:
figures = verificator.plot_results(
    verificator.result,
    save=False,
    show=True,
    directory_path=verificator.working_directory,
)

# %%
# The output value versus the convergence variable:
figures["convergence_cross_validation"]

# %%
# The error versus the converged value:
figures["error_versus_element_size"]

# %%
# The cpu time versus the relative error with respect to the Richardson extrapolation:
figures["relative_error_versus_cpu_time"]

# %%
# The element size versus the relative error with respect to the Richardson extrapolation:
figures["relative_error_versus_element_size"]

# %%
# It is also possible to prescribe an element size ratio,
# which allows to automatically construct the element size array:

model.default_input_data["element_size"] = atleast_1d(NOMINAL_ELEMENT_SIZE)
verificator.execute(
    model=model,
    element_size_variable_name="element_size",
    element_size_ratio=RATIO,
    output_name="reaction_forces",
)

# %%
# The Richardson extrapolation, Grid Convergence Index
# and Relative Discretization Error are stored in the result:
verificator.result.extrapolation

# %%
# as well as the error of the output of interest wrt the
# Richardson extrapolation:
verificator.result.element_wise_metrics
