# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
from __future__ import annotations

import pandas as pd
import streamlit as st
from gemseo.datasets.io_dataset import IODataset
from numpy import array_str
from numpy import atleast_1d
from numpy import vstack

FLOAT_PRECISION = 3
ELEMENT_SIZE_PRECISION = 4
REFERENCE_PREFIX = "Ref"


def set_output_selection(result):
    """A select box to choose the output variable.

    Args:
        result: The result of a verification.
    """
    metric_names = pd.unique(list(result.integrated_metrics.keys()))
    output_names = result.element_wise_metrics.get_variable_names(
        group_name=metric_names[0]
    )

    return st.selectbox(
        "Output name",
        output_names,
    )


def convergence_renaming(name, prefix=""):
    """Rename an output variable of a convergence verification."""
    return f"|{name}-extrapol|"


def comparison_renaming(name, prefix=""):
    """Rename an output variable of a code verification."""
    return f"{prefix}[{name}]"


def prepare_overall_dataset(
    result, metric_names, output_names, renamer=None, add_output_data=True
):
    """Prepare the final dataset used in the dashboard.

    Args:
        result: A verification result.
        metric_names: The names of the selected metrics.
        output_names: The names of the selected output variables.
        renamer: A function to rename output variable names to more expressive names and
        also to ensure that the variable names of the final dataset are unique
        (useful to further convert this dataset to mono-index dataframe).
        add_output_data: Whether to add the output variables to the error metrics in
        the final dataset.

    Returns: A dataset containing the inpout variables, the selected metrics with
    unique variable names, and possibly the raw output variables.
    """
    # Rename element-wise metrics to ensure variable names are unique.
    group_names = [IODataset.INPUT_GROUP]
    group_names.extend(metric_names)
    overall_dataset = result.element_wise_metrics.get_view(
        group_names=group_names
    ).copy()
    if renamer:
        for metric_name in metric_names:
            for name in overall_dataset.get_variable_names(group_name=metric_name):
                new_name = renamer(name, metric_name)
                overall_dataset.rename_variable(name, new_name, group_name=metric_name)

    # Drop unused outputs from the metric group
    for metric_name in metric_names:
        for output_name in overall_dataset.get_variable_names(group_name=metric_name):
            if output_name not in [renamer(name, metric_name) for name in output_names]:
                overall_dataset.drop(output_name, axis=1, level=1, inplace=True)

    if add_output_data:
        variable_names = output_names
        name_to_value = {
            name: result.simulation_and_reference
            .get_view(group_names=IODataset.OUTPUT_GROUP, variable_names=name)
            .to_numpy()
            .T
            for name in variable_names
        }
        overall_dataset.add_group(
            IODataset.OUTPUT_GROUP,
            data=vstack([name_to_value[name] for name in variable_names]).T,
            variable_names=variable_names,
            variable_names_to_n_components={
                name: name_to_value[name].shape[0] for name in variable_names
            },
        )

    return overall_dataset


def add_description(description, ds):
    """Add element-wise description to the dataset.

    Args:
        description: The description of the dataset lines.
        ds: A dataset from a verification result.

    Returns:
        A mono-index dataframe where the line description are added in the first column.
    """
    if "element_wise" in description:
        ds.add_variable("description", description["element_wise"])

    df = ds.copy()
    df.columns = ds.get_columns()

    if "element_wise" in description:
        # Put description column in first position.
        cols = df.columns.to_list()
        cols = cols[-1:] + cols[:-1]
        df = df[cols]

    return df


def get_formatted_value(value, precision: int = FLOAT_PRECISION):
    """Rounds either a float or a NumPy array.

    Args:
        value: The data to round.
        precision: The rounding precision.

    Returns: The rounded data.
    """
    is_float = isinstance(value, float)
    if is_float:
        return str(round(value, precision))
    return array_str(atleast_1d(value), precision=precision)
