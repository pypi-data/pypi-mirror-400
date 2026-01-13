# ZeroProofML v0.4.0: The Algebraic Turn

ZeroProofML 0.4.0 completes the migration from transreal arithmetic to **signed common meadows (SCM)**. Division by zero and domain errors now flow to the absorptive bottom element `⊥`, while gradient policies and optional projective tuples keep training stable without guard rails. This release also brings stricter CI, coverage enforcement, and release-ready packaging.

## Why Signed Common Meadows?
- **Single absorptive bottom (`⊥`)** replaces the transreal `±∞` and `Φ`, simplifying graph semantics and enabling compiler-friendly code.
- **Weak sign operator** keeps orientation near singularities to distinguish `+∞` from `-∞` targets.
- **Fracterm flattening** lets rational heads collapse to a single `P/Q` check, with `⊥` detected once at the boundary.

## Training on Smooth, Inferring on Strict
- Projective mode lifts rational heads to `(N, D)` tuples with detached renormalization, keeping training smooth while decoding back to strict SCM for inference.
- Gradient policies gate how `⊥` influences backpropagation, avoiding dead zones while preserving exact forward semantics.

## Release Highlights
- SCM-aware loss stack (implicit, margin, sign consistency, and coverage) tuned for robotics and safety-critical tasks.
- Coverage-first training loop with adaptive sampling and deterministic inference thresholds.
- CI and packaging tightened: ruff/black/isort, `mypy --strict`, 90% coverage gate, and ready-to-upload wheels.

## Try It
```bash
pip install zeroproofml==0.4.0
```
Or build from source with the release helper:
```bash
python scripts/release_v0_4_0.py --skip-twine
```

## Looking Ahead
This release anchors the algebraic foundation. Follow-up work will focus on XLA compilation checks, adaptive rejection tuning, and public benchmarks comparing SCM to the archived transreal models.
