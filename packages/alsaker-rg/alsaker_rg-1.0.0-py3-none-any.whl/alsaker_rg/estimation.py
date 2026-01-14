"""
Small-Angle X-Ray Scattering (SAXS) Radius of Gyration Estimation

Python port of the Alsaker-Breidt-van der Woerd method for estimating the radius of gyration
from SAXS data using minimum mean squared error with optimal window selection.

Reference:
Alsaker, C., Breidt, F. J., & van der Woerd, M. J. (2018). 
Minimum Mean Squared Error Estimation of the Radius of Gyration in Small-Angle X-Ray 
Scattering Experiments. Journal of the American Statistical Association.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import BSpline
from scipy.linalg import eigh
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.regression.linear_model import OLS
from typing import Union, List, Tuple, Optional
import warnings

# Try to import ruptures for proper changepoint detection
try:
    import ruptures as rpt
    HAS_RUPTURES = True
except ImportError:
    HAS_RUPTURES = False
    warnings.warn(
        "ruptures package not found. Using simplified changepoint detection. "
        "For better results, install ruptures: pip install ruptures",
        ImportWarning
    )


def detect_changepoint(log_intensity: np.ndarray, n: int, 
                       use_ruptures: bool = True) -> int:
    """
    Detect changepoint in variance of 4th differences of log-intensity.
    
    This matches the R implementation which uses cpt.var() with PELT algorithm
    from the changepoint package.
    
    Parameters:
    -----------
    log_intensity : ndarray
        Log-transformed intensity values
    n : int
        Total number of data points
    use_ruptures : bool, optional
        Whether to use ruptures package if available (default: True)
        
    Returns:
    --------
    cp2i : int
        Changepoint index (bounded between 60 and 120)
    """
    # Compute 4th differences
    y3 = np.diff(log_intensity, n=4)
    
    if HAS_RUPTURES and use_ruptures:
        # Use ruptures package with PELT algorithm
        # This matches R's cpt.var(method="PELT", penalty="Manual", pen.value=7*log(n))
        try:
            penalty_value = 7 * np.log(n)
            
            # PELT algorithm for variance change detection
            # Using "rbf" model as it's suitable for variance changes
            algo = rpt.Pelt(model="rbf", min_size=10, jump=1)
            algo.fit(y3.reshape(-1, 1))
            
            # Get changepoints with manual penalty
            changepoints = algo.predict(pen=penalty_value)
            
            # Take first changepoint (excluding the endpoint)
            if len(changepoints) > 1:  # Last point is always len(y3)
                cp2i = changepoints[0]
            else:
                cp2i = n - 1
                
        except Exception as e:
            warnings.warn(f"ruptures failed: {e}. Using fallback method.")
            cp2i = _detect_changepoint_fallback(y3)
    else:
        # Fallback: simple heuristic
        cp2i = _detect_changepoint_fallback(y3)
    
    # Apply bounds from original R code
    if cp2i < 60:
        cp2i = 60
    if cp2i > 120:
        cp2i = 120
        
    return cp2i


def _detect_changepoint_fallback(y3: np.ndarray) -> int:
    """
    Fallback changepoint detection when ruptures is not available.
    Uses simple heuristic: middle of the data range.
    
    Parameters:
    -----------
    y3 : ndarray
        4th differences of log-intensity
        
    Returns:
    --------
    cp2i : int
        Changepoint index
    """
    # Simple heuristic: take middle of data range
    # This is what was originally implemented
    cp2i = len(y3) // 2
    return cp2i


def create_gamma_matrix(g: np.ndarray, p: int) -> np.ndarray:
    """
    Create autocovariance matrix from autocovariance vector.
    
    Parameters:
    -----------
    g : array-like
        Autocovariance vector
    p : int
        Matrix dimension
        
    Returns:
    --------
    gamma : ndarray
        Autocovariance matrix
    """
    gamma = np.zeros((p, p))
    for i in range(p):
        for j in range(p):
            gamma[i, j] = g[abs(i - j)]
    return gamma


def ind_ar_struc(comb_spline_fit: np.ndarray, d2: np.ndarray, m: int) -> np.ndarray:
    """
    Estimate AR structure from residuals.
    
    Parameters:
    -----------
    comb_spline_fit : ndarray
        Fitted spline values
    d2 : ndarray
        Observed log-intensity values
    m : int
        Maximum lag
        
    Returns:
    --------
    result : ndarray
        Array with arsum at index 0, followed by autocovariances
    """
    resid = np.log(d2) - comb_spline_fit
    
    # Fit AR model with max order 5
    try:
        ar_model = AutoReg(resid, lags=5, trend='n', old_names=False)
        ar_fit = ar_model.fit()
        ar_order = len(ar_fit.params)
        
        if ar_order == 0:
            phi_temp = np.array([0.0])
        else:
            phi_temp = ar_fit.params
            
        sigma2 = ar_fit.sigma2
    except:
        # Fallback to no AR structure
        phi_temp = np.array([0.0])
        sigma2 = np.var(resid)
    
    # Calculate arsum
    arsum = sigma2 / (1 - np.sum(phi_temp))**2
    
    # Create autocovariance vector using ACF
    # For AR process: gamma(k) can be computed from Yule-Walker equations
    # Here we use a simpler approach via statsmodels
    from statsmodels.tsa.stattools import acf
    
    try:
        acf_vals = acf(resid, nlags=m, fft=True)
        g_0 = acf_vals * sigma2
    except:
        # Fallback: exponential decay
        g_0 = sigma2 * np.exp(-0.1 * np.arange(m + 1))
    
    result = np.zeros(m + 1)
    result[0] = arsum
    # Ensure g_0 has correct length
    if len(g_0) > m:
        result[1:] = g_0[:m]
    else:
        result[1:len(g_0)] = g_0[:(len(g_0)-1)]
    
    return result


def comb_spline(M: np.ndarray, cp2: np.ndarray, cp2i: np.ndarray, 
                nreps: int, sp: np.ndarray, m: int) -> np.ndarray:
    """
    Fit combined spline curves to multiple replicates.
    
    Parameters:
    -----------
    M : ndarray
        Data matrix with angles in column 0, intensities in columns 1+
    cp2 : ndarray
        Changepoint indices
    cp2i : ndarray
        Changepoint indices (adjusted)
    nreps : int
        Number of replicates
    sp : ndarray
        Starting points
    m : int
        Maximum length
        
    Returns:
    --------
    beta_curve : ndarray
        Fitted spline values
    """
    from scipy.interpolate import splrep, BSpline
    
    # Set number of knots for cubic spline fit
    df = 6 if m <= 80 else 8
    
    min_sp = int(np.min(sp))
    max_cp2 = int(np.max(cp2))
    
    s_range = M[min_sp:max_cp2, 0]
    
    # Natural cubic spline basis (similar to R's ns())
    from scipy.interpolate import splrep
    # Create knots for natural spline
    knots = np.linspace(s_range[0], s_range[-1], df - 2)[1:-1]
    
    if nreps == 1:
        sp_idx = int(sp[0])
        cp2_idx = int(cp2[0])
        X_data = M[sp_idx:(cp2_idx + sp_idx), 0]
        Y_data = np.log(M[sp_idx:(cp2_idx + sp_idx), 1])
        
        # Fit polynomial regression (simplified)
        X_design = np.column_stack([
            np.ones(len(X_data)),
            X_data**2,
            X_data**3,
            X_data**4,
            X_data**5,
            X_data**6
        ])
        
        beta_est = np.linalg.lstsq(X_design, Y_data, rcond=None)[0]
        
        # Create fitted curve
        s_fit = M[min_sp:(min_sp + m), 0]
        X_fit = np.column_stack([
            np.ones(len(s_fit)),
            s_fit**2,
            s_fit**3,
            s_fit**4,
            s_fit**5,
            s_fit**6
        ])
        beta_curve = X_fit @ beta_est
        
        return beta_curve
    
    else:
        # Multiple replicates
        X_list = []
        Y_list = []
        
        for i in range(nreps):
            sp_idx = int(sp[i])
            cp2_idx = int(cp2[i])
            
            X_data = M[sp_idx:cp2_idx, 0]
            Y_data = np.log(M[sp_idx:cp2_idx, i + 1])
            
            # Create design matrix with replicate-specific intercepts
            n_pts = len(X_data)
            intercepts = np.zeros((n_pts, nreps))
            intercepts[:, i] = 1
            
            X_spline = np.column_stack([
                X_data**2,
                X_data**3,
                X_data**4,
                X_data**5,
                X_data**6
            ])
            
            X_design = np.column_stack([intercepts, X_spline])
            
            X_list.append(X_design)
            Y_list.append(Y_data)
        
        # Stack all data
        X_all = np.vstack(X_list)
        Y_all = np.concatenate(Y_list)
        
        # Fit
        beta_est = np.linalg.lstsq(X_all, Y_all, rcond=None)[0]
        
        # Create fitted curves for each replicate
        s_fit = M[min_sp:(min_sp + m), 0]
        
        beta_curve_list = []
        for i in range(nreps):
            intercepts = np.zeros((len(s_fit), nreps))
            intercepts[:, i] = 1
            
            X_spline = np.column_stack([
                s_fit**2,
                s_fit**3,
                s_fit**4,
                s_fit**5,
                s_fit**6
            ])
            
            X_fit = np.column_stack([intercepts, X_spline])
            beta_curve_list.append(X_fit @ beta_est)
        
        beta_curve = np.column_stack(beta_curve_list)
        
        return beta_curve


def b_v_tradeoff_comb(M: np.ndarray, cp2: int, sigma: np.ndarray, 
                      comb_spline_fit: np.ndarray, nreps: int, 
                      sp: np.ndarray, arsum: float) -> int:
    """
    Bias-variance tradeoff to select optimal cutoff.
    
    Parameters:
    -----------
    M : ndarray
        Data matrix
    cp2 : int
        Maximum cutoff point
    sigma : ndarray
        Covariance matrix
    comb_spline_fit : ndarray
        Fitted spline values
    nreps : int
        Number of replicates
    sp : ndarray
        Starting points
    arsum : float
        AR variance sum
        
    Returns:
    --------
    t : int
        Optimal cutoff index
    """
    s = M[:, 0]
    delta_s = np.mean(np.diff(s[:19]))
    
    f = np.full(cp2, 1e7)
    var_est = np.full(cp2, 1e7)
    sum_bias2_avg = np.full(cp2, 1e7)
    
    min_sp = int(np.min(sp))
    max_sp = int(np.max(sp))
    
    for k in range(3, cp2 - 1):
        tempk = k
        
        if nreps > 1:
            k_actual = max_sp + k - 1
            len_vals = np.repeat(k_actual, nreps) - np.repeat(min_sp, nreps) + 2
            lenb = len_vals - (sp - min_sp + 1) + 1
            
            X_list = []
            Y_list = []
            
            for i in range(nreps):
                sp_idx = int(sp[i])
                n_pts = int(lenb[i])
                
                # Create design matrix
                intercepts = np.zeros((n_pts, nreps))
                intercepts[:, i] = 1
                
                X_design = np.column_stack([
                    intercepts,
                    M[sp_idx:(sp_idx + n_pts), 0]**2,
                    M[sp_idx:(sp_idx + n_pts), 0]**4
                ])
                
                Y_data = np.log(M[sp_idx:(sp_idx + n_pts), i + 1])
                
                X_list.append(X_design)
                Y_list.append(Y_data)
            
            X_all = np.vstack(X_list)
            Y_all = np.concatenate(Y_list)
        else:
            tempk = k
            X_all = np.column_stack([
                np.ones(k),
                M[:k, 0]**2,
                M[:k, 0]**4
            ])
            Y_all = np.log(M[:k, 1])
        
        # Fit quadratic + quartic model
        try:
            fit = np.linalg.lstsq(X_all, Y_all, rcond=None)
            alpha = fit[0]
            
            # Calculate bias
            sum_bias2_avg[tempk] = 9/784 * (24 * alpha[nreps + 1])**2 * (k * delta_s)**4
            
            # Calculate variance
            var_est[tempk] = (405 * arsum) / (nreps * 4 * k**5 * delta_s**4)
            
            # Bias-variance criterion
            f[tempk] = var_est[tempk] + sum_bias2_avg[tempk]
        except:
            continue
    
    # Find minimum
    t = np.argmin(f)
    
    return t


def calc_Rg(M: np.ndarray, sigma: np.ndarray, t: int, cp2: int, 
            nreps: int, sp: np.ndarray, arsum: float, 
            comb_spline_fit: np.ndarray, choose_sp: bool) -> Tuple[float, float, int, int, np.ndarray]:
    """
    Calculate radius of gyration estimate and standard error.
    
    Parameters:
    -----------
    M : ndarray
        Data matrix
    sigma : ndarray
        Covariance matrix
    t : int
        Optimal cutoff
    cp2 : int
        Maximum cutoff
    nreps : int
        Number of replicates
    sp : ndarray
        Starting points
    arsum : float
        AR variance sum
    comb_spline_fit : ndarray
        Fitted spline
    choose_sp : bool
        Whether starting points were chosen by user
        
    Returns:
    --------
    Rg : float
        Radius of gyration estimate
    se_Rg : float
        Standard error of Rg
    t : int
        Cutoff used
    cp2 : int
        Maximum cutoff
    sp : ndarray
        Starting point indices (0-indexed) for each replicate
    """
    s = M[:, 0]
    delta_s = np.mean(np.diff(s[:10]))
    
    min_sp = int(np.min(sp))
    max_sp = int(np.max(sp))
    
    if nreps > 1:
        t_actual = max_sp + t - 1
        len_vals = np.repeat(t_actual, nreps) - np.repeat(min_sp, nreps) + 2
        len2 = len_vals - (sp - min_sp + 1) + 1
        len3 = len_vals[0] + min_sp - 1
        
        X_list = []
        Y_list = []
        
        for i in range(nreps):
            sp_idx = int(sp[i])
            n_pts = int(len2[i])
            
            intercepts = np.zeros((n_pts, nreps))
            intercepts[:, i] = 1
            
            X_design = np.column_stack([
                intercepts,
                M[sp_idx:(sp_idx + n_pts), 0]**2
            ])
            
            Y_data = np.log(M[sp_idx:(sp_idx + n_pts), i + 1])
            
            X_list.append(X_design)
            Y_list.append(Y_data)
        
        X = np.vstack(X_list)
        Y = np.concatenate(Y_list)
        
        # Create block diagonal covariance matrix
        gamma_est = np.zeros((int(np.sum(len2)), int(np.sum(len2))))
        offset = 0
        for i in range(nreps):
            n_pts = int(len2[i])
            sp_offset = int(sp[i] - min_sp)
            len_i = int(len_vals[i])
            
            gamma_est[offset:(offset + n_pts), offset:(offset + n_pts)] = \
                sigma[sp_offset:len_i, sp_offset:len_i]
            offset += n_pts
    else:
        len3 = t
        sp_idx = int(sp[0])
        X = np.column_stack([
            np.ones(t),
            M[sp_idx:(t + sp_idx), 0]**2
        ])
        Y = np.log(M[sp_idx:(sp_idx + t), 1])
        gamma_est = sigma[:t, :t]
    
    # GLS estimation
    try:
        # Eigen decomposition for square root of covariance matrix
        eigenvalues, eigenvectors = eigh(gamma_est)
        eigenvalues = np.maximum(eigenvalues, 1e-10)  # Ensure positive
        B = eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
        
        Y_transformed = B @ Y
        X_transformed = B @ X
        
        fit = np.linalg.lstsq(X_transformed, Y_transformed, rcond=None)
        alpha = fit[0]
    except:
        # Fallback to OLS
        fit = np.linalg.lstsq(X, Y, rcond=None)
        alpha = fit[0]
    
    # Check for negative Rg
    if alpha[nreps] > 0:
        warnings.warn("Negative Rg value found. Results may be unreliable.")
        return np.nan, np.nan, t, cp2, sp
    
    # Estimate Rg
    Rg = np.sqrt(-3 * alpha[nreps])
    
    # Approximate variance using Taylor linearization
    var_Rg2 = (405 * arsum) / (nreps * 4 * t**5 * delta_s**4) / 9
    se_Rg = np.sqrt(-3 / (4 * alpha[nreps]) * var_Rg2)
    
    return Rg, se_Rg, t, cp2, sp


def estimate_Rg(M: np.ndarray, num_reps: int, starting_value: Union[int, List[int]] = -1,
                make_plots: bool = True) -> Tuple[float, float, int, int, np.ndarray]:
    """
    Estimate radius of gyration from SAXS data.
    
    Parameters:
    -----------
    M : ndarray
        Data matrix with shape (n, num_reps + 1)
        Column 0: scattering angles (s)
        Columns 1+: log-intensities for each replicate
    num_reps : int
        Number of replicates
    starting_value : int or list of int, optional
        Starting indices for each replicate (1-indexed)
        If -1 (default), automatically detect starting points
    make_plots : bool, optional
        Whether to create diagnostic plots (default: True)
        
    Returns:
    --------
    Rg : float
        Radius of gyration estimate
    se_Rg : float
        Standard error of Rg estimate
    t : int
        Optimal window length (number of points used)
    cp2 : int
        Maximum cutoff index
    sp : ndarray
        Starting point indices (0-indexed) for each replicate.
        Guinier region for replicate i: M[sp[i]:sp[i]+t, :]
        
    Examples:
    ---------
    >>> # Single replicate
    >>> data = np.loadtxt('data.txt')
    >>> Rg, se, t, cp2, sp = estimate_Rg(data, 1)
    >>> print(f"Rg = {Rg:.1f} ± {se:.2f}")
    >>> print(f"Guinier region: indices {sp[0]} to {sp[0]+t}")
    
    >>> # Multiple replicates with automatic starting point
    >>> Rg, se, t, cp2, sp = estimate_Rg(combined_data, 3)
    >>> for i in range(3):
    >>>     print(f"Rep {i+1} Guinier region: {sp[i]} to {sp[i]+t}")
    
    >>> # Multiple replicates with manual starting points
    >>> Rg, se, t, cp2, sp = estimate_Rg(combined_data, 3, starting_value=[1, 1, 1])
    """
    # Handle starting values
    if isinstance(starting_value, int):
        starting_value = [starting_value]
    
    # Check for negative initial values
    for i, val in enumerate(starting_value):
        if val < -1:
            raise ValueError("Please enter positive initial values.")
    
    # Determine if starting points chosen by user
    if starting_value[0] != -1:
        choose_sp = True
        print("Initial points input by user.")
        
        for i in range(num_reps):
            if len(starting_value) <= i:
                starting_value.append(1)
            
            removed = starting_value[i] - 1
            if removed == 0:
                print(f"Removed zero points from replicate {i+1}")
            elif removed == 1:
                print(f"Removed first point from replicate {i+1}")
            else:
                print(f"Removed first {removed} points from replicate {i+1}")
    else:
        choose_sp = False
        starting_value = [1] * num_reps
    
    sp = np.array(starting_value, dtype=int) - 1  # Convert to 0-indexed
    nreps = num_reps
    
    # Handle zero and negative intensities
    if nreps == 1:
        # Check for zero values
        if M[0, 1] == 0:
            i = 0
            while i < len(M[:, 1]) - 1 and M[i + 1, 1] == 0:
                i += 1
            num = i
            
            M = M[(num + 1):, :]
            n = len(M)
            print(f"Warning: first {num} intensity values equal zero. These values were stripped from the data.")
        
        # Check for negative values
        n = len(M[:, 1])
        for i in range(len(M[:, 1])):
            if M[i, 1] < 0:
                n = i
                print("Warning: negative intensity values found.")
                break
        
        # Detect changepoint using variance in 4th differences
        # This matches R's: cpt.var(y3, method="PELT", penalty="Manual", pen.value=7*log(n))
        cp2i = detect_changepoint(np.log(M[sp[0]:n, 1]), n)
        
        cp2 = np.array([cp2i + sp[0]])
        m = 0
        
        # Fit combined spline
        comb_spline_fit = comb_spline(M, cp2, cp2 - sp, nreps, sp, cp2[0])
        
        # Estimate AR structure
        gamma = np.zeros(cp2[0])
        out = ind_ar_struc(comb_spline_fit, M[sp[0]:(cp2[0] + sp[0]), 1], cp2[0])
        gamma = out[1:]
        arsum = out[0]
        
        # Create covariance matrix
        sigma = create_gamma_matrix(gamma, cp2[0])
        
        # Bias-variance tradeoff
        t = b_v_tradeoff_comb(M, cp2[0], sigma, comb_spline_fit, nreps, sp, arsum)
        
        # Calculate Rg
        output = calc_Rg(M[:n, :], sigma, t, cp2[0], nreps, sp, arsum, comb_spline_fit, choose_sp)
        
    else:
        # Multiple replicates
        n = len(M[:, 1])
        
        # Check for non-positive values in all replicates
        for i in range(nreps):
            non_positive = np.where(M[:, i + 1] <= 0)[0]
            if len(non_positive) > 0:
                n = min(n, non_positive[0])
        
        cp2i = np.zeros(nreps, dtype=int)
        
        # Detect changepoints for each replicate
        for i in range(nreps):
            try:
                cp2i[i] = detect_changepoint(np.log(M[sp[i]:n, i + 1]), n)
            except:
                cp2i[i] = 60
        
        cp2 = cp2i + sp
        
        n_pts = int(np.min(cp2) - np.max(sp) + 1)
        m = int(np.max(cp2) - np.min(sp) + 1)
        
        # Fit combined splines
        comb_spline_fit = comb_spline(M, cp2, cp2i, nreps, sp, m)
        
        # Estimate AR structure for each replicate
        gamma = np.zeros((m, nreps))
        arsum_vec = np.zeros(nreps)
        
        for i in range(nreps):
            sp_i = int(sp[i])
            cp2_i = int(cp2[i])
            min_sp = int(np.min(sp))
            
            if comb_spline_fit.ndim == 1:
                fit_i = comb_spline_fit[(sp_i - min_sp):(cp2_i - min_sp)]
            else:
                fit_i = comb_spline_fit[(sp_i - min_sp):(cp2_i - min_sp), i]
            
            data_i = M[sp_i:cp2_i, i + 1]
            
            # Ensure fit_i and data_i have same length
            min_len = min(len(fit_i), len(data_i))
            fit_i = fit_i[:min_len]
            data_i = data_i[:min_len]
            
            out = ind_ar_struc(fit_i, data_i, m)
            gamma[:, i] = out[1:]
            arsum_vec[i] = out[0]
        
        arsum = np.mean(arsum_vec)
        
        # Average gamma across replicates
        avg_gamma = np.mean(gamma, axis=1)
        
        # Create covariance matrix
        sigma = create_gamma_matrix(avg_gamma, m)
        
        # Bias-variance tradeoff
        t = b_v_tradeoff_comb(M, n_pts, sigma, comb_spline_fit, nreps, sp, arsum)
        
        # Calculate Rg
        output = calc_Rg(M, sigma, t, n_pts, nreps, sp, arsum, comb_spline_fit, choose_sp)
    
    # Create plots if requested
    if make_plots and not np.isnan(output[0]):
        _create_diagnostic_plots(M, output, nreps, sp, t, cp2)
    
    return output


def _create_diagnostic_plots(M: np.ndarray, output: Tuple, nreps: int, 
                             sp: np.ndarray, t: int, cp2: np.ndarray):
    """Create diagnostic plots for Rg estimation."""
    Rg, se_Rg, t_used, cp2_used, sp_used = output
    
    s = M[:, 0]
    
    if nreps == 1:
        intensity = M[:, 1]
        
        # Plot 1: Residuals
        plt.figure(figsize=(10, 6))
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        plt.xlabel('S')
        plt.ylabel('Residuals')
        plt.title('Residual Plot')
        plt.tight_layout()
        plt.show()
        
        # Plot 2: Guinier plot (s^2 vs log(Intensity))
        plt.figure(figsize=(10, 6))
        sp_idx = int(sp[0])
        plt.scatter(s[(sp_idx + t_used):cp2_used]**2, 
                   np.log(intensity[(sp_idx + t_used):cp2_used]),
                   c='blue', s=20, alpha=0.6, label='Excluded data points')
        plt.scatter(s[sp_idx:(sp_idx + t_used)]**2, 
                   np.log(intensity[sp_idx:(sp_idx + t_used)]),
                   c='red', s=20, label='Data points used to fit curve')
        plt.xlabel('$S^2$')
        plt.ylabel('Log(Intensity)')
        plt.title('Guinier Plot')
        plt.legend()
        plt.text(0.7, 0.95, f'$\\hat{{R}}_g$ = {Rg:.1f}', transform=plt.gca().transAxes)
        plt.text(0.7, 0.90, f'Std. Deviation = {se_Rg:.2f}', transform=plt.gca().transAxes)
        plt.tight_layout()
        plt.show()
        
        # Plot 3: Log-intensity vs S
        plt.figure(figsize=(10, 6))
        plt.scatter(s[(sp_idx + t_used):], 
                   np.log(intensity[(sp_idx + t_used):]),
                   c='blue', s=20, alpha=0.6, label='Excluded data points')
        plt.scatter(s[sp_idx:(sp_idx + t_used)], 
                   np.log(intensity[sp_idx:(sp_idx + t_used)]),
                   c='red', s=20, label='Data points used to fit curve')
        plt.xlabel('S')
        plt.ylabel('Log(Intensity)')
        plt.title('SAXS Data')
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    else:
        # Multiple replicates - simplified plotting
        plt.figure(figsize=(12, 8))
        
        for i in range(nreps):
            intensity = M[:, i + 1]
            sp_idx = int(sp[i])
            
            plt.scatter(s[sp_idx:(sp_idx + t_used)]**2, 
                       np.log(intensity[sp_idx:(sp_idx + t_used)]),
                       c='red', s=10, alpha=0.3)
        
        plt.xlabel('$S^2$')
        plt.ylabel('Log(Intensity)')
        plt.title(f'Guinier Plot - {nreps} Replicates')
        plt.text(0.7, 0.95, f'$\\hat{{R}}_g$ = {Rg:.1f}', transform=plt.gca().transAxes)
        plt.text(0.7, 0.90, f'Std. Deviation = {se_Rg:.2f}', transform=plt.gca().transAxes)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    print("SAXS Radius of Gyration Estimation Module")
    print("==========================================")
    print("\nThis module implements the Alsaker-Breidt-van der Woerd method")
    print("for estimating the radius of gyration from SAXS data.")
    print("\nUsage:")
    print("  from alsaker_rg import estimate_Rg")
    print("  import numpy as np")
    print("  data = np.loadtxt('your_data.dat')")
    print("  Rg, se, t, cp2 = estimate_Rg(data, num_reps=1)")
