# ALP-ttbar Toy MC v2.6 — Post-Registration Results: Multi-Seed Ensemble in Displaced Light ALP → e⁺e⁻

**Author:** Won Shik Paik (Independent Researcher, Auckland, New Zealand)
**Date:** 2026-11-20
**DOI:** https://doi.org/10.5281/zenodo.24373115
**GitHub:** https://github.com/wspaik5/ALP-ttbar-Toy-MC-v2.6-Post-Registration-Multi-Seed-Ensemble
**Preregistration:** https://doi.org/10.5281/zenodo.24361872
**Builds on:** v2.5 preregistration and results, https://doi.org/10.5281/zenodo.24329044 and https://doi.org/10.5281/zenodo.24341050; v2.4 preregistration and results, https://doi.org/10.5281/zenodo.24296796 and https://doi.org/10.5281/zenodo.24302619; v2.3 preregistration and results, https://doi.org/10.5281/zenodo.24244893 and https://doi.org/10.5281/zenodo.24273586; v2.2 preregistration and results, https://doi.org/10.5281/zenodo.24189990 and https://doi.org/10.5281/zenodo.24238224; v2.1 preregistration and results, https://doi.org/10.5281/zenodo.24063091 and https://doi.org/10.5281/zenodo.24136462; v2.0 series overview, https://doi.org/10.5281/zenodo.24056097; toy study motivated by arXiv:2610.38932 (Alimena, Niedziela et al.) [E6]
**Status:** post-registration (computation completed; preregistered protocol followed)

> **Disclaimer.** Independent personal toy study, not affiliated with the authors of arXiv:2610.38932 or arXiv:2306.08686, nor with the CMS, ATLAS, LHCb or ALICE Collaborations or the FCC study. Detector numbers are assumed; only qualitative trends and ratios are meaningful.

---

## 0. Executive Summary

The v2.6 ensemble (N_seeds = 50) reveals that the v2.5 single-seed results are broadly representative for HV degradation but substantially misleading for Tag degradation at low mass. Key findings:

1. **HV degradation is highly stable across seeds.** The relative standard deviation σ_HV / HV̄ is 0.16% at 17 MeV (η = 2.0), confirming the prediction S1 (< 0.5%). The ensemble mean (1.1396×) is close to the v2.5 single-seed value (1.1393×).

2. **Tag degradation at 17 MeV exhibits large stochastic variation.** The relative standard deviation σ_Tag / Taḡ is 7.4%, far exceeding the predicted < 1% (S2 REFUTED). The v2.5 single-seed Tag (1.6892×) lies within the ensemble distribution (mean 1.7371 ± 0.1292), but the ensemble reveals a spread from ~1.5 to ~2.1×. This stochastic sensitivity was not anticipated from the N_sig = 50,000 event count and appears to arise from the tag formula's sensitivity to the exact positions of rare vertices near material bands.

3. **P3 (Tag/HV ratio decrease ≥ 3%) is REFUTED by the ensemble.** The ensemble mean decrease is only 0.38%, with 42% of seeds exceeding the 3% threshold. The v2.5 single-seed result of −3.1% was a stochastic artefact of the specific seed pair. This is the most consequential finding: the apparent "advantage" of the v2.5 geometry in suppressing the Tag/HV ratio at 17 MeV does not survive ensemble averaging (M1 REFUTED).

4. **Deconflation deltas are robust.** ΔHV at 17 MeV = +0.0452 ± 0.0010, consistent with the predicted 0.040–0.050 range (D1 CONFIRMED). All 50 seeds show positive ΔHV at all masses (D3 CONFIRMED). However, ΔTag at 17 MeV = +0.0021, well below the predicted 0.004–0.012 range (D2 REFUTED), indicating that the deconflation's impact on the tag is negligible at the lowest mass.

5. **V5 fails at 200 MeV.** The prediction that deconflation deltas are more stable than absolute values (σ(ΔHV) < σ(HV)) holds at 17, 50, and 100 MeV but fails at 200 MeV, where σ(ΔHV)/σ(HV) = 1.08. At 200 MeV, the smaller Lorentz boost (γβ = p/m decreases with increasing mass at comparable momenta) produces a shorter mean lab-frame decay length and hence a more concentrated z-distribution, with fewer decay vertices reaching the outer sensor disks where the SENSOR_DISK_Z resolution correction matters. The deconflation effect is correspondingly smaller (ΔHV ≈ +0.020), and the cancellation of stochastic variation in the within-seed difference is incomplete.

**Overall: 6 of 10 primary predictions confirmed, 4 refuted (S2, M1, M2, D2). G1–G3 and G5 passed; G4 not met (10/18 seed-0 comparisons match published v2.5, with 8 expected mismatches from the N_SIG change). 5 of 6 validations passed (V5 partial failure at 200 MeV). The principal lesson is that Tag degradation at 17 MeV is dominated by stochastic variation, making single-seed Tag conclusions unreliable at low mass.**

