# Fracterm Flattening in ZeroProofML

Common meadow theory guarantees that any term over the signature can be
flattened into a single rational function `P(x)/Q(x)` (see `concept.tex`).
ZeroProofML adopts this result for **Fused Rational Units (FRUs)** to make
singularity detection and policy selection predictable without expanding
the entire network.

## Engineering Scope

- **Local flattening only.** To avoid degree explosion, flattening is
  restricted to small rational heads instead of whole models; the rest of
  the network stays in standard SCM or projective form (see `concept.tex`).
- **Constant-time checks.** By keeping the rational part flattened, we can
  decide whether a forward pass hits the ⊥-producing denominator with an
  `O(1)` check on `Q_head`, rather than walking each intermediate layer.
- **Projective compatibility.** FRU outputs can be decoded either strictly
  into SCM values or as projective tuples `(N, D)` during training, keeping
  gradients smooth around poles.

## Implementation Status

- `zeroproof.scm.fracterm` provides symbolic utilities for representing and simplifying small `P/Q` terms.
- `zeroproof.layers.fru.FractermRationalUnit` currently enforces the *degree-growth and depth* constraints from `concept.tex` and provides a lightweight placeholder `flatten(...)` helper; it is not yet a full automatic “flatten an arbitrary PyTorch subgraph” pass.

## Worked Example

Consider a two-layer FRU `((x + 1) / x) / (x - 1)`. Flattening produces

```text
P(x) = x + 1
Q(x) = x(x - 1)
```

so the singularities live at `x ∈ {0, 1}` and can be detected by checking
`Q(x)` once, instead of monitoring every intermediate op.

## Authoring Guidelines

1. Represent rational heads explicitly as `(numerator, denominator)` pairs
   or helper classes so the final denominator is easy to inspect.
2. Prefer shallow FRUs (depth ≤ 5) to keep polynomial degrees manageable,
   matching the hard limit in the migration plan.
3. Document where flattening occurs in layer docstrings so Sphinx/MkDocs
   can surface the singularity story alongside the API.

## References

- J.A. Bergstra and A. Ponse, *Common Meadows* (2019 revision)
- J.A. Bergstra and J.V. Tucker, *Fracterm calculus and totalised fields*
