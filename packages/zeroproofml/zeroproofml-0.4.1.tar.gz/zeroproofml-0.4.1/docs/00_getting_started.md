# Getting Started with ZeroProofML v0.4 (SCM)

ZeroProofML v0.4 replaces Transreal arithmetic with Signed Common Meadows (SCM), where division by zero yields a single absorptive bottom value (⊥). This guide walks through installation and a minimal SCM workflow.

## Install
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```
2. Install the package in editable mode for iterative work:
   ```bash
   pip install -e .
   ```

## Quickstart
```python
from zeroproof.scm.ops import scm_add, scm_div
from zeroproof.scm.value import scm_real, scm_bottom

x = scm_real(3.0)
y = scm_real(0.0)

print(scm_div(x, y))   # SCMValue(⊥) — absorptive bottom on division by zero
print(scm_add(scm_bottom(), x))  # SCMValue(⊥) — bottom absorbs addition
```

## Projective vs. Strict SCM
- **SCM mode (default):** All operations propagate ⊥ according to meadow axioms. Gradient policies shape backpropagation near singularities.
- **Projective mode (optional):** Rational heads run on homogeneous tuples (N, D) during training for smooth optimisation; decoding back to SCM introduces ⊥ only at the boundary.

## What Changed from v0.3
- No Transreal tags (+∞, −∞, Φ); a single ⊥ represents all singular states.
- Guard logic has been removed—one SCM check at the output replaces layer-by-layer conditionals.
- Gradient handling is explicit via policies (clamp, project, reject, passthrough) defined in `zeroproof.autodiff.policies`.

## Next Steps
- Read [SCM Foundations](01_scm_foundations.md) for the algebraic rules we follow.
- Explore [Projective Learning](02_projective_learning.md) if you train rational heads.
- Consult [Migration Guide](../MIGRATION.md) to port v0.3 code.
