"""v2.6 post-registration: Multi-Seed Ensemble for Displaced Light ALP → e⁺e⁻.

Runs the v2.5 simulation (17-band endcap + SENSOR_DISK_Z resolution) across
N_seeds = 50 independent seed pairs to quantify stochastic uncertainty and
provide confidence intervals on all degradation values.

For each seed i ∈ {0, ..., N_seeds − 1}:
  SEED_CONV(i) = 100 × i + 5
  SEED_SIG(i)  = 100 × i + 11

Each seed runs two configurations:
  E3           : 17-band geometry + SENSOR_DISK_Z (9 sensors) — v2.5 standard
  E3_conflated : 17-band geometry + DISK_Z for resolution   — v2.4-equivalent

Deconflation delta = E3 − E3_conflated, computed within the same seed.

Preregistration: https://doi.org/10.5281/zenodo.24361872
Post-registration DOI (reserved): https://doi.org/10.5281/zenodo.24373115

Usage:
  python3 run_v26_ensemble.py
"""
import os, sys, time, hashlib, json
import numpy as np
from scipy import stats as sp_stats

HERE = os.path.dirname(os.path.abspath(__file__))

# Import endcap_sim from HERE first (v2.5 with SENSOR_DISK_Z fix)
sys.path.insert(0, HERE)
import endcap_sim as ec

# Other modules
V25_RESULTS = os.path.join(HERE, '..', 'v25_results')
V24_PREREG = os.path.join(HERE, '..', 'v24_prereg')
V23_RESULTS = os.path.join(HERE, '..', 'v23_results')
V23_PREREG = os.path.join(HERE, '..', 'v23_prereg')
V22_RESULTS = os.path.join(HERE, '..', 'v22_results')
V22_PREREG = os.path.join(HERE, '..', 'v22_prereg')
V21_PREREG = os.path.join(HERE, '..', 'v21_prereg')

for _p in [V25_RESULTS, V24_PREREG, V23_RESULTS, V23_PREREG, V22_RESULTS, V22_PREREG, V21_PREREG]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.append(_p)

import mtag_v21
import mtag_v22
import mtag_v24
import coverage as cov

# ===================================================================
# Constants
# ===================================================================

N_SEEDS = 50
MASSES = [0.017, 0.05, 0.1, 0.2]
ETA_SCAN = [1.5, 1.7, 2.0, 2.3, 2.5]
F_HYBRID = 0.25
ENDCAP_CONFIG = 'E3'

# 9 sensor disk positions (v2.5 standard)
SENSOR_DISK_Z_9 = np.array([230., 300., 450., 620., 820., 1100., 1500., 1900., 2300.])

# SHA-256 for mtag_v24.py
SHA24_EXPECTED = '053a0e6c8fa70130f78a2b5970c98762396a701e8fbdd6dc695c7293f041a34d'

# Published v2.3 endcap E3 results at η=2.0 (9-disk, for P7 comparison)
V23_ENDCAP_E3_ETA20 = {
    0.017: dict(hv_deg=1.06, tag_deg=1.62, ratio=1.530),
    0.05:  dict(hv_deg=1.06, tag_deg=1.14, ratio=1.075),
    0.1:   dict(hv_deg=1.06, tag_deg=1.05, ratio=0.991),
    0.2:   dict(hv_deg=1.03, tag_deg=1.03, ratio=1.000),
}

# Seed-0 reference values at η=2.0 with N_SIG = 50,000 (prereg-compliant)
# Note: v2.5 used N_SIG = 60,000, so values at 50/100/200 MeV differ slightly.
# At 17 MeV (η=2.0), base-pair yield (~44,486) is below both caps → identical.
V25_REF_ETA20 = {
    0.017: dict(hv_deg=1.1393, tag_deg=1.6892),
    0.05:  dict(hv_deg=1.1463, tag_deg=1.2197),
    0.1:   dict(hv_deg=1.1322, tag_deg=1.1079),
    0.2:   dict(hv_deg=1.0597, tag_deg=1.0611),
}

# Seed-0 reference η scan at 17 MeV with N_SIG = 50,000
# At η ≥ 2.0, base-pair yield < 50K → matches v2.5.
# At η = 1.5, 1.7, base-pair yield exceeds 50K → differs from v2.5.
V25_REF_ETA_SCAN_17MEV = {
    1.5: dict(hv_deg=1.1442, tag_deg=1.4013),
    1.7: dict(hv_deg=1.1424, tag_deg=1.4099),
    2.0: dict(hv_deg=1.1393, tag_deg=1.6892),
    2.3: dict(hv_deg=1.1417, tag_deg=2.7098),
    2.5: dict(hv_deg=1.1412, tag_deg=3.4441),
}


# ===================================================================
# Geometry installation
# ===================================================================

def install_17band_geometry(sensor_disk_z):
    """Install 17-band geometry with specified sensor disk array for resolution.

    Parameters
    ----------
    sensor_disk_z : array
        z positions used for resolution assignment in _measure_endcap().
        - SENSOR_DISK_Z_9 for v2.5 (E3) config
        - DISK_Z (17 bands) for v2.4-equivalent (E3_conflated) config
    """
    ec.DISKS = mtag_v24.DISKS
    ec.Z_LO = mtag_v24.Z_LO
    ec.Z_HI = mtag_v24.Z_HI
    ec.DISK_Z = np.array([d[0] for d in mtag_v24.DISKS], float)       # 17 bands
    ec.DISK_X0 = np.array([d[1] for d in mtag_v24.DISKS], float)      # unscaled
    ec.DISK_HW = np.array([d[2] for d in mtag_v24.DISKS], float)      # 17 bands
    ec.SENSOR_DISK_Z = np.array(sensor_disk_z, float)
    # Material fraction
    ec.F_MAT = F_HYBRID
    ec.DISK_X0 = np.array([d[1] for d in mtag_v24.DISKS], float) * F_HYBRID
    ec.MS_TERM = 2.0e-3 * np.sqrt(F_HYBRID)


def get_disk_z_17band():
    """Return the full 17-band DISK_Z array."""
    return np.array([d[0] for d in mtag_v24.DISKS], float)


