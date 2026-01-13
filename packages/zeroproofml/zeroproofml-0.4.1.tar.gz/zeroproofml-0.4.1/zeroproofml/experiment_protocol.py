from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


PROTOCOL_VERSION = "v1"


@dataclass(frozen=True)
class InvalidOutputPolicy:
    """
    Defines how invalid predictions are handled in reporting.

    Protocol requirement: always report MSE on valid-only samples AND success_rate.
    Optionally report a penalized MSE that counts invalid samples as a fixed penalty.
    """

    mse_valid_only: bool = True
    report_success_rate: bool = True
    report_penalized_mse: bool = True
    invalid_penalty_mse: float = 1.0


@dataclass(frozen=True)
class ComputeBudgetPolicy:
    """
    Defines what "fair compute" means for learned methods.
    """

    budget_mode: str = "optimizer_steps"  # "optimizer_steps" | "epochs" | "wall_clock"
    hpo_max_trials: int = 0


def protocol_v1(
    *,
    domain: str,
    suite_name: str,
    invalid_policy: Optional[InvalidOutputPolicy] = None,
    compute_budget: Optional[ComputeBudgetPolicy] = None,
    notes: str | None = None,
) -> Dict[str, Any]:
    """
    Return a machine-readable protocol block to embed into run JSONs.
    """
    invalid_policy = invalid_policy or InvalidOutputPolicy()
    compute_budget = compute_budget or ComputeBudgetPolicy()
    return {
        "protocol_version": PROTOCOL_VERSION,
        "domain": str(domain),
        "suite_name": str(suite_name),
        "invalid_output_policy": asdict(invalid_policy),
        "compute_budget_policy": asdict(compute_budget),
        "baseline_taxonomy": {
            "analytic_reference": ["DLS", "DLS-Adaptive"],
            "learned_non_projective": [
                "MLP",
                "MLP+PoleHead",
                "Rational+ε",
                "Smooth",
                "LearnableEps",
                "EpsEnsemble",
            ],
            "learned_projective_meadow": ["ZeroProofML-SCM-Basic", "ZeroProofML-SCM-Full"],
        },
        "key_learned_baseline": "EpsEnsemble",
        "notes": notes,
    }