**Important caveat:** this is a toy Monte Carlo with a simplified geometry; conclusions describe the behaviour of this toy model, not design directives for real hardware.

**Note on N_SIG.** The preregistration specifies N_sig = 50,000 signal events per mass point (§2, table row). The simulation code uses N_SIG = 50,000 as the subsample cap after base-pair selection, matching the preregistered value. At 17 MeV with η = 2.0 (seed 0), only ~44,486 events pass selection, so the cap is not reached. At 50, 100 and 200 MeV, more events pass selection and the cap applies. The published v2.5 results used N_SIG = 60,000, so seed-0 values in this study differ from v2.5 at mass points where the cap binds (50, 100, 200 MeV at η = 2.0, and 17 MeV at η = 1.5 and η = 1.7); see §7 for the detailed comparison.

---

## 1. Ensemble Configuration

Following the preregistration §2, the simulation swept N_seeds = 50 independent seed pairs with all other parameters held at their v2.5 values.

**Seed formula:** SEED_CONV(i) = 100 × i + 5, SEED_SIG(i) = 100 × i + 11, for i ∈ {0, ..., 49}.

**Configurations per seed:**
- **E3** (v2.5): 17-band endcap geometry with SENSOR_DISK_Z = [230, 300, 450, 620, 820, 1100, 1500, 1900, 2300] for resolution assignment
- **E3_conflated** (v2.4-equivalent): 17-band geometry with SENSOR_DISK_Z = DISK_Z (all 17 bands used for resolution), restoring the pre-v2.5 conflation

**Fixed parameters:** 17-band geometry (DISK_Z, DISK_X0, DISK_HW from v2.4), resolution threshold 50 mm, σ_z(pixel) = 1.0 mm, σ_z(strip) = 3.0 mm, material fraction f = 0.25, N_sig = 50,000 per mass point (matching preregistration §2), masses = [0.017, 0.05, 0.1, 0.2] GeV, η scan = [1.5, 1.7, 2.0, 2.3, 2.5], tag formula = mtag_v24.

**Runtime:** 1669 s (27.8 min) total. Each seed took ~30–37 s. The η scan at non-reference η values ran only the 17 MeV mass point (the reference mass for the η-dependence study), following the preregistration design.

---

## 2. Sanity Gates

| Gate | Description | Result |
|------|-------------|--------|
| G1 | Code identity: SHA-256 of mtag_v24.py = `053a0e6c8fa70130f78a2b5970c98762396a701e8fbdd6dc695c7293f041a34d` | **PASS** |
| G2 | Tag formula: λ > 0 far from bands (683.03), λ < 0 near bands (−3.34) | **PASS** |
| G3 | Coverage: n_σ=2.0 C=0.0704 (ref 0.070), n_σ=3.0 C=0.0852 (ref 0.085), n_σ=4.0 C=0.1000 (ref 0.100); all within 5 × 10⁻⁴ | **PASS** |
| G4 | Seed i = 0 reproduces published v2.5 values to 4 decimal places | **NOT MET (10/18 matched)** |
| G5 | Seed i = 25 re-run: bitwise identical at all 4 masses (HV and Tag match to 6 decimal places) | **PASS** |

**G1–G3 and G5 passed. G4 is not met (10/18 matched).** The preregistered criterion requires all 18 seed-0 values to match published v2.5 to 4 decimal places. The 8 mismatches arise from the N_SIG change: v2.5 was published with N_SIG = 60,000, while this study uses N_SIG = 50,000 (matching the preregistration §2). At mass/η points where the base-pair yield exceeds 50,000 but not 60,000 (50 and 200 MeV at η = 2.0; η = 1.5 and 1.7 at 17 MeV), the event-count cap produces different seed-0 values. Some mismatches are small (e.g. 100 MeV Tag: 1.1073 → 1.1079) while others are larger (e.g. 17 MeV η = 1.5 Tag: 1.3986 → 1.4013). At η = 2.0 / 17 MeV (yield ≈ 44,486 < 50,000) and η ≥ 2.3 at 17 MeV, seed-0 exactly reproduces v2.5. Reproducibility at N_SIG = 50,000 is separately confirmed: re-running seed-0 and seed-25 with the current code gives bitwise-identical results (G5 PASS).

---

## 3. Ensemble Results

### 3.1 Endcap E3 at η = 2.0

| Mass [MeV] | HV mean ± σ | HV 95% CI | Tag mean ± σ | Tag 95% CI |
|-------------|-------------|-----------|--------------|------------|
| 17 | 1.1396 ± 0.0018 | [1.1392, 1.1401] | 1.7371 ± 0.1292 | [1.7013, 1.7729] |
| 50 | 1.1473 ± 0.0022 | [1.1467, 1.1480] | 1.2211 ± 0.0128 | [1.2175, 1.2246] |
| 100 | 1.1186 ± 0.0076 | [1.1165, 1.1207] | 1.1104 ± 0.0030 | [1.1096, 1.1113] |
| 200 | 1.0555 ± 0.0016 | [1.0550, 1.0559] | 1.0614 ± 0.0013 | [1.0610, 1.0617] |

