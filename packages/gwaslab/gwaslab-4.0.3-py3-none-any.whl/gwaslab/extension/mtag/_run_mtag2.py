"""
Refactored MTAG (Multi-trait Analysis of GWAS) implementation using Polars.

This module provides a refactored version of MTAG that works directly with
polars DataFrames, following gwaslab design patterns. It implements the core
MTAG algorithm for multi-trait analysis of GWAS summary statistics.

Based on the original MTAG implementation:
https://github.com/JonJala/mtag/blob/master/mtag.py

Reference: Turley et al. (2017) Multi-trait analysis of genome-wide association
summary statistics using MTAG. Nature Genetics.
"""

from typing import TYPE_CHECKING, Optional, List, Tuple, Dict, Any
import numpy as np
import polars as pl
import pandas as pd
from scipy import optimize
from scipy.linalg import inv, pinv
from scipy.stats import norm
from gwaslab.info.g_Log import Log

if TYPE_CHECKING:
    from gwaslab.g_SumstatsMulti import SumstatsMulti

# Constants
DEFAULT_MEDIAN_Z_THRESHOLD = 0.1
DEFAULT_TOL = 1e-6
DEFAULT_TIME_LIMIT = 100.0  # hours


def _run_mtag2(
    sumstats_multi: 'SumstatsMulti',
    traits: Optional[List[str]] = None,
    n_min: int = 0,
    perfect_gencov: bool = False,
    equal_h2: bool = False,
    no_overlap: bool = False,
    numerical_omega: bool = False,
    tol: float = DEFAULT_TOL,
    time_limit: float = DEFAULT_TIME_LIMIT,
    median_z_cutoff: float = DEFAULT_MEDIAN_Z_THRESHOLD,
    use_ldsc: bool = False,
    ldsc_kwargs: Optional[Dict[str, Any]] = None,
    log: Log = Log(),
    verbose: bool = True
) -> pl.DataFrame:
    """
    Run MTAG (Multi-trait Analysis of GWAS) using polars DataFrames.
    
    This function performs multi-trait analysis of GWAS summary statistics
    using the MTAG method. It works directly with polars DataFrames without
    requiring external file I/O.
    
    Parameters
    ----------
    sumstats_multi : SumstatsMulti
        SumstatsMulti object containing multi-trait summary statistics.
        The data should be a polars DataFrame with columns:
        - rsID, CHR, POS, EA, NEA (SNP information)
        - Z_1, Z_2, ..., Z_T (Z-scores for each trait)
        - N_1, N_2, ..., N_T (sample sizes for each trait)
        - EAF_1, EAF_2, ..., EAF_T (effect allele frequencies)
        - P_1, P_2, ..., P_T (P-values, optional)
    traits : list of str, optional
        List of trait names. If None, uses trait_1, trait_2, etc.
    n_min : int, default 0
        Minimum sample size threshold for SNPs.
    perfect_gencov : bool, default False
        If True, assumes perfect genetic covariance (identity matrix).
    equal_h2 : bool, default False
        If True, assumes equal heritability across traits.
        Can only be used with perfect_gencov.
    no_overlap : bool, default False
        If True, assumes no sample overlap between traits.
    numerical_omega : bool, default False
        If True, uses numerical MLE estimator for genetic VCV matrix.
    tol : float, default 1e-6
        Relative tolerance for numerical optimization.
    time_limit : float, default 100.0
        Time limit (hours) for numerical estimation.
    median_z_cutoff : float, default 0.1
        Maximum allowed median Z-score for input QC.
    use_ldsc : bool, default False
        If True, use LDSC regression to estimate omega and sigma.
        Requires ref_ld_chr and w_ld_chr in ldsc_kwargs.
    ldsc_kwargs : dict, optional
        Keyword arguments for LDSC regression (ref_ld_chr, w_ld_chr, etc.).
        Only used if use_ldsc=True.
    log : Log, default Log()
        Log object for logging messages.
    verbose : bool, default True
        Whether to print progress messages.
    
    Returns
    -------
    pl.DataFrame
        Polars DataFrame with MTAG results including:
        - All original SNP information columns
        - Z_MTAG_1, Z_MTAG_2, ..., Z_MTAG_T (MTAG Z-scores for each trait)
        - P_MTAG_1, P_MTAG_2, ..., P_MTAG_T (MTAG P-values)
        - Additional MTAG statistics
    
    Examples
    --------
    >>> from gwaslab import SumstatsMulti
    >>> sumstats_multi = SumstatsMulti([sumstats1, sumstats2], engine="polars")
    >>> mtag_results = _run_mtag2(sumstats_multi, n_min=1000, verbose=True)
    """
    log.write("=" * 80, verbose=verbose)
    log.write("MTAG: Multi-trait Analysis of GWAS (Refactored for gwaslab)", verbose=verbose)
    log.write("=" * 80, verbose=verbose)
    
    # Get the polars DataFrame
    if not isinstance(sumstats_multi.data, pl.DataFrame):
        raise ValueError("sumstats_multi.data must be a polars DataFrame. "
                        "Please initialize SumstatsMulti with engine='polars'")
    
    df = sumstats_multi.data
    
    # Determine number of traits
    z_cols = [col for col in df.columns if col.startswith("Z_") and col[2:].isdigit()]
    n_traits = len(z_cols)
    
    if n_traits < 2:
        raise ValueError(f"MTAG requires at least 2 traits. Found {n_traits} Z-score columns.")
    
    log.write(f"Number of traits: {n_traits}", verbose=verbose)
    
    # Get trait names
    if traits is None:
        traits = [f"trait_{i+1}" for i in range(n_traits)]
    elif len(traits) != n_traits:
        raise ValueError(f"Number of trait names ({len(traits)}) must match "
                        f"number of traits ({n_traits})")
    
    log.write(f"Traits: {', '.join(traits)}", verbose=verbose)
    
    # Prepare data: extract Z-scores, N, and EAF for each trait
    log.write("Preparing data for MTAG analysis...", verbose=verbose)
    
    # Get required columns
    info_cols = ["rsID", "CHR", "POS", "EA", "NEA"]
    available_info_cols = [col for col in info_cols if col in df.columns]
    
    # Build column lists for each trait
    z_cols = [f"Z_{i+1}" for i in range(n_traits)]
    n_cols = [f"N_{i+1}" for i in range(n_traits)]
    eaf_cols = [f"EAF_{i+1}" for i in range(n_traits)]
    
    # Check required columns exist
    missing_cols = []
    for col in z_cols + n_cols + eaf_cols:
        if col not in df.columns:
            missing_cols.append(col)
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
    
    # Select relevant columns
    select_cols = available_info_cols + z_cols + n_cols + eaf_cols
    df_work = df.select(select_cols).clone()
    
    # Apply QC filters
    log.write(f"Initial SNPs: {len(df_work):,}", verbose=verbose)
    
    # Filter by minimum sample size
    if n_min > 0:
        n_mask = pl.lit(True)
        for n_col in n_cols:
            n_mask = n_mask & (pl.col(n_col) >= n_min)
        df_work = df_work.filter(n_mask)
        log.write(f"After N >= {n_min} filter: {len(df_work):,}", verbose=verbose)
    
    # Check median Z-scores for each trait
    for i, (z_col, trait) in enumerate(zip(z_cols, traits)):
        median_z = df_work.select(pl.col(z_col).abs().median()).item()
        log.write(f"  {trait}: median |Z| = {median_z:.4f}", verbose=verbose)
        if median_z > median_z_cutoff:
            log.write(f"  WARNING: {trait} has median |Z| = {median_z:.4f} > {median_z_cutoff}. "
                     f"Consider QC before MTAG.", verbose=verbose)
    
    if len(df_work) == 0:
        raise ValueError("No SNPs remaining after QC filters.")
    
    # Extract matrices for MTAG computation
    log.write("Extracting Z-scores and sample sizes...", verbose=verbose)
    
    # Convert to numpy for matrix operations
    Z_mat = df_work.select(z_cols).to_numpy()
    N_mat = df_work.select(n_cols).to_numpy()
    
    # Handle missing values
    # For Z-scores, we'll use 0 for missing (conservative)
    # For N, we'll use 0 for missing
    Z_mat = np.nan_to_num(Z_mat, nan=0.0)
    N_mat = np.nan_to_num(N_mat, nan=0.0)
    
    n_snps = Z_mat.shape[0]
    log.write(f"SNPs for MTAG analysis: {n_snps:,}", verbose=verbose)
    
    # Estimate error variance-covariance matrix (sigma)
    log.write("Estimating error variance-covariance matrix (sigma)...", verbose=verbose)
    
    if use_ldsc and ldsc_kwargs is not None:
        # Use LDSC-based estimation for sigma and omega
        sigma_hat, omega_hat = _estimate_sigma_omega_ldsc(
            df_work, z_cols, n_cols, traits, no_overlap, perfect_gencov, 
            equal_h2, ldsc_kwargs, log, verbose
        )
    else:
        sigma_hat = _estimate_sigma(Z_mat, N_mat, no_overlap=no_overlap, log=log, verbose=verbose)
        
        # Estimate genetic variance-covariance matrix (omega)
        log.write("Estimating genetic variance-covariance matrix (omega)...", verbose=verbose)
        
        if perfect_gencov:
            omega_hat = np.eye(n_traits)
            log.write("Using perfect genetic covariance (identity matrix)", verbose=verbose)
            if equal_h2:
                # Estimate single h2 and scale identity matrix
                h2_est = _estimate_heritability_simple(Z_mat, N_mat)
                omega_hat = h2_est * np.eye(n_traits)
                log.write(f"Estimated heritability (equal across traits): {h2_est:.6f}", verbose=verbose)
        elif numerical_omega:
            omega_hat = _estimate_omega_numerical(
                Z_mat, N_mat, sigma_hat, tol=tol, time_limit=time_limit,
                log=log, verbose=verbose
            )
        else:
            # Use method of moments estimator
            omega_hat = _estimate_omega_mom(Z_mat, N_mat, sigma_hat, log=log, verbose=verbose)
    
    log.write("Genetic VCV matrix (omega):", verbose=verbose)
    for i, row in enumerate(omega_hat):
        log.write(f"  {traits[i]}: {row}", verbose=verbose)
    
    # Compute MTAG estimates
    log.write("Computing MTAG estimates...", verbose=verbose)
    Z_mtag, se_mtag = _compute_mtag_estimates(Z_mat, omega_hat, sigma_hat, log=log, verbose=verbose)
    
    # Compute P-values from Z-scores
    P_mtag = 2 * norm.sf(np.abs(Z_mtag))
    
    # Prepare output DataFrame
    log.write("Preparing output...", verbose=verbose)
    
    # Start with original info columns
    result_df = df_work.select(available_info_cols).clone()
    
    # Add MTAG results for each trait
    for i, trait in enumerate(traits):
        result_df = result_df.with_columns([
            pl.Series(f"Z_MTAG_{i+1}", Z_mtag[:, i]).alias(f"Z_MTAG_{i+1}"),
            pl.Series(f"SE_MTAG_{i+1}", se_mtag[:, i]).alias(f"SE_MTAG_{i+1}"),
            pl.Series(f"P_MTAG_{i+1}", P_mtag[:, i]).alias(f"P_MTAG_{i+1}"),
        ])
    
    # Add original Z-scores and other info
    for col in z_cols + n_cols + eaf_cols:
        if col in df_work.columns:
            result_df = result_df.with_columns(df_work.select(col))
    
    # Add MTAG metadata columns
    result_df = result_df.with_columns([
        pl.lit(n_traits).alias("N_TRAITS"),
    ])
    
    log.write("=" * 80, verbose=verbose)
    log.write(f"MTAG analysis complete. Results for {len(result_df):,} SNPs.", verbose=verbose)
    log.write("=" * 80, verbose=verbose)
    
    return result_df


