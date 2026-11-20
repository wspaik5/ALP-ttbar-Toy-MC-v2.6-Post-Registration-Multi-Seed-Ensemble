"""Generate v2.6 post-registration PDF from README.md content."""
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

HERE = os.path.dirname(os.path.abspath(__file__))

# Output filename following project convention
PDF_NAME = "ALP-ttbar_Toy-MC_v2.6_Post-Registration_Multi-Seed-Ensemble_2026-11-20.pdf"

def build_pdf():
    doc = SimpleDocTemplate(
        os.path.join(HERE, PDF_NAME),
        pagesize=A4,
        topMargin=20*mm, bottomMargin=20*mm,
        leftMargin=18*mm, rightMargin=18*mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        'DocTitle', parent=styles['Title'],
        fontSize=14, leading=18, spaceAfter=6,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontSize=8, leading=10, textColor=HexColor('#555555'),
        alignment=TA_CENTER, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        'Disclaimer', parent=styles['Normal'],
        fontSize=7.5, leading=10, textColor=HexColor('#666666'),
        leftIndent=10*mm, rightIndent=10*mm,
        spaceBefore=4, spaceAfter=8,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        'SectionHead', parent=styles['Heading1'],
        fontSize=12, leading=15, spaceBefore=14, spaceAfter=6,
        textColor=HexColor('#1a1a1a'),
    ))
    styles.add(ParagraphStyle(
        'SubHead', parent=styles['Heading2'],
        fontSize=10, leading=13, spaceBefore=10, spaceAfter=4,
        textColor=HexColor('#333333'),
    ))
    styles.add(ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=9, leading=12, spaceAfter=4,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        'BodyBold', parent=styles['Normal'],
        fontSize=9, leading=12, spaceAfter=4,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        'SmallBody', parent=styles['Normal'],
        fontSize=8, leading=10, spaceAfter=3,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontSize=7.5, leading=9,
    ))
    styles.add(ParagraphStyle(
        'RefStyle', parent=styles['Normal'],
        fontSize=7.5, leading=9.5, spaceAfter=1,
        leftIndent=8*mm, firstLineIndent=-8*mm,
    ))

    story = []

    # ---- TITLE ----
    story.append(Paragraph(
        "ALP-ttbar Toy MC v2.6 — Post-Registration Results:<br/>"
        "Multi-Seed Ensemble in Displaced Light ALP → e<super>+</super>e<super>−</super>",
        styles['DocTitle']
    ))
    story.append(Paragraph("Won Shik Paik (Independent Researcher, Auckland, New Zealand)", styles['Meta']))
    story.append(Paragraph("2026-11-20", styles['Meta']))
    story.append(Paragraph(
        "DOI: 10.5281/zenodo.24373115 &nbsp;|&nbsp; "
        "Preregistration: 10.5281/zenodo.24361872", styles['Meta']
    ))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "<i>Disclaimer.</i> Independent personal toy study, not affiliated with the authors of "
        "arXiv:2610.38932 or arXiv:2306.08686, nor with the CMS, ATLAS, LHCb or ALICE "
        "Collaborations or the FCC study. Detector numbers are assumed; only qualitative "
        "trends and ratios are meaningful.",
        styles['Disclaimer']
    ))

    # Helper
    def S(text, style='Body'):
        story.append(Paragraph(text, styles[style]))
    def head(num, title):
        story.append(Paragraph(f"{num}. {title}", styles['SectionHead']))
    def subhead(title):
        story.append(Paragraph(title, styles['SubHead']))
    def sp(h=2):
        story.append(Spacer(1, h*mm))

    def make_table(headers, rows, col_widths=None):
        data = [headers] + rows
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('LEADING', (0,0), (-1,-1), 9),
            ('BACKGROUND', (0,0), (-1,0), HexColor('#e8e8e8')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.4, HexColor('#cccccc')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t)

    # ---- 0. EXECUTIVE SUMMARY ----
    head("0", "Executive Summary")

    S("<b>1. HV degradation is highly stable across seeds.</b> The relative standard deviation "
      "σ_HV / HV is 0.16% at 17 MeV (η = 2.0), confirming prediction S1. The ensemble mean "
      "(1.1396×) is close to the v2.5 single-seed value (1.1393×).")

    S("<b>2. Tag degradation at 17 MeV exhibits large stochastic variation.</b> The relative "
      "standard deviation σ_Tag / Tag is 7.4%, far exceeding the predicted &lt; 1% (S2 REFUTED). "
      "This sensitivity arises from the tag formula's response to rare vertices near material bands.")

    S("<b>3. P3 (Tag/HV ratio decrease ≥ 3%) is REFUTED.</b> The ensemble mean decrease is only "
      "0.38%, with 42% of seeds exceeding the 3% threshold. The v2.5 single-seed result of −3.1% "
      "was a stochastic artefact (M1 REFUTED).")

    S("<b>4. Deconflation deltas are robust.</b> ΔHV at 17 MeV = +0.0452 ± 0.0010 (D1 CONFIRMED). "
      "All 50 seeds show positive ΔHV at all masses (D3 CONFIRMED). ΔTag at 17 MeV = +0.0021, "
      "below the predicted range (D2 REFUTED).")

    S("<b>5. V5 fails at 200 MeV.</b> σ(ΔHV)/σ(HV) = 1.08, indicating incomplete stochastic "
      "cancellation where the deconflation effect is weakest.")

    S("<b>Overall: 6/10 primary predictions confirmed, 4 refuted (S2, M1, M2, D2). "
      "G1–G3 and G5 passed; G4 not met (10/18 seed-0 comparisons match published v2.5, "
      "with 8 expected mismatches from the N_SIG change). "
      "5/6 validations passed.</b> The principal lesson is that Tag degradation at 17 MeV is "
      "dominated by stochastic variation, making single-seed Tag conclusions unreliable at low mass.")

    # ---- 1. ENSEMBLE CONFIGURATION ----
    head("1", "Ensemble Configuration")
    S("The simulation swept N_seeds = 50 independent seed pairs with all other parameters held "
      "at their v2.5 values. Seed formula: SEED_CONV(i) = 100 × i + 5, SEED_SIG(i) = 100 × i + 11, "
      "for i ∈ {0, ..., 49}.")

    S("Two configurations per seed: <b>E3</b> (v2.5: 17-band + SENSOR_DISK_Z resolution) and "
      "<b>E3_conflated</b> (v2.4-equivalent: 17-band + DISK_Z resolution). Fixed parameters: "
      "17-band geometry, resolution threshold 50 mm, σ_z(pixel) = 1.0 mm, σ_z(strip) = 3.0 mm, "
      "f = 0.25, N_sig = 50,000 (matching preregistration §2), "
      "masses = [17, 50, 100, 200] MeV, η = [1.5, 1.7, 2.0, 2.3, 2.5], "
      "tag formula = mtag_v24. Total runtime: 1669 s (27.8 min).")

    # ---- 2. SANITY GATES ----
    head("2", "Sanity Gates")
    make_table(
        ['Gate', 'Description', 'Result'],
        [
            ['G1', 'SHA-256 of mtag_v24.py matches v2.5 record', 'PASS'],
            ['G2', 'Tag formula: λ > 0 far from bands, λ < 0 near bands', 'PASS'],
            ['G3', 'Coverage within 5 × 10⁻⁴ at n_σ = 2, 3, 4', 'PASS'],
            ['G4', 'Seed i = 0 reproduces v2.5 to 4 d.p. (all 18 values)', 'NOT MET (10/18)'],
            ['G5', 'Seed i = 25 re-run: bitwise identical at all 4 masses', 'PASS'],
        ],
        col_widths=[30, 310, 40],
    )
    sp()
    S("<b>G4 not met.</b> The preregistered criterion requires all 18 seed-0 values to match published "
      "v2.5 to 4 decimal places. The published v2.5 reference (DOI: 10.5281/zenodo.24341050) was generated "
      "with N_SIG = 60,000; the v2.6 preregistration specifies N_SIG = 50,000 (§2 parameter table). "
      "With the same seed (i = 0), 10 of 18 comparisons match; the remaining 8 "
      "deviate due to the N_SIG change affecting stochastic vertex counts. Some mismatches are small "
      "(e.g. 100 MeV Tag: 1.1073 → 1.1079) while others are larger "
      "(e.g. 17 MeV η = 1.5 Tag: 1.3986 → 1.4013). "
      "G1–G3 and G5 passed unconditionally.")

    # ---- 3. ENSEMBLE RESULTS ----
    head("3", "Ensemble Results")

    subhead("3.1 Endcap E3 at η = 2.0")
    make_table(
        ['Mass', 'HV mean ± σ', 'HV 95% CI', 'Tag mean ± σ', 'Tag 95% CI'],
        [
            ['17 MeV',  '1.1396 ± 0.0018', '[1.1392, 1.1401]', '1.7371 ± 0.1292', '[1.7013, 1.7729]'],
            ['50 MeV',  '1.1473 ± 0.0022', '[1.1467, 1.1480]', '1.2211 ± 0.0128', '[1.2175, 1.2246]'],
            ['100 MeV', '1.1186 ± 0.0076', '[1.1165, 1.1207]', '1.1104 ± 0.0030', '[1.1096, 1.1113]'],
            ['200 MeV', '1.0555 ± 0.0016', '[1.0550, 1.0559]', '1.0614 ± 0.0013', '[1.0610, 1.0617]'],
        ],
        col_widths=[45, 85, 80, 85, 80],
    )
    sp()
    S("Tag σ at 17 MeV (0.1292, 7.4% relative) is two orders of magnitude larger than HV σ "
      "(0.0018, 0.16% relative). This disparity decreases with mass: at 200 MeV, both are ~0.1%.")

    subhead("3.2 Deconflation Deltas at η = 2.0")
    make_table(
        ['Mass', 'ΔHV mean ± σ', 'ΔHV 95% CI', 'ΔTag mean ± σ', 'ΔTag 95% CI'],
        [
            ['17 MeV',  '+0.0452 ± 0.0010', '[+0.0449, +0.0454]', '+0.0021 ± 0.0032', '[+0.0012, +0.0029]'],
            ['50 MeV',  '+0.0474 ± 0.0013', '[+0.0470, +0.0478]', '+0.0499 ± 0.0024', '[+0.0492, +0.0506]'],
            ['100 MeV', '+0.0369 ± 0.0045', '[+0.0357, +0.0382]', '+0.0396 ± 0.0011', '[+0.0392, +0.0399]'],
            ['200 MeV', '+0.0196 ± 0.0017', '[+0.0191, +0.0201]', '+0.0233 ± 0.0007', '[+0.0231, +0.0235]'],
        ],
        col_widths=[45, 85, 82, 85, 82],
    )
    sp()
    S("All ΔHV values are positive at all masses and all seeds (D3 CONFIRMED). "
      "ΔHV relative variation is 2.3% at 17 MeV — a stable, structural shift. "
      "ΔTag is positive on average but negative in 14/50 seeds at 17 MeV (28%), "
      "reflecting the tag's large stochastic variation at low mass.")

    subhead("3.3 η Scan at 17 MeV (E3)")
    make_table(
        ['η', 'HV mean ± σ', 'HV 95% CI', 'Tag mean ± σ', 'Tag 95% CI'],
        [
            ['1.5', '1.1423 ± 0.0020', '[1.1418, 1.1429]', '1.3824 ± 0.0284', '[1.3745, 1.3903]'],
            ['1.7', '1.1411 ± 0.0016', '[1.1406, 1.1415]', '1.4237 ± 0.0266', '[1.4163, 1.4311]'],
            ['2.0', '1.1396 ± 0.0018', '[1.1392, 1.1401]', '1.7371 ± 0.1292', '[1.7013, 1.7729]'],
            ['2.3', '1.1381 ± 0.0021', '[1.1375, 1.1386]', '2.6136 ± 0.1032', '[2.5850, 2.6423]'],
            ['2.5', '1.1374 ± 0.0025', '[1.1367, 1.1381]', '3.3221 ± 0.1205', '[3.2887, 3.3555]'],
        ],
        col_widths=[25, 85, 82, 85, 82],
    )

    # ---- 4. VALIDATIONS ----
    head("4", "Validations")
    make_table(
        ['ID', 'Description', 'Result', 'Detail'],
        [
            ['V1', 'HV ≥ 1.0 everywhere', 'PASS', 'No violations'],
            ['V2', 'Tag ≥ 1.0 at 17 MeV', 'PASS', 'No violations'],
            ['V3', 'σ_HV/HV < 1%', 'PASS', '0.1562%'],
            ['V4', 'HV η-independence CV < 2%', 'PASS', 'CV = 0.1795%'],
            ['V5', 'σ(ΔHV)/σ(HV) < 1.0 all masses', 'FAIL', '200 MeV: 1.08'],
            ['V6', 'Coverage seed-independent', 'PASS', 'Seed-independent by construction (shared geometric inputs)'],
        ],
        col_widths=[22, 150, 32, 160],
    )
    sp()
    S("<b>V5 discussion.</b> The deconflation delta is more stable than the absolute at 17, 50, "
      "and 100 MeV (σ-ratio 0.58–0.61). At 200 MeV, the smaller Lorentz boost "
      "(γβ = p/m decreases with mass at comparable momenta) produces a shorter mean "
      "lab-frame decay length and a more concentrated z-distribution, with fewer vertices "
      "reaching the deconflation-sensitive region. The deconflation effect is correspondingly "
      "small (ΔHV ≈ +0.020), leaving stochastic cancellation incomplete.")

    # ---- 5. PREDICTIONS ----
    head("5", "Predictions")

    subhead("5.1 Seed Variability (S1–S4)")
    make_table(
        ['ID', 'Predicted', 'Observed', 'Verdict'],
        [
            ['S1', 'σ_HV/HV < 0.5%', '0.16%', 'CONFIRMED'],
            ['S2', 'σ_Tag/Tag < 1.0%', '7.44%', 'REFUTED'],
            ['S3', 'σ(ΔHV)/|ΔHV| < 5%', '2.30%', 'CONFIRMED'],
            ['S4', 'σ_HV(200)/(HV(200)−1) > σ_HV(17)/(HV(17)−1)', '0.028 > 0.013', 'CONFIRMED'],
        ],
        col_widths=[22, 180, 85, 70],
    )
    sp()
    S("<b>S2 refutation:</b> The tag formula's p_conv convolution weights depend on exact vertex "
      "positions relative to material bands. We hypothesise that a small number of near-band vertices "
      "may dominate the tag response (leverage effect), amplifying stochastic variation well beyond "
      "√N counting statistics. This hypothesis has not been verified by event-level analysis.")

    subhead("5.2 Marginal Results (M1–M3)")
    make_table(
        ['ID', 'Predicted', 'Observed', 'Verdict'],
        [
            ['M1', 'P3 mean decrease ≥ 2.5%; >50% seeds ≥ 3%', 'mean = 0.38%; 42% ≥ 3%', 'REFUTED'],
            ['M2', 'P7 mean dev. 2.5–3.5%; CI straddles 3%', 'mean = 2.47%; CI [2.43, 2.52]%', 'REFUTED'],
            ['M3', 'HV, Tag means > 1.05 at 200 MeV; >90%', 'HV 1.0555 (100%), Tag 1.0614 (100%)', 'CONFIRMED'],
        ],
        col_widths=[22, 160, 130, 55],
    )
    sp()
    S("<b>M1 (P3):</b> The v2.5 single-seed Tag/HV decrease of −3.1% is not confirmed. "
      "The ensemble mean decrease is 0.38%, spanning −18% to +14% across seeds. "
      "The specific seed pair (5, 11) produced a below-average Tag, yielding an apparent ratio decrease.")
    S("<b>M2 (P7):</b> The ensemble mean deviation (2.47%) is entirely below 3%. P7 PASSES "
      "with high confidence. Secondary (G5 baseline 1.02661×): mean deviation 2.81%, CI [2.77, 2.85]%.")

    subhead("5.3 Deconflation Robustness (D1–D3)")
    make_table(
        ['ID', 'Predicted', 'Observed', 'Verdict'],
        [
            ['D1', 'ΔHV at 17 MeV: 0.040–0.050', '+0.0452 [0.0449, 0.0454]', 'CONFIRMED'],
            ['D2', 'ΔTag at 17 MeV: 0.004–0.012', '+0.0021 [0.0012, 0.0029]', 'REFUTED'],
            ['D3', 'ΔHV > 0 at all masses, all seeds', '100% confirmed', 'CONFIRMED'],
        ],
        col_widths=[22, 150, 140, 55],
    )
    sp()
    S("<b>D2 refutation:</b> The ensemble mean ΔTag at 17 MeV is +0.0021, below the predicted "
      "0.004–0.012. The tag's large stochastic variation (σ ≈ 0.13) dwarfs the deconflation effect. "
      "The 95% CI excludes zero, confirming a statistically significant but small positive shift.")

    subhead("5.4 One-Sided p-Values (Prereg §2.5)")
    S("As specified in the preregistration (§2.5), one-sided t-tests are reported for the marginal results:")
    make_table(
        ['Test', 'Null Hypothesis', 't-stat', 'p-value', 'Interpretation'],
        [
            ['P3 (3%)', 'Mean decrease ≥ 3.0%', '−2.512', '7.67e−3', 'Below P3 threshold'],
            ['P3 (2.5%)', 'Mean decrease ≥ 2.5%', '−2.033', '2.37e−2', 'Below M1 threshold'],
            ['P7', 'Mean |dev| ≥ 3%', '−24.31', '2.69e−29', 'P7 PASS confirmed'],
            ['M3 HV', 'Mean HV ≤ 1.05', '+24.53', '1.79e−29', 'HV > 1.05 confirmed'],
            ['M3 Tag', 'Mean Tag ≤ 1.05', '+63.58', '4.72e−49', 'Tag > 1.05 confirmed'],
        ],
        col_widths=[45, 100, 40, 55, 115],
    )
    sp()
    S("All tests use Student's t with df = 49. M3 uses t.sf() to avoid float underflow at extreme values.")

    # ---- FIGURES ----
    head("6", "Figures")

    fig_files = [
        ('fig1_distribution_histograms.png', 'Figure 1: HV and Tag distributions at η = 2.0 (N = 50 seeds)'),
        ('fig2_deconflation_boxplots.png', 'Figure 2: Deconflation deltas (E3 − E3_conflated) box plots'),
        ('fig3_p3_scatter.png', 'Figure 3: P3 — Tag/HV ratio decrease vs seed index (21/50 seeds ≥ 3%)'),
        ('fig4_eta_band_plot.png', 'Figure 4: η-dependence at 17 MeV (mean ± 1σ bands)'),
        ('fig5_marginal_decisions.png', 'Figure 5: Marginal result decision plots (P3, P7, V3)'),
    ]

    page_width = A4[0] - 36*mm  # usable width
    for fname, caption in fig_files:
        fpath = os.path.join(HERE, fname)
        if os.path.exists(fpath):
            img = Image(fpath, width=page_width, height=page_width * 0.45)
            img.hAlign = 'CENTER'
            story.append(KeepTogether([img, Spacer(1, 2*mm),
                Paragraph(f"<i>{caption}</i>", styles['SmallBody'])]))
            sp(4)

    # ---- 7. DISCUSSION ----
    story.append(PageBreak())
    head("7", "Discussion")

    subhead("7.1 Tag Stochastic Sensitivity")
    S("The v2.6 ensemble's most consequential result is that Tag degradation at low ALP mass "
      "is dominated by stochastic variation, not structural parameters. With σ/mean = 7.4% at "
      "17 MeV (vs 0.16% for HV), single-seed Tag measurements at this mass carry negligible "
      "statistical weight for quantitative comparisons.")
    S("This sensitivity explains the v2.5 \"P3 marginal result\" (3.1% decrease, 0.1 pp above "
      "threshold) as entirely within the stochastic noise floor. The hypothesised mechanism is the "
      "tag formula's nonlinear sensitivity to vertex positions near material bands: the p_conv "
      "convolution may assign high weight to near-band vertices, with rare events dominating the "
      "tag response. This hypothesis awaits event-level verification.")

    subhead("7.2 Implications")
    S("<b>P3 is not supported.</b> The claimed advantage of v2.5 geometry in suppressing "
      "Tag/HV ratio at 17 MeV does not survive ensemble averaging.")
    S("<b>P7 is robustly confirmed.</b> 17-band HV at 200 MeV is within 3% of baseline "
      "(mean 2.47%, CI entirely below 3%).")
    S("<b>V3 refutation is robust.</b> 200 MeV degradation exceeds 1.05 for both HV and Tag "
      "across the full ensemble (100% of seeds).")
    S("<b>Deconflation is validated.</b> ΔHV is stable (2.3% relative variation) and consistent "
      "with v2.5 single-seed values.")
    S("<b>Tag at 17 MeV requires larger event samples.</b> Future studies targeting Tag precision "
      "at low mass would need N_sig ≫ 50,000 or variance-reduction techniques.")

    # ---- 8. LIMITATIONS ----
    head("8", "Limitations")
    S("1. <b>Ensemble size:</b> N = 50 gives HV CI half-width ~0.0005× (0.04%), sufficient "
      "for all HV judgements. For Tag at 17 MeV, CI half-width is 0.036× (~2%).")
    S("2. <b>Seed formula:</b> Deterministic (100i + offset). SeedSequence deferred. "
      "Consistent statistics across 50 seeds suggest no pathological correlations.")
    S("3. <b>Fixed analysis choices:</b> CIs characterise stochastic uncertainty only, "
      "not systematic uncertainty from parameter choices.")
    S("4. <b>P7 baseline sensitivity:</b> Evaluated against fixed v2.3 baselines "
      "(1.030× published, 1.02661× recomputed), not per-seed 9-disk results.")
    S("5. <b>Tag leverage effect (hypothesis):</b> The large Tag variation may arise from "
      "the tag formula's sensitivity to rare near-band vertices. This hypothesis has not been verified "
      "by event-level analysis. Increasing N_sig (beyond v2.6 scope) would test it.")

    # ---- 9. CONCLUSION ----
    head("9", "Conclusion")
    S("The v2.6 multi-seed ensemble fulfils its primary purpose: quantifying the stochastic "
      "uncertainty floor and providing confidence intervals for marginal results. The principal "
      "finding — Tag degradation at 17 MeV is dominated by stochastic variation (σ/mean = 7.4%) "
      "— was not anticipated in the preregistration and invalidates single-seed Tag conclusions "
      "at low mass. This demonstrates the value of preregistered ensemble analysis: had the v2.5 "
      "P3 result (−3.1%) been accepted at face value, subsequent work could have been built on "
      "a stochastic artefact.")
    S("The deconflation (SENSOR_DISK_Z fix) remains well-validated: ΔHV is stable, positive "
      "at all masses and seeds, and consistent with v2.5. The key performance metrics (P7, V3, M3) "
      "are robust across the ensemble.")

    # ---- 10. FUTURE DIRECTIONS ----
    head("10", "Future Directions")
    S("The v2.6 ensemble results suggest several avenues for future investigation. "
      "These are presented as possibilities, not commitments; each would require its "
      "own preregistration cycle.")

    subhead("10.1 Variance Reduction for Tag at Low Mass")
    S("Tag's 7.4% relative variation at 17 MeV reveals that N_sig = 50,000 is "
      "insufficient for precise Tag conclusions at low ALP mass. Scaling N_sig to "
      "500,000 or beyond could reduce the Tag standard error by √5 or more, bringing "
      "the 95% CI half-width from ~2% to below 1%. Variance-reduction techniques "
      "(importance sampling, antithetic variates) or stratified seed designs "
      "(numpy SeedSequence) could also improve ensemble coverage.")

    subhead("10.2 Systematic Uncertainty Exploration")
    S("The v2.6 ensemble quantifies stochastic uncertainty only, with all analysis "
      "parameters held fixed. A natural extension would vary the material scale f "
      "(e.g. 0.5–2.0), the resolution threshold n_σ (1.5–3.0), or both, to separate "
      "material-model systematics from stochastic noise. A combined stochastic + "
      "systematic grid of (seed, parameter) combinations would yield a full "
      "uncertainty budget.")

    subhead("10.3 Geometry Extensions")
    S("The current comparison is binary: 9-disk vs 17-band. Intermediate configurations "
      "(e.g. 13-band, varied disk spacing) could reveal whether the deconflation benefit "
      "scales smoothly. Extending the toy MC to include a simplified barrel geometry "
      "would test whether the displaced-vertex sensitivity advantage transfers to "
      "the central η region.")

    subhead("10.4 Tag Formula Diagnostics")
    S("The Tag metric's extreme stochastic sensitivity at low mass appears to be a "
      "mathematical property of the formula's structure. Dedicated studies could "
      "decompose the Tag variance by analysis stage (conversion generation, hit "
      "resolution, vertex fitting, tag assignment) and develop stabilised alternatives "
      "(trimmed means, robust estimators) with reduced outlier sensitivity.")

    subhead("10.5 Full-Simulation Benchmarks")
    S("If comparable quantities become available from full GEANT4 simulations of the "
      "Phase-2 tracker, a calibration study could assess how well the toy MC's "
      "relative comparisons track full-simulation results, establishing the domain "
      "of validity of the toy approach.")

    subhead("10.6 P7 Baseline Refinement")
    S("Generating a per-seed 9-disk baseline (rather than using the fixed v2.3 "
      "published value 1.030×) would enable paired within-seed comparisons, "
      "eliminating the ~0.3% systematic offset noted in §8 and providing a more "
      "precise measure of 17-band convergence at high mass.")

    # ---- 11. REFERENCES ----
    head("11", "References")
    subhead("Internal References")
    refs_internal = [
        "I1: v2.0 series overview, DOI: 10.5281/zenodo.24056097",
        "I2: v2.1 preregistration, DOI: 10.5281/zenodo.24063091",
        "I3: v2.1 results, DOI: 10.5281/zenodo.24136462",
        "I4: v2.2 preregistration, DOI: 10.5281/zenodo.24189990",
        "I5: v2.2 results, DOI: 10.5281/zenodo.24238224",
        "I6: v2.3 preregistration, DOI: 10.5281/zenodo.24244893",
        "I7: v2.3 results, DOI: 10.5281/zenodo.24273586",
        "I8: v2.4 preregistration, DOI: 10.5281/zenodo.24296796",
        "I9: v2.4 results, DOI: 10.5281/zenodo.24302619",
        "I10: v2.5 preregistration, DOI: 10.5281/zenodo.24329044",
        "I11: v2.5 results, DOI: 10.5281/zenodo.24341050",
        "I12: v2.6 preregistration, DOI: 10.5281/zenodo.24361872",
        "I13: v2.6 results (this document), DOI: 10.5281/zenodo.24373115",
    ]
    for r in refs_internal:
        story.append(Paragraph(r, styles['RefStyle']))

    subhead("External References")
    refs_external = [
        "E1: CMS Collaboration, JINST 13 (2018) P10034, arXiv:1807.03289.",
        "E2: ATLAS Collaboration, JINST 11 (2016) P11020, arXiv:1609.04305.",
        "E3: S. F. Koch et al., arXiv:2412.04686.",
        "E4: CMS Collaboration, CMS-TDR-014 (2017).",
        "E5: Purdue University, CMS tracker Phase-2 assembly (2026).",
        "E6: J. Alimena, J. Niedziela et al., arXiv:2610.38932.",
        "E7: L. Rygaard et al., arXiv:2306.08686.",
        "E8: LHCb Collaboration, arXiv:2611.00230, 2026.",
    ]
    for r in refs_external:
        story.append(Paragraph(r, styles['RefStyle']))

    # ---- 12. REPRODUCIBILITY ----
    head("12", "Reproducibility")
    S("Code: run_v26_ensemble.py (new), endcap_sim.py, mtag_v24.py "
      "(SHA-256: 053a0e6c...f041a34d), coverage.py, mtag_v21.py, mtag_v22.py, "
      "make_charts_v26.py. Data: v26_results.npy, v26_run.log. "
      "Seed formula: SEED_CONV(i) = 100i + 5, SEED_SIG(i) = 100i + 11, i ∈ {0, ..., 49}. "
      "Reproduce: python3 run_v26_ensemble.py (~28 min).")

    doc.build(story)
    print(f"  PDF saved: {PDF_NAME}")

if __name__ == '__main__':
    build_pdf()
