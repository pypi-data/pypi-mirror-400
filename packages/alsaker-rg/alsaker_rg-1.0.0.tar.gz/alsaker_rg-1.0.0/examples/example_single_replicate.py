"""
Example: Single replicate SAXS data analysis

This example demonstrates how to estimate the radius of gyration (Rg)
from a single SAXS intensity curve.

Reference: file2.R from original R code
"""

import numpy as np
from alsaker_rg import estimate_Rg


def main():
    """Run single replicate example."""
    
    print("=" * 70)
    print("Single Replicate SAXS Analysis Example")
    print("=" * 70)
    print()
    
    # Example 1: Read data by navigating to file (interactive)
    # In Python, you can use a file dialog or specify the path directly
    
    # For demonstration, we'll show how to load data from a file:
    # Uncomment one of the following methods:
    
    # Method 1: Direct file path
    # data = np.loadtxt("oval_01C_S008_0_01.dat")
    
    # Method 2: Interactive file selection (requires tkinter)
    # from tkinter import Tk, filedialog
    # Tk().withdraw()
    # filename = filedialog.askopenfilename(
    #     title="Select SAXS data file",
    #     filetypes=[("Data files", "*.dat *.txt"), ("All files", "*.*")]
    # )
    # data = np.loadtxt(filename)
    
    # Method 3: Generate synthetic data for demonstration
    print("Generating synthetic SAXS data for demonstration...")
    s = np.linspace(0.01, 0.5, 400)  # Scattering angles
    Rg_true = 30.0  # True radius of gyration
    I0 = 1000.0     # Forward scattering intensity
    
    # Guinier equation with noise
    log_intensity = np.log(I0) - (1/3) * Rg_true**2 * s**2
    # Add some AR(1) noise
    noise = np.zeros(len(s))
    noise[0] = np.random.normal(0, 0.1)
    for i in range(1, len(s)):
        noise[i] = 0.7 * noise[i-1] + np.random.normal(0, 0.1)
    
    log_intensity += noise
    intensity = np.exp(log_intensity)
    
    # Add error column (not used by the algorithm, but often present in SAXS data)
    errors = np.sqrt(intensity) / 10
    
    data = np.column_stack([s, intensity, errors])
    
    print(f"Data shape: {data.shape}")
    print(f"True Rg: {Rg_true:.1f} Å")
    print()
    
    # -----------------------------------------------------------------------
    # Example 1a: Single replicate with user-specified initial angle (5th point)
    # -----------------------------------------------------------------------
    print("Example 1a: User-specified starting point (5th data point)")
    print("-" * 70)
    
    Rg1, se1, t1, cp2_1, sp1 = estimate_Rg(data, num_reps=1, starting_value=5, make_plots=False)
    
    print(f"Estimated Rg: {Rg1:.1f} ± {se1:.2f} Å")
    print(f"Window length: {t1} points")
    print(f"Guinier region: indices {sp1[0]} to {sp1[0]+t1-1}")
    print(f"s range: {data[sp1[0], 0]:.4f} to {data[sp1[0]+t1-1, 0]:.4f} Å⁻¹")
    print(f"Maximum cutoff: {cp2_1}")
    print()
    
    # -----------------------------------------------------------------------
    # Example 1b: Single replicate with automatic starting point selection
    # -----------------------------------------------------------------------
    print("Example 1b: Automatic starting point selection")
    print("-" * 70)
    
    Rg2, se2, t2, cp2_2, sp2 = estimate_Rg(data, num_reps=1, make_plots=False)
    
    print(f"Estimated Rg: {Rg2:.1f} ± {se2:.2f} Å")
    print(f"Window length: {t2} points")
    print(f"Guinier region: indices {sp2[0]} to {sp2[0]+t2-1}")
    print(f"s range: {data[sp2[0], 0]:.4f} to {data[sp2[0]+t2-1, 0]:.4f} Å⁻¹")
    print(f"Maximum cutoff: {cp2_2}")
    print()
    
    # -----------------------------------------------------------------------
    # Notes on data file formats
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Notes on Data File Formats")
    print("=" * 70)
    print("""
For standard text files (.dat, .txt, etc.) without a header:
    data = np.loadtxt("example.dat")

For files with a one-line header:
    data = np.loadtxt("example.txt", skiprows=1)

For CSV files without a header:
    data = np.loadtxt("example.csv", delimiter=",")

For CSV files with a header:
    import pandas as pd
    df = pd.read_csv("example.csv")
    data = df.values

Expected data format:
- Column 0: Scattering angles (s)
- Column 1: Intensity values
- Column 2: (Optional) Error estimates (not used by algorithm)
    """)


if __name__ == "__main__":
    main()