**Key observation:** The Tag standard deviation at 17 MeV (σ = 0.1292, relative 7.4%) is two orders of magnitude larger than the HV standard deviation (σ = 0.0018, relative 0.16%). This disparity decreases sharply with mass: at 200 MeV, σ_Tag = 0.0012 (relative 0.11%) is comparable to σ_HV = 0.0015 (relative 0.14%). The tag formula's extreme sensitivity to stochastic vertex positions at 17 MeV is the central finding of the v2.6 ensemble.

### 3.2 E3_conflated (v2.4-equivalent) at η = 2.0

| Mass [MeV] | HV mean ± σ | Tag mean ± σ |
|-------------|-------------|--------------|
| 17 | 1.0945 ± 0.0017 | 1.7350 ± 0.1295 |
| 50 | 1.0999 ± 0.0015 | 1.1712 ± 0.0144 |
| 100 | 1.0817 ± 0.0062 | 1.0709 ± 0.0028 |
| 200 | 1.0359 ± 0.0012 | 1.0381 ± 0.0010 |

### 3.3 Deconflation Deltas (E3 − E3_conflated) at η = 2.0

| Mass [MeV] | ΔHV mean ± σ | ΔHV 95% CI | ΔTag mean ± σ | ΔTag 95% CI |
|-------------|--------------|------------|---------------|-------------|
| 17 | +0.0452 ± 0.0010 | [+0.0449, +0.0454] | +0.0021 ± 0.0032 | [+0.0012, +0.0029] |
| 50 | +0.0474 ± 0.0013 | [+0.0470, +0.0478] | +0.0499 ± 0.0024 | [+0.0492, +0.0506] |
| 100 | +0.0369 ± 0.0045 | [+0.0357, +0.0382] | +0.0396 ± 0.0011 | [+0.0392, +0.0399] |
| 200 | +0.0196 ± 0.0017 | [+0.0191, +0.0201] | +0.0233 ± 0.0007 | [+0.0231, +0.0235] |

**All ΔHV values are positive** at all masses and all seeds (D3 CONFIRMED). The ΔHV values are tightly distributed (σ/|mean| = 2.2% at 17 MeV), confirming that the SENSOR_DISK_Z deconflation effect is a stable, structural shift rather than a stochastic fluctuation. Note that ΔTag is also positive on average at all masses, but at 17 MeV it is negative in 14 of 50 seeds (28%), reflecting the tag's large stochastic variation at low mass.

### 3.4 η Scan at 17 MeV (E3)

| η | HV mean ± σ | HV 95% CI | Tag mean ± σ | Tag 95% CI |
|-----|-------------|-----------|--------------|------------|
| 1.5 | 1.1423 ± 0.0020 | [1.1418, 1.1429] | 1.3824 ± 0.0284 | [1.3745, 1.3903] |
| 1.7 | 1.1411 ± 0.0016 | [1.1406, 1.1415] | 1.4237 ± 0.0266 | [1.4163, 1.4311] |
| 2.0 | 1.1396 ± 0.0018 | [1.1392, 1.1401] | 1.7371 ± 0.1292 | [1.7013, 1.7729] |
| 2.3 | 1.1381 ± 0.0021 | [1.1375, 1.1386] | 2.6136 ± 0.1032 | [2.5850, 2.6423] |
| 2.5 | 1.1374 ± 0.0025 | [1.1367, 1.1381] | 3.3221 ± 0.1205 | [3.2887, 3.3555] |

The HV degradation shows the expected mild η-dependence (CV = 0.18%, V4 PASS). Tag degradation's stochastic variation increases dramatically at forward η: from 2.0% at η = 1.5 to 7.4% at η = 2.0, then 3.9% at η = 2.3, and 3.6% at η = 2.5. The nonmonotonic behaviour reflects the interplay between the number of material bands traversed and the tag formula's sensitivity pattern.

---

## 4. Validations

| ID | Description | Result | Detail |
|----|-------------|--------|--------|
| V1 | HV ≥ 1.0 at all masses, all η, all seeds | **PASS** | No violations |
| V2 | Tag ≥ 1.0 at 17 MeV, all η, all seeds | **PASS** | No violations |
| V3 | σ_HV / HV̄ < 1% at 17 MeV, η = 2.0 | **PASS** | 0.1562% |
| V4 | HV η-independence CV < 2% at 17 MeV | **PASS** | CV = 0.1795% |
| V5 | σ(ΔHV) / σ(HV) < 1.0 at all masses | **FAIL** | PASS at 17 (0.58), 50 (0.59), 100 (0.60); FAIL at 200 (1.08) |
| V6 | Coverage identical across all seeds | **PASS** | Seed-independent by construction: coverage_ratio() takes only geometric inputs (disk positions, z boundaries, n_sig, sigma) with no random-seed dependency |

