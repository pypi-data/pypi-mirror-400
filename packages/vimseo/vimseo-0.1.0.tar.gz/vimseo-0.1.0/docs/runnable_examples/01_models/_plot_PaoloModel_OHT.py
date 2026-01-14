# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
# copyright section to be added automatically by syntax check
"""
Overview of the PaoloModel for load case OHT
========================================================================================


"""

from __future__ import annotations

from vims import EXAMPLE_RUNS_DIR_NAME

from vimseo.api import create_model
from vimseo.core.base_integrated_model import IntegratedModelSettings

# %%
# First, let's instantiate the model for a given load case:

model_name = "PaoloModel"
load_case = "OHT"
model = create_model(
    model_name,
    load_case,
    check_subprocess=True,
    model_options=IntegratedModelSettings(
        directory_archive_root=f"../{EXAMPLE_RUNS_DIR_NAME}/archive/model_gallery",
        directory_scratch_root=f"../{EXAMPLE_RUNS_DIR_NAME}/scratch/model_gallery",
        cache_file_path=f"../{EXAMPLE_RUNS_DIR_NAME}/caches/model_gallery/{model_name}_{load_case}_cache.hdf",
    ),
)

# %%
# The model description can be accessed like this:

print(model.description)

# %%
# An illustration of the load case:

model.show_image()

# %%
# The model is executed with its default input values:

model.execute()

# %%
# And the results are visualised with the pre-defined plots:

figures = model.plot_results(show=True)


# %%
# Plot of reaction_force_vs_pseudo_time

figures["reaction_force_vs_pseudo_time"]

# %%
# Plot of d_reaction_force_d_E_vs_pseudo_time

figures["d_reaction_force_d_E_vs_pseudo_time"]

# %%
# Plot of d_reaction_force_d_nu_vs_pseudo_time

figures["d_reaction_force_d_nu_vs_pseudo_time"]

# %%
# Plot of d_reaction_force_d_sigma_y_0_vs_pseudo_time

figures["d_reaction_force_d_sigma_y_0_vs_pseudo_time"]

# %%
# Plot of d_reaction_force_d_sigma_y_u_vs_pseudo_time

figures["d_reaction_force_d_sigma_y_u_vs_pseudo_time"]

# %%
# Plot of d_reaction_force_d_delta_vs_pseudo_time

figures["d_reaction_force_d_delta_vs_pseudo_time"]
