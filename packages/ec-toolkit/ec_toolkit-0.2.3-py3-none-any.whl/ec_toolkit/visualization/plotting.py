from ec_toolkit.analysis.thermodynamics import compute_eta_td, compute_g_max
import numpy as np
from ec_toolkit.models.classes import Mechanism
import matplotlib.pyplot as plt
import warnings
from mpl_toolkits.axisartist.axislines import SubplotZero
from matplotlib.transforms import Bbox


def plot_free_energy(
    mech: Mechanism,
    *,
    labels: list[str] | None = None,
    op: float | None = None,
    sym_fac: int | None = None,
    ref_el: str | None = None,
    annotate_eta: bool = False,
    annotate_gmax: bool = True,
    annotate_gmax_coord: tuple[int, int] | None = None,
    ax: plt.Axes | None = None,
    base_fontsize: float = 10.0,
    **step_kwargs,
) -> plt.Axes:
    """
    Plot a free-energy diagram for a Mechanism instance using axisartist arrowed axes.

    - Accepts compute_g_max(...) that returns either:
        (Gmax, (i,j), biased_profile)  [old]
      or (Gmax, (i,j), biased_profile, op_returned)  [new].
      If the 4-tuple is returned, op_returned will be used when deciding the displayed U.
    - Uses SubplotZero and places x axis at the bottom and y axis on the left,
      both ending with arrow heads.
    - `labels` (optional list[str]) when provided must have length N+1 and will be
      displayed on the top-left of each plateau (one label per intermediate).
    - base_fontsize controls overall text scaling.
    """
    if not isinstance(mech, Mechanism):
        raise TypeError("plot_free_energy requires a Mechanism instance as `mech`.")

    if sym_fac is None:
        sym_fac = mech.sym_fac

    # semantic font sizes derived from base_fontsize
    fs = float(base_fontsize)
    fs_axis_label = fs * 1.2
    fs_annotation = fs * 1.0
    fs_plateau_label = fs * 0.9

    # zero-bias intermediate free energies and metadata
    rif_zero = np.asarray(
        mech.reaction_intermediate_free_energies(sym_fac=sym_fac), dtype=float
    )
    el = np.asarray(mech.el_steps, dtype=bool)
    eq_pot = float(mech.eq_pot)
    is_oxid = bool(mech.is_oxidation_reaction)

    N_plus_1 = rif_zero.size

    # decide which op to plot: if None => equilibrium (0.0)
    plot_op = 0.0 if op is None else float(op)

    # ----- call compute_g_max exactly once to obtain biased profile for plot_op -----
    gmax_res = compute_g_max(mech, plot_op, sym_fac=sym_fac)

    # Accept either 3-tuple (old) or 4-tuple (new)
    if not (isinstance(gmax_res, tuple) and len(gmax_res) in (3, 4)):
        raise RuntimeError(
            "plot_free_energy requires compute_g_max(mech, op) to return a tuple "
            "of length 3 or 4: (Gmax, (i,j), biased_profile[, op_returned])."
        )

    # unpack robustly
    if len(gmax_res) == 4:
        Gmax, gmax_idx_pair, biased, op_returned = gmax_res
    else:
        Gmax, gmax_idx_pair, biased = gmax_res
        op_returned = plot_op  # fallback to the op we passed

    # Accept biased as (N+1,) or (1, N+1)
    biased_arr = np.asarray(biased, dtype=float)
    if biased_arr.ndim == 2 and biased_arr.shape[0] == 1:
        rif_plot = biased_arr[0].copy()
    elif biased_arr.ndim == 1:
        rif_plot = biased_arr.copy()
    else:
        raise RuntimeError(
            "compute_g_max returned a biased_profile with unexpected shape; "
            "expected 1-D array (N+1,) or 2-D array with shape (1, N+1)."
        )

    # extend last value so final horizontal plateau is visible (step plotting uses 'post')
    ys = np.concatenate((rif_plot, [rif_plot[-1]]))
    xs = np.arange(ys.size)

    # create SubplotZero and register it on the current figure (no fallback)
    fig = plt.gcf()
    ax = SubplotZero(fig, 111)
    fig.add_subplot(ax)

    # Show bottom and left axes with arrowheads; hide all others (including xzero/yzero)
    for direction in ("bottom", "left"):
        ax.axis[direction].set_axisline_style("-|>")
        ax.axis[direction].set_visible(True)

    # hide the remaining axes if present
    for direction in ("top", "right", "xzero", "yzero"):
        if direction in ax.axis:
            ax.axis[direction].set_visible(False)

    # plot the step profile
    ax.step(xs, ys, where="post", **step_kwargs)

    # compute limits and small pads for arrowheads
    x_min, x_max = xs[0], xs[-1]
    y_min, y_max = float(np.nanmin(ys)), float(np.nanmax(ys))

    # axis length (fallback to 1.0 if degenerate)
    raw_y_span = y_max - y_min
    y_range = raw_y_span if raw_y_span > 0 else 1.0

    x_range = x_max - x_min if x_max > x_min else 1.0
    x_pad = 0.06 * x_range
    y_pad = 0.08 * y_range

    # --- special rule: if highest value is (close to) 0.0, set upper y to 0 + 5% * axis_length
    if np.isclose(y_max, 0.0):
        y_top = 0.0 + 0.05 * y_range
        # ensure top is above bottom with a small margin
        if y_top <= y_min + 1e-12:
            # choose a tiny positive top so axis is visible
            y_top = y_min + 0.05 * max(abs(y_min), 1.0)
    else:
        y_top = y_max

    # set limits so we have space for axis arrows; x axis is at the bottom of the axes
    ax.set_xlim(x_min, x_max + x_pad)
    ax.set_ylim(y_min - y_pad, y_top)

    # REMOVE x-axis ticks and labels (keep axis label)
    ax.set_xticks([])
    ax.set_xticklabels([])
    # scale left tick labels to plateau label size
    try:
        ax.axis["left"].major_ticklabels.set_fontsize(fs_plateau_label)
    except Exception:
        # axisartist may not expose major_ticklabels in older versions; ignore
        pass

    # axis labels (AxisArtist)
    ax.set_ylabel("Free energy (eV)")
    ax.set_xlabel("Reaction coordinate")
    ax.axis["left"].label.set(fontsize=fs_axis_label, fontweight="bold")
    ax.axis["bottom"].label.set(fontsize=fs_axis_label, fontweight="bold")

    # U label: dynamic placement based on the maximum of the biased profile
    # use op_returned if compute_g_max provided it (keeps display consistent)
    used_op = (
        float(op_returned) if np.asarray(op_returned).size == 1 else float(plot_op)
    )
    if is_oxid:
        U = eq_pot + used_op
    else:
        U = eq_pot - used_op

    ref_el_label = mech.ref_el if ref_el is None else str(ref_el)

    # determine placement: upper-right if max in [0, 0.1], else upper-left
    max_val = float(np.nanmax(rif_plot))
    if 0.0 <= max_val <= 0.1:
        xpos, ypos, ha = 0.95, 0.97, "right"
    else:
        xpos, ypos, ha = 0.01, 0.97, "left"

    ax.text(
        xpos,
        ypos,
        rf"$U_{{{ref_el_label}}} = {U:.2f}\,$V",
        transform=ax.transAxes,
        va="top",
        ha=ha,
        fontsize=fs_annotation,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7),
    )

    # annotate η_TD (computed at equilibrium op=0) if requested
    if annotate_eta:
        if op is not None and not np.isclose(op, 0.0):
            warnings.warn(
                "annotate_eta computes η_TD at equilibrium (op=None or op=0). Using equilibrium profile.",
                UserWarning,
            )
        eta, step_i = compute_eta_td(mech, sym_fac=sym_fac)
        # compute equilibrium biased profile directly from rif_zero
        n_e_up_to = np.empty(N_plus_1, dtype=int)
        n_e_up_to[0] = 0
        n_e_up_to[1:] = np.cumsum(el, dtype=int)
        bias_eq = (eq_pot + 0.0) * n_e_up_to
        rif_eq = (rif_zero - bias_eq) if is_oxid else (rif_zero + bias_eq)

        y0 = float(rif_eq[step_i - 1])
        y1 = float(rif_eq[step_i])
        ax.annotate(
            "",
            xy=(step_i + 0.1, y1),
            xytext=(step_i + 0.1, y0),
            arrowprops=dict(arrowstyle="->", linestyle="-.", lw=1.2, color="green"),
        )
        ax.text(
            step_i + 0.2,
            (y0 + y1) / 2,
            rf"$\eta_{{TD}} = {eta:.2f}\,\mathrm{{V}}$",
            va="center",
            rotation=90,
            color="green",
            fontsize=fs_annotation,
        )

    # annotate G_max at the plotted overpotential if requested
    if annotate_gmax:
        i, j = gmax_idx_pair
        # note: gmax returns 1-based indices for (start_step, end_intermediate)
        y0 = float(rif_plot[i - 1])
        y1 = float(rif_plot[j - 1])

        # draw the vertical dashed G_max arrow (slightly centered between plateaus)
        vert_x = j - 0.5
        ax.annotate(
            "",
            xy=(vert_x, y1),
            xytext=(vert_x, y0),
            arrowprops=dict(arrowstyle="->", linestyle="--", lw=1.2, color="red"),
        )

        # dotted red horizontal guide from lower platform (left edge) to the G_max arrow
        x_start = float(i)
        x_end = float(vert_x)
        ax.plot(
            [x_start, x_end],
            [y0, y0],
            linestyle=":",
            color="red",
            linewidth=1.5,
            zorder=2,
        )

        # prepare label text
        gmax_text = rf"$G_{{\mathrm{{max}}}} = {float(Gmax):.2f}\,$eV"

        # --- collect occupied bboxes (display coords) ----------------
        fig = ax.figure
        fig.canvas.draw()  # ensure renderer-up-to-date
        renderer = fig.canvas.get_renderer()

        occupied_bboxes = []

        # 1) existing text / annotation / patch bboxes (title, labels, other annotations)
        #    only include visible artists that provide a bbox
        for artist in ax.get_children():
            try:
                if not getattr(artist, "get_visible", lambda: True)():
                    continue
                # many artists implement get_window_extent(renderer)
                tb = artist.get_window_extent(renderer)
                # skip zero-area bboxes (some artists return degenerate extents)
                if tb is not None and tb.width > 0 and tb.height > 0:
                    occupied_bboxes.append(tb)
            except Exception:
                # not all artists expose window extents reliably; ignore failures
                continue

        # 2) Line2D objects — add their full bbox (conservative)
        for line in ax.get_lines():
            if not line.get_visible():
                continue
            try:
                xd = np.asarray(line.get_xdata())
                yd = np.asarray(line.get_ydata())
                if xd.size == 0:
                    continue
                pts = np.column_stack((xd, yd))
                disp_pts = ax.transData.transform(pts)
                x0d, y0d = np.min(disp_pts, axis=0)
                x1d, y1d = np.max(disp_pts, axis=0)
                occupied_bboxes.append(Bbox.from_extents(x0d, y0d, x1d, y1d))
            except Exception:
                continue

        # 3) per-plateau bbox rectangles (tighter than full line bbox)
        plateau_half_height = max(0.005 * y_range, 1e-8)  # in data units
        for k in range(len(ys) - 1):
            x0, x1 = float(k), float(k + 1)
            y_plateau = float(ys[k])
            rect_pts = np.array(
                [
                    [x0, y_plateau - plateau_half_height],
                    [x1, y_plateau + plateau_half_height],
                ]
            )
            try:
                disp_rect = ax.transData.transform(rect_pts)
                x0d, y0d = np.min(disp_rect, axis=0)
                x1d, y1d = np.max(disp_rect, axis=0)
                occupied_bboxes.append(Bbox.from_extents(x0d, y0d, x1d, y1d))
            except Exception:
                continue

        # helper: test overlap in display coords
        def bbox_overlaps_any(bbox, others):
            for ob in others:
                if bbox.overlaps(ob):
                    return True
            return False

        # candidate placements in data coords (x, y)
        mid_y = 0.5 * (y0 + y1)
        cand_data = [
            (j - 0.3, mid_y),  # right, vertically centered (preferred)
            (j - 1.75, mid_y),  # left, centered (close)
            (j - 0.3, y0 - 0.005 * y_range),  # right & below lower plateau
            (j - 1.75, y0 - 0.005 * y_range),  # left & below lower plateau
            (vert_x + 0.2, y1 + 0.005 * y_range),  # above and centered on arrow
            (j - 1.75, y1 + 0.005 * y_range),  # left & above top plateau
            (j - 0.3, y1 + 0.005 * y_range),  # right & above top plateau
        ]

        chosen = None
        # Try candidates: measure text bbox using alpha=0 (visible True so renderer computes extent).
        for cx, cy in cand_data:
            tmp = ax.text(
                cx,
                cy,
                gmax_text,
                va="center",
                ha="left",
                fontsize=fs_annotation,
                transform=ax.transData,
                alpha=0.0,
                zorder=1,
            )
            fig.canvas.draw()
            try:
                tbbox = tmp.get_window_extent(renderer)
            except Exception:
                tmp.remove()
                continue
            if not bbox_overlaps_any(tbbox, occupied_bboxes):
                chosen = (cx, cy)
                tmp.remove()
                break
            tmp.remove()

        # if none free, pick candidate with minimal overlap area
        if chosen is None:
            best = None
            best_overlap = float("inf")
            for cx, cy in cand_data:
                tmp = ax.text(
                    cx,
                    cy,
                    gmax_text,
                    va="center",
                    ha="left",
                    fontsize=fs_annotation,
                    transform=ax.transData,
                    alpha=0.0,
                    zorder=1,
                )
                fig.canvas.draw()
                try:
                    tbbox = tmp.get_window_extent(renderer)
                except Exception:
                    tmp.remove()
                    continue
                # compute total overlap area with occupied boxes
                total_overlap = 0.0
                for ob in occupied_bboxes:
                    x0i = max(tbbox.x0, ob.x0)
                    x1i = min(tbbox.x1, ob.x1)
                    y0i = max(tbbox.y0, ob.y0)
                    y1i = min(tbbox.y1, ob.y1)
                    if x1i > x0i and y1i > y0i:
                        total_overlap += (x1i - x0i) * (y1i - y0i)
                if total_overlap < best_overlap:
                    best_overlap = total_overlap
                    best = (cx, cy)
                tmp.remove()
            chosen = best if best is not None else cand_data[0]

        # finally draw the visible label where chosen
        tx, ty = chosen
        ax.text(
            tx,
            ty,
            gmax_text,
            va="center",
            ha="left",
            zorder=5,
            fontsize=fs_annotation,
            color="red",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.5),
        )

    # --- draw labels on top-left of each plateau if requested ------------------
    if labels is not None:
        # normalize labels length to N+1
        if len(labels) < N_plus_1:
            warnings.warn(
                f"labels has length {len(labels)} but expected {N_plus_1}; missing labels will be empty.",
                UserWarning,
            )
            labels = list(labels) + [""] * (N_plus_1 - len(labels))
        elif len(labels) > N_plus_1:
            warnings.warn(
                f"labels has length {len(labels)} but expected {N_plus_1}; extra labels will be ignored.",
                UserWarning,
            )
            labels = list(labels)[:N_plus_1]

        # small vertical offset in data units (use fraction of original y_range)
        v_offset = max(0.002 * y_range, 1e-6)

        # draw each label at left edge of plateau k (plateau k is at y = ys[k], spans x=[k, k+1])
        for k, lab in enumerate(labels):
            if not lab:
                continue
            x_pos = k + 0.02  # slightly right of left edge
            y_pos = float(ys[k]) + v_offset
            ax.text(
                x_pos,
                y_pos,
                str(lab),
                transform=ax.transData,
                va="bottom",
                ha="left",
                fontsize=fs_plateau_label,
            )

    ax.margins(x=0.02)
    return ax
