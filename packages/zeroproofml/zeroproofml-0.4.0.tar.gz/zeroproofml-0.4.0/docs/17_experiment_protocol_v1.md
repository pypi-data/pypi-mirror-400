# Experiment Protocol v1 (Paper Suite)

This document defines the **scientifically accurate comparison protocol** used by the paper suites (Phase 12+).
It is intended to make results reproducible, ceteris paribus, and suitable for TMLR-style reporting.

## Protocol ID

- `protocol_version`: `v1`

## Core Rules (Ceteris Paribus)

1. **Same dataset** per seed and domain; dataset hash recorded.
2. **Same train/test split** for all methods; split indices persisted in the run JSON.
3. **Comparable model capacity** for learned baselines (parameter-count matched within a small tolerance when feasible).
4. **Comparable compute budget** for learned methods:
   - Default budget mode: **optimizer steps** (not wall-clock).
   - Report both epochs and derived optimizer steps; steps are primary for fairness.
5. **Hyperparameter search budget** is fixed per method family (same number of trials) and recorded.

Analytic references (e.g., DLS) are included for context, but are not the primary “learned baseline to beat”.

## Invalid Output Policy

Some methods may produce invalid outputs (e.g., NaN/Inf, SCM ⊥/bottom).

Protocol requires reporting BOTH:

- `mse_valid_only`: MSE computed only on samples where the method produced a valid decoded prediction.
- `success_rate`: fraction of samples producing valid decoded outputs.

Optionally, suites may also report:

- `mse_with_penalty`: invalid samples count as a fixed penalty (to enable a single scalar objective).

The policy and penalty are recorded in the run metadata so comparisons are explicit.

## Primary Metrics (Robotics Suite)

- **Overall decoded MSE** (plus success/coverage rate).
- **Near-pole bucket MSE** for B0/B1/B2 (and counts), bucketing by `|det(J)|`.
- **Rollout metrics**:
  - mean tracking error
  - failure rate / gap rate (if applicable)
  - joint step max and percentiles (P95/P99)

## Secondary Metrics (Resources / Time)

Per method, record:

- parameter count
- training time (wall clock)
- inference latency (optional; batch and single-sample)
- peak RSS (CPU) and peak CUDA memory (if GPU)

## Baseline Taxonomy (v1)

- **Analytic reference**: `DLS`, `DLS-Adaptive`
- **Learned non-projective** (Torch-first in Phase 12): `MLP`, `MLP+PoleHead`, `Rational+ε`, `Smooth`, `LearnableEps`, `EpsEnsemble`
- **Learned projective/meadow**: `ZeroProofML-SCM-Basic`, `ZeroProofML-SCM-Full`

## “Key baseline to beat”

For learned-method claims, the key baseline is:

- `EpsEnsemble` (strong engineering regularization baseline),
with the single-model `Rational+ε` / `Smooth` family as additional comparators.

`DLS` is not required to be beaten on overall MSE for a learned-method claim; it is a reference point.
