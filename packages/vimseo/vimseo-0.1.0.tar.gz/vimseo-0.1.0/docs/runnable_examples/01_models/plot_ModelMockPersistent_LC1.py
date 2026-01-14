# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
# copyright section to be added automatically by syntax check
"""
Overview of the MockModelPersistent for load case LC1
========================================================================================

 A toy model for testing purpose of persistent data
"""

from __future__ import annotations

from vimseo.api import create_model
from vimseo.storage_management.base_storage_manager import PersistencyPolicy

# %%
# First, let's instantiate the model for a given load case:

model = create_model(
    "MockModelPersistent",
    "LC1",
    check_subprocess=True,
    directory_scratch_persistency=PersistencyPolicy.DELETE_ALWAYS,
    directory_archive_persistency=PersistencyPolicy.DELETE_ALWAYS,
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
