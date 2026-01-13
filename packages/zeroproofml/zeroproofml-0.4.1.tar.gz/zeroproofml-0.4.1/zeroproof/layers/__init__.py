# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Neural network layers built on Signed Common Meadows."""

from __future__ import annotations

from zeroproof.layers.fru import FractermRationalUnit
from zeroproof.layers.normalization import SCMNorm, SCMSoftmax
from zeroproof.layers.scm_rational import (
    BasisFunction,
    ChebyshevBasis,
    CustomBasis,
    MonomialBasis,
    SCMRationalLayer,
)

__all__ = [
    "FractermRationalUnit",
    "SCMRationalLayer",
    "SCMNorm",
    "SCMSoftmax",
    "BasisFunction",
    "MonomialBasis",
    "ChebyshevBasis",
    "CustomBasis",
]
