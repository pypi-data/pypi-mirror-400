# Framework Integrations Guide

This guide explains how ZeroProof integrates with NumPy, PyTorch, JAX, and TensorBoard, how to run the unified integration suite, and how to set up a CPU‑friendly environment. It also notes common pitfalls and how to resolve them.

## Install

- From PyPI (recommended):
  - `pip install zeroproofml`
  - Extras:
    - PyTorch: `pip install zeroproofml[torch]`
    - JAX: `pip install zeroproofml[jax]`
  - All extras: `pip install zeroproofml[all]`

- From source (development):
  - `pip install -e .[dev]`

- CPU‑only integrations (laptops without a dedicated GPU):
  - `pip install -r requirements-int.txt`
  - This installs NumPy, CPU‑only PyTorch and JAX, TensorBoard, and matplotlib.
  - If pip pulled a CUDA PyTorch on a CPU‑only machine, override with CPU wheels:
    - `pip install --index-url https://download.pytorch.org/whl/cpu torch`
  - If JAX CPU wheels are unavailable for your platform, use:
    - `pip install -U "jax[cpu]"`

Tip (JAX precision): set 64‑bit for parity with NumPy/Torch and to suppress dtype warnings.

- Via env var (shell): `export JAX_ENABLE_X64=1`
- Programmatically (Python):
  ```python
  import jax
  jax.config.update("jax_enable_x64", True)
  ```

## Backends

### NumPy
- Layer: `NPRational`
- Trainer: `NumpyTRTrainer` with `NumpyTrainingConfig`
- Usage (parity path): see `zeroproof/utils/parity.py::_numpy_run`
- Outputs: metrics dict including per‑bucket MSE (B0..B4) when available.

### PyTorch
- Layer: `TorchTRRational` (+ multi‑head variant)
- Trainer: `train_torch_rational(model, x, y, TorchTrainingConfig)`
- Gradient modes: Mask‑REAL (default), SATURATING, HYBRID (via `GradientModeConfig`, trainer exposes `gradient_mode`, `delta`, `gmax`).
- Determinism: trainer enables `torch.use_deterministic_algorithms(True)` when `deterministic=True`; a unit test verifies reproducibility (`tests/unit/test_torch_determinism.py`).
- Tensor output for loss: use `model.forward_values(x)`; `model(x)` returns TRTensor (values+tags).

### JAX
- Array wrapper: `TRJaxArray(values, tags)` with pytree registration.
- Primitives: `tr_add`, `tr_mul`, `tr_div`, `tr_log`, `tr_sqrt` defined with `custom_vjp` (Mask‑REAL/VJP‑safe; compatible bwd signatures).
- Deterministic reductions: `tr_sum_jax`, `tr_mean_jax` pairwise via `lax.associative_scan` (order‑stable within tolerance on CPU).
- Trainer: `train_jax_rational(theta0, phi0, x, y, JaxTrainingConfig)`; Hybrid schedule in‑graph (hysteresis on |Q| percentiles).
- Precision: recommend enabling x64 for parity.

## TensorBoard

Unified writer: `zeroproof/loggers/ZPTBWriter` (used by trainers).

- Scalars: `loss`, `coverage`, `non_real_frac`, `q_min_epoch`, bucketed MSE (B0..B4), and schedule params (λ, τ, etc.).
- Histograms: `tags`, `|Q|`, `grad_abs`.
- Images: bar chart of per‑bucket MSE.
- HParams & Run metadata: seed, dataset checksum (when provided in configs), policy flags.

Default log dirs:
- Torch: `runs/torch_tr`
- JAX: `runs/jax_tr`

Launch: `tensorboard --logdir runs`

## Parity and Unified Runner

Parity helpers live in `zeroproof/utils/parity.py` and the unified runner is `scripts/run_integration_suite.py`.

Run all relevant unit tests plus a quick parity pass:

```bash
python scripts/run_integration_suite.py --out local_reports/integration_latest --quick
```

- Output:
  - Log: `local_reports/.../integration_suite.log`
  - Parity JSON: `local_reports/.../parity_results.json`
- Exit status: reflects pytest status (`pytest_exit=0` on success). Parity status is reported in the log as `parity_ok=True/False`.
- CPU friendliness: the runner sets thread pool env vars (e.g., `OMP_NUM_THREADS`) to 2 on ≤4‑thread CPUs, selects matplotlib Agg, disables CUDA visibility, and enables JAX x64.
- Flags:
  - `--quick` uses smaller samples/epochs to keep runtimes low on laptops.
  - `--threads N` to override BLAS/OMP threads.

## Common Issues

- “No module named 'zeroproof'” during parity: the runner adds the repo root to `sys.path`; run it from the project root.
- JAX `custom_vjp` backward signature errors: fixed in our bridge; if you see version‑related issues, pin to a recent CPU build, e.g. `jax[cpu]==0.4.26`, or use `requirements-int.txt`.
- PyTorch installed with CUDA on CPU‑only machines: install CPU wheels via `--index-url https://download.pytorch.org/whl/cpu`.
- JAX float64 warnings: enable x64 (`JAX_ENABLE_X64=1`) or accept float32 numerics (parity tolerances may need adjustment).

## Examples

- Torch quick demo: `python examples/torch_quick_demo.py` then `tensorboard --logdir runs/torch_tr`
- JAX quick demo: `python examples/jax_quick_demo.py` then `tensorboard --logdir runs/jax_tr`
- Compare backends (prints metrics): `python examples/compare_backends_quick.py`

## Recommended Laptop Setup (2C/4T i5‑7200U)

- Install `requirements-int.txt`.
- Use `--quick` mode on the runner.
- Keep threads to 2: `python scripts/run_integration_suite.py --threads 2 --quick --out local_reports/integration_latest`
- Expect: all unit tests pass; parity for NumPy, JAX, and Torch reports within tolerance.