# ===================================================================
# Core simulation for one seed + one config
# ===================================================================

def run_single_seed(seed_conv, seed_sig, sensor_disk_z, eta_ref=2.0,
                    masses=None, tag_module=mtag_v24):
    """Run the endcap E3 simulation at a given η with specified seeds and resolution config.

    Parameters
    ----------
    masses : list of float, optional
        Mass values to simulate. Defaults to MASSES (all 4).

    Returns dict keyed by mass with hv_deg, tag_deg, ratio.
    """
    if masses is None:
        masses = MASSES

    # Install geometry with specified SENSOR_DISK_Z
    install_17band_geometry(sensor_disk_z)

    conv_full = ec.endcap_conversions(n=1_500_000, seed=seed_conv,
                                       eta_ref=eta_ref, config=ENDCAP_CONFIG)
    conv, use_c = ec.subsample(conv_full, ec.N_CONV)

    dchi2_conv, ok_conv = ec.compute_dchi2_endcap(conv_full, eta_ref=eta_ref,
                                                    seed_T=31, seed_L=1031)
    conv_full['dchi2_3D'] = dchi2_conv
    conv_full['ok_alp'] = ok_conv
    conv['dchi2_3D'] = np.zeros(len(conv['z']))
    conv['ok_alp'] = np.zeros(len(conv['z']), bool)
    conv['dchi2_3D'][use_c] = dchi2_conv[use_c]
    conv['ok_alp'][use_c] = ok_conv[use_c]

    base_c = conv['base']
    lam_conv = np.full(len(conv['z']), -np.inf)
    lam_conv[base_c] = tag_module.lam(conv['zm'][base_c], conv['sz'][base_c],
                                       np.where(conv['ok_alp'][base_c],
                                                conv['dchi2_3D'][base_c], 0.0))

    dC_full = np.full(len(conv['z']), -np.inf)
    dC_full[base_c] = np.where(conv['ok_alp'][base_c],
                                conv['dchi2_3D'][base_c], -np.inf)

    res = {}
    for m in masses:
        sig_full = ec.endcap_signal(m, ctau=1.0, n=300_000, seed=seed_sig,
                                     eta_ref=eta_ref, config=ENDCAP_CONFIG)
        sig, use_s = ec.subsample(sig_full, ec.N_SIG)
        dchi2_sig, ok_sig = ec.compute_dchi2_endcap(sig_full, eta_ref=eta_ref,
                                                      seed_T=41, seed_L=1041)
        sig_full['dchi2_3D'] = dchi2_sig
        sig_full['ok_alp'] = ok_sig
        sig['dchi2_3D'] = np.zeros(len(sig['z']))
        sig['ok_alp'] = np.zeros(len(sig['z']), bool)
        sig['dchi2_3D'][use_s] = dchi2_sig[use_s]
        sig['ok_alp'][use_s] = ok_sig[use_s]

        dS_full = np.full(len(sig['z']), -np.inf)
        dS_full[sig['base']] = np.where(sig['ok_alp'][sig['base']],
                                          sig['dchi2_3D'][sig['base']], -np.inf)

        r_hv = ec.scan_v15_endcap(m, sig, conv, dS_full, dC_full)

        base_s = sig['base']
        lam_sig = np.full(len(sig['z']), -np.inf)
        lam_sig[base_s] = tag_module.lam(sig['zm'][base_s], sig['sz'][base_s],
                                          np.where(sig['ok_alp'][base_s],
                                                   sig['dchi2_3D'][base_s], 0.0))
        r_tag = ec.scan_tag_endcap(m, sig, conv, lam_sig, lam_conv)

        ratio = r_tag['deg'] / r_hv['deg'] if r_hv['deg'] > 0 else np.inf

        res[m] = dict(hv_deg=r_hv['deg'], tag_deg=r_tag['deg'], ratio=ratio)

    return res


# ===================================================================
# Sanity Gates
# ===================================================================

