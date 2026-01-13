"""
Minimal Signed Common Meadow (SCM) quickstart.
"""
from __future__ import annotations

import torch

from zeroproof.scm.ops import scm_add, scm_div, scm_mul
from zeroproof.scm.value import scm_bottom, scm_real
from zeroproof.layers import SCMRationalLayer


def basic_scm_arithmetic() -> None:
    a = scm_real(2.0)
    b = scm_real(-3.0)
    zero = scm_real(0.0)
    print("a + b =", scm_add(a, b))
    print("a * b =", scm_mul(a, b))
    print("a / 0 =", scm_div(a, zero))
    print("⊥ absorbs multiplication:", scm_mul(a, scm_bottom()))


def rational_forward() -> None:
    x = torch.tensor([-2.0, -0.5, 0.0, 0.5, 2.0])
    layer = SCMRationalLayer(1, 1)
    with torch.no_grad():
        layer.numerator[:] = torch.tensor([0.0, 1.0])
        layer.denominator[:] = torch.tensor([1.0, 0.1])
    y, bottom = layer(x)
    print("inputs    :", x.tolist())
    print("outputs   :", torch.nan_to_num(y, nan=float("nan")).tolist())
    print("⊥ mask    :", bottom.tolist())


def main() -> None:
    print("-- SCM arithmetic --")
    basic_scm_arithmetic()
    print("\n-- SCMRational forward --")
    rational_forward()


if __name__ == "__main__":
    main()