**V5 discussion.** The deconflation delta is more stable than the absolute value at 17, 50, and 100 MeV (σ-ratio 0.58–0.60), where the SENSOR_DISK_Z fix substantially changes the resolution assignment near several sensor disks. At 200 MeV, the proper decay length cτ is fixed by the code (not resampled), so the decay-vertex z-distribution is structurally identical across configurations; what changes is only the resolution assignment. The higher mass means a smaller Lorentz boost (γβ = p/m decreases with increasing mass at comparable momenta), producing a shorter mean lab-frame decay length and a more concentrated z-distribution near the interaction point, with fewer decay vertices reaching the outer regions where sensor-disk and non-sensor-disk resolutions differ. The deconflation effect is correspondingly smaller (ΔHV ≈ +0.020), and the cancellation of stochastic variation in the within-seed difference is incomplete. The V5 failure at 200 MeV reflects the reduced deconflation leverage at higher mass, not a change in lifetime.

---

## 5. Predictions

### 5.1 Seed Variability (S1–S4)

| ID | Predicted | Observed | Verdict |
|----|-----------|----------|---------|
| S1 | σ_HV / HV̄ < 0.5% | 0.16% | **CONFIRMED** |
| S2 | σ_Tag / Taḡ < 1.0% | 7.44% | **REFUTED** |
| S3 | σ(ΔHV) / \|ΔHV̄\| < 5% | 2.30% | **CONFIRMED** |
| S4 | σ_HV(200) / (HV̄(200)−1) > σ_HV(17) / (HV̄(17)−1) | 0.028 > 0.013 | **CONFIRMED** |

**S2 refutation analysis.** The Tag at 17 MeV shows 7.4% relative variation, far exceeding the predicted < 1%. The prediction assumed that with N_sig = 50,000 events, the sampling noise in the degradation ratio would be O(10⁻³). This assumption is correct for the HV strategy (which counts events passing a simple veto threshold) but fails for the tag strategy, where the p_conv convolution weights depend on the exact positions of vertices relative to material bands. We hypothesise that a small number of vertices near a band boundary may dominate the tag response, introducing a leverage effect that amplifies stochastic variation well beyond √N counting statistics. This hypothesis has not been verified by direct event-level analysis and remains a candidate explanation for the observed instability.

Note: the preregistration specified N_sig = 50,000 and the code uses N_SIG = 50,000. At 17 MeV (η = 2.0), only ~44,486 events pass base-pair selection, so the cap is not reached. The prediction assumed this sample size would suffice for Tag stability, which it does not.

### 5.2 Marginal Results (M1–M3)

| ID | Predicted | Observed | Verdict |
|----|-----------|----------|---------|
| M1 | P3 mean decrease ≥ 2.5%; > 50% seeds ≥ 3% | mean decrease = 0.38%; 42% seeds ≥ 3% | **REFUTED** |
| M2 | P7 mean deviation 2.5–3.5%; CI straddles 3% | mean = 2.47%; CI = [2.43%, 2.52%] | **REFUTED** |
| M3 | HV, Tag means > 1.05 at 200 MeV; > 90% seeds | HV mean = 1.0555 (100%), Tag mean = 1.0614 (100%) | **CONFIRMED** |

**M1 (P3) discussion.** The v2.5 single-seed Tag/HV ratio decrease of −3.1% is not confirmed by the ensemble. The ensemble mean decrease is only 0.38%, with individual seeds spanning from −18% (increase in Tag/HV) to +14% (decrease). The 3% threshold lies well within the distribution, with 42% of seeds exceeding it. The v2.5 single-seed result was a stochastic artefact: the specific seed pair (5, 11) happened to produce a Tag value (1.6892) that was below the ensemble mean (1.7371), yielding an apparently significant ratio decrease.

**M2 (P7) discussion.** The ensemble mean HV at 200 MeV (1.0555×) gives a 2.47% deviation from the v2.3 published baseline (1.030×). The 95% CI is [2.43%, 2.52%], entirely below 3%. This confirms that P7 PASSES (HV within 3% of baseline) with high confidence. The v2.5 single-seed (N_SIG = 60,000) deviation of 2.90% was above the ensemble mean due to seed-0 producing a higher 200 MeV HV at the larger sample size. With the Gate 5 recomputed baseline (1.02661×), the mean deviation is 2.81% (CI [2.77%, 2.85%]), still below 3%.

**M3 (V3) discussion.** V3 refutation is robust: 100% of seeds exceed 1.05 for both HV and Tag at 200 MeV. The ensemble means (HV = 1.0555, Tag = 1.0614) are ~0.5–1.1% above the threshold, confirming that the 200 MeV degradation meaningfully exceeds the convergence benchmark.

