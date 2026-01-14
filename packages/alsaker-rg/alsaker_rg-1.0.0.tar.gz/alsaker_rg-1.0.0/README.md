# SAXS Radius of Gyration Estimation

Python implementation of the Alsaker-Breidt-van der Woerd method for estimating the radius of gyration from Small-Angle X-ray Scattering (SAXS) data.

This package is a Python migration of the original R code by Cody Alsaker, F. Jay Breidt, and Mark J. van der Woerd, available at the Colorado State University Mountain Scholar repository: https://mountainscholar.org/items/4c08f6d5-0f9b-4d45-a35a-ad39b59d3161

**Data Source Acknowledgment:** The original R code and research data are provided under the [CSU Research Data Terms of Use](https://lib.colostate.edu/find/csu-digital-repository/policies-guidelines-forms/research-data-terms-of-use/), which requires proper attribution and compliance with any applicable licenses.

## Overview

This package provides a statistically rigorous method for estimating the radius of gyration (Rg) from SAXS intensity data. The method uses:

- **Optimal window selection** via minimum mean squared error (MSE) criterion
- **Generalized least squares** estimation accounting for autocorrelation
- **Automatic outlier detection** for starting point selection
- **Multiple replicate support** with proper variance estimation

### Reference

Alsaker, C., Breidt, F. J., & van der Woerd, M. J. (2018). Minimum Mean Squared Error Estimation of the Radius of Gyration in Small-Angle X-Ray Scattering Experiments. *Journal of the American Statistical Association*. DOI: [10.1080/01621459.2017.1408467](https://doi.org/10.1080/01621459.2017.1408467)

## What is SAXS?

Small-Angle X-ray Scattering (SAXS) is a technique for determining low-resolution structural information about biological macromolecules (proteins, DNA, RNA) in solution. When a sample is exposed to X-rays, the scattered intensity at different angles provides information about the molecule's shape and size.

The **radius of gyration** (Rg) is a fundamental structural parameter that describes the spread of mass in a molecule - analogous to the standard deviation of a probability distribution.

## Installation

### From PyPI (recommended)

```bash
# Basic installation
pip install alsaker-rg

# With optional changepoint detection (recommended)
pip install alsaker-rg[changepoint]

# With all optional dependencies
pip install alsaker-rg[all]
```

### From Source

```bash
git clone https://github.com/biosaxs-dev/alsaker-rg.git
cd alsaker-rg
pip install -e .

# Or with optional dependencies
pip install -e .[changepoint]
```

**Note:** The `ruptures` package is optional but recommended for proper changepoint detection using the PELT algorithm (matches the original R implementation). If not installed, the code will use a simplified fallback heuristic.

## Quick Start

### Single Replicate

```python
import numpy as np
from alsaker_rg import estimate_Rg

# Load your SAXS data
# Expected format: Column 0 = angles, Column 1 = intensities
data = np.loadtxt("your_data.dat")

# Estimate Rg with automatic starting point selection
Rg, se, t, cp2, sp = estimate_Rg(data, num_reps=1)

print(f"Rg = {Rg:.1f} ± {se:.2f} Å")
print(f"Guinier region: {t} points starting at index {sp[0]}")
print(f"s range: {data[sp[0], 0]:.4f} to {data[sp[0]+t-1, 0]:.4f} Å⁻¹")
```

### Multiple Replicates

```python
import numpy as np
from alsaker_rg import estimate_Rg

# Load multiple replicate files
data1 = np.loadtxt("replicate_01.dat")
data2 = np.loadtxt("replicate_02.dat")
data3 = np.loadtxt("replicate_03.dat")

# Combine: angles + intensities from each replicate
combined = np.column_stack([
    data1[:, 0],  # angles
    data1[:, 1],  # intensity rep 1
    data2[:, 1],  # intensity rep 2
    data3[:, 1],  # intensity rep 3
])

# Estimate Rg from 3 replicates
Rg, se, t, cp2, sp = estimate_Rg(combined, num_reps=3)

print(f"Rg = {Rg:.1f} ± {se:.2f} Å")
print(f"Used {t} points per replicate")
for i in range(3):
    print(f"  Rep {i+1}: indices {sp[i]} to {sp[i]+t-1}")
```

## Function Reference

### `estimate_Rg(M, num_reps, starting_value=-1, make_plots=True)`

Estimate the radius of gyration from SAXS data.

**Parameters:**
- `M` (ndarray): Data matrix with shape (n, num_reps + 1)
  - Column 0: scattering angles (s)
  - Columns 1+: intensities for each replicate
- `num_reps` (int): Number of replicates
- `starting_value` (int or list, optional): Starting indices (1-indexed)
  - Default: -1 (automatic detection)
  - Single value: applied to all replicates
  - List: different starting point for each replicate
- `make_plots` (bool, optional): Create diagnostic plots (default: True)

**Returns:**
- `Rg` (float): Radius of gyration estimate (Ångströms)
- `se` (float): Standard error of estimate
- `t` (int): Optimal window length (number of points used)
- `cp2` (int): Maximum cutoff index
- `sp` (ndarray): Starting point indices (0-indexed) for each replicate
  - Guinier region for replicate i: `M[sp[i]:sp[i]+t, :]`

## Examples

Run the provided example scripts:

```bash
# Single replicate example
python example_single_replicate.py

# Multiple replicates example
python example_multiple_replicates.py

# Changepoint detection comparison (with/without ruptures)
python demo_changepoint_detection.py
```

## Data Format

Your SAXS data should be a text file with:
- **Column 0**: Scattering angles (s) in Ångströms⁻¹
- **Column 1**: Intensity values
- **Column 2** (optional): Error estimates (not used by algorithm)

Example:
```
0.0100  1000.50  15.2
0.0105   998.32  15.1
0.0110   995.87  15.0
...
```

## Scientific Background

### Guinier Approximation

For small scattering angles, the intensity follows:

```
ln I(s) = ln I(0) - (1/3) * Rg² * s² + O(s⁴)
```

### Method Advantages

Compared to classical Guinier analysis:

1. **Optimal window selection**: Balances bias and variance automatically
2. **Accounts for autocorrelation**: Uses GLS instead of OLS
3. **Automatic outlier detection**: Removes problematic initial points
4. **Multiple replicate support**: Proper variance estimation
5. **Objective and reproducible**: Eliminates subjective choices

## File Structure

```
alsaker-rg/
├── alsaker_rg.py                  # Main module
├── example_single_replicate.py    # Single replicate example
├── example_multiple_replicates.py # Multiple replicate example
├── README.md                       # This file
├── original/                       # Original R code and paper
│   ├── R-code/
│   │   ├── file1.R               # Main R functions
│   │   ├── file2.R               # Single replicate examples
│   │   └── file3.R               # Multiple replicate examples
│   └── 2018, Cody Alsaker.pdf    # Published paper
└── requirements.txt               # Python dependencies (optional)
```

## Citation

If you use this software in your research, please cite:

```bibtex
@article{alsaker2018minimum,
  title={Minimum Mean Squared Error Estimation of the Radius of Gyration 
         in Small-Angle X-Ray Scattering Experiments},
  author={Alsaker, Cody and Breidt, F Jay and van der Woerd, Mark J},
  journal={Journal of the American Statistical Association},
  year={2018},
  publisher={Taylor \& Francis},
  doi={10.1080/01621459.2017.1408467}
}
```

## Acknowledgments

This Python package was developed with assistance from **GitHub Copilot**, which helped migrate the original R code to Python and establish the modern package structure.

## License

See LICENSE file for details.

## Comparison with R Code

### Function Correspondence

| R Function | Python Function |
|------------|----------------|
| `estimate_Rg()` | `estimate_Rg()` |
| `comb_spline()` | `comb_spline()` |
| `ind_ar_struc()` | `ind_ar_struc()` |
| `create_gamma_matrix()` | `create_gamma_matrix()` |
| `b_v_tradeoff_comb()` | `b_v_tradeoff_comb()` |
| `calc_Rg()` | `calc_Rg()` |

### Key Differences

1. **Return values** (Enhancement): Python version returns 5 values `(Rg, se, t, cp2, sp)` vs R's 4 values `(Rg, se, t, cp2)`
   - Added `sp`: Starting point indices for each replicate
   - Allows users to report the exact Guinier region: `s[sp[i]:sp[i]+t]`
   - Essential for scientific reporting and reproducibility
   
2. **Array indexing**: Python uses 0-based indexing (R uses 1-based)

3. **Libraries**: NumPy/SciPy vs base R

4. **Time series**: statsmodels vs R's ar()

5. **Plotting**: matplotlib vs base R graphics

## Support

For questions or issues:
- GitHub Issues: https://github.com/biosaxs-dev/alsaker-rg/issues
