from __future__ import annotations

from gemseo.disciplines.analytic import AnalyticDiscipline
from numpy import atleast_1d

from vimseo.api import create_model
from vimseo.core.base_integrated_model import IntegratedModel
from vimseo.core.components.discipline_wrapper_component import (
    DisciplineWrapperComponent,
)

if __name__ == "__main__":
    model = create_model("BendingTestAnalytical", "Cantilever")

    input_transform = AnalyticDiscipline({"length": "lengthOverWidth*width"})

    input_transform.default_input_data.update({"lengthOverWidth": atleast_1d(1.0)})
    input_transform.default_input_data.update({
        "width": model.default_input_data["width"]
    })

    output_transform = AnalyticDiscipline({
        "dplt_adim_at_force": "dplt_at_force_location/length"
    })
    output_transform.default_input_data.update({
        "length": model.default_input_data["length"]
    })

    # The transformed space model has the following chain of components:
    # [input_tranform,
    # model.pre_processor, model.run_processor, model.post_processor,
    # output_transform]
    transformed_input_model = IntegratedModel(
        "Beam_Cantilever",
        [
            DisciplineWrapperComponent("Beam_Cantilever", input_transform),
            *list(model._chain.disciplines),
            DisciplineWrapperComponent("Beam_Cantilever", output_transform),
        ],
    )

    print(transformed_input_model.input_grammar)
    print(transformed_input_model.output_grammar)

    model.cache = None
    transformed_input_model.cache = None
    output_data = transformed_input_model.execute({"lengthOverWidth": atleast_1d(2.0)})

    print(transformed_input_model.get_input_data())
    print(transformed_input_model.get_output_data())

    print(output_data["dplt_adim_at_force"])

    assert (
        transformed_input_model._chain.disciplines[1].get_input_data()["length"]
        == 2 * transformed_input_model.get_input_data()["width"]
    )
    assert (
        output_data["dplt_adim_at_force"]
        == transformed_input_model._chain.disciplines[-2].get_output_data()[
            "dplt_at_force_location"
        ]
        / transformed_input_model._chain.disciplines[1].get_input_data()["length"]
    )