### 5.3 Deconflation Robustness (D1–D3)

| ID | Predicted | Observed | Verdict |
|----|-----------|----------|---------|
| D1 | ΔHV at 17 MeV: 0.040–0.050 | +0.0452 [0.0449, 0.0454] | **CONFIRMED** |
| D2 | ΔTag at 17 MeV: 0.004–0.012 | +0.0021 [0.0012, 0.0029] | **REFUTED** |
| D3 | ΔHV > 0 at all masses, all seeds | 100% confirmed | **CONFIRMED** |

**D2 refutation analysis.** The ensemble mean ΔTag at 17 MeV is +0.0021, well below the predicted 0.004–0.012 range. The v2.5 single-seed ΔTag was +0.007 (also within the predicted range). The discrepancy arises because the tag's large stochastic variation (σ ≈ 0.13) dwarfs the deconflation effect. The ΔTag is real but small: the 95% CI excludes zero [+0.0012, +0.0029], confirming a statistically significant positive shift. The deconflation primarily affects HV (via the veto boundary) rather than Tag (via the p_conv convolution) at the lowest mass.

### 5.4 One-Sided p-Values (Prereg §2.5)

As specified in the preregistration (§2.5), one-sided t-tests are reported for the marginal results:

| Test | Null Hypothesis | t-statistic | One-sided p-value | Interpretation |
|------|----------------|-------------|-------------------|----------------|
| P3 (own 3%) | True mean Tag/HV decrease ≥ 3.0% | −2.512 | 7.67 × 10⁻³ | Mean decrease (0.38%) is significantly below the P3 threshold |
| P3 (M1 2.5%) | True mean Tag/HV decrease ≥ 2.5% | −2.033 | 2.37 × 10⁻² | Also below the M1 threshold |
| P7 | True mean |HV/baseline − 1| ≥ 3% | −24.31 | 2.69 × 10⁻²⁹ | Mean deviation (2.47%) is far below 3%, confirming P7 PASS with overwhelming significance |
| M3 (HV) | True mean HV at 200 MeV ≤ 1.05 | +24.53 | 1.79 × 10⁻²⁹ | HV mean (1.0555) significantly exceeds the convergence threshold |
| M3 (Tag) | True mean Tag at 200 MeV ≤ 1.05 | +63.58 | 4.72 × 10⁻⁴⁹ | Tag mean (1.0614) significantly exceeds the convergence threshold |

All tests use Student's t-distribution with df = 49 (N_seeds − 1). P3 and P7 are left-tailed (testing whether the observed value is below threshold); M3 tests are right-tailed (computed with t.sf() to avoid float underflow).

---

## 6. Discussion

### 6.1 Tag Stochastic Sensitivity — The Principal Finding

The v2.6 ensemble's most consequential result is the revelation that Tag degradation at low ALP mass is dominated by stochastic variation, not by structural parameters. With a relative standard deviation of 7.4% at 17 MeV (compared to 0.16% for HV), single-seed Tag measurements at this mass carry negligible statistical weight for quantitative comparisons.

This sensitivity explains several puzzling features of earlier versions:
- The large Tag/HV ratio at 17 MeV reported since v2.3 (1.483–1.530) was partly a stochastic feature of the specific seed pair.
- The v2.5 "P3 marginal result" (3.1% decrease, 0.1 pp above threshold) was entirely within the stochastic noise floor.
- The apparent insensitivity of ΔTag to the deconflation at 17 MeV (D2) is not a failure of the fix but rather a masking effect: the stochastic variation is 60× larger than the systematic shift.

The physical mechanism is the tag formula's nonlinear sensitivity to vertex positions near material bands. The p_conv convolution assigns high weight to vertices near a band (where the photon conversion probability is high), and the tag likelihood λ flips sign at the band boundary. When a small number of rare, high-weight vertices shift in or out of the near-band region due to stochastic seed variation, the tag response changes substantially.

### 6.2 Implications for the Toy MC Series

The ensemble results prompt several reinterpretations:

1. **P3 is not supported.** The claimed advantage of v2.5 geometry in suppressing Tag/HV ratio at 17 MeV does not survive ensemble averaging. Future versions should not build on the P3 single-seed conclusion.

2. **P7 is robustly confirmed.** The 17-band HV degradation at 200 MeV is within 3% of the 9-disk baseline with high confidence (ensemble mean 2.47%, CI entirely below 3%).

3. **V3 refutation is robust.** The 200 MeV degradation exceeds 1.05 for both HV and Tag across the full ensemble.

4. **Deconflation is validated.** The ΔHV values are stable (σ/mean = 2.3%) and consistent with v2.5 single-seed values. The deconflation is a genuine structural effect that is not an artefact of the seed choice.

5. **Tag at 17 MeV requires larger event samples.** A future study targeting Tag precision at low mass would need to increase N_sig substantially (perhaps to 500,000 or more) or employ variance-reduction techniques.

