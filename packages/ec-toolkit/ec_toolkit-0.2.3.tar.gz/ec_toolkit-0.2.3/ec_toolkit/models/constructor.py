import warnings
import keyword
from ec_toolkit.models.classes import Compound, ElementaryStep, Mechanism


def mechanism_constructor(
    name: str,
    step_stoich: list,
    step_labels: list | None,
    el_steps: list,
    *,
    eq_pot: float,
    is_oxidation_reaction: bool,
    sym_fac: int,
    ref_el: str,
    correction_step: int | None = None,  # 1-based index or None (requires Python 3.10+)
):
    """
    Create a Mechanism constructor for a given template.

    Parameters
    ----------
    correction_step : int | None
        If provided (1-based), the template will mark that elementary step with
        apply_correction=True. The wrapper returned will NOT require species that
        appear *only* in that correction step (they are ignored during user input).
    """
    # basic checks
    N = len(step_stoich)
    if len(el_steps) != N:
        raise ValueError("len(el_steps) must equal number of steps")
    if step_labels is not None and len(step_labels) != N:
        raise ValueError("len(step_labels) must equal number of steps or be None")

    # validate correction_step if given (1-based)
    if correction_step is not None:
        if not isinstance(correction_step, int):
            raise TypeError("correction_step must be an integer 1..N or None")
        if correction_step < 1 or correction_step > N:
            raise ValueError(f"correction_step must be between 1 and {N} (inclusive)")
        corr_idx = correction_step - 1
    else:
        corr_idx = None

    # ordered unique template species (appearance order)
    species_required = []
    for s in step_stoich:
        for k in s.keys():
            if k not in species_required:
                species_required.append(k)

    # count appearances of each species across all steps
    species_counts: dict = {}
    for s in step_stoich:
        for k in s.keys():
            species_counts[k] = species_counts.get(k, 0) + 1

    # species to ignore: those that appear in correction step AND nowhere else (count == 1)
    if corr_idx is not None:
        species_in_corr = set(step_stoich[corr_idx].keys())
        species_to_ignore = {
            sp for sp in species_in_corr if species_counts.get(sp, 0) == 1
        }
    else:
        species_to_ignore = set()

    # species that the wrapper must ask for: remove only those that belong exclusively to correction step
    species_required_wrapper = [
        s for s in species_required if s not in species_to_ignore
    ]

    # safe-name mapping: only replace '-' -> '_' as requested, then make valid
    def _initial_safe(orig: str) -> str:
        return orig.replace("-", "_")

    def _make_valid_identifier(s: str) -> tuple[str, bool]:
        """Make valid identifier: replace non-alnum/_ with '_', prefix '_' if starts with digit,
        append '_' if a Python keyword. Return (identifier, warned_flag)."""
        warned = False
        out_chars = []
        for ch in s:
            if ch.isalnum() or ch == "_":
                out_chars.append(ch)
            else:
                out_chars.append("_")
                warned = True
        out = "".join(out_chars)
        if out and out[0].isdigit():
            out = "_" + out
            warned = True
        if keyword.iskeyword(out):
            out = out + "_"
            warned = True
        return out, warned

    orig_to_safe = {}
    safe_to_orig = {}
    warns = []
    for orig in species_required_wrapper:
        safe1 = _initial_safe(orig)
        safe_final, warned_flag = _make_valid_identifier(safe1)
        if warned_flag:
            warns.append((orig, safe1, safe_final))
        if safe_final in safe_to_orig and safe_to_orig[safe_final] != orig:
            raise ValueError(
                f"Template '{name}' produced a name collision: "
                f"'{safe_to_orig[safe_final]}' and '{orig}' both map to kw '{safe_final}'. "
                "Rename species to avoid collisions."
            )
        orig_to_safe[orig] = safe_final
        safe_to_orig[safe_final] = orig

    # print a creation hint (concise)
    safe_list = [orig_to_safe[o] for o in species_required_wrapper]
    ignore_list = sorted(list(species_to_ignore))
    hint = (
        f"[mechanism_constructor] template '{name}' created — call the returned constructor with keywords: "
        f"{', '.join(safe_list) if safe_list else '(no species required)'}"
    )
    if corr_idx is not None:
        hint += f"  (correction applied at step {correction_step}; species {ignore_list} are ignored because they appear only in the correction step)"
    print(hint)

    if warns:
        for orig, safe1, safe_final in warns:
            warnings.warn(
                f"Template species name '{orig}' required adjustment: intermediate '{safe1}' → kw '{safe_final}'. "
                "Avoid unusual characters in template species names.",
                UserWarning,
            )

    # inner builder from mapping original_name -> Compound
    def _build_from_map(provided_map: dict):
        # validate keys: required wrapper species must be supplied
        provided_keys = set(provided_map.keys())
        missing = [s for s in species_required_wrapper if s not in provided_keys]
        if missing:
            raise KeyError(
                f"Template '{name}' requires species {sorted(species_required_wrapper)}; missing {sorted(missing)}."
            )
        extra = [k for k in provided_keys if k not in species_required_wrapper]
        if extra:
            raise TypeError(f"Constructor got unexpected species keys: {sorted(extra)}")

        # build ElementaryStep objects
        steps = []
        for i, stoich_map in enumerate(step_stoich):
            stoich_compounds = {}
            for sp_name, coeff in stoich_map.items():
                if sp_name in provided_map:
                    # normal: user provided the Compound
                    stoich_compounds[provided_map[sp_name]] = float(coeff)
                else:
                    # not provided: must be because it's inside the correction step and ignored by wrapper
                    if (
                        corr_idx is not None
                        and i == corr_idx
                        and sp_name in species_to_ignore
                    ):
                        warnings.warn(
                            f"Species '{sp_name}' for correction step {correction_step} not provided — "
                            "(safe because correction step does not use energies).",
                            UserWarning,
                        )
                    else:
                        # missing species for non-correction step (or a correction species that actually appears elsewhere) -> error
                        raise KeyError(
                            f"Species '{sp_name}' required for step {i + 1} is missing from constructor call."
                        )

            label = step_labels[i] if step_labels is not None else f"step_{i + 1}"
            apply_corr_flag = i == corr_idx
            steps.append(
                ElementaryStep(
                    stoich=stoich_compounds,
                    label=label,
                    is_electrochemical=bool(el_steps[i]),
                    apply_correction=bool(apply_corr_flag),
                )
            )

        mech = Mechanism(
            steps=steps,
            eq_pot=float(eq_pot),
            sym_fac=int(sym_fac),
            ref_el=str(ref_el),
            is_oxidation_reaction=bool(is_oxidation_reaction),
        )
        return mech

    # create wrapper: keyword-only safe names; runtime-check each arg is Compound
    if species_required_wrapper:
        safe_params = ", ".join(orig_to_safe[orig] for orig in species_required_wrapper)
        signature = f"*, {safe_params}"
    else:
        safe_params = ""
        signature = ""  # no args

    wrapper_name = f"{name}_constructor".replace("-", "_")

    body_lines = []
    if species_required_wrapper:
        body_lines.append(
            "    # runtime type checks (each parameter must be a Compound)"
        )
        for orig in species_required_wrapper:
            safe = orig_to_safe[orig]
            body_lines.append(f"    if not isinstance({safe}, Compound):")
            body_lines.append(
                f"        raise TypeError('Parameter {safe} must be a Compound instance')"
            )
    body_lines.append(
        "    # map wrapper kwargs (safe names) back to template original names"
    )
    body_lines.append("    provided_map = {}")
    for orig in species_required_wrapper:
        safe = orig_to_safe[orig]
        body_lines.append(f"    provided_map[{orig!r}] = {safe}")
    body_lines.append("    return _build_from_map(provided_map)")

    # choose function signature depending on whether params exist
    if signature:
        wrapper_src = f"def {wrapper_name}({signature}):\n" + "\n".join(body_lines)
    else:
        # no args
        wrapper_src = f"def {wrapper_name}():\n" + "\n".join(body_lines)

    wrapper_ns = {"_build_from_map": _build_from_map, "Compound": Compound}
    exec(wrapper_src, wrapper_ns)
    wrapper = wrapper_ns[wrapper_name]

    # build docstring that IDEs will display (parameters listed as Compound)
    params_lines = ["Parameters", "----------"]
    for orig in species_required_wrapper:
        safe = orig_to_safe[orig]
        params_lines.append(f"{safe} : Compound")
        params_lines.append(f"    Compound species '{orig}'.")
    if corr_idx is not None:
        params_lines.append("")
        params_lines.append("Note")
        params_lines.append("----")
        params_lines.append(
            f"Species appearing only in correction step (step {correction_step}) are not required by this constructor: "
            f"{sorted(list(species_to_ignore))}."
        )
    params_text = "\n".join(params_lines)

    wrapper.__doc__ = (
        f"Mechanism constructor for template '{name}'.\n\n"
        f"{params_text}\n\n"
        f"Returns\n"
        f"-------\n"
        f"Mechanism\n"
        f"    Mechanism with an equilibrium potential of {eq_pot}, is_oxidation_reaction={is_oxidation_reaction}, "
        f"sym_fac={sym_fac}, in the {ref_el} scale. Correction step: {correction_step!r}.\n\n"
        f"Call using keyword-only arguments (hyphen '-' replaced by '_' in kw names)."
    )

    # helpful example string attached for copy/paste
    if species_required_wrapper:
        example_args = ", ".join(
            f"{orig_to_safe[o]}=<Compound>" for o in species_required_wrapper
        )
        wrapper.example_call = f"{wrapper.__name__}({example_args})"
    else:
        wrapper.example_call = f"{wrapper.__name__}()"

    # attach introspection metadata
    wrapper.template_name = name
    wrapper.template_species = tuple(species_required)
    wrapper.template_species_wrapper = tuple(species_required_wrapper)
    wrapper.template_safe_names = tuple(
        orig_to_safe[o] for o in species_required_wrapper
    )
    wrapper.template_steps = N
    wrapper.template_eq_pot = float(eq_pot)
    wrapper.template_is_oxidation_reaction = bool(is_oxidation_reaction)
    wrapper.template_sym_fac = int(sym_fac)
    wrapper.template_ref_el = str(ref_el)
    wrapper.template_correction_step = correction_step

    return wrapper
