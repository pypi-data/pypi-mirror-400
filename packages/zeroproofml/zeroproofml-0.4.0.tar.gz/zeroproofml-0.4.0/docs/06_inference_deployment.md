# Inference & Deployment

Inference in ZeroProofML v0.4 uses strict SCM semantics: no stochastic thresholds and explicit ⊥ outputs for singular inputs.

## Runtime Rules
- Use a fixed `τ_infer` to decide when denominators are treated as singular (`|Q| < τ_infer` ⇒ ⊥).
- When you know the training-time margin `τ_train` (typically `τ_train > τ_infer`), you can *detect* the training–inference gap region `τ_infer ≤ |Q| < τ_train` and treat it as numerically risky at deployment time (e.g., log it, trigger fallbacks, or tighten `τ_infer`).
- No gradient policies are applied; forward behaviour matches the strict SCM decode rule used by `zeroproof.inference.mode.strict_inference`.
- Encode ⊥ as `nan` when bridging to IEEE-754 via `utils.ieee_bridge.to_ieee`.

## Exporting Models
- TorchScript: projective operations avoid Python-side branching, enabling `torch.jit.script(model)` for deployment.
- ONNX: supported where custom ops permit; ensure ⊥ propagation is preserved.
- Checkpoints: saved via `SCMTrainer.save_checkpoint`, compatible with both SCM-only and projective graphs.

## Safety Checklist
- Validate coverage on a held-out set using `losses.coverage.coverage` before shipping.
- Monitor the rate of ⊥ outputs in production; aggressive rejection loss during training usually lowers this.
- For robotics or control, ensure sign consistency loss was active so orientation of infinities is preserved.
