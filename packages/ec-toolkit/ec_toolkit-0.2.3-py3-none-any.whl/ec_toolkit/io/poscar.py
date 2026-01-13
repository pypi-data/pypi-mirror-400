from pathlib import Path
from ase.io import read, write
from ase import Atoms
import numpy as np
import re


class PoscarParser:
    """
    ASE‑backed POSCAR I/O, with full support for VASP 'Selective dynamics' flags.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        # Load into ASE Atoms (always Cartesian internally)
        self._atoms: Atoms = read(str(path), format="vasp")

        # Read raw lines to extract flags and original coord mode
        raw = self.path.read_text().splitlines()

        # Header layout:
        # 0: comment
        # 1: scale
        # 2–4: lattice vectors
        # 5: species
        # 6: counts
        # 7: maybe "Selective dynamics"
        idx = 7
        self._sel_dyn_present = False
        if raw[idx].strip().lower().startswith("s"):
            self._sel_dyn_present = True
            idx += 1

        # Next line is coordinate mode ("Direct" or "Cartesian")
        self._coord_mode = raw[idx].strip().lower()
        idx += 1

        # Compute how many atoms
        counts = list(map(int, raw[6].split()))
        self._n_atoms = sum(counts)

        # Parse the coordinate block and flags
        coords, flags = [], []
        for line in raw[idx : idx + self._n_atoms]:
            parts = re.split(r"\s+", line.strip())
            coords.append(list(map(float, parts[:3])))
            if self._sel_dyn_present:
                flags.append([p.upper() == "T" for p in parts[3:6]])
        self.coords = np.array(coords)
        self._selective_flags = (
            np.array(flags, dtype=bool) if self._sel_dyn_present else None
        )

    @property
    def lattice(self) -> np.ndarray:
        return self._atoms.cell.array

    @property
    def species(self) -> list[str]:
        return list(self._atoms.get_chemical_symbols())

    @property
    def species_counts(self) -> dict[str, int]:
        from collections import Counter

        return dict(Counter(self.species))

    @property
    def coords_direct(self) -> np.ndarray:
        if self._coord_mode != "direct":
            raise AttributeError("POSCAR was not in Direct mode")
        return self._atoms.get_scaled_positions()

    @property
    def coords_cart(self) -> np.ndarray:
        if self._coord_mode != "cartesian":
            raise AttributeError("POSCAR was not in Cartesian mode")
        return self._atoms.get_positions()

    @property
    def selective_dynamics(self) -> np.ndarray | None:
        """(N_atoms × 3) boolean mask of True = free, False = fixed; None if not present."""
        return self._selective_flags

    @property
    def coord_mode(self) -> str:
        return self._coord_mode

    def write(self, path: Path):
        # 1) Let ASE write the basic POSCAR (no flags)
        write(
            str(path),
            self._atoms,
            format="vasp",
            direct=(self._coord_mode == "direct"),
        )

        # 2) If no flags, we’re done
        if not self._sel_dyn_present:
            return

        # 3) Post‑process to inject 'Selective dynamics' and flags
        out = Path(path).read_text().splitlines()
        # Find the index of the coordinate mode line (first 'direct' or 'cartesian')
        mode_idx = next(
            i
            for i, ln in enumerate(out)
            if ln.strip().lower() in ("direct", "cartesian")
        )
        # Insert the 'Selective dynamics' line before coordinates
        out.insert(mode_idx, "Selective dynamics")
        # Starting at mode_idx+1, append flags to each coordinate line
        for i in range(self._n_atoms):
            flag_str = " ".join("T" if f else "F" for f in self._selective_flags[i])
            out[mode_idx + 1 + i] += "  " + flag_str

        # 4) Write back the patched file
        Path(path).write_text("\n".join(out) + "\n")
