# 📚 Quick‑Start Example Files

In this guide you’ll learn:

* how to copy the built‑in **design (.aedt)** and **configuration (.yaml)** templates  
* how to open a design safely in Python with [`PyaedtFileParameters`](api/pyaedt_file_parameters.md)

You’ll use these files later in the [Simulation](guides/simulations.md) and [Automation](guides/automation.md) tutorials.

---

## 1 Before you begin

!!! info
    Make sure **quansys is already installed** — see the [Installation guide](install.md) if you need help.

---

## 2 Example bundles

| Bundle | AEDT file | Config file | Purpose |
|--------|-----------|-------------|---------|
| `simple`  | `simple_design.aedt`  | `simple_config.yaml`  | Basic single‑sweep model |
| `complex` | `complex_design.aedt` | `complex_config.yaml` | Multi‑analysis setup |

---

## 3 Copy the files

When you installed **quansys**, a CLI tool named `quansys` was added to your PATH—its `example` subcommand copies these demo files for hands‑on learning.


```bash  
quansys example --help            # show all options  

# Most common commands  
quansys example                    # → simple AEDT + YAML  
quansys example --type complex     # → complex AEDT + YAML  
quansys example --no-config        # → AEDT only
```  

*Manual fallback (working from a cloned repo)*

```bash  
cp <PATH_TO_REPO>/src/quansys/examples/simple_design.aedt .  
cp <PATH_TO_REPO>/src/quansys/examples/simple_config.yaml .  
```

---

## 4 Open the AEDT file safely

!!! example "Open an AEDT file in Python"
    ```python
    from quansys.workflow import PyaedtFileParameters  
    
    params = PyaedtFileParameters("simple_design.aedt")  
    
    with params.open_pyaedt_file() as hfss:  
        print(f"Design name: {hfss.design_name}")
    ```  

!!! danger "Avoid simultaneous access"
    Don’t open the same `.aedt` project in both the HFSS GUI **and** a Python script at the same time — file corruption can occur.

---

## 5 Next steps

1. Run your first analysis → [🧪Simulation guide](guides/simulations.md)  
2. Scale up with sweeps → [⚙️Automation guide](guides/automation.md)  
3. Prefer the CLI → [🖥️Terminal & CLI](guides/terminal.md)
