from quansys.simulation import EigenmodeAnalysis
from quansys.workflow import PyaedtFileParameters

params = PyaedtFileParameters(
    file_path="simple_design.aedt",
    design_name="my_design",
    non_graphical=False,  # headless HFSS
)

eigen = EigenmodeAnalysis(design_name="my_design", setup_name="Setup1")

with params.open_pyaedt_file() as hfss:
    result = eigen.analyze(hfss)

print("Q‑factor (mode 1):", result.results[1].quality_factor)
print("Frequency  (mode 1):", result.results[1].frequency)