### 6.3 Visualisation Summary

Five figures are included in this repository:

- **fig1_distribution_histograms.png** — HV and Tag distributions at η = 2.0 for all 4 masses. The HV histograms are narrow and symmetric; the Tag histograms at 17 MeV show a broad, right-skewed distribution.
- **fig2_deconflation_boxplots.png** — Box plots of ΔHV and ΔTag, with v2.5 single-seed values marked as red stars. ΔTag at 17 MeV is near zero with large IQR.
- **fig3_p3_scatter.png** — Tag/HV ratio decrease vs seed index, showing 21/50 seeds above the 3% threshold. The ensemble mean (0.38%) is far below 3%.
- **fig4_eta_band_plot.png** — Mean ± 1σ bands for HV and Tag across η at 17 MeV. HV bands are narrow; Tag bands widen dramatically from η = 1.7 onward.
- **fig5_marginal_decisions.png** — Decision plots for P3, P7, and v2.5 V3, showing ensemble distributions relative to thresholds. Note: the V3 panel shows the v2.5 convergence check (HV, Tag > 1.05 at 200 MeV); the v2.6 V3 is a separate validation (HV relative scatter < 1% at 17 MeV).

---

## 7. v2.5 Reference Comparison

### 7.1 Endcap E3 at η = 2.0: v2.5 Single-Seed vs Ensemble Mean

The v2.5 published results used N_SIG = 60,000; this study uses N_SIG = 50,000 (matching the preregistration). At 17 MeV (η = 2.0), the base-pair yield (~44,486) is below both caps, so seed-0 values are identical. At 50, 100, and 200 MeV, the cap binds and values differ between the two N_SIG settings.

| Mass [MeV] | v2.5 HV (60K) | Ensemble HV (50K) | Δ | v2.5 Tag (60K) | Ensemble Tag (50K) | Δ |
|-------------|---------------|-------------------|---|----------------|---------------------|---|
| 17 | 1.1393 | 1.1396 | +0.0003 | 1.6892 | 1.7371 | +0.0479 |
| 50 | 1.1458 | 1.1473 | +0.0015 | 1.2191 | 1.2211 | +0.0020 |
| 100 | 1.1322 | 1.1186 | −0.0136 | 1.1073 | 1.1104 | +0.0031 |
| 200 | 1.0598 | 1.0555 | −0.0043 | 1.0611 | 1.0614 | +0.0003 |

The HV shift from v2.5 single-seed to ensemble mean reflects both the N_SIG change (at 50+ MeV) and stochastic variation. At 17 MeV, the shift is purely stochastic: seed-0 is identical, so the +0.0003 difference is the ensemble mean's offset from seed-0. At 100 MeV, the −0.0136 shift (approximately 1.8σ from the ensemble mean) includes contributions from both the reduced sample size and the specific seed realisation. The Tag shift at 17 MeV (+0.048) is 0.37σ — within the expected stochastic range but highlighting the seed pair's below-average Tag value.

### 7.2 η Scan at 17 MeV: v2.5 Single-Seed vs Ensemble Mean

At η = 1.5 and η = 1.7, the base-pair yield at 17 MeV exceeds 50,000, so the N_SIG cap binds and the v2.5 (60K) seed-0 values differ from this study's seed-0 values. At η ≥ 2.0, yield < 50K and seed-0 is identical.

| η | v2.5 HV (60K) | Ensemble HV (50K) | v2.5 Tag (60K) | Ensemble Tag (50K) |
|-----|---------------|-------------------|----------------|---------------------|
| 1.5 | 1.1431 | 1.1423 | 1.3986 | 1.3824 |
| 1.7 | 1.1427 | 1.1411 | 1.4095 | 1.4237 |
| 2.0 | 1.1393 | 1.1396 | 1.6892 | 1.7371 |
| 2.3 | 1.1417 | 1.1381 | 2.7098 | 2.6136 |
| 2.5 | 1.1412 | 1.1374 | 3.4441 | 3.3221 |

---

## 8. Limitations

1. **Ensemble size.** N_seeds = 50 provides moderate statistical power. The 95% CI half-width on the HV mean is ~0.0005× (~0.04%), sufficient for all HV-based judgements. For Tag at 17 MeV, the CI half-width is 0.036× (~2%), which is adequate to establish the stochastic dominance but insufficient for precise point estimates.

2. **Seed formula.** The deterministic formula (100i + offset) generates correlated seed values. While numpy's Mersenne Twister is designed for independence from different seeds, a more robust approach (SeedSequence) is deferred. The consistent statistics across the 50 seeds suggest no pathological correlations.

3. **Fixed analysis choices.** The ensemble varies only random seeds, not analysis parameters. The confidence intervals characterise stochastic uncertainty only, not systematic uncertainty from parameter choices (n_σ, f, resolution threshold).