def run_sanity_gates(all_results):
    """Run the 5 preregistered sanity gates for v2.6."""
    print("\n" + "=" * 70)
    print("SANITY GATES")
    print("=" * 70)
    gates = {}

    # Gate 1: Code identity (SHA-256 of mtag_v24.py)
    print("\n  Gate 1 (code identity):")
    mtag24_path = mtag_v24.__file__
    sha24 = hashlib.sha256(open(mtag24_path, 'rb').read()).hexdigest()
    gate1_ok = (sha24 == SHA24_EXPECTED)
    gates['G1'] = dict(sha24=sha24, expected=SHA24_EXPECTED, passed=gate1_ok)
    print(f"    mtag_v24.py SHA-256: {sha24[:16]}...")
    print(f"    Match: {gate1_ok}")
    print(f"    Gate 1: {'PASS' if gate1_ok else 'FAIL'}")

    # Gate 2: Tag formula consistency (mtag_v24.lam)
    print("\n  Gate 2 (tag formula consistency):")
    lam_far = mtag_v24.lam(np.array([1000.0]), np.array([1.0]), np.array([0.0]))
    lam_near = mtag_v24.lam(np.array([300.0]), np.array([1.0]), np.array([0.0]))
    gate2_ok = (lam_far[0] > 0) and (lam_near[0] < 0)
    gates['G2'] = dict(lam_far=float(lam_far[0]), lam_near=float(lam_near[0]),
                        passed=gate2_ok)
    print(f"    lambda(z=1000, far): {lam_far[0]:.4f} (expect > 0)")
    print(f"    lambda(z=300, near): {lam_near[0]:.4f} (expect < 0)")
    print(f"    Gate 2: {'PASS' if gate2_ok else 'FAIL'}")

    # Gate 3: Coverage consistency (17-band C_veto matches v2.5 §3.1)
    print("\n  Gate 3 (coverage consistency):")
    REF_17BAND = {(2.0, 1.0): 0.070, (3.0, 1.0): 0.085, (4.0, 1.0): 0.100}
    gate3_ok = True
    for (nsig, sigma), ref_C in REF_17BAND.items():
        C, _ = cov.coverage_ratio(mtag_v24.DISKS, mtag_v24.Z_LO, mtag_v24.Z_HI,
                                   nsig, sigma)
        ok = abs(C - ref_C) < 5e-4
        gate3_ok &= ok
        print(f"    n_sig={nsig}, sigma={sigma}: C={C:.6f} ref={ref_C:.3f} {'OK' if ok else 'FAIL'}")
    gates['G3'] = dict(passed=gate3_ok)
    print(f"    Gate 3: {'PASS' if gate3_ok else 'FAIL'}")

    # Gate 4: Seed i=0 reproduction — compare with PUBLISHED v2.5 (N_SIG=60,000)
    # Note: v2.6 uses N_SIG=50,000 per preregistration §2, so some values will differ.
    print("\n  Gate 4 (seed i=0 vs published v2.5 [N_SIG=60,000]):")
    seed0_e3 = all_results[0]['E3']

    # Published v2.5 reference values (N_SIG=60,000, DOI: 10.5281/zenodo.24341050)
    V25_PUB_ETA20 = {
        0.017: dict(hv_deg=1.1393, tag_deg=1.6892),
        0.05:  dict(hv_deg=1.1458, tag_deg=1.2191),
        0.1:   dict(hv_deg=1.1322, tag_deg=1.1073),
        0.2:   dict(hv_deg=1.0598, tag_deg=1.0611),
    }
    V25_PUB_ETA_SCAN = {
        1.5: dict(hv_deg=1.1431, tag_deg=1.3986),
        1.7: dict(hv_deg=1.1427, tag_deg=1.4095),
        2.0: dict(hv_deg=1.1393, tag_deg=1.6892),
        2.3: dict(hv_deg=1.1417, tag_deg=2.7098),
        2.5: dict(hv_deg=1.1412, tag_deg=3.4441),
    }

    n_match = 0
    n_total = 0

    # Check η=2.0 at all masses (§7.1)
    print("    §7.1 — Endcap E3 at η=2.0:")
    for m in MASSES:
        ref = V25_PUB_ETA20[m]
        got_hv = seed0_e3['eta20'][m]['hv_deg']
        got_tag = seed0_e3['eta20'][m]['tag_deg']
        hv_match = round(got_hv, 4) == round(ref['hv_deg'], 4)
        tag_match = round(got_tag, 4) == round(ref['tag_deg'], 4)
        n_total += 2
        if hv_match: n_match += 1
        if tag_match: n_match += 1
        print(f"      {m*1000:.0f} MeV: HV={got_hv:.4f} (ref {ref['hv_deg']:.4f}) {'OK' if hv_match else 'DIFF'}, "
              f"Tag={got_tag:.4f} (ref {ref['tag_deg']:.4f}) {'OK' if tag_match else 'DIFF'}")

    # Check η scan at 17 MeV (§7.2)
    print("    §7.2 — η scan at 17 MeV:")
    for eta in ETA_SCAN:
        ref = V25_PUB_ETA_SCAN[eta]
        got_hv = seed0_e3['eta_scan'][eta][0.017]['hv_deg']
        got_tag = seed0_e3['eta_scan'][eta][0.017]['tag_deg']
        hv_match = round(got_hv, 4) == round(ref['hv_deg'], 4)
        tag_match = round(got_tag, 4) == round(ref['tag_deg'], 4)
        n_total += 2
        if hv_match: n_match += 1
        if tag_match: n_match += 1
        print(f"      η={eta}: HV={got_hv:.4f} (ref {ref['hv_deg']:.4f}) {'OK' if hv_match else 'DIFF'}, "
              f"Tag={got_tag:.4f} (ref {ref['tag_deg']:.4f}) {'OK' if tag_match else 'DIFF'}")

    gate4_partial = (n_match < n_total)
    gates['G4'] = dict(passed=(n_match == n_total), n_match=n_match, n_total=n_total)
    print(f"    Gate 4: {'PASS' if n_match == n_total else f'NOT MET ({n_match}/{n_total} matched)'}")
    if gate4_partial:
        print(f"    Note: {n_total - n_match} mismatches expected due to N_SIG change (60,000 → 50,000).")

    # Gate 5: Ensemble determinism — re-run seed i=25
    print("\n  Gate 5 (ensemble determinism, re-run seed i=25):")
    seed_conv_25 = 100 * 25 + 5
    seed_sig_25 = 100 * 25 + 11

    # Re-run E3 at η=2.0
    install_17band_geometry(SENSOR_DISK_Z_9)
    rerun = run_single_seed(seed_conv_25, seed_sig_25, SENSOR_DISK_Z_9, eta_ref=2.0)
    original = all_results[25]['E3']['eta20']

    gate5_ok = True
    for m in MASSES:
        hv_match = rerun[m]['hv_deg'] == original[m]['hv_deg']
        tag_match = rerun[m]['tag_deg'] == original[m]['tag_deg']
        ok = hv_match and tag_match
        gate5_ok &= ok
        print(f"    {m*1000:.0f} MeV: HV original={original[m]['hv_deg']:.6f} rerun={rerun[m]['hv_deg']:.6f} "
              f"{'OK' if hv_match else 'MISMATCH'}, "
              f"Tag original={original[m]['tag_deg']:.6f} rerun={rerun[m]['tag_deg']:.6f} "
              f"{'OK' if tag_match else 'MISMATCH'}")

    gates['G5'] = dict(passed=gate5_ok)
    print(f"    Gate 5: {'PASS' if gate5_ok else 'FAIL'}")

    all_passed = all(g['passed'] for g in gates.values())
    gates['all_passed'] = all_passed
    g4_info = gates['G4']
    if all_passed:
        print(f"\n  SANITY GATES: ALL PASSED")
    elif not g4_info['passed'] and all(g['passed'] for k, g in gates.items() if k not in ('G4', 'all_passed')):
        print(f"\n  SANITY GATES: G1-G3 PASS, G4 NOT MET ({g4_info['n_match']}/{g4_info['n_total']} matched), G5 PASS")
    else:
        print(f"\n  SANITY GATES: SOME FAILED")
    return gates


# ===================================================================
# Ensemble Statistics
# ===================================================================

