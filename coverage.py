"""v2.3 Coverage Ratio calculator (preregistered).

Computes the veto coverage ratio C_veto(n_sigma, sigma) for arbitrary
band geometries: the fraction of the fiducial coordinate range covered
by the union of all material-veto bands.

  C_veto = |⋃_i [x_i - HW_i - n_sigma*sigma, x_i + HW_i + n_sigma*sigma]| / L_fiducial

The union accounts for band overlaps (each position counted at most once).
"""
import numpy as np


def coverage_ratio(bands, lo, hi, nsig, sigma):
    """Compute the veto coverage ratio for a set of material bands.

    Parameters
    ----------
    bands : list of (position, X0, half_width) tuples
        Material band definitions (same format as mtag_v21.BANDS or mtag_v22.DISKS).
    lo, hi : float
        Fiducial coordinate range [lo, hi].
    nsig : float
        Veto width in units of the position resolution sigma.
    sigma : float or array_like
        Position resolution (scalar or per-band array).

    Returns
    -------
    C : float
        Veto coverage ratio, 0 <= C <= 1.
    intervals : list of (lo, hi) tuples
        Merged veto intervals within the fiducial range.
    """
    sigma = np.atleast_1d(np.asarray(sigma, float))
    if len(sigma) == 1:
        sigma = np.full(len(bands), sigma[0])

    # Build raw intervals
    raw = []
    for i, (x, _x0, hw) in enumerate(bands):
        a = x - hw - nsig * sigma[i]
        b = x + hw + nsig * sigma[i]
        raw.append((a, b))

    # Sort and merge
    raw.sort()
    merged = [list(raw[0])]
    for a, b in raw[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])

    # Clip to fiducial range and sum
    L = hi - lo
    total = 0.0
    clipped = []
    for a, b in merged:
        a_c = max(a, lo)
        b_c = min(b, hi)
        if b_c > a_c:
            total += b_c - a_c
            clipped.append((a_c, b_c))

    C = total / L if L > 0 else 0.0
    return min(C, 1.0), clipped


def coverage_table(bands, lo, hi, nsig_values, sigma_values):
    """Compute C_veto for a grid of (n_sigma, sigma) values.

    Returns
    -------
    table : list of (nsig, sigma, C_veto) tuples
    """
    table = []
    for nsig in nsig_values:
        for sigma in sigma_values:
            C, _ = coverage_ratio(bands, lo, hi, nsig, sigma)
            table.append((nsig, sigma, C))
    return table


# Convenience functions for barrel and endcap
def barrel_coverage(nsig, sigma):
    """Barrel coverage using v2.1 band definitions."""
    from mtag_v21 import BANDS, R_LO, R_HI
    return coverage_ratio(BANDS, R_LO, R_HI, nsig, sigma)


def endcap_coverage(nsig, sigma):
    """Endcap coverage using v2.2 disk definitions."""
    from mtag_v22 import DISKS, Z_LO, Z_HI
    return coverage_ratio(DISKS, Z_LO, Z_HI, nsig, sigma)


if __name__ == '__main__':
    from mtag_v21 import BANDS, R_LO, R_HI
    from mtag_v22 import DISKS, Z_LO, Z_HI

    print('=== Barrel coverage (14 bands, R = 0.5–800 mm) ===')
    for nsig in [2.0, 3.0, 4.0]:
        for sigma in [1.0, 3.0]:
            C, intervals = coverage_ratio(BANDS, R_LO, R_HI, nsig, sigma)
            print(f'  n_sigma={nsig:.0f}, sigma_r={sigma:.0f} mm: C = {C:.4f} ({C*100:.1f}%), {len(intervals)} merged intervals')

    print()
    print('=== Endcap coverage (9 disks, z = 200–2500 mm) ===')
    for nsig in [2.0, 3.0, 4.0]:
        for sigma in [1.0, 3.0]:
            C, intervals = coverage_ratio(DISKS, Z_LO, Z_HI, nsig, sigma)
            print(f'  n_sigma={nsig:.0f}, sigma_z={sigma:.0f} mm: C = {C:.4f} ({C*100:.1f}%), {len(intervals)} merged intervals')

    print()
    print('=== Validation V3: material fraction (n_sigma=0, sigma->0) ===')
    C_barrel, _ = coverage_ratio(BANDS, R_LO, R_HI, 0.0, 0.001)
    C_endcap, _ = coverage_ratio(DISKS, Z_LO, Z_HI, 0.0, 0.001)
    hw_barrel = sum(2 * hw for _, _, hw in BANDS)
    hw_endcap = sum(2 * hw for _, _, hw in DISKS)
    print(f'  Barrel: C = {C_barrel:.4f}, analytic = {hw_barrel / (R_HI - R_LO):.4f}')
    print(f'  Endcap: C = {C_endcap:.4f}, analytic = {hw_endcap / (Z_HI - Z_LO):.4f}')
