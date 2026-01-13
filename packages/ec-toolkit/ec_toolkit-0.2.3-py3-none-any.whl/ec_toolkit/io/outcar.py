import numpy as np
import re
from typing import Sequence, Callable
from pathlib import Path
from ec_toolkit.io.vasp_helpers import read_reverse_order
from astropy import constants as const
from astropy import units as u
import warnings


class OutcarParser:
    T: float = 298.15  # default temperature (K)

    @staticmethod
    def read_edft(path: Path) -> float:
        for line in read_reverse_order(path, max_lines=2000):
            if "sigma" in line.lower():
                return float(line.split()[-1])
        raise RuntimeError(f"No electronic energy ('sigma') line found in {path!r}")

    @staticmethod
    def read_zpe_tds(path: Path, calc_tds: bool = True) -> tuple[float, float, bool]:
        """
        Parse frequencies from a ZPE OUTCAR and compute (ZPE_eV, TΔS_eV, has_imag).

        Policy implemented:
          - Frequencies matched by regex "<number> cm-1".
          - Negative numbers or lines containing "f/i" are treated as imaginary:
            they are NOT included in ZPE/TΔS sums but cause has_imag=True.
          - ZPE is computed from real positive frequencies only (0.5*h*nu).
          - For entropy (TΔS) frequencies are floored to 50 cm^-1.
          - If no real positive frequencies are found, ZPE and TΔS return 0.0.
        """
        freq_re = re.compile(r"([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s*cm-1", re.I)
        freqs_cm_real = []  # positive (real) frequencies in cm^-1
        has_imag = False

        # read file and extract all cm^-1 numbers robustly
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                # find all numeric tokens followed by "cm-1"
                for m in freq_re.finditer(line):
                    try:
                        val = float(m.group(1))
                    except ValueError:
                        continue
                    # detect imaginary indicator by line content or negative value
                    if "f/i" in line.lower() or val <= 0.0:
                        has_imag = True
                        # skip adding to real-frequency list
                        continue
                    freqs_cm_real.append(val)

        if len(freqs_cm_real) == 0:
            # no real vibrational modes to contribute
            return 0.0, 0.0, has_imag

        # convert frequencies to Hz using astropy units
        freqs_hz = (u.Quantity(freqs_cm_real, u.cm**-1) * const.c).to(u.Hz)

        # ZPE: sum(0.5 * h * nu) per mode, convert to eV
        zpe_j = (0.5 * const.h * freqs_hz).sum()
        zpe_eV = zpe_j.to(u.eV).value

        if not calc_tds:
            return float(zpe_eV), 0.0, has_imag

        # For entropy, floor frequencies below 50 cm^-1 (on cm^-1 scale)
        freqs_floor_cm = np.maximum(np.array(freqs_cm_real, dtype=float), 50.0)
        freqs_floor_hz = (u.Quantity(freqs_floor_cm, u.cm**-1) * const.c).to(u.Hz)

        # dimensionless x = h ν / (k_B T)
        T_q = OutcarParser.T * u.K
        x = (const.h * freqs_floor_hz) / (const.k_B * T_q)  # Quantity (dimensionless)
        x_val = x.value  # numpy array

        # stable vectorized evaluation for s_i = k_B [ x/(exp(x)-1) - ln(1 - exp(-x)) ]
        # handle large x (avoid overflow) using expm1 and where masks
        with np.errstate(
            over="ignore", under="ignore", divide="ignore", invalid="ignore"
        ):
            # safe term1: x / (e^x - 1) using expm1 for accuracy at small x
            denom = np.expm1(x_val)
            term1 = np.where(denom != 0.0, x_val / denom, 0.0)
            # term2: log(1 - e^{-x}) = log(-expm1(-x)) ; compute stable for large x
            term2 = np.log1p(-np.exp(-x_val))
            s_per_mode = const.k_B * (term1 - term2)  # Quantity with units J/K

        s_total = u.Quantity(s_per_mode).sum()  # J / K per molecule
        tds_j = (s_total * T_q).to(u.J)  # J per molecule
        tds_eV = tds_j.to(u.eV).value

        return float(zpe_eV), float(tds_eV), bool(has_imag)

    @staticmethod
    def read_converged(path: Path) -> bool:
        lines = list(read_reverse_order(path, max_lines=200))
        return any("reached required accuracy" in line.lower() for line in lines[:200])

    @classmethod
    def auto_read(
        cls,
        workdir: Path,
        subdirs: Sequence[str],
        *,
        calc_tds: bool = False,
        zpe_locator: Callable[[Path, str], Path] | None = None,
        check_structure: bool = False,
    ) -> tuple[list[float], list[float], list[float], list[bool] | None]:
        """
        Goes through each dir and combines the other classmethods.

        For each folder in `subdirs` under `workdir`, read:
          - EDFT       ← workdir/d/OUTCAR
          - ZPE & TΔS  ← path returned by zpe_locator(workdir, d)

        If check_structure=True the method additionally checks:
          - read_converged(OUTCAR) -> bool (ionic relaxation converged)
          - whether the ZPE OUTCAR contains imaginary frequencies (has_imag flag
            returned by read_zpe_tds). The final check-flag for a directory is
            True only when (read_converged is True) AND (has_imag is False).

        Returns
        -------
        If check_structure is False:
            (edft_list, zpe_list, tds_list)
        If check_structure is True:
            (edft_list, zpe_list, tds_list, check_list)
            where check_list[k] == (read_converged for dir k) and (not has_imag for dir k)
        """
        # default: look in workdir/d/zpe/OUTCAR
        if zpe_locator is None:

            def zpe_locator(wd: Path, d: str) -> Path:
                return wd / d / "zpe" / "OUTCAR"

        edfts: list[float] = []
        zpes: list[float] = []
        tdss: list[float] = []
        checks: list[bool] = []

        for d in subdirs:
            base = workdir / d
            efile = base / "OUTCAR"

            # EDFT (raises if not found / parse fails)
            edft = cls.read_edft(efile)
            edfts.append(edft)

            # ZPE + TΔS + imaginary-flag
            zfile = zpe_locator(workdir, d)
            if zfile.exists():
                zpe, tds, has_imag = cls.read_zpe_tds(zfile, calc_tds)
            else:
                warnings.warn(
                    f"No ZPE/TdS OUTCAR found at {zfile!r}; setting ZPE and TdS to 0",
                    UserWarning,
                    stacklevel=2,
                )
                zpe, tds, has_imag = 0.0, 0.0, True

            zpes.append(zpe)
            tdss.append(tds)

            # convergence of the energy run itself
            is_conv = cls.read_converged(efile)

            # final "check_structure" boolean: True only if converged AND no imag freqs
            checks.append(bool(is_conv and (not bool(has_imag))))

        if check_structure:
            return edfts, zpes, tdss, checks
        return edfts, zpes, tdss