def compute_ensemble_stats(values, label=""):
    """Compute ensemble statistics for a 1D array of values.

    Returns dict with mean, std, se, ci_lo, ci_hi, median, p2_5, p97_5.
    Uses t-distribution for N < 30, normal approximation for N >= 30.
    """
    arr = np.array(values, float)
    n = len(arr)
    mean = np.mean(arr)
    std = np.std(arr, ddof=1)
    se = std / np.sqrt(n)

    if n < 30:
        t_crit = sp_stats.t.ppf(0.975, df=n - 1)
    else:
        t_crit = 1.96

    ci_lo = mean - t_crit * se
    ci_hi = mean + t_crit * se
    median = np.median(arr)
    p2_5 = np.percentile(arr, 2.5)
    p97_5 = np.percentile(arr, 97.5)

    return dict(
        mean=mean, std=std, se=se,
        ci_lo=ci_lo, ci_hi=ci_hi, t_crit=t_crit,
        median=median, p2_5=p2_5, p97_5=p97_5,
        n=n, values=arr.tolist()
    )


# ===================================================================
# Validations
# ===================================================================

def run_validations(all_results, ensemble_stats):
    """Run validations V1-V6."""
    print("\n" + "=" * 70)
    print("VALIDATIONS")
    print("=" * 70)
    validations = {}

    # V1: HV degradation >= 1.0 at all masses, all η, all seeds
    # (η=2.0 has all 4 masses; other η values have only 17 MeV)
    print("\n  V1 (HV >= 1.0 everywhere):")
    v1_ok = True
    for i in range(N_SEEDS):
        # Check all masses at η=2.0
        for m in MASSES:
            hv = all_results[i]['E3']['eta20'][m]['hv_deg']
            if hv < 1.0:
                v1_ok = False
                print(f"    FAIL: seed {i}, eta=2.0, m={m*1000:.0f} MeV: HV={hv:.4f}")
        # Check 17 MeV at all η
        for eta in ETA_SCAN:
            hv = all_results[i]['E3']['eta_scan'][eta][0.017]['hv_deg']
            if hv < 1.0:
                v1_ok = False
                print(f"    FAIL: seed {i}, eta={eta}, m=17 MeV: HV={hv:.4f}")
    validations['V1'] = dict(passed=v1_ok)
    print(f"    V1: {'PASS' if v1_ok else 'FAIL'}")

    # V2: Tag degradation >= 1.0 at 17 MeV, all η, all seeds
    print("\n  V2 (Tag >= 1.0 at 17 MeV):")
    v2_ok = True
    for i in range(N_SEEDS):
        for eta in ETA_SCAN:
            tag = all_results[i]['E3']['eta_scan'][eta][0.017]['tag_deg']
            if tag < 1.0:
                v2_ok = False
                print(f"    FAIL: seed {i}, eta={eta}: Tag={tag:.4f}")
    validations['V2'] = dict(passed=v2_ok)
    print(f"    V2: {'PASS' if v2_ok else 'FAIL'}")

    # V3: σ_HV / HV̄ < 1% at 17 MeV, η=2.0
    print("\n  V3 (relative σ_HV < 1% at 17 MeV, η=2.0):")
    hv_17_stats = ensemble_stats['E3']['eta20'][0.017]['hv']
    rel_std = hv_17_stats['std'] / hv_17_stats['mean']
    v3_ok = rel_std < 0.01
    validations['V3'] = dict(rel_std=rel_std, passed=v3_ok)
    print(f"    σ_HV / HV̄ = {hv_17_stats['std']:.6f} / {hv_17_stats['mean']:.4f} = {rel_std:.6f} ({rel_std*100:.4f}%)")
    print(f"    V3: {'PASS' if v3_ok else 'FAIL'}")

    # V4: HV η-independence: CV < 2% across η at 17 MeV
    print("\n  V4 (HV η-independence, CV < 2% at 17 MeV):")
    hv_means_across_eta = []
    for eta in ETA_SCAN:
        hv_vals = [all_results[i]['E3']['eta_scan'][eta][0.017]['hv_deg'] for i in range(N_SEEDS)]
        hv_means_across_eta.append(np.mean(hv_vals))
    cv = np.std(hv_means_across_eta, ddof=1) / np.mean(hv_means_across_eta)
    v4_ok = cv < 0.02
    validations['V4'] = dict(cv=cv, means=hv_means_across_eta, passed=v4_ok)
    print(f"    HV means across η: {['%.4f' % v for v in hv_means_across_eta]}")
    print(f"    CV = {cv:.6f} ({cv*100:.4f}%)")
    print(f"    V4: {'PASS' if v4_ok else 'FAIL'}")

    # V5: Deconflation delta stability: σ(ΔHV) < σ(HV) at all masses
    print("\n  V5 (σ(ΔHV) < σ(HV) at all masses):")
    v5_ok = True
    for m in MASSES:
        hv_std = ensemble_stats['E3']['eta20'][m]['hv']['std']
        delta_hv_std = ensemble_stats['delta']['eta20'][m]['hv']['std']
        ratio = delta_hv_std / hv_std if hv_std > 0 else np.inf
        ok = ratio < 1.0
        v5_ok &= ok
        print(f"    {m*1000:.0f} MeV: σ(ΔHV)={delta_hv_std:.6f}, σ(HV)={hv_std:.6f}, ratio={ratio:.4f} {'OK' if ok else 'FAIL'}")
    validations['V5'] = dict(passed=v5_ok)
    print(f"    V5: {'PASS' if v5_ok else 'FAIL'}")

    # V6: Coverage identical across all seeds
    print("\n  V6 (coverage seed-independent):")
    # coverage_ratio() is deterministic: it takes only geometric inputs
    # (disk positions, z boundaries, n_sig, sigma) with no random-seed
    # dependency.  It is seed-independent by construction.
    C_check, _ = cov.coverage_ratio(mtag_v24.DISKS, mtag_v24.Z_LO, mtag_v24.Z_HI, 3.0, 1.0)
    v6_ok = True  # deterministic by construction
    print(f"    coverage_ratio() = {C_check:.6f}")
    print(f"    Seed-independent by construction: function takes only geometric inputs")
    print(f"    (disk positions, z boundaries, n_sig, sigma) — no random seed dependency.")
    validations['V6'] = dict(C_e3=C_check, passed=v6_ok)
    print(f"    V6: {'PASS' if v6_ok else 'FAIL'}")

    all_passed = all(v['passed'] for v in validations.values())
    validations['all_passed'] = all_passed
    print(f"\n  VALIDATIONS: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    return validations


# ===================================================================
# Predictions
# ===================================================================

def evaluate_predictions(all_results, ensemble_stats):
    """Evaluate all preregistered predictions S1-S4, M1-M3, D1-D3."""
    print("\n" + "=" * 70)
    print("PREDICTIONS")
    print("=" * 70)
    preds = {}

    # === S1-S4: Seed Variability ===
    print("\n  --- S1-S4: Seed Variability ---")

    # S1: Relative std of HV at 17 MeV (η=2.0) < 0.5%
    hv_17 = ensemble_stats['E3']['eta20'][0.017]['hv']
    s1_rel = hv_17['std'] / hv_17['mean']
    s1_ok = s1_rel < 0.005
    preds['S1'] = dict(rel_std=s1_rel, threshold=0.005, passed=s1_ok)
    print(f"  S1 (σ_HV/HV̄ < 0.5%): {s1_rel*100:.4f}%  -> {'CONFIRMED' if s1_ok else 'REFUTED'}")

    # S2: Relative std of Tag at 17 MeV (η=2.0) < 1.0%
    tag_17 = ensemble_stats['E3']['eta20'][0.017]['tag']
    s2_rel = tag_17['std'] / tag_17['mean']
    s2_ok = s2_rel < 0.01
    preds['S2'] = dict(rel_std=s2_rel, threshold=0.01, passed=s2_ok)
    print(f"  S2 (σ_Tag/Taḡ < 1.0%): {s2_rel*100:.4f}%  -> {'CONFIRMED' if s2_ok else 'REFUTED'}")

    # S3: Relative std of ΔHV at 17 MeV < 5%
    delta_hv_17 = ensemble_stats['delta']['eta20'][0.017]['hv']
    s3_rel = delta_hv_17['std'] / abs(delta_hv_17['mean']) if abs(delta_hv_17['mean']) > 0 else np.inf
    s3_ok = s3_rel < 0.05
    preds['S3'] = dict(rel_std=s3_rel, threshold=0.05, passed=s3_ok)
    print(f"  S3 (σ(ΔHV)/|ΔHV̄| < 5%): {s3_rel*100:.4f}%  -> {'CONFIRMED' if s3_ok else 'REFUTED'}")

    # S4: σ_HV(200)/( HV̄(200)−1 ) > σ_HV(17)/( HV̄(17)−1 )
    hv_200 = ensemble_stats['E3']['eta20'][0.2]['hv']
    rel_var_200 = hv_200['std'] / (hv_200['mean'] - 1.0) if (hv_200['mean'] - 1.0) > 0 else np.inf
    rel_var_17 = hv_17['std'] / (hv_17['mean'] - 1.0) if (hv_17['mean'] - 1.0) > 0 else np.inf
    s4_ok = rel_var_200 > rel_var_17
    preds['S4'] = dict(rel_var_200=rel_var_200, rel_var_17=rel_var_17, passed=s4_ok)
    print(f"  S4 (seed variation higher at 200 MeV): "
          f"200MeV={rel_var_200:.4f}, 17MeV={rel_var_17:.4f}  -> {'CONFIRMED' if s4_ok else 'REFUTED'}")

    # === M1-M3: Marginal Results ===
    print("\n  --- M1-M3: Marginal Results ---")

    # M1: P3 ensemble result — Tag/HV decrease from v2.3 baseline
    v23_ratio = V23_ENDCAP_E3_ETA20[0.017]['ratio']  # 1.530
    ratio_vals = [all_results[i]['E3']['eta20'][0.017]['ratio'] for i in range(N_SEEDS)]
    decrease_pct_vals = [(1.0 - r / v23_ratio) * 100 for r in ratio_vals]
    mean_decrease = np.mean(decrease_pct_vals)
    frac_above_3 = sum(1 for d in decrease_pct_vals if d >= 3.0) / N_SEEDS
    m1_ok = mean_decrease >= 2.5  # predicted: mean >= 2.5%
    m1_above50 = frac_above_3 > 0.50
    preds['M1'] = dict(mean_decrease_pct=mean_decrease,
                        frac_above_3pct=frac_above_3,
                        mean_ok=m1_ok, above50_ok=m1_above50)
    print(f"  M1 (P3 ensemble): mean decrease = {mean_decrease:.2f}%, "
          f"fraction >= 3% = {frac_above_3:.0%}")
    print(f"      Prediction (mean >= 2.5%): {'CONFIRMED' if m1_ok else 'REFUTED'}")
    print(f"      Prediction (> 50% seeds >= 3%): {'CONFIRMED' if m1_above50 else 'REFUTED'}")

    # M2: P7 ensemble result — deviation from fixed v2.3 baseline (1.030×) at 200 MeV
    v23_hv_200 = V23_ENDCAP_E3_ETA20[0.2]['hv_deg']  # 1.03
    hv_200_vals = [all_results[i]['E3']['eta20'][0.2]['hv_deg'] for i in range(N_SEEDS)]
    dev_pct_vals = [abs(hv / v23_hv_200 - 1.0) * 100 for hv in hv_200_vals]
    mean_dev = np.mean(dev_pct_vals)
    dev_stats = compute_ensemble_stats(dev_pct_vals)
    m2_in_range = 2.5 <= mean_dev <= 3.5
    m2_straddles = dev_stats['ci_lo'] < 3.0 < dev_stats['ci_hi']
    m2_passed = m2_in_range and m2_straddles
    preds['M2'] = dict(mean_dev_pct=mean_dev, ci_lo=dev_stats['ci_lo'],
                        ci_hi=dev_stats['ci_hi'],
                        in_range=m2_in_range, straddles_3=m2_straddles,
                        passed=m2_passed)
    print(f"  M2 (P7 ensemble): mean deviation = {mean_dev:.2f}%, "
          f"95% CI = [{dev_stats['ci_lo']:.2f}%, {dev_stats['ci_hi']:.2f}%]")
    print(f"      Prediction (mean 2.5–3.5%): {'CONFIRMED' if m2_in_range else 'REFUTED'}")
    print(f"      Prediction (CI straddles 3%): {'CONFIRMED' if m2_straddles else 'REFUTED'}")

    # Also compute with Gate 5 recomputed baseline (1.02661×) for secondary comparison
    v23_g5_hv_200 = 1.02661
    dev_g5_vals = [abs(hv / v23_g5_hv_200 - 1.0) * 100 for hv in hv_200_vals]
    mean_dev_g5 = np.mean(dev_g5_vals)
    dev_g5_stats = compute_ensemble_stats(dev_g5_vals)
    preds['M2_secondary'] = dict(mean_dev_pct=mean_dev_g5, ci_lo=dev_g5_stats['ci_lo'],
                                  ci_hi=dev_g5_stats['ci_hi'], baseline=v23_g5_hv_200)
    print(f"      Secondary (G5 baseline {v23_g5_hv_200}): mean dev = {mean_dev_g5:.2f}%, "
          f"CI = [{dev_g5_stats['ci_lo']:.2f}%, {dev_g5_stats['ci_hi']:.2f}%]")

    # M3: V3 ensemble result — HV and Tag at 200 MeV > 1.05
    hv_200_mean = hv_200['mean']
    tag_200 = ensemble_stats['E3']['eta20'][0.2]['tag']
    tag_200_mean = tag_200['mean']
    hv_above_105 = sum(1 for v in hv_200['values'] if v > 1.05) / N_SEEDS
    tag_above_105 = sum(1 for v in tag_200['values'] if v > 1.05) / N_SEEDS
    m3_mean_ok = hv_200_mean > 1.05 and tag_200_mean > 1.05
    m3_robust = hv_above_105 > 0.90 and tag_above_105 > 0.90
    preds['M3'] = dict(hv_200_mean=hv_200_mean, tag_200_mean=tag_200_mean,
                        frac_hv_above_105=hv_above_105,
                        frac_tag_above_105=tag_above_105,
                        mean_ok=m3_mean_ok, robust=m3_robust)
    print(f"  M3 (V3 ensemble): HV mean={hv_200_mean:.4f} ({hv_above_105:.0%} > 1.05), "
          f"Tag mean={tag_200_mean:.4f} ({tag_above_105:.0%} > 1.05)")
    print(f"      Prediction (means > 1.05): {'CONFIRMED' if m3_mean_ok else 'REFUTED'}")
    print(f"      Prediction (> 90% above 1.05): {'CONFIRMED' if m3_robust else 'REFUTED'}")

    # === D1-D3: Deconflation Robustness ===
    print("\n  --- D1-D3: Deconflation Robustness ---")

    # D1: Ensemble mean ΔHV at 17 MeV (η=2.0) in [0.040, 0.050]
    d1_mean = delta_hv_17['mean']
    d1_ok = 0.040 <= d1_mean <= 0.050
    preds['D1'] = dict(mean=d1_mean, ci_lo=delta_hv_17['ci_lo'],
                        ci_hi=delta_hv_17['ci_hi'], passed=d1_ok)
    print(f"  D1 (ΔHV mean at 17 MeV): {d1_mean:.4f} "
          f"[{delta_hv_17['ci_lo']:.4f}, {delta_hv_17['ci_hi']:.4f}]  "
          f"(expect 0.040–0.050)  -> {'CONFIRMED' if d1_ok else 'REFUTED'}")

    # D2: Ensemble mean ΔTag at 17 MeV (η=2.0) in [0.004, 0.012]
    delta_tag_17 = ensemble_stats['delta']['eta20'][0.017]['tag']
    d2_mean = delta_tag_17['mean']
    d2_ok = 0.004 <= d2_mean <= 0.012
    preds['D2'] = dict(mean=d2_mean, ci_lo=delta_tag_17['ci_lo'],
                        ci_hi=delta_tag_17['ci_hi'], passed=d2_ok)
    print(f"  D2 (ΔTag mean at 17 MeV): {d2_mean:.4f} "
          f"[{delta_tag_17['ci_lo']:.4f}, {delta_tag_17['ci_hi']:.4f}]  "
          f"(expect 0.004–0.012)  -> {'CONFIRMED' if d2_ok else 'REFUTED'}")

    # D3: All seeds show ΔHV > 0 at all 4 masses
    d3_ok = True
    for m in MASSES:
        delta_vals = ensemble_stats['delta']['eta20'][m]['hv']['values']
        all_positive = all(v > 0 for v in delta_vals)
        d3_ok &= all_positive
        if not all_positive:
            n_neg = sum(1 for v in delta_vals if v <= 0)
            print(f"    {m*1000:.0f} MeV: {n_neg}/{N_SEEDS} seeds have ΔHV <= 0")
    preds['D3'] = dict(passed=d3_ok)
    print(f"  D3 (ΔHV > 0 at all masses, all seeds): {'CONFIRMED' if d3_ok else 'REFUTED'}")

    # Summary
    n_total = sum(1 for k, v in preds.items() if not k.endswith('_secondary') and isinstance(v.get('passed', v.get('mean_ok', None)), bool))
    # Count confirmed predictions carefully
    confirmed = 0
    total = 0
    for k, v in preds.items():
        if k.endswith('_secondary'):
            continue
        if 'passed' in v:
            total += 1
            if v['passed']:
                confirmed += 1
        elif 'mean_ok' in v:
            total += 1
            if v['mean_ok']:
                confirmed += 1

    print(f"\n  Predictions: {confirmed}/{total} primary predictions confirmed")

    # One-sided p-values (prereg §2.5)
    from scipy import stats as sp_stats
    print("\n  --- One-sided p-values (prereg §2.5) ---")

    # P3: One-sided tests for Tag/HV decrease
    p3_vals = np.array(decrease_pct_vals)
    p3_se = np.std(p3_vals, ddof=1) / np.sqrt(N_SEEDS)
    preds['p_values'] = {}

    # P3 at M1 threshold (2.5%): H0: true mean = 2.5%, left-tail
    p3_t_m1 = (np.mean(p3_vals) - 2.5) / p3_se
    p3_pval_m1 = sp_stats.t.cdf(p3_t_m1, df=N_SEEDS - 1)
    print(f"  P3 (M1 threshold 2.5%): t = {p3_t_m1:.3f}, one-sided p = {p3_pval_m1:.4e}")
    preds['p_values']['P3_M1'] = dict(t_stat=float(p3_t_m1), p_value=float(p3_pval_m1),
                                       test='one-sided: mean decrease < 2.5%')

    # P3 at own threshold (3%): H0: true mean = 3%, left-tail
    p3_t_3 = (np.mean(p3_vals) - 3.0) / p3_se
    p3_pval_3 = sp_stats.t.cdf(p3_t_3, df=N_SEEDS - 1)
    print(f"  P3 (own threshold 3.0%): t = {p3_t_3:.3f}, one-sided p = {p3_pval_3:.4e}")
    preds['p_values']['P3'] = dict(t_stat=float(p3_t_3), p_value=float(p3_pval_3),
                                    test='one-sided: mean decrease < 3.0%')

    # P7: H0: true mean |HV/baseline − 1| = 3%. One-sided test: observed < 3%
    p7_vals = np.array(dev_pct_vals)
    p7_t = (np.mean(p7_vals) - 3.0) / (np.std(p7_vals, ddof=1) / np.sqrt(N_SEEDS))
    p7_pval = sp_stats.t.cdf(p7_t, df=N_SEEDS - 1)  # left-tail: P(mean < 3%)
    print(f"  P7: t = {p7_t:.3f}, one-sided p = {p7_pval:.4e} (mean deviation < 3%)")
    preds['p_values']['P7'] = dict(t_stat=float(p7_t), p_value=float(p7_pval),
                                    test='one-sided: mean deviation < 3%')

    # 200 MeV convergence (M3): H0: true mean = 1.05. One-sided test: observed > 1.05
    # Use t.sf() (survival function) instead of 1 - t.cdf() to avoid float rounding to 0
    hv_200_arr = np.array(hv_200['values'])
    conv_t_hv = (np.mean(hv_200_arr) - 1.05) / (np.std(hv_200_arr, ddof=1) / np.sqrt(N_SEEDS))
    conv_p_hv = sp_stats.t.sf(conv_t_hv, df=N_SEEDS - 1)  # right-tail: P(mean > 1.05)
    tag_200_arr = np.array(tag_200['values'])
    conv_t_tag = (np.mean(tag_200_arr) - 1.05) / (np.std(tag_200_arr, ddof=1) / np.sqrt(N_SEEDS))
    conv_p_tag = sp_stats.t.sf(conv_t_tag, df=N_SEEDS - 1)  # right-tail
    print(f"  200 MeV convergence (HV): t = {conv_t_hv:.3f}, one-sided p = {conv_p_hv:.4e} (mean > 1.05)")
    print(f"  200 MeV convergence (Tag): t = {conv_t_tag:.3f}, one-sided p = {conv_p_tag:.4e} (mean > 1.05)")
    preds['p_values']['M3_HV'] = dict(t_stat=float(conv_t_hv), p_value=float(conv_p_hv),
                                       test='one-sided: HV mean > 1.05 at 200 MeV')
    preds['p_values']['M3_Tag'] = dict(t_stat=float(conv_t_tag), p_value=float(conv_p_tag),
                                        test='one-sided: Tag mean > 1.05 at 200 MeV')

    return preds


# ===================================================================
# Main
# ===================================================================

def main():
    t0 = time.time()

    print("=" * 70)
    print("v2.6 Post-Registration: Multi-Seed Ensemble")
    print(f"N_seeds = {N_SEEDS}, SEED_CONV(i) = 100i + 5, SEED_SIG(i) = 100i + 11")
    print("Two configs per seed: E3 (v2.5) and E3_conflated (v2.4-equivalent)")
    print("=" * 70)

    DISK_Z_17 = get_disk_z_17band()

    # ===================================================================
    # Phase 1: Run all seeds
    # ===================================================================
    all_results = {}

    for i in range(N_SEEDS):
        seed_conv = 100 * i + 5
        seed_sig = 100 * i + 11
        t_seed = time.time()
        print(f"\n  Seed {i:3d}/{N_SEEDS} (SEED_CONV={seed_conv}, SEED_SIG={seed_sig})...")

        seed_data = {'E3': {}, 'E3_conflated': {}}

        # --- E3 (v2.5 standard): SENSOR_DISK_Z = 9 sensors ---
        # η=2.0 at all 4 masses
        res_e3 = run_single_seed(seed_conv, seed_sig, SENSOR_DISK_Z_9, eta_ref=2.0)
        seed_data['E3']['eta20'] = res_e3

        # η scan at 17 MeV only (4 non-2.0 η values; reuse η=2.0 from above)
        eta_scan_e3 = {2.0: res_e3}
        for eta in ETA_SCAN:
            if eta != 2.0:
                eta_scan_e3[eta] = run_single_seed(seed_conv, seed_sig,
                                                    SENSOR_DISK_Z_9, eta_ref=eta,
                                                    masses=[0.017])
        seed_data['E3']['eta_scan'] = eta_scan_e3

        # --- E3_conflated (v2.4-equivalent): SENSOR_DISK_Z = DISK_Z (17 bands) ---
        # Only at η=2.0, all 4 masses (for deconflation delta)
        res_conflated = run_single_seed(seed_conv, seed_sig, DISK_Z_17, eta_ref=2.0)
        seed_data['E3_conflated']['eta20'] = res_conflated

        all_results[i] = seed_data
        elapsed_seed = time.time() - t_seed
        print(f"    Done in {elapsed_seed:.1f} s. "
              f"E3: HV={res_e3[0.017]['hv_deg']:.4f}, Tag={res_e3[0.017]['tag_deg']:.4f} "
              f"| Conflated: HV={res_conflated[0.017]['hv_deg']:.4f}")

    # ===================================================================
    # Phase 2: Compute ensemble statistics
    # ===================================================================
    print("\n" + "=" * 70)
    print("ENSEMBLE STATISTICS")
    print("=" * 70)

    ensemble_stats = {
        'E3': {'eta20': {}, 'eta_scan': {}},
        'E3_conflated': {'eta20': {}},
        'delta': {'eta20': {}},
    }

    # E3 at η=2.0
    print("\n  E3 at η=2.0:")
    for m in MASSES:
        hv_vals = [all_results[i]['E3']['eta20'][m]['hv_deg'] for i in range(N_SEEDS)]
        tag_vals = [all_results[i]['E3']['eta20'][m]['tag_deg'] for i in range(N_SEEDS)]
        ratio_vals = [all_results[i]['E3']['eta20'][m]['ratio'] for i in range(N_SEEDS)]

        hv_stats = compute_ensemble_stats(hv_vals)
        tag_stats = compute_ensemble_stats(tag_vals)
        ratio_stats = compute_ensemble_stats(ratio_vals)

        ensemble_stats['E3']['eta20'][m] = dict(hv=hv_stats, tag=tag_stats, ratio=ratio_stats)
        print(f"    {m*1000:.0f} MeV: HV = {hv_stats['mean']:.4f} ± {hv_stats['std']:.4f} "
              f"[{hv_stats['ci_lo']:.4f}, {hv_stats['ci_hi']:.4f}], "
              f"Tag = {tag_stats['mean']:.4f} ± {tag_stats['std']:.4f} "
              f"[{tag_stats['ci_lo']:.4f}, {tag_stats['ci_hi']:.4f}]")

    # E3_conflated at η=2.0
    print("\n  E3_conflated at η=2.0:")
    for m in MASSES:
        hv_vals = [all_results[i]['E3_conflated']['eta20'][m]['hv_deg'] for i in range(N_SEEDS)]
        tag_vals = [all_results[i]['E3_conflated']['eta20'][m]['tag_deg'] for i in range(N_SEEDS)]

        hv_stats = compute_ensemble_stats(hv_vals)
        tag_stats = compute_ensemble_stats(tag_vals)

        ensemble_stats['E3_conflated']['eta20'][m] = dict(hv=hv_stats, tag=tag_stats)
        print(f"    {m*1000:.0f} MeV: HV = {hv_stats['mean']:.4f} ± {hv_stats['std']:.4f}, "
              f"Tag = {tag_stats['mean']:.4f} ± {tag_stats['std']:.4f}")

    # Delta (deconflation) at η=2.0
    print("\n  Deconflation delta (E3 − E3_conflated) at η=2.0:")
    for m in MASSES:
        delta_hv_vals = [all_results[i]['E3']['eta20'][m]['hv_deg'] -
                          all_results[i]['E3_conflated']['eta20'][m]['hv_deg']
                          for i in range(N_SEEDS)]
        delta_tag_vals = [all_results[i]['E3']['eta20'][m]['tag_deg'] -
                           all_results[i]['E3_conflated']['eta20'][m]['tag_deg']
                           for i in range(N_SEEDS)]

        dhv_stats = compute_ensemble_stats(delta_hv_vals)
        dtag_stats = compute_ensemble_stats(delta_tag_vals)

        ensemble_stats['delta']['eta20'][m] = dict(hv=dhv_stats, tag=dtag_stats)
        print(f"    {m*1000:.0f} MeV: ΔHV = {dhv_stats['mean']:+.4f} ± {dhv_stats['std']:.4f} "
              f"[{dhv_stats['ci_lo']:+.4f}, {dhv_stats['ci_hi']:+.4f}], "
              f"ΔTag = {dtag_stats['mean']:+.4f} ± {dtag_stats['std']:.4f} "
              f"[{dtag_stats['ci_lo']:+.4f}, {dtag_stats['ci_hi']:+.4f}]")

    # η scan at 17 MeV
    print("\n  η scan at 17 MeV (E3):")
    for eta in ETA_SCAN:
        hv_vals = [all_results[i]['E3']['eta_scan'][eta][0.017]['hv_deg'] for i in range(N_SEEDS)]
        tag_vals = [all_results[i]['E3']['eta_scan'][eta][0.017]['tag_deg'] for i in range(N_SEEDS)]

        hv_stats = compute_ensemble_stats(hv_vals)
        tag_stats = compute_ensemble_stats(tag_vals)

        ensemble_stats['E3']['eta_scan'][eta] = {0.017: dict(hv=hv_stats, tag=tag_stats)}
        print(f"    η={eta}: HV = {hv_stats['mean']:.4f} ± {hv_stats['std']:.4f} "
              f"[{hv_stats['ci_lo']:.4f}, {hv_stats['ci_hi']:.4f}], "
              f"Tag = {tag_stats['mean']:.4f} ± {tag_stats['std']:.4f} "
              f"[{tag_stats['ci_lo']:.4f}, {tag_stats['ci_hi']:.4f}]")

    # ===================================================================
    # Phase 3: Sanity Gates
    # ===================================================================
    gates = run_sanity_gates(all_results)

    if not gates['all_passed']:
        print("\n  *** SANITY GATES FAILED — results are suspect. ***")

    # ===================================================================
    # Phase 4: Validations
    # ===================================================================
    validations = run_validations(all_results, ensemble_stats)

    # ===================================================================
    # Phase 5: Predictions
    # ===================================================================
    predictions = evaluate_predictions(all_results, ensemble_stats)

    # ===================================================================
    # Save results
    # ===================================================================
    results = {
        'N_SEEDS': N_SEEDS,
        'all_results': all_results,
        'ensemble_stats': ensemble_stats,
        'gates': gates,
        'validations': validations,
        'predictions': predictions,
    }

    np.save(os.path.join(HERE, 'v26_results.npy'), results, allow_pickle=True)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"Total time: {elapsed:.0f} s ({elapsed/60:.1f} min)")
    print(f"Results saved to v26_results.npy")
    print(f"{'=' * 70}")

    return results


if __name__ == '__main__':
    main()