4. **P7 baseline sensitivity.** P7 is evaluated against the fixed v2.3 published baseline (1.030×) and the Gate 5 recomputed baseline (1.02661×). The ensemble does not re-run a separate 9-disk geometry per seed. The baseline comparison introduces a ~0.3% systematic offset that could be addressed in future work.

5. **Tag leverage effect (hypothesis).** The large Tag variation at low mass may arise from the tag formula's sensitivity to rare vertices near material-band boundaries — a leverage effect in which a small number of events dominate the tag response. This hypothesis is consistent with the observed pattern but has not been verified by direct event-level analysis. Increasing N_sig (beyond the scope of v2.6) would test whether the variation decreases as expected under this interpretation.

---

## 9. Conclusion

The v2.6 multi-seed ensemble fulfils its primary purpose: quantifying the stochastic uncertainty floor of the toy MC and providing confidence intervals for marginal results. The principal finding — that Tag degradation at 17 MeV is dominated by stochastic variation (σ/mean = 7.4%) — was not anticipated in the preregistration and invalidates single-seed Tag conclusions at low mass. This discovery demonstrates the value of the preregistered ensemble approach: had the v2.5 P3 result (−3.1%) been accepted at face value, subsequent work could have been built on a stochastic artefact.

The deconflation (SENSOR_DISK_Z fix) remains well-validated: ΔHV is stable (2.3% relative variation), positive at all masses and seeds, and consistent with the v2.5 single-seed measurement. The 17-band geometry's key performance metrics (P7, V3, M3) are robust across the ensemble.

---

## 10. Future Directions

The v2.6 ensemble results suggest several avenues for future investigation. These are presented as possibilities, not commitments; each would require its own preregistration cycle.

### 10.1 Variance Reduction for Tag at Low Mass

The dominant finding of v2.6 — Tag's 7.4% relative variation at 17 MeV — reveals that the current effective event sample size (N_sig = 50,000 cap, ~44,486 at 17 MeV after base-pair selection) is insufficient for precise Tag conclusions at low ALP mass. Potential approaches include:

- **Increased statistics.** Scaling N_sig to 500,000 or beyond could reduce the Tag standard error substantially, potentially bringing the 95% CI half-width from ~2% to below 1%. This would clarify whether the Tag/HV ratio decrease (P3) is genuinely near zero or merely unresolvable at current sample sizes.
- **Variance-reduction techniques.** Importance sampling or antithetic variates applied to the conversion-point generation could reduce Tag variance without proportionally increasing compute cost.
- **Stratified seed design.** Rather than a simple deterministic formula, a stratified or quasi-random seed sequence (e.g. numpy SeedSequence) could improve ensemble coverage and reduce correlations.

### 10.2 Systematic Uncertainty Exploration

The v2.6 ensemble quantifies stochastic uncertainty only: all analysis parameters (n_σ = 2, material scale f = 1.0, resolution thresholds) are held fixed across seeds. A natural extension would vary these parameters:

- **Material scale scan.** Varying f across a range (e.g. 0.5–2.0) while holding seeds fixed would separate material-model systematics from stochastic noise. This could clarify whether the HV degradation's mass dependence is robust against material assumptions.
- **Resolution threshold sensitivity.** The n_σ cut used for the two-hypothesis vertex fit could be varied (e.g. 1.5, 2.0, 2.5, 3.0) to assess whether the deconflation signal ΔHV is sensitive to this choice.
- **Combined stochastic + systematic ensemble.** A grid of (seed, parameter) combinations would yield a full uncertainty budget, distinguishing genuinely robust conclusions from those that hold only at the nominal parameter point.

### 10.3 Geometry Extensions

- **Intermediate geometries.** The current comparison is binary: 9-disk (v2.3 baseline) vs 17-band (v2.5/v2.6). Investigating intermediate configurations (e.g. 13-band, or 17-band with varied disk spacing) could reveal whether the deconflation benefit scales smoothly with the number of sensor planes.
- **Barrel region.** All versions to date focus on the endcap. Extending the toy MC to include a simplified barrel geometry would test whether the displaced-vertex sensitivity advantage of finer segmentation transfers to the central η region.

### 10.4 Tag Formula Diagnostics

The Tag metric's extreme stochastic sensitivity at low mass appears to be a mathematical property of the formula's structure — specifically, how small fluctuations in vertex-fit residuals are amplified through the tagging ratio. Dedicated diagnostic studies could:

- **Decompose the Tag variance.** Identify which stage of the analysis chain (conversion generation, hit resolution, vertex fitting, tag assignment) contributes most to the final Tag variance at 17 MeV.
- **Develop a stabilised Tag metric.** A modified tag formula with reduced sensitivity to outlier events (e.g. trimmed means, robust estimators) could provide more stable low-mass conclusions while preserving discriminating power at higher masses.

### 10.5 Comparison with Full-Simulation Benchmarks

