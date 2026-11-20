"""v2.1 likelihood material tag (preregistered). Pure function of the measured vertex radius r_m [mm], the per-pair reported
radial resolution sigma_r [mm] and the opening-angle statistic dchi2 (Delta chi2_3D); no truth information.
  p_conv(r) = sum_b c_b * [Phi((r - R_b + HW_b)/s) - Phi((r - R_b - HW_b)/s)] / (2 HW_b),  c_b ∝ X0_b, sum_b c_b = 1
  p_sig(r)  = 1 / (800 - 0.5) mm^-1 on the base-selection range (flat, signal-agnostic)
  lambda    = dchi2 / 2 + ln[p_sig(r) / p_conv(r)]          (pairs without a valid dchi2 use dchi2 = 0)"""
import numpy as np
from scipy.special import ndtr

BANDS = [(22, 0.003, 0.5), (29, 0.02, 3), (68, 0.02, 3), (109, 0.02, 3), (160, 0.02, 3), (185, 0.05, 5),
         (255, 0.04, 4), (339, 0.04, 4), (418, 0.04, 4), (498, 0.04, 4), (550, 0.08, 10),
         (608, 0.03, 4), (692, 0.03, 4), (780, 0.03, 4)]          # (radius, X0 at f = 1, half-width) as bkg.py
R_LO, R_HI = 0.5, 800.0
P_FLOOR = 1e-300


def p_conv(r, s, bands=BANDS):
    R = np.array([b[0] for b in bands], float); X = np.array([b[1] for b in bands], float); H = np.array([b[2] for b in bands], float)
    c = X / X.sum()
    r = np.asarray(r, float)[..., None]; s = np.maximum(np.asarray(s, float), 1e-6)[..., None]
    return (c * (ndtr((r - R + H) / s) - ndtr((r - R - H) / s)) / (2 * H)).sum(-1)


def p_sig(r):
    return np.full(np.shape(r), 1.0 / (R_HI - R_LO))


def lam(r, s, dchi2):
    d = np.where(np.isfinite(dchi2), dchi2, 0.0)
    return 0.5 * d + np.log(p_sig(r)) - np.log(np.maximum(p_conv(r, s), P_FLOOR))


TGRID = (None, -4.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 25.0)   # None = no cut