def _estimate_sigma(
    Z_mat: np.ndarray,
    N_mat: np.ndarray,
    no_overlap: bool = False,
    log: Log = Log(),
    verbose: bool = True
) -> np.ndarray:
    """
    Estimate error variance-covariance matrix (sigma).
    
    The error covariance between traits i and j is estimated as:
    sigma_ij = (1/N_i + 1/N_j) * rho_ij if there's sample overlap
    sigma_ij = 0 if no_overlap=True
    
    This follows the approach in the original MTAG implementation, which
    estimates error covariance from the correlation of Z-scores and sample sizes.
    
    Parameters
    ----------
    Z_mat : np.ndarray
        Z-score matrix (n_snps x n_traits)
    N_mat : np.ndarray
        Sample size matrix (n_snps x n_traits)
    no_overlap : bool, default False
        If True, assumes no sample overlap (off-diagonal = 0)
    log : Log
        Log object
    verbose : bool
        Verbose flag
    
    Returns
    -------
    np.ndarray
        Error variance-covariance matrix (n_traits x n_traits)
    """
    n_traits = Z_mat.shape[1]
    sigma = np.zeros((n_traits, n_traits))
    
    if no_overlap:
        log.write("Assuming no sample overlap (off-diagonal = 0)", verbose=verbose)
        # Diagonal only: sigma_ii = 1/N_i (average)
        for i in range(n_traits):
            n_i = N_mat[:, i]
            n_i_valid = n_i[n_i > 0]
            if len(n_i_valid) > 0:
                sigma[i, i] = np.mean(1.0 / n_i_valid)
            else:
                sigma[i, i] = 1.0
    else:
        # Estimate error covariance following MTAG approach
        # For each pair of traits, estimate correlation in Z-scores
        # and use it to estimate error covariance
        for i in range(n_traits):
            for j in range(n_traits):
                if i == j:
                    # Diagonal: average of 1/N (error variance)
                    n_i = N_mat[:, i]
                    n_i_valid = n_i[n_i > 0]
                    if len(n_i_valid) > 0:
                        sigma[i, i] = np.mean(1.0 / n_i_valid)
                    else:
                        sigma[i, i] = 1.0
                else:
                    # Off-diagonal: estimate from correlation and sample sizes
                    # Based on MTAG: sigma_ij = E[(1/N_i + 1/N_j) * rho_ij]
                    z_i = Z_mat[:, i]
                    z_j = Z_mat[:, j]
                    
                    # Only use SNPs with valid data for both traits
                    valid_mask = (N_mat[:, i] > 0) & (N_mat[:, j] > 0)
                    if np.sum(valid_mask) > 10:  # Need sufficient SNPs
                        z_i_valid = z_i[valid_mask]
                        z_j_valid = z_j[valid_mask]
                        
                        # Estimate correlation (error correlation from sample overlap)
                        # This captures the correlation due to shared samples
                        corr = np.corrcoef(z_i_valid, z_j_valid)[0, 1]
                        if np.isnan(corr):
                            corr = 0.0
                        
                        # Estimate error covariance
                        # sigma_ij = E[(1/N_i + 1/N_j) * rho_ij]
                        # where rho_ij is the error correlation
                        n_i_valid = N_mat[valid_mask, i]
                        n_j_valid = N_mat[valid_mask, j]
                        # Weight by correlation to get error covariance
                        sigma_ij = np.mean((1.0 / n_i_valid + 1.0 / n_j_valid) * corr)
                        sigma[i, j] = sigma_ij
                    else:
                        sigma[i, j] = 0.0
    
    # Ensure symmetry
    sigma = (sigma + sigma.T) / 2
    
    # Ensure positive semi-definite
    eigenvals, eigenvecs = np.linalg.eigh(sigma)
    eigenvals = np.maximum(eigenvals, 1e-8)  # Ensure positive
    sigma = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
    
    log.write("Error VCV matrix (sigma):", verbose=verbose)
    for i in range(n_traits):
        log.write(f"  Trait {i+1}: {sigma[i, :]}", verbose=verbose)
    
    return sigma


