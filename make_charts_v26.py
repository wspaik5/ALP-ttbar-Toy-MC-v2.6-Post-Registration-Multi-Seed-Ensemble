"""v2.6 post-registration charts: ensemble distribution visualizations.

Generates 5 figures as specified in the preregistration §6.3:
  1. Distribution histograms (HV and Tag at each mass, η=2.0)
  2. Box plots of deconflation deltas (ΔHV, ΔTag at each mass)
  3. Scatter plot of Tag/HV ratio vs seed index (P3 threshold)
  4. η-dependence band plot (mean ± 1σ for HV and Tag at 17 MeV)
  5. Marginal result decision plots (P3, P7, V3)
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

HERE = os.path.dirname(os.path.abspath(__file__))

# Load results
results = np.load(os.path.join(HERE, 'v26_results.npy'), allow_pickle=True).item()
all_results = results['all_results']
N_SEEDS = results['N_SEEDS']
MASSES = [0.017, 0.05, 0.1, 0.2]
MASS_LABELS = ['17 MeV', '50 MeV', '100 MeV', '200 MeV']
ETA_SCAN = [1.5, 1.7, 2.0, 2.3, 2.5]

# v2.5 reference values
V25_REF = {
    0.017: dict(hv=1.1393, tag=1.6892),
    0.05:  dict(hv=1.1463, tag=1.2197),
    0.1:   dict(hv=1.1322, tag=1.1079),
    0.2:   dict(hv=1.0597, tag=1.0611),
}

V23_RATIO_17MEV = 1.530
V23_HV_200MEV = 1.03

plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 8,
    'figure.dpi': 150,
})


def extract_values(key_path):
    """Extract array of values across all seeds for a given path."""
    vals = []
    for i in range(N_SEEDS):
        d = all_results[i]
        for key in key_path:
            d = d[key]
        vals.append(d)
    return np.array(vals)


# ===================================================================
# Figure 1: Distribution Histograms
# ===================================================================

fig1, axes1 = plt.subplots(2, 4, figsize=(14, 7))
fig1.suptitle('v2.6 Ensemble: HV and Tag Distribution at η = 2.0 (N = 50 seeds)', fontsize=13, y=0.98)

for j, (m, ml) in enumerate(zip(MASSES, MASS_LABELS)):
    hv_vals = [all_results[i]['E3']['eta20'][m]['hv_deg'] for i in range(N_SEEDS)]
    tag_vals = [all_results[i]['E3']['eta20'][m]['tag_deg'] for i in range(N_SEEDS)]

    ax_hv = axes1[0, j]
    ax_hv.hist(hv_vals, bins=15, color='#4C72B0', alpha=0.7, edgecolor='white')
    ax_hv.axvline(V25_REF[m]['hv'], color='red', linestyle='--', linewidth=1.5, label=f'v2.5 = {V25_REF[m]["hv"]:.4f}')
    ax_hv.axvline(np.mean(hv_vals), color='black', linestyle='-', linewidth=1.0, label=f'mean = {np.mean(hv_vals):.4f}')
    ax_hv.set_title(f'HV — {ml}')
    ax_hv.set_xlabel('Degradation [×]')
    ax_hv.legend(fontsize=7)

    ax_tag = axes1[1, j]
    ax_tag.hist(tag_vals, bins=15, color='#DD8452', alpha=0.7, edgecolor='white')
    ax_tag.axvline(V25_REF[m]['tag'], color='red', linestyle='--', linewidth=1.5, label=f'v2.5 = {V25_REF[m]["tag"]:.4f}')
    ax_tag.axvline(np.mean(tag_vals), color='black', linestyle='-', linewidth=1.0, label=f'mean = {np.mean(tag_vals):.4f}')
    ax_tag.set_title(f'Tag — {ml}')
    ax_tag.set_xlabel('Degradation [×]')
    ax_tag.legend(fontsize=7)

axes1[0, 0].set_ylabel('Count')
axes1[1, 0].set_ylabel('Count')
fig1.tight_layout(rect=[0, 0, 1, 0.95])
fig1.savefig(os.path.join(HERE, 'fig1_distribution_histograms.png'), bbox_inches='tight')
print("  Saved fig1_distribution_histograms.png")


# ===================================================================
# Figure 2: Box Plots of Deconflation Deltas
# ===================================================================

fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(10, 5))
fig2.suptitle('v2.6 Ensemble: Deconflation Deltas (E3 − E3_conflated) at η = 2.0', fontsize=13)

delta_hv_data = []
delta_tag_data = []
for m in MASSES:
    dhv = [all_results[i]['E3']['eta20'][m]['hv_deg'] -
           all_results[i]['E3_conflated']['eta20'][m]['hv_deg']
           for i in range(N_SEEDS)]
    dtag = [all_results[i]['E3']['eta20'][m]['tag_deg'] -
            all_results[i]['E3_conflated']['eta20'][m]['tag_deg']
            for i in range(N_SEEDS)]
    delta_hv_data.append(dhv)
    delta_tag_data.append(dtag)

bp1 = ax2a.boxplot(delta_hv_data, tick_labels=MASS_LABELS, patch_artist=True,
                     boxprops=dict(facecolor='#4C72B0', alpha=0.6),
                     medianprops=dict(color='red', linewidth=1.5))
ax2a.set_title('ΔHV (deconflation)')
ax2a.set_ylabel('Delta [×]')
ax2a.axhline(0, color='gray', linestyle=':', linewidth=0.8)
# Mark v2.5 single-seed deltas
v25_deltas_hv = [0.046, 0.047, 0.039, 0.024]
for j, d in enumerate(v25_deltas_hv):
    ax2a.plot(j + 1, d, 'r*', markersize=10, zorder=5)

bp2 = ax2b.boxplot(delta_tag_data, tick_labels=MASS_LABELS, patch_artist=True,
                     boxprops=dict(facecolor='#DD8452', alpha=0.6),
                     medianprops=dict(color='red', linewidth=1.5))
ax2b.set_title('ΔTag (deconflation)')
ax2b.set_ylabel('Delta [×]')
ax2b.axhline(0, color='gray', linestyle=':', linewidth=0.8)
v25_deltas_tag = [0.007, 0.049, 0.039, 0.023]
for j, d in enumerate(v25_deltas_tag):
    ax2b.plot(j + 1, d, 'r*', markersize=10, zorder=5, label='v2.5 single-seed' if j == 0 else '')
ax2b.legend(fontsize=8)

fig2.tight_layout()
fig2.savefig(os.path.join(HERE, 'fig2_deconflation_boxplots.png'), bbox_inches='tight')
print("  Saved fig2_deconflation_boxplots.png")


# ===================================================================
# Figure 3: Scatter Plot — Tag/HV Ratio vs Seed Index (P3)
# ===================================================================

fig3, ax3 = plt.subplots(figsize=(10, 5))

ratio_vals = [all_results[i]['E3']['eta20'][0.017]['ratio'] for i in range(N_SEEDS)]
decrease_pct = [(1.0 - r / V23_RATIO_17MEV) * 100 for r in ratio_vals]

colors = ['#2ecc71' if d >= 3.0 else '#e74c3c' for d in decrease_pct]
ax3.scatter(range(N_SEEDS), decrease_pct, c=colors, s=40, alpha=0.8, edgecolors='k', linewidths=0.5)
ax3.axhline(3.0, color='black', linestyle='--', linewidth=1.5, label='P3 threshold (3%)')
ax3.axhline(np.mean(decrease_pct), color='blue', linestyle='-', linewidth=1.0,
            label=f'Ensemble mean = {np.mean(decrease_pct):.2f}%')
# v2.5 single-seed
ax3.axhline(3.1, color='red', linestyle=':', linewidth=1.0, label='v2.5 single-seed = 3.1%')

ax3.set_xlabel('Seed Index')
ax3.set_ylabel('Tag/HV Decrease from v2.3 Baseline [%]')
ax3.set_title('P3 Marginal Result: Tag/HV Ratio Decrease at 17 MeV (η = 2.0)')
n_above = sum(1 for d in decrease_pct if d >= 3.0)
ax3.annotate(f'{n_above}/{N_SEEDS} seeds ≥ 3%', xy=(0.98, 0.95), xycoords='axes fraction',
             ha='right', va='top', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='gray'))
ax3.legend(loc='lower right')
ax3.set_xlim(-1, N_SEEDS)

fig3.tight_layout()
fig3.savefig(os.path.join(HERE, 'fig3_p3_scatter.png'), bbox_inches='tight')
print("  Saved fig3_p3_scatter.png")


# ===================================================================
# Figure 4: η-Dependence Band Plot
# ===================================================================

fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(12, 5))
fig4.suptitle('v2.6 Ensemble: η Dependence at 17 MeV (mean ± 1σ)', fontsize=13)

hv_means = []
hv_stds = []
tag_means = []
tag_stds = []
for eta in ETA_SCAN:
    hv_vals = [all_results[i]['E3']['eta_scan'][eta][0.017]['hv_deg'] for i in range(N_SEEDS)]
    tag_vals = [all_results[i]['E3']['eta_scan'][eta][0.017]['tag_deg'] for i in range(N_SEEDS)]
    hv_means.append(np.mean(hv_vals))
    hv_stds.append(np.std(hv_vals, ddof=1))
    tag_means.append(np.mean(tag_vals))
    tag_stds.append(np.std(tag_vals, ddof=1))

hv_means = np.array(hv_means)
hv_stds = np.array(hv_stds)
tag_means = np.array(tag_means)
tag_stds = np.array(tag_stds)

ax4a.fill_between(ETA_SCAN, hv_means - hv_stds, hv_means + hv_stds,
                    alpha=0.3, color='#4C72B0', label='±1σ')
ax4a.plot(ETA_SCAN, hv_means, 'o-', color='#4C72B0', markersize=6, label='Ensemble mean')
# v2.5 reference
v25_hv_eta = [1.1442, 1.1424, 1.1393, 1.1417, 1.1412]
ax4a.plot(ETA_SCAN, v25_hv_eta, 's--', color='red', markersize=5, alpha=0.7, label='v2.5 single-seed')
ax4a.set_xlabel('η')
ax4a.set_ylabel('HV Degradation [×]')
ax4a.set_title('HV at 17 MeV')
ax4a.legend()

ax4b.fill_between(ETA_SCAN, tag_means - tag_stds, tag_means + tag_stds,
                    alpha=0.3, color='#DD8452', label='±1σ')
ax4b.plot(ETA_SCAN, tag_means, 'o-', color='#DD8452', markersize=6, label='Ensemble mean')
v25_tag_eta = [1.4013, 1.4099, 1.6892, 2.7098, 3.4441]
ax4b.plot(ETA_SCAN, v25_tag_eta, 's--', color='red', markersize=5, alpha=0.7, label='v2.5 single-seed')
ax4b.set_xlabel('η')
ax4b.set_ylabel('Tag Degradation [×]')
ax4b.set_title('Tag at 17 MeV')
ax4b.legend()

fig4.tight_layout(rect=[0, 0, 1, 0.93])
fig4.savefig(os.path.join(HERE, 'fig4_eta_band_plot.png'), bbox_inches='tight')
print("  Saved fig4_eta_band_plot.png")


# ===================================================================
# Figure 5: Marginal Result Decision Plots (P3, P7, V3)
# ===================================================================

fig5, (ax5a, ax5b, ax5c) = plt.subplots(1, 3, figsize=(15, 5))
fig5.suptitle('v2.6 Ensemble: Marginal Result Decision Plots', fontsize=13)

# P3: Tag/HV decrease distribution
ax5a.hist(decrease_pct, bins=20, color='#4C72B0', alpha=0.7, edgecolor='white')
ax5a.axvline(3.0, color='red', linestyle='--', linewidth=2, label='Threshold (3%)')
ax5a.axvline(np.mean(decrease_pct), color='black', linestyle='-', linewidth=1.5,
             label=f'Mean = {np.mean(decrease_pct):.2f}%')
ax5a.set_xlabel('Tag/HV Decrease [%]')
ax5a.set_ylabel('Count')
ax5a.set_title('P3: Tag/HV Ratio Decrease')
ax5a.legend(fontsize=8)

# P7: HV deviation from v2.3 baseline at 200 MeV
hv_200_vals = [all_results[i]['E3']['eta20'][0.2]['hv_deg'] for i in range(N_SEEDS)]
dev_pct = [abs(hv / V23_HV_200MEV - 1.0) * 100 for hv in hv_200_vals]
ax5b.hist(dev_pct, bins=20, color='#DD8452', alpha=0.7, edgecolor='white')
ax5b.axvline(3.0, color='red', linestyle='--', linewidth=2, label='Threshold (3%)')
ax5b.axvline(np.mean(dev_pct), color='black', linestyle='-', linewidth=1.5,
             label=f'Mean = {np.mean(dev_pct):.2f}%')
ax5b.set_xlabel('|HV/baseline − 1| [%]')
ax5b.set_ylabel('Count')
ax5b.set_title('P7: HV Deviation at 200 MeV')
ax5b.legend(fontsize=8)

# V3: HV and Tag at 200 MeV vs 1.05 threshold
ax5c.hist(hv_200_vals, bins=15, alpha=0.6, color='#4C72B0', edgecolor='white', label='HV')
tag_200_vals = [all_results[i]['E3']['eta20'][0.2]['tag_deg'] for i in range(N_SEEDS)]
ax5c.hist(tag_200_vals, bins=15, alpha=0.6, color='#DD8452', edgecolor='white', label='Tag')
ax5c.axvline(1.05, color='red', linestyle='--', linewidth=2, label='v2.5 V3 threshold (1.05)')
ax5c.set_xlabel('Degradation [×]')
ax5c.set_ylabel('Count')
ax5c.set_title('v2.5 V3: 200 MeV Convergence')
ax5c.legend(fontsize=8)

fig5.tight_layout(rect=[0, 0, 1, 0.93])
fig5.savefig(os.path.join(HERE, 'fig5_marginal_decisions.png'), bbox_inches='tight')
print("  Saved fig5_marginal_decisions.png")

plt.close('all')
print("\n  All 5 figures saved.")
