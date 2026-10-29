"""Fixed-horizon, user-level experiment inference. No repeated-peeking claims."""
from math import sqrt
import numpy as np
from scipy.stats import norm, chi2


def wilson(successes, n, alpha=0.05):
    if n <= 0:
        raise ValueError("A retention denominator must be positive")
    z = norm.ppf(1 - alpha / 2)
    p = successes / n
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    half = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return float(center-half), float(center+half)


def compare(k0, n0, k1, n1):
    """Treatment minus control; Newcombe independent Wilson difference interval."""
    p0, p1 = k0/n0, k1/n1
    pooled = (k0+k1)/(n0+n1)
    se = sqrt(pooled*(1-pooled)*(1/n0+1/n1))
    delta = p1-p0
    p_value = float(2*norm.sf(abs(delta/se))) if se else 1.0
    lo0, hi0 = wilson(k0, n0)
    lo1, hi1 = wilson(k1, n1)
    low = delta - sqrt((p1-lo1)**2 + (hi0-p0)**2)
    high = delta + sqrt((hi1-p1)**2 + (p0-lo0)**2)
    return {"control_rate":p0, "treatment_rate":p1, "delta":delta,
            "relative_change":delta/p0 if p0 else None,
            "ci_low":low, "ci_high":high, "p_value":p_value}


def holm(p_values):
    order = np.argsort(p_values)
    adjusted = [0.0]*len(p_values)
    previous = 0.0
    for i, ix in enumerate(order):
        previous = max(previous, min(1.0, (len(p_values)-i)*p_values[ix]))
        adjusted[int(ix)] = previous
    return adjusted


def srm(n0, n1):
    """Conditional on assumed equal allocation; intended split is not supplied."""
    expected = (n0+n1)/2
    stat = ((n0-expected)**2 + (n1-expected)**2)/expected
    return {"chi_square":stat, "p_value":float(chi2.sf(stat,1)),
            "assumed_control_share":0.5, "threshold":0.01,
            "allocation_verified":False}


def required_n(baseline, absolute_mde, power=0.8, alpha=0.05):
    """Normal approximation, equal-size two-sided test, no sequential correction."""
    alternative = baseline - absolute_mde
    if not 0 < alternative < 1 or not 0 < baseline < 1:
        raise ValueError("MDE must leave both rates between 0 and 1")
    average = (baseline+alternative)/2
    numerator = (norm.ppf(1-alpha/2)*sqrt(2*average*(1-average))
                 + norm.ppf(power)*sqrt(baseline*(1-baseline)+alternative*(1-alternative)))**2
    return int(np.ceil(numerator/absolute_mde**2))