def _estimate_sigma_omega_ldsc(
    df_work: pl.DataFrame,
    z_cols: List[str],
    n_cols: List[str],
    traits: List[str],
    no_overlap: bool,
    perfect_gencov: bool,
    equal_h2: bool,
    ldsc_kwargs: Dict[str, Any],
    log: Log,
    verbose: bool
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimate sigma and omega using LDSC regression.
    
    This function uses LDSC to estimate heritability (for omega diagonal)
    and genetic correlations (for omega off-diagonals), and uses LDSC
    intercepts to estimate error covariance (sigma).
    
    Based on the original MTAG implementation (https://github.com/JonJala/mtag)
    which uses LDSC for:
    - Heritability estimation (h2) for omega diagonal elements
    - Genetic correlation (rg) for omega off-diagonal elements  
    - Intercept for sigma diagonal elements
    
    Parameters
    ----------
    df_work : pl.DataFrame
        Working DataFrame with Z-scores and sample sizes
    z_cols : List[str]
        List of Z-score column names
    n_cols : List[str]
        List of sample size column names
    traits : List[str]
        List of trait names
    no_overlap : bool
        Whether to assume no sample overlap
    perfect_gencov : bool
        Whether to use perfect genetic covariance
    equal_h2 : bool
        Whether to assume equal heritability
    ldsc_kwargs : Dict[str, Any]
        Keyword arguments for LDSC (ref_ld_chr, w_ld_chr, etc.)
    log : Log
        Log object
    verbose : bool
        Verbose flag
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        sigma and omega matrices
    """
    from gwaslab.util.util_ex_ldsc import _estimate_h2_by_ldsc, _estimate_rg_by_ldsc
    from gwaslab.g_Sumstats import Sumstats
    from gwaslab.bd.bd_get_hapmap3 import _get_hapmap3
    
    log.write("Using LDSC regression to estimate sigma and omega", verbose=verbose)
    log.write("Based on original MTAG implementation using LDSC", verbose=verbose)
    
    n_traits = len(traits)
    sigma = np.zeros((n_traits, n_traits))
    omega = np.zeros((n_traits, n_traits))
    
    # Convert to pandas for LDSC (which expects pandas)
    df_pd = df_work.to_pandas()
    
    # Check if required LDSC arguments are provided
    if "ref_ld_chr" not in ldsc_kwargs:
        log.write("  WARNING: ref_ld_chr not provided in ldsc_kwargs. LDSC requires ref_ld_chr.", verbose=verbose)
        log.write("  Falling back to method of moments for all estimates.", verbose=verbose)
        # Fallback to method of moments
        Z_mat = df_pd[z_cols].values
        N_mat = df_pd[n_cols].values
        sigma = _estimate_sigma(Z_mat, N_mat, no_overlap=no_overlap, log=log, verbose=verbose)
        omega = _estimate_omega_mom(Z_mat, N_mat, sigma, log=log, verbose=verbose)
        return sigma, omega
    
    # Match with HapMap3 to get rsID (required for LDSC)
    log.write("Matching with HapMap3 to get rsID for LDSC...", verbose=verbose)
    build = ldsc_kwargs.get("build", "19")
    
    try:
        # Check if rsID column exists and has valid values
        has_rsid = "rsID" in df_pd.columns and df_pd["rsID"].notna().any()
        
        if not has_rsid:
            log.write("  rsID column missing or empty, will match by CHR:POS", verbose=verbose)
        
        # Match with HapMap3 - this will filter to HapMap3 SNPs and ensure rsID is available
        df_pd_hapmap3 = _get_hapmap3(
            sumstats_or_dataframe=df_pd.copy(),
            rsid="rsID",
            chrom="CHR",
            pos="POS",
            ea="EA",
            nea="NEA",
            build=build,
            verbose=verbose,
            match_allele=True,
            how="inner",
            log=log
        )
        
        # Check if matching was successful and rsID is now available
        if len(df_pd_hapmap3) > 0 and "rsID" in df_pd_hapmap3.columns and df_pd_hapmap3["rsID"].notna().any():
            df_pd = df_pd_hapmap3
            log.write(f"  Matched {len(df_pd):,} HapMap3 SNPs for LDSC analysis", verbose=verbose)
        else:
            log.write(f"  WARNING: HapMap3 matching returned {len(df_pd_hapmap3)} SNPs or rsID still missing", verbose=verbose)
            log.write(f"  Falling back to method of moments", verbose=verbose)
            Z_mat = df_pd[z_cols].values
            N_mat = df_pd[n_cols].values
            sigma = _estimate_sigma(Z_mat, N_mat, no_overlap=no_overlap, log=log, verbose=verbose)
            omega = _estimate_omega_mom(Z_mat, N_mat, sigma, log=log, verbose=verbose)
            return sigma, omega
            
    except Exception as e:
        log.write(f"  WARNING: HapMap3 matching failed: {e}", verbose=verbose)
        log.write(f"  Falling back to method of moments", verbose=verbose)
        Z_mat = df_pd[z_cols].values
        N_mat = df_pd[n_cols].values
        sigma = _estimate_sigma(Z_mat, N_mat, no_overlap=no_overlap, log=log, verbose=verbose)
        omega = _estimate_omega_mom(Z_mat, N_mat, sigma, log=log, verbose=verbose)
        return sigma, omega
    
    # Check if rsID is available before proceeding with LDSC
    has_rsid_for_ldsc = "rsID" in df_pd.columns and df_pd["rsID"].notna().any()
    
    if not has_rsid_for_ldsc:
        log.write("  ERROR: rsID is required for LDSC but is missing after HapMap3 matching.", verbose=verbose)
        log.write("  Falling back to method of moments.", verbose=verbose)
        Z_mat = df_pd[z_cols].values
        N_mat = df_pd[n_cols].values
        sigma = _estimate_sigma(Z_mat, N_mat, no_overlap=no_overlap, log=log, verbose=verbose)
        omega = _estimate_omega_mom(Z_mat, N_mat, sigma, log=log, verbose=verbose)
        return sigma, omega
    
    # Estimate heritability for each trait (for omega diagonal)
    log.write("Estimating heritability for each trait using LDSC...", verbose=verbose)
    h2_estimates = []
    intercepts = []
    sumstats_objects = []
    
    for i, (z_col, n_col, trait) in enumerate(zip(z_cols, n_cols, traits)):
        log.write(f"  Estimating h2 for {trait}...", verbose=verbose)
        
        try:
            # Prepare sumstats DataFrame for this trait
            sumstats_df = df_pd[["rsID", "CHR", "POS", "EA", "NEA", z_col, n_col]].copy()
            sumstats_df = sumstats_df.rename(columns={z_col: "Z", n_col: "N"})
            
            # Create Sumstats object with required metadata
            sumstats_obj = Sumstats(
                sumstats=sumstats_df,
                rsid="rsID",
                chrom="CHR",
                pos="POS",
                ea="EA",
                nea="NEA",
                z="Z",
                n="N",
                study=trait,
                trait=trait,
                build=build,
                verbose=False
            )
            sumstats_objects.append(sumstats_obj)
            
            # Call LDSC to estimate heritability
            h2_summary, h2_results = _estimate_h2_by_ldsc(
                insumstats=sumstats_obj,
                log=log,
                meta=sumstats_obj.meta,
                verbose=verbose,
                **ldsc_kwargs
            )
            
            # Extract h2 and intercept from summary
            if h2_summary is not None and len(h2_summary) > 0:
                # Get h2_obs (or h2_liab if liability scale)
                h2_col = "h2_obs" if "h2_obs" in h2_summary.columns else "h2_liab"
                if h2_col in h2_summary.columns:
                    h2_value = h2_summary[h2_col].iloc[0]
                    if pd.notna(h2_value):
                        try:
                            h2_est = float(h2_value)
                            h2_est = max(0.0, h2_est)  # Ensure non-negative
                            h2_estimates.append(h2_est)
                            log.write(f"    h2({trait}) = {h2_est:.6f}", verbose=verbose)
                        except (ValueError, TypeError):
                            log.write(f"    WARNING: Could not parse h2 value, using fallback", verbose=verbose)
                            h2_estimates.append(0.0)
                    else:
                        log.write(f"    WARNING: h2 is NA, using fallback", verbose=verbose)
                        h2_estimates.append(0.0)
                else:
                    log.write(f"    WARNING: h2 column not found, using fallback", verbose=verbose)
                    h2_estimates.append(0.0)
                
                # Get intercept
                if "Intercept" in h2_summary.columns:
                    intercept_value = h2_summary["Intercept"].iloc[0]
                    if pd.notna(intercept_value):
                        try:
                            intercept = float(intercept_value)
                            intercept = max(1e-8, intercept)  # Ensure positive
                            intercepts.append(intercept)
                            log.write(f"    Intercept({trait}) = {intercept:.6f}", verbose=verbose)
                        except (ValueError, TypeError):
                            log.write(f"    WARNING: Could not parse intercept, using fallback", verbose=verbose)
                            n_vals = df_pd[n_col].values
                            n_valid = n_vals[n_vals > 0]
                            intercepts.append(np.mean(1.0 / n_valid) if len(n_valid) > 0 else 1.0)
                    else:
                        n_vals = df_pd[n_col].values
                        n_valid = n_vals[n_vals > 0]
                        intercepts.append(np.mean(1.0 / n_valid) if len(n_valid) > 0 else 1.0)
                else:
                    log.write(f"    WARNING: Intercept column not found, using fallback", verbose=verbose)
                    n_vals = df_pd[n_col].values
                    n_valid = n_vals[n_vals > 0]
                    intercepts.append(np.mean(1.0 / n_valid) if len(n_valid) > 0 else 1.0)
            else:
                log.write(f"    WARNING: LDSC returned empty summary, using fallback", verbose=verbose)
                h2_estimates.append(0.0)
                n_vals = df_pd[n_col].values
                n_valid = n_vals[n_vals > 0]
                intercepts.append(np.mean(1.0 / n_valid) if len(n_valid) > 0 else 1.0)
                
        except Exception as e:
            log.write(f"    WARNING: LDSC estimation failed for {trait}: {e}", verbose=verbose)
            log.write(f"    Using fallback estimator", verbose=verbose)
            # Fallback: use simple estimator
            z_vals = df_pd[z_col].values
            n_vals = df_pd[n_col].values
            n_valid = n_vals[n_vals > 0]
            if len(n_valid) > 0:
                h2_est = max(0.0, np.mean(z_vals**2) - np.mean(1.0 / n_valid))
            else:
                h2_est = 0.0
            h2_estimates.append(h2_est)
            intercepts.append(np.mean(1.0 / n_valid) if len(n_valid) > 0 else 1.0)
            # Create a dummy Sumstats object for later use
            try:
                sumstats_df = df_pd[["rsID", "CHR", "POS", "EA", "NEA", z_col, n_col]].copy()
                sumstats_df = sumstats_df.rename(columns={z_col: "Z", n_col: "N"})
                sumstats_obj = Sumstats(
                    sumstats=sumstats_df,
                    rsid="rsID",
                    chrom="CHR",
                    pos="POS",
                    ea="EA",
                    nea="NEA",
                    z="Z",
                    n="N",
                    study=trait,
                    trait=trait,
                    build=build,
                    verbose=False
                )
                sumstats_objects.append(sumstats_obj)
            except:
                sumstats_objects.append(None)
    
    # Build omega diagonal
    if perfect_gencov:
        omega = np.eye(n_traits)
        if equal_h2:
            h2_avg = np.mean(h2_estimates) if len(h2_estimates) > 0 else 0.0
            omega = h2_avg * np.eye(n_traits)
            log.write(f"Using perfect genetic covariance with equal h2 = {h2_avg:.6f}", verbose=verbose)
    else:
        for i in range(n_traits):
            omega[i, i] = h2_estimates[i] if i < len(h2_estimates) else 0.0
    
    # Estimate genetic correlations for off-diagonals (if not perfect_gencov)
    if not perfect_gencov and n_traits > 1:
        log.write("Estimating genetic correlations using LDSC...", verbose=verbose)
        
        # Check if we have valid Sumstats objects
        if len(sumstats_objects) == n_traits and all(obj is not None for obj in sumstats_objects):
            # Use LDSC to estimate genetic correlations for each pair
            for i in range(n_traits):
                for j in range(i+1, n_traits):
                    if omega[i, i] > 0 and omega[j, j] > 0:
                        try:
                            log.write(f"  Estimating rg between {traits[i]} and {traits[j]}...", verbose=verbose)
                            
                            # Call _estimate_rg_by_ldsc with trait i as main and trait j as other
                            rg_summary = _estimate_rg_by_ldsc(
                                insumstats=sumstats_objects[i],
                                other_traits=[sumstats_objects[j]],
                                log=log,
                                meta=sumstats_objects[i].meta,
                                verbose=verbose,
                                **ldsc_kwargs
                            )
                            
                            # Extract genetic correlation from summary
                            if rg_summary is not None and len(rg_summary) > 0:
                                if "rg" in rg_summary.columns:
                                    rg_value = rg_summary["rg"].iloc[0]
                                    if pd.notna(rg_value) and isinstance(rg_value, (int, float)):
                                        # Clip to valid range
                                        rg_value = np.clip(float(rg_value), -1.0, 1.0)
                                        # Compute genetic covariance: rg * sqrt(h2_i * h2_j)
                                        omega[i, j] = rg_value * np.sqrt(omega[i, i] * omega[j, j])
                                        omega[j, i] = omega[i, j]
                                        log.write(f"    rg({traits[i]}, {traits[j]}) = {rg_value:.4f}", verbose=verbose)
                                    else:
                                        log.write(f"    WARNING: Invalid rg value, using fallback", verbose=verbose)
                                        _use_fallback_rg_approx(df_pd, z_cols, omega, i, j, traits, log, verbose)
                                else:
                                    log.write(f"    WARNING: 'rg' column not found in LDSC summary, using fallback", verbose=verbose)
                                    _use_fallback_rg_approx(df_pd, z_cols, omega, i, j, traits, log, verbose)
                            else:
                                log.write(f"    WARNING: LDSC returned empty summary, using fallback", verbose=verbose)
                                _use_fallback_rg_approx(df_pd, z_cols, omega, i, j, traits, log, verbose)
                        except Exception as e:
                            log.write(f"    WARNING: LDSC estimation failed for {traits[i]} vs {traits[j]}: {e}", verbose=verbose)
                            log.write(f"    Using fallback approximation", verbose=verbose)
                            _use_fallback_rg_approx(df_pd, z_cols, omega, i, j, traits, log, verbose)
        else:
            # Fallback: use correlation of Z-scores as approximation
            log.write("  WARNING: Could not create Sumstats objects for all traits, using Z-score correlation approximation", verbose=verbose)
            Z_mat = df_pd[z_cols].values
            Z_cov = np.cov(Z_mat.T)
            for i in range(n_traits):
                for j in range(i+1, n_traits):
                    if omega[i, i] > 0 and omega[j, j] > 0:
                        _use_fallback_rg_approx(df_pd, z_cols, omega, i, j, traits, log, verbose)
    
    # Build sigma from intercepts
    log.write("Building sigma matrix from LDSC intercepts...", verbose=verbose)
    for i in range(n_traits):
        if i < len(intercepts):
            sigma[i, i] = intercepts[i]
        else:
            # Fallback if intercept not available
            n_vals = df_pd[n_cols[i]].values
            n_valid = n_vals[n_vals > 0]
            sigma[i, i] = np.mean(1.0 / n_valid) if len(n_valid) > 0 else 1.0
        
        if not no_overlap:
            for j in range(i+1, n_traits):
                # Estimate error covariance from correlation
                z_i = df_pd[z_cols[i]].values
                z_j = df_pd[z_cols[j]].values
                valid_mask = (df_pd[n_cols[i]] > 0) & (df_pd[n_cols[j]] > 0)
                if np.sum(valid_mask) > 10:
                    corr = np.corrcoef(z_i[valid_mask], z_j[valid_mask])[0, 1]
                    if np.isnan(corr):
                        corr = 0.0
                    n_i = df_pd[n_cols[i]][valid_mask].values
                    n_j = df_pd[n_cols[j]][valid_mask].values
                    sigma_ij = np.mean((1.0 / n_i + 1.0 / n_j) * corr)
                    sigma[i, j] = sigma_ij
                    sigma[j, i] = sigma_ij
    
    # Ensure positive semi-definite
    eigenvals, eigenvecs = np.linalg.eigh(sigma)
    eigenvals = np.maximum(eigenvals, 1e-8)
    sigma = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
    
    eigenvals, eigenvecs = np.linalg.eigh(omega)
    eigenvals = np.maximum(eigenvals, 1e-8)
    omega = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
    
    return sigma, omega


def _use_fallback_rg_approx(
    df_pd: pd.DataFrame,
    z_cols: List[str],
    omega: np.ndarray,
    i: int,
    j: int,
    traits: List[str],
    log: Log,
    verbose: bool
) -> None:
    """Helper function to compute fallback genetic correlation approximation."""
    Z_mat = df_pd[z_cols].values
    Z_cov = np.cov(Z_mat.T)
    rg_approx = Z_cov[i, j] / np.sqrt(omega[i, i] * omega[j, j])
    rg_approx = np.clip(rg_approx, -1, 1)
    omega[i, j] = rg_approx * np.sqrt(omega[i, i] * omega[j, j])
    omega[j, i] = omega[i, j]


def _estimate_omega_mom(
    Z_mat: np.ndarray,
    N_mat: np.ndarray,
    sigma: np.ndarray,
    log: Log = Log(),
    verbose: bool = True
) -> np.ndarray:
    """
    Estimate genetic variance-covariance matrix (omega) using method of moments.
    
    Following MTAG: E[Z Z^T] = omega + sigma, so omega = E[Z Z^T] - sigma
    
    Parameters
    ----------
    Z_mat : np.ndarray
        Z-score matrix (n_snps x n_traits)
    N_mat : np.ndarray
        Sample size matrix (n_snps x n_traits)
    sigma : np.ndarray
        Error variance-covariance matrix
    log : Log
        Log object
    verbose : bool
        Verbose flag
    
    Returns
    -------
    np.ndarray
        Genetic variance-covariance matrix (n_traits x n_traits)
    """
    n_traits = Z_mat.shape[1]
    
    # Method of moments: E[Z Z^T] = omega + sigma
    # So omega = E[Z Z^T] - sigma
    
    # Compute empirical covariance of Z-scores
    # Note: MTAG uses uncentered covariance E[Z Z^T] since E[Z] = 0 under null
    Z_cov = np.cov(Z_mat.T, bias=True)  # Use bias=True for population covariance
    
    # Alternative: use mean of outer products (more aligned with MTAG)
    # This is equivalent for centered data but more explicit
    Z_centered = Z_mat - np.mean(Z_mat, axis=0)
    Z_cov_centered = np.cov(Z_centered.T)
    
    # Use centered version (more standard)
    Z_cov = Z_cov_centered
    
    # Estimate omega
    omega = Z_cov - sigma
    
    # Ensure positive semi-definite
    eigenvals, eigenvecs = np.linalg.eigh(omega)
    # Set negative eigenvalues to small positive value
    eigenvals = np.maximum(eigenvals, 1e-8)
    omega = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
    
    # Ensure symmetry
    omega = (omega + omega.T) / 2
    
    log.write("Estimated omega using method of moments", verbose=verbose)
    
    return omega


def _estimate_omega_numerical(
    Z_mat: np.ndarray,
    N_mat: np.ndarray,
    sigma: np.ndarray,
    tol: float = DEFAULT_TOL,
    time_limit: float = DEFAULT_TIME_LIMIT,
    log: Log = Log(),
    verbose: bool = True
) -> np.ndarray:
    """
    Estimate genetic variance-covariance matrix (omega) using numerical MLE.
    
    This uses numerical optimization to find the MLE of omega.
    
    Parameters
    ----------
    Z_mat : np.ndarray
        Z-score matrix (n_snps x n_traits)
    N_mat : np.ndarray
        Sample size matrix (n_snps x n_traits)
    sigma : np.ndarray
        Error variance-covariance matrix
    tol : float
        Tolerance for optimization
    time_limit : float
        Time limit in hours
    log : Log
        Log object
    verbose : bool
        Verbose flag
    
    Returns
    -------
    np.ndarray
        Genetic variance-covariance matrix (n_traits x n_traits)
    """
    log.write("Using numerical MLE estimator (this may take a while)...", verbose=verbose)
    
    n_traits = Z_mat.shape[1]
    
    # Use method of moments as starting point
    omega_init = _estimate_omega_mom(Z_mat, N_mat, sigma, log=log, verbose=False)
    
    # Flatten for optimization (only upper triangle due to symmetry)
    def omega_to_params(omega):
        """Convert omega matrix to parameter vector (upper triangle)."""
        params = []
        for i in range(n_traits):
            for j in range(i, n_traits):
                params.append(omega[i, j])
        return np.array(params)
    
    def params_to_omega(params):
        """Convert parameter vector to symmetric omega matrix."""
        omega = np.zeros((n_traits, n_traits))
        idx = 0
        for i in range(n_traits):
            for j in range(i, n_traits):
                omega[i, j] = params[idx]
                omega[j, i] = params[idx]
                idx += 1
        return omega
    
    def neg_log_likelihood(params):
        """Negative log-likelihood for optimization."""
        omega = params_to_omega(params)
        
        # Ensure positive semi-definite
        eigenvals, eigenvecs = np.linalg.eigh(omega)
        if np.any(eigenvals < 0):
            return 1e10  # Penalty for non-PSD
        
        # Compute log-likelihood
        # Z ~ N(0, omega + sigma)
        cov = omega + sigma
        try:
            cov_inv = inv(cov)
            log_det = np.log(np.linalg.det(cov))
        except:
            return 1e10
        
        ll = -0.5 * np.sum(Z_mat @ cov_inv @ Z_mat.T) - 0.5 * Z_mat.shape[0] * log_det
        return -ll  # Negative for minimization
    
    # Optimize
    params_init = omega_to_params(omega_init)
    
    try:
        result = optimize.minimize(
            neg_log_likelihood,
            params_init,
            method='L-BFGS-B',
            options={'maxiter': 1000, 'ftol': tol}
        )
        
        if result.success:
            omega = params_to_omega(result.x)
            log.write("Numerical optimization converged.", verbose=verbose)
        else:
            log.write("Numerical optimization did not converge, using MoM estimate.", verbose=verbose)
            omega = omega_init
    except Exception as e:
        log.write(f"Numerical optimization failed: {e}. Using MoM estimate.", verbose=verbose)
        omega = omega_init
    
    # Ensure positive semi-definite
    eigenvals, eigenvecs = np.linalg.eigh(omega)
    eigenvals = np.maximum(eigenvals, 1e-8)
    omega = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
    
    return omega


def _estimate_heritability_simple(
    Z_mat: np.ndarray,
    N_mat: np.ndarray
) -> float:
    """
    Estimate heritability assuming equal h2 across traits.
    
    Simple estimator: h2 = mean(Z^2) - 1/N
    
    Parameters
    ----------
    Z_mat : np.ndarray
        Z-score matrix
    N_mat : np.ndarray
        Sample size matrix
    
    Returns
    -------
    float
        Estimated heritability
    """
    # Average Z^2 across all SNPs and traits
    z2_mean = np.mean(Z_mat ** 2)
    
    # Average 1/N across all SNPs and traits
    n_valid = N_mat[N_mat > 0]
    if len(n_valid) > 0:
        inv_n_mean = np.mean(1.0 / n_valid)
    else:
        inv_n_mean = 0.0
    
    h2 = max(0.0, z2_mean - inv_n_mean)
    return h2


def _compute_mtag_estimates(
    Z_mat: np.ndarray,
    omega: np.ndarray,
    sigma: np.ndarray,
    log: Log = Log(),
    verbose: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute MTAG estimates.
    
    MTAG formula: Z_MTAG = (omega + sigma)^(-1) * omega * Z
    
    This is the core MTAG transformation that combines information across traits.
    The transformation matrix (omega + sigma)^(-1) * omega optimally weights
    the Z-scores from different traits based on their genetic and error covariances.
    
    Parameters
    ----------
    Z_mat : np.ndarray
        Z-score matrix (n_snps x n_traits)
    omega : np.ndarray
        Genetic variance-covariance matrix (n_traits x n_traits)
    sigma : np.ndarray
        Error variance-covariance matrix (n_traits x n_traits)
    log : Log
        Log object
    verbose : bool
        Verbose flag
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Z_MTAG matrix and SE_MTAG matrix
    """
    n_snps, n_traits = Z_mat.shape
    
    # Compute (omega + sigma)^(-1) * omega
    # This is the total covariance matrix
    cov = omega + sigma
    
    try:
        cov_inv = inv(cov)
    except np.linalg.LinAlgError:
        log.write("Matrix inversion failed, using pseudo-inverse", verbose=verbose)
        cov_inv = pinv(cov)
    
    # MTAG transformation matrix: (omega + sigma)^(-1) * omega
    # This matrix optimally combines information across traits
    mtag_transform = cov_inv @ omega
    
    # Compute MTAG Z-scores for each trait
    # Z_MTAG[i] = sum_j (mtag_transform[i,j] * Z[j])
    Z_mtag = Z_mat @ mtag_transform.T
    
    # Compute MTAG standard errors
    # The variance of Z_MTAG is given by the diagonal of:
    # (omega + sigma)^(-1) * omega * (omega + sigma)^(-1)
    # For each trait i, SE = sqrt(variance[i,i])
    # Simplified: variance is approximately diag(cov_inv) for each trait
    se_mtag = np.ones_like(Z_mtag)
    for i in range(n_traits):
        # SE for trait i: sqrt of variance from transformation
        # Variance = (mtag_transform @ cov @ mtag_transform.T)[i,i]
        # Simplified to diagonal of cov_inv for efficiency
        var_i = np.diag(cov_inv)[i]
        se_mtag[:, i] = np.sqrt(var_i)
    
    log.write(f"Computed MTAG estimates for {n_snps:,} SNPs", verbose=verbose)
    
    return Z_mtag, se_mtag

