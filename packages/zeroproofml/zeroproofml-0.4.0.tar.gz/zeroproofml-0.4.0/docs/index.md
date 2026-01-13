# ZeroProofML v0.4 Documentation Hub

This documentation set tracks the SCM migration described in `concept.tex`. The sections below mirror the phases in `todo.md` and surface the material that is already implemented in code.

## Structure
- Files prefixed with `00_…`–`06_…` are the core “read in order” guides.
- Higher-numbered files are reference, add-ons, and engineering notes.
- `docs/theory/` contains deeper algebraic notes (also numbered).
- `docs/archive_tr/` contains legacy Transreal-era documentation for historical reference.

## Core Guides
- [00_getting_started.md](00_getting_started.md) — install, run the quickstart, and understand the new SCM primitives.
- [01_scm_foundations.md](01_scm_foundations.md) — algebraic background for signed common meadows and the absorptive bottom.
- [02_projective_learning.md](02_projective_learning.md) — when and how to enable projective (N, D) mode.
- [03_gradient_policies.md](03_gradient_policies.md) — choosing masking/clamping/projective strategies.
- [04_loss_functions.md](04_loss_functions.md) — implicit, margin, sign consistency, and rejection losses.
- [05_training_guide.md](05_training_guide.md) — trainer loop, mixed precision, and coverage heuristics.
- [06_inference_deployment.md](06_inference_deployment.md) — strict SCM semantics, safety margins, and export notes.

## Engineering Notes
- [07_projective_training_dev.md](07_projective_training_dev.md) — developer walk-through of tuple renormalization and SCM decode.
- [15_debug_logging.md](15_debug_logging.md) — capturing trainer metrics via `log_hook`.
- [16_verification_report.md](16_verification_report.md) — what the v0.4 SCM code implements.

## Reference Material
- [MIGRATION.md](../MIGRATION.md) — breaking changes and v0.3 → v0.4 translations.
- [concept.tex](../concept.tex) — conceptual framework for the algebraic turn.
- [theory/](theory/00_overview.md) — SCM algebra, weak signs, and fracterm flattening.
- [08_api_reference.md](08_api_reference.md) — public API surface summary for SCM, autodiff, and projective helpers.
- [09_bridge_summary.md](09_bridge_summary.md) — scalar IEEE bridge and vectorised SCM masks.
- [10_bridge_extended.md](10_bridge_extended.md) — worked examples for NumPy/Torch masks and projective heads.
- [11_integrations.md](11_integrations.md) — integration patterns for NumPy/Torch/JAX.
- [12_float64_enforcement.md](12_float64_enforcement.md) — dtype guidance and singular threshold notes.
- [17_experiment_protocol_v1.md](17_experiment_protocol_v1.md) — scientifically accurate paper-suite protocol.

## Training Add-Ons
- [13_adaptive_loss_guide.md](13_adaptive_loss_guide.md) — coverage control and rejection loss wiring.
- [14_adaptive_loss_summary.md](14_adaptive_loss_summary.md) — quick summary of coverage/rejection.

## Optimization
- [19_optimization_summary.md](19_optimization_summary.md) — performance levers and testing summary.
- [20_optimization_guide.md](20_optimization_guide.md) — deeper performance notes and profiling guidance.

## Benchmarks & Examples
- Updated scripts in `examples/` demonstrate SCM operations, projective tuples, and coverage control.
- Benchmark notebooks and runners in `benchmarks/` compare SCM against the archived Transreal path.
- Benchmarks overview: [18_benchmarks.md](18_benchmarks.md).

## Archives
- Transreal and wheel-mode materials now live in `docs/archive_tr/` for historical reference only.
  This includes the former `docs/topics/` deep-dives (now under `docs/archive_tr/topics/`).

## How to Navigate
- Start with **Getting Started** to verify your environment.
- Move to **SCM Foundations** before implementing custom layers or losses.
- Use the guides as a checklist when wiring projective heads or selecting gradient policies.
- Cross-reference `todo.md` to see which documentation items are still in progress.
