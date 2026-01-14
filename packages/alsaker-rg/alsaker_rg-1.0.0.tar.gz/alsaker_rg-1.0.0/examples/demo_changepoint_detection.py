"""
Demonstration: Changepoint Detection Comparison

This script shows the difference between using ruptures (PELT algorithm)
versus the simple fallback heuristic.
"""

import numpy as np
import matplotlib.pyplot as plt
from alsaker_rg import detect_changepoint, HAS_RUPTURES
from alsaker_rg.estimation import _detect_changepoint_fallback


def main():
    print("=" * 70)
    print("Changepoint Detection Comparison")
    print("=" * 70)
    print()
    print(f"ruptures package available: {HAS_RUPTURES}")
    print()
    
    # Generate synthetic SAXS data
    np.random.seed(42)
    s = np.linspace(0.01, 0.5, 400)
    Rg_true = 30.0
    I0 = 1000.0
    
    # Guinier region (first ~100 points)
    log_intensity = np.log(I0) - (1/3) * Rg_true**2 * s**2
    
    # Add AR(1) noise
    noise = np.zeros(len(s))
    noise[0] = np.random.normal(0, 0.1)
    for i in range(1, len(s)):
        noise[i] = 0.7 * noise[i-1] + np.random.normal(0, 0.1)
    
    log_intensity += noise
    
    # Compute 4th differences
    y3 = np.diff(log_intensity, n=4)
    
    print("Data characteristics:")
    print(f"  Total points: {len(s)}")
    print(f"  4th differences: {len(y3)} points")
    print()
    
    # Test changepoint detection
    print("-" * 70)
    print("Changepoint Detection Results")
    print("-" * 70)
    
    if HAS_RUPTURES:
        # With ruptures (PELT)
        cp_ruptures = detect_changepoint(log_intensity, len(s), use_ruptures=True)
        print(f"Using ruptures (PELT):    cp = {cp_ruptures}")
    else:
        print("ruptures not available")
    
    # Fallback heuristic
    cp_fallback = _detect_changepoint_fallback(y3)
    # Apply same bounds
    cp_fallback = min(max(60, cp_fallback), 120)
    print(f"Using fallback heuristic: cp = {cp_fallback}")
    print()
    
    # Visualize the difference
    if HAS_RUPTURES:
        plt.figure(figsize=(14, 10))
        
        # Plot 1: Log-intensity
        plt.subplot(3, 1, 1)
        plt.plot(s, log_intensity, 'b-', alpha=0.6, linewidth=1)
        plt.axvline(s[cp_ruptures], color='red', linestyle='--', 
                   label=f'ruptures: cp={cp_ruptures}')
        plt.axvline(s[cp_fallback], color='green', linestyle='--', 
                   label=f'fallback: cp={cp_fallback}')
        plt.xlabel('Scattering angle (s)')
        plt.ylabel('Log(Intensity)')
        plt.title('SAXS Log-Intensity Curve')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 2: 4th differences
        plt.subplot(3, 1, 2)
        s_diff = s[2:-2]  # Adjust for 4th differences
        plt.plot(s_diff, y3, 'b-', alpha=0.6, linewidth=1)
        if cp_ruptures < len(s_diff):
            plt.axvline(s_diff[cp_ruptures], color='red', linestyle='--', 
                       label=f'ruptures: cp={cp_ruptures}')
        if cp_fallback < len(s_diff):
            plt.axvline(s_diff[cp_fallback], color='green', linestyle='--', 
                       label=f'fallback: cp={cp_fallback}')
        plt.xlabel('Scattering angle (s)')
        plt.ylabel('4th Difference')
        plt.title('4th Differences of Log-Intensity (used for changepoint detection)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 3: Guinier plot
        plt.subplot(3, 1, 3)
        plt.scatter(s[:cp_ruptures]**2, log_intensity[:cp_ruptures], 
                   c='red', s=20, alpha=0.6, label='ruptures region')
        plt.scatter(s[cp_ruptures:]**2, log_intensity[cp_ruptures:], 
                   c='blue', s=20, alpha=0.3, label='excluded (ruptures)')
        
        # Show fallback region with different marker
        if cp_fallback != cp_ruptures:
            if cp_fallback < cp_ruptures:
                plt.scatter(s[cp_fallback:cp_ruptures]**2, 
                          log_intensity[cp_fallback:cp_ruptures], 
                          c='orange', s=30, marker='x', alpha=0.8,
                          label='difference region')
        
        plt.xlabel('$s^2$')
        plt.ylabel('Log(Intensity)')
        plt.title('Guinier Plot (linearity expected in low s^2 region)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('changepoint_comparison.png', dpi=150, bbox_inches='tight')
        print("Visualization saved to 'changepoint_comparison.png'")
        plt.show()
    
    print()
    print("=" * 70)
    print("Interpretation")
    print("=" * 70)
    print("""
The PELT algorithm from ruptures detects the point where the variance
of the 4th differences changes, indicating where the Guinier quadratic
approximation starts breaking down.

The fallback heuristic simply uses the middle of the data range, which
works reasonably but may not be optimal for all datasets.

Key points:
- ruptures (PELT): Statistical changepoint detection, adapts to data
- Fallback: Simple heuristic, always picks middle of range
- Both are bounded between 60-120 points for stability
- Final cutoff is further refined by bias-variance optimization
    """)


if __name__ == "__main__":
    main()
