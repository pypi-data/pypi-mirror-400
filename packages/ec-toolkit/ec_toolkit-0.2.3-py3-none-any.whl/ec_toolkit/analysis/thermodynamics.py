import numpy as np
from ec_toolkit.models.classes import Mechanism


def compute_g_max(
    mech: Mechanism,
    op: float | np.ndarray,
    sym_fac: int | None = None,
) -> tuple[
    float | np.ndarray, tuple[int, int] | np.ndarray, np.ndarray, float | np.ndarray
]:
    """
    Compute G_max and return (G_max, (start_1based, end_1based), biased_profiles, op_returned).

    The returned op_returned is:
      - a float when a scalar op was passed in
      - an np.ndarray (shape (M,)) when an array of overpotentials was passed in

    Effective potential used:
      eq_eff = eq_pot + op    (for oxidation)
      eq_eff = eq_pot - op    (for reduction)

    The bias matrix is eq_eff * n_e_up_to (n_e_up_to >= 0 is number of el steps up to each intermediate).
    Historical rule applied to construct biased profiles:
      - oxidation: biased = rif_row - bias_matrix
      - reduction:  biased = rif_row + bias_matrix
    """
    if sym_fac is None:
        sym_fac = mech.sym_fac
    rif = np.asarray(
        mech.reaction_intermediate_free_energies(sym_fac=sym_fac), dtype=float
    )
    el = np.asarray(mech.el_steps, dtype=bool)
    eq_pot = float(mech.eq_pot)
    is_oxid = bool(mech.is_oxidation_reaction)

    if rif.ndim != 1:
        raise ValueError(
            "Mechanism.reaction_intermediate_free_energies must return 1-D array (length N+1)."
        )
    N_plus_1 = rif.size
    N = N_plus_1 - 1
    if el.size != N:
        raise ValueError(
            "Length mismatch: mech.el_steps must have length N where rif has length N+1."
        )
    if not np.any(el):
        raise ValueError(
            "Mechanism has no electrochemical steps (el_steps all False); G_max undefined."
        )

    # cumulative electrochemical counts at intermediates (non-negative, 0..)
    n_e_up_to = np.empty(N_plus_1, dtype=int)
    n_e_up_to[0] = 0
    n_e_up_to[1:] = np.cumsum(el, dtype=int)

    # normalize op to array form, remember whether scalar
    op_arr = np.asarray(op, dtype=float)
    if op_arr.ndim == 0 or op_arr.size == 1:
        op_vals = np.atleast_1d(float(op_arr.ravel()[0]))
        scalar_op = True
    else:
        op_vals = op_arr.ravel()
        scalar_op = False
    M = op_vals.size

    # effective eq potential for each op: eq + op (oxidation) or eq - op (reduction)
    if is_oxid:
        eq_eff = (eq_pot + op_vals).reshape(M, 1)
    else:
        eq_eff = (eq_pot - op_vals).reshape(M, 1)

    bias_matrix = eq_eff * n_e_up_to.reshape(1, -1)  # (M, N+1)
    rif_row = rif.reshape(1, -1)  # (1, N+1)

    # historical application: oxidation subtracts bias, reduction adds bias
    if is_oxid:
        biased_matrix = rif_row - bias_matrix
    else:
        biased_matrix = rif_row + bias_matrix

    G_max_list = np.empty(M, dtype=float)
    idx_pairs = np.empty((M, 2), dtype=int)

    # For each row compute suffix max value and earliest suffix argmax index in O(N)
    for r in range(M):
        bm = biased_matrix[r]  # shape (N+1,)

        suffix_val = np.empty(N_plus_1, dtype=float)
        suffix_idx = np.empty(N_plus_1, dtype=int)

        last_val = bm[-1]
        last_idx = N
        suffix_val[N] = last_val
        suffix_idx[N] = last_idx

        for k in range(N - 1, -1, -1):
            v = bm[k]
            if v >= last_val:
                last_val = v
                last_idx = k
            suffix_val[k] = last_val
            suffix_idx[k] = last_idx

        candidate = suffix_val[1:] - bm[:-1]  # length N
        candidate_masked = np.where(el, candidate, -np.inf)

        s_best = int(np.argmax(candidate_masked))
        best_val = float(candidate_masked[s_best])
        end_idx = int(suffix_idx[s_best + 1])

        G_max_list[r] = best_val
        idx_pairs[r, 0] = s_best + 1
        idx_pairs[r, 1] = end_idx + 1

    # prepare op_returned in the same "shape type" as the input
    if scalar_op:
        op_returned: float = float(op_vals[0])
        return (
            float(G_max_list[0]),
            (int(idx_pairs[0, 0]), int(idx_pairs[0, 1])),
            biased_matrix[0].copy(),
            op_returned,
        )
    else:
        return G_max_list.copy(), idx_pairs.copy(), biased_matrix.copy(), op_vals.copy()


def compute_eta_td(mech: Mechanism, *, sym_fac: int | None = None) -> tuple[float, int]:
    """
    Compute thermodynamic overpotential η_TD at zero applied bias (U = eq_pot),
    returning (eta_eV, step_index_1based).

    eta is defined as the largest uphill step between consecutive reaction
    intermediates when the intermediates are evaluated at U = eq_pot.
    """
    if not isinstance(mech, Mechanism):
        raise TypeError("compute_eta_td requires a Mechanism instance as `mech`.")

    if sym_fac is None:
        sym_fac = mech.sym_fac

    # zero-bias (internal) reaction intermediates (length N+1)
    rif_zero = np.asarray(
        mech.reaction_intermediate_free_energies(sym_fac=sym_fac), dtype=float
    )
    el = np.asarray(mech.el_steps, dtype=bool)
    eq_pot = float(mech.eq_pot)
    is_oxid = bool(mech.is_oxidation_reaction)

    if rif_zero.ndim != 1:
        raise ValueError(
            "mech.reaction_intermediate_free_energies(...) must return a 1-D array (length N+1)."
        )
    N_plus_1 = rif_zero.size
    N = N_plus_1 - 1
    if el.size != N:
        raise ValueError("mech.el_steps must have length N (where rif has length N+1).")
    if not np.any(el):
        raise ValueError("Mechanism has no electrochemical steps; η_TD undefined.")

    # build n_e_up_to: number of electrochemical steps in [0..k-1] for each intermediate k
    n_e_up_to = np.empty(N_plus_1, dtype=int)
    n_e_up_to[0] = 0
    n_e_up_to[1:] = np.cumsum(el, dtype=int)

    # biased profile at U = eq_pot (op == 0)
    bias_eq = eq_pot * n_e_up_to
    biased_eq = rif_zero - bias_eq if is_oxid else rif_zero + bias_eq

    # per-step uphill deltas between consecutive intermediates
    deltas = biased_eq[1:] - biased_eq[:-1]  # length N

    # handle non-finite: treat NaN/inf as -inf for argmax selection, but error if all non-finite
    finite_mask = np.isfinite(deltas)
    if not finite_mask.any():
        raise ValueError("All computed step ΔG values at equilibrium are non-finite.")
    safe_deltas = np.where(finite_mask, deltas, -np.inf)

    idx0 = int(np.argmax(safe_deltas))  # 0-based step index (0..N-1)
    eta = float(safe_deltas[idx0])
    return eta, idx0 + 1  # 1-based step index