This toy MC series intentionally uses simplified geometry and tracking. If comparable quantities become available from full GEANT4 simulations of the Phase-2 tracker (e.g. material-budget maps, vertex-resolution profiles, or displaced-vertex reconstruction efficiencies), a calibration study could assess how well the toy MC's relative comparisons (between geometry configurations) track the full-simulation results. This would help establish the domain of validity of the toy approach.

### 10.6 P7 Baseline Refinement

The current P7 evaluation uses the fixed v2.3 published baseline (1.030×). A cleaner approach would generate a per-seed 9-disk baseline, allowing a paired comparison within each seed. This would eliminate the ~0.3% systematic offset noted in §8 and provide a more precise measure of the 17-band geometry's convergence at high mass.

---

## 11. References

### Internal References (ALP-ttbar Toy MC Series)

- I1: v2.0 series overview, https://doi.org/10.5281/zenodo.24056097
- I2: v2.1 preregistration, https://doi.org/10.5281/zenodo.24063091
- I3: v2.1 results, https://doi.org/10.5281/zenodo.24136462
- I4: v2.2 preregistration, https://doi.org/10.5281/zenodo.24189990
- I5: v2.2 results, https://doi.org/10.5281/zenodo.24238224
- I6: v2.3 preregistration, https://doi.org/10.5281/zenodo.24244893
- I7: v2.3 results, https://doi.org/10.5281/zenodo.24273586
- I8: v2.4 preregistration, https://doi.org/10.5281/zenodo.24296796
- I9: v2.4 results, https://doi.org/10.5281/zenodo.24302619
- I10: v2.5 preregistration, https://doi.org/10.5281/zenodo.24329044
- I11: v2.5 results, https://doi.org/10.5281/zenodo.24341050
- I12: v2.6 preregistration, https://doi.org/10.5281/zenodo.24361872
- I13: v2.6 results (this document), https://doi.org/10.5281/zenodo.24373115

### External References

- E1: CMS Collaboration, Precision measurement of the structure of the CMS inner tracking system using nuclear interactions, JINST 13 (2018) P10034, arXiv:1807.03289.
- E2: ATLAS Collaboration, A measurement of material in the ATLAS tracker using secondary hadronic interactions in 7 TeV pp collisions, JINST 11 (2016) P11020, arXiv:1609.04305.
- E3: S. F. Koch et al., Measuring the ATLAS ITk pixel detector material via multiple scattering of positrons at the CERN PS, arXiv:2412.04686.
- E4: CMS Collaboration, The Phase-2 Upgrade of the CMS Tracker, CERN-LHCC-2017-009, CMS-TDR-014 (2017).
- E5: Purdue University, Purdue Physics and Astronomy, CMS tracker retirement and Phase-2 forward tracking assembly (November 2026); Norbert Neumeister et al.
- E6: J. Alimena, J. Niedziela et al., Hunting for Long-Lived ALPs in Top Events via Displaced Dielectron Pairs at the LHC, arXiv:2610.38932.
- E7: L. Rygaard et al., Top Secrets: Long-Lived ALPs in Top Production, arXiv:2306.08686.
- E8: LHCb Collaboration, Evidence for B⁰ → μ⁺μ⁻, arXiv:2611.00230, 2026.

---

## 12. Reproducibility

**Code files (all included in this repository):**
- `run_v26_ensemble.py`: ensemble orchestrator (new for v2.6)
- `endcap_sim.py`: endcap simulation with SENSOR_DISK_Z fix (unchanged from v2.5)
- `mtag_v24.py`: 17-band endcap tag (SHA-256: `053a0e6c8fa70130f78a2b5970c98762396a701e8fbdd6dc695c7293f041a34d`; unchanged from v2.4)
- `coverage.py`: coverage-ratio calculator (unchanged from v2.3)
- `mtag_v21.py`: frozen barrel tag (unchanged from v2.1)
- `mtag_v22.py`: frozen endcap tag (unchanged from v2.2)
- `make_charts_v26.py`: visualisation script (new for v2.6)

**Data files:**
- `v26_results.npy`: complete ensemble data (all 50 seeds × 2 configs × all masses and η points)
- `v26_run.log`: full console output log

**Figures:**
- `fig1_distribution_histograms.png`
- `fig2_deconflation_boxplots.png`
- `fig3_p3_scatter.png`
- `fig4_eta_band_plot.png`
- `fig5_marginal_decisions.png`

**Dependencies:** Python 3.10+, NumPy ≥ 1.24, SciPy ≥ 1.10, Matplotlib ≥ 3.7, ReportLab ≥ 4.0. Install via `pip install -r requirements.txt`.

**To reproduce:** `python3 run_v26_ensemble.py` (runtime ~28 min on a single core). Charts: `python3 make_charts_v26.py`. PDF: `python3 generate_pdf.py`.

**Seed formula:** SEED_CONV(i) = 100 × i + 5, SEED_SIG(i) = 100 × i + 11, for i ∈ {0, ..., 49}.

---
