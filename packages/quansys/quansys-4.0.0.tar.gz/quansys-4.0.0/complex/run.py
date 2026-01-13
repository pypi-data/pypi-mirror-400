from pathlib import Path
from quansys.simulation import QuantumEPR, ConfigJunction, EigenmodeAnalysis
from quansys.workflow import (
    WorkflowConfig,
    PyaedtFileParameters,
    DesignVariableBuilder,
    execute_workflow,
)
from pycaddy.sweeper import DictSweep

cfg = WorkflowConfig(
    pyaedt_file_parameters=PyaedtFileParameters(
        file_path=Path("complex_design.aedt"), non_graphical=False
    ),
    builder=DesignVariableBuilder(design_name="my_design"),
    builder_sweep=[
        DictSweep(
            parameters={
                "junction_inductance": ["10nh", "11nh"],
            }
        )
    ],
    simulations={
        "eigenmode": EigenmodeAnalysis(design_name="my_design", setup_name="Setup1"),
        "quantum": QuantumEPR(
            design_name="my_design",
            setup_name="Setup1",
            modes_to_labels={1: "transmon", 2: "readout"},
            junctions_infos=[
                ConfigJunction(
                    line_name="transmon_junction_line",
                    inductance_variable_name="junction_inductance",
                )
            ],
        ),
    },
    aggregation_dict={
        "eigenmode_results": ["build", "eigenmode"],
        "quantum_results": ["build", "quantum"],
    },
)

execute_workflow(cfg)
