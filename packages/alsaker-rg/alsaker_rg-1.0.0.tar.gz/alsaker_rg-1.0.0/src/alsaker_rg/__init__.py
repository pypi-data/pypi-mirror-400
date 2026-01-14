"""
alsaker_rg: Statistical estimation of radius of gyration from SAXS data

This package provides a statistically rigorous method for estimating the radius 
of gyration (Rg) from Small-Angle X-ray Scattering (SAXS) data using minimum mean 
squared error with optimal window selection.

Reference:
    Alsaker, C., Breidt, F. J., & van der Woerd, M. J. (2018). 
    Minimum Mean Squared Error Estimation of the Radius of Gyration in 
    Small-Angle X-Ray Scattering Experiments. 
    Journal of the American Statistical Association.
    DOI: 10.1080/01621459.2017.1408467
"""

__version__ = "1.0.0"
__author__ = "Cody Alsaker, F. Jay Breidt, Mark J. van der Woerd"
__author_email__ = "biosaxs-dev@github.com"

from .estimation import (
    estimate_Rg,
    detect_changepoint,
    create_gamma_matrix,
    ind_ar_struc,
    comb_spline,
    b_v_tradeoff_comb,
    calc_Rg,
    HAS_RUPTURES,
)

__all__ = [
    "estimate_Rg",
    "detect_changepoint",
    "create_gamma_matrix",
    "ind_ar_struc",
    "comb_spline",
    "b_v_tradeoff_comb",
    "calc_Rg",
    "HAS_RUPTURES",
]
