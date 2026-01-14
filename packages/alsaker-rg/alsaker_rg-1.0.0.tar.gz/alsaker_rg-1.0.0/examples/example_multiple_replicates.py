"""
Example: Multiple replicate SAXS data analysis

This example demonstrates how to estimate the radius of gyration (Rg)
from multiple SAXS intensity curves (replicates).

Reference: file3.R from original R code
"""

import numpy as np
from alsaker_rg import estimate_Rg


def main():
    """Run multiple replicate examples."""
    
    print("=" * 70)
    print("Multiple Replicate SAXS Analysis Example")
    print("=" * 70)
    print()
    
    # -----------------------------------------------------------------------
    # Load data from multiple files
    # -----------------------------------------------------------------------
    print("For real data, you would load multiple files like this:")
    print("""
    data1 = np.loadtxt("myo2_07D_S215_0_01.dat")
    data2 = np.loadtxt("myo2_07D_S215_0_02.dat")
    data3 = np.loadtxt("myo2_07D_S215_0_03.dat")
    # ... etc.
    
    # Combine into single array:
    # Keep angles from first replicate, intensities from all
    combined_data = np.column_stack([
        data1[:400, 0],  # angles
        data1[:400, 1],  # intensity replicate 1
        data2[:400, 1],  # intensity replicate 2
        data3[:400, 1],  # intensity replicate 3
        # ... etc.
    ])
    """)
    print()
    
    # -----------------------------------------------------------------------
    # Generate synthetic data for demonstration
    # -----------------------------------------------------------------------
    print("Generating synthetic SAXS data for demonstration...")
    
    n_points = 400
    n_replicates = 10
    s = np.linspace(0.01, 0.5, n_points)
    Rg_true = 28.0
    I0 = 1200.0
    
    # Generate multiple replicates with correlated noise
    replicates = []
    for rep in range(n_replicates):
        log_intensity = np.log(I0) - (1/3) * Rg_true**2 * s**2
        
        # Add AR(1) noise
        noise = np.zeros(n_points)
        noise[0] = np.random.normal(0, 0.08)
        for i in range(1, n_points):
            noise[i] = 0.75 * noise[i-1] + np.random.normal(0, 0.08)
        
        log_intensity += noise
        intensity = np.exp(log_intensity)
        replicates.append(intensity)
    
    # Combine into single array
    combined_data = np.column_stack([s] + replicates)
    
    print(f"Combined data shape: {combined_data.shape}")
    print(f"  - Angles: column 0")
    print(f"  - Intensities: columns 1-{n_replicates}")
    print(f"True Rg: {Rg_true:.1f} Å")
    print()
    
    # -----------------------------------------------------------------------
    # Example 1: Single replicate (using only first two columns)
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Example 1: Single replicate analysis")
    print("=" * 70)
    
    Rg1, se1, t1, cp2_1, sp1 = estimate_Rg(
        combined_data[:, :2], 
        num_reps=1, 
        starting_value=1,
        make_plots=False
    )
    
    print(f"Estimated Rg: {Rg1:.1f} ± {se1:.2f} Å")
    print()
    
    # -----------------------------------------------------------------------
    # Example 2: Three replicates (first four columns)
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Example 2: Three replicate analysis")
    print("=" * 70)
    
    Rg3, se3, t3, cp2_3, sp3 = estimate_Rg(
        combined_data[:, :4], 
        num_reps=3, 
        starting_value=[1, 1, 1],
        make_plots=False
    )
    
    print(f"Estimated Rg: {Rg3:.1f} ± {se3:.2f} Å")
    print()
    
    # -----------------------------------------------------------------------
    # Example 3: All ten replicates
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Example 3: Ten replicate analysis")
    print("=" * 70)
    
    Rg10, se10, t10, cp2_10, sp10 = estimate_Rg(
        combined_data, 
        num_reps=10, 
        starting_value=[1]*10,
        make_plots=False
    )
    
    print(f"Estimated Rg: {Rg10:.1f} ± {se10:.2f} Å")
    print()
    
    # -----------------------------------------------------------------------
    # Example 4: Different starting points for different replicates
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Example 4: Custom starting points for each replicate")
    print("=" * 70)
    print("Deleting first 3 points from replicate 4, no deletion for others")
    
    starting_points = [1, 1, 1, 4, 1, 1, 1, 1, 1, 1]
    
    Rg_custom, se_custom, t_custom, cp2_custom, sp_custom = estimate_Rg(
        combined_data, 
        num_reps=10, 
        starting_value=starting_points,
        make_plots=False
    )
    
    print(f"Estimated Rg: {Rg_custom:.1f} ± {se_custom:.2f} Å")
    print()
    
    # -----------------------------------------------------------------------
    # Example 5: Automatic starting point detection
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Example 5: Automatic starting point detection (recommended)")
    print("=" * 70)
    
    # With 3 replicates
    Rg_auto3, se_auto3, t_auto3, cp2_auto3, sp_auto3 = estimate_Rg(
        combined_data[:, :4], 
        num_reps=3,
        make_plots=False
    )
    
    print("Three replicates:")
    print(f"Estimated Rg: {Rg_auto3:.1f} ± {se_auto3:.2f} Å")
    print()
    
    # With all 10 replicates
    Rg_auto10, se_auto10, t_auto10, cp2_auto10, sp_auto10 = estimate_Rg(
        combined_data, 
        num_reps=10,
        make_plots=False
    )
    
    print("Ten replicates:")
    print(f"Estimated Rg: {Rg_auto10:.1f} ± {se_auto10:.2f} Å")
    print()
    
    # -----------------------------------------------------------------------
    # Summary comparison
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("Summary: Effect of Number of Replicates")
    print("=" * 70)
    print(f"True Rg:         {Rg_true:.1f} Å")
    print(f"1 replicate:     {Rg1:.1f} ± {se1:.2f} Å")
    print(f"3 replicates:    {Rg_auto3:.1f} ± {se_auto3:.2f} Å")
    print(f"10 replicates:   {Rg_auto10:.1f} ± {se_auto10:.2f} Å")
    print()
    print("Note: More replicates generally reduce standard error")
    print()


if __name__ == "__main__":
    main()
