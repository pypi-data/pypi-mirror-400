# EC Toolkit

Electrochemical thermodynamics toolkit for VASP workflows:  
– Parse `OUTCAR` & `POSCAR`  
– Build reaction mechanisms from DFT energies, ZPE, and entropy  
– Compute ΔG profiles, overpotentials, & G<sub>max</sub>
– Plot free‐energy diagrams

---

## Features

- **I/O parsers**
  - `OutcarParser.read_edft`, `OutcarParser.read_zpe_tds`, `OutcarParser.read_converged`, `OutcarParser.auto_read`
  - `PoscarParser` backed by ASE, full support for selective dynamics
- **Data models**
  - `Compound`, `ElementaryStep`, `Mechanism`, `mechanism_constructor`
- **Thermo analysis**
  - `compute_eta_td`, `compute_g_max`
- **Visualization**
  - `plot_free_energy` with optional η<sub>TD</sub> and G<sub>max</sub> annotations

---

## Installation

```bash
pip install ec-toolkit
```

---

## Quickstart

```python
from pathlib import Path
import matplotlib.pyplot as plt

from ec_toolkit.io.outcar import OutcarParser
from ec_toolkit.models.classes import Compound, ElementaryStep, Mechanism
from ec_toolkit.models.constructor import mechanism_constructor
from ec_toolkit.analysis.thermodynamics import compute_g_max, compute_eta_td
from ec_toolkit.visualization.plotting import plot_free_energy

# 1) Read energies from VASP runs
workdir = Path("my_vasp_runs").expanduser()
steps   = ["M", "M-OH", "M-O", "M-OOH"]

# Request TΔS computation and structure check (checks that EDFT run converged AND
# that the ZPE OUTCAR contained no imaginary frequencies). When check_structure=True
# auto_read returns (edfts, zpes, tdss, check_list).
edfts, zpes, tdss, conv_list = OutcarParser.auto_read(
    workdir, steps, calc_tds=True, check_structure=True
)

# 2) Wrap as Compounds
compounds = {
    name: Compound(name, {"dft": e, "zpe": z, "tds": t}, converged=conv)
    for name, e, z, t, conv in zip(steps, edfts, zpes, tdss, conv_list)
}

# 3) Stoichiometry / mechanism construction (example for OER mononuclear)
oer_mononuc_steps = [
    {"M-OH": +1.0, "H2": +0.5, "M": -1.0, "H2O": -1.0},
    {"M-O": +1.0, "H2": +0.5, "M-OH": -1.0},
    {"M-OOH": +1.0, "H2": +0.5, "M-O": -1.0, "H2O": -1.0},
    {"M": +1.0, "H2": +0.5, "O2": +1, "M-OOH": -1.0},
]
oer_mononuc_labels = ["M→M-OH", "M-OH→M-O", "M-O→M-OOH", "M-OOH→M"]
oer_mononuc_elmask = [True, True, True, True]

# Build a mechanism-constructor / factory (constructor returns
# a callable that you then call with Compound objects - returns a Mechanism directly).
oer_mononuc_mechanism = mechanism_constructor(
    "oer_mononuc",
    step_stoich=oer_mononuc_steps,
    step_labels=oer_mononuc_labels,
    el_steps=oer_mononuc_elmask,
    eq_pot=1.23,
    is_oxidation_reaction=True,
    sym_fac=1,
    ref_el="RHE",
    correction_step=4,
)

h2o = Compound("h2o", {"dft": -14.321257, "zpe": 0, "tds": 0}, converged=True)
h2 = Compound("h2", {"dft": -6.900225, "zpe": 0, "tds": 0}, converged=True)

# instantiate the Mechanism using the constructor returned above
oer_mono = oer_mononuc_mechanism(
    M=compounds["M"],
    M_OH=compounds["M-OH"],
    M_O=compounds["M-O"],
    M_OOH=compounds["M-OOH"],
    H2=h2,
    H2O=h2o,
)

# 4) Plot (plotting uses the biased profile produced by compute_g_max under the hood)
plot_free_energy(mech=oer_mono, op=0, annotate_eta=False, labels=["M", "M-OH", "M-O", "M-OOH", "M + H2O"])
plt.show()
```

### Custom ZPE locator

By default ZPE/TdS is looked for under s1/zpe/OUTCAR, but you can customize. If your ZPE runs live elsewhere (e.g. in step1_zpe), pass your own locator:

```python
def my_zpe_locator(wd: Path, step: str) -> Path:
    return wd / f"{step}_zpe" / "OUTCAR"

edfts, zpes, tdss = OutcarParser.auto_read(
    workdir, steps, calc_tds=True,
    zpe_locator=my_zpe_locator
)
```

---

## License

This project is released under the MIT License. See [License](./LICENSE) for details.

---

## Contributors

- Noel Marks
- Maksim Sokolov
