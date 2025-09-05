# model_trainer.py — fast-screen Granger (prefix Wald) + p-value labels + fixed multiprocessing pickling
# -------------------------------------------------------------------------------------------------
# Changes in this revision:
# 1) **Fixed multiprocessing error**: moved the ARIMA test worker to a **top-level** function
#    (`arima_test_worker`) so ProcessPoolExecutor can pickle it on macOS/Windows.
# 2) **Heatmap annotations**: the Granger heatmap now prints **p-values in each off-diagonal cell**
#    (diagonal left blank). Values are formatted as 1.2e-5 (for very small) or 0.123 (otherwise),
#    with automatic white/black text color for contrast.
# 3) Kept the fast-screen Granger pipeline (screening + single-fit prefix Wald), caches, and all plots.
# -------------------------------------------------------------------------------------------------

import os
import json
import math
import warnings
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA

from concurrent.futures import ProcessPoolExecutor, as_completed
import joblib

FIG_DIR = "figures"
MODEL_DIR = "models"
PNG_DIR = "pngs"

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

# -------------------------------------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------------------------------------

def find_dataset(user_path: str = None) -> str:
    candidates = [
        user_path,
        'data/combined_spike_periods_vcm3_ft509_edc_all_timestamps_fixed.csv',
        '/mnt/data/combined_spike_periods_vcm3_ft509_edc_all_timestamps_fixed.csv',
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    raise FileNotFoundError('CSV not found: combined_spike_periods_vcm3_ft509_edc_all_timestamps_fixed.csv')


def get_file_mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)
    except Exception:
        return -1.0


def savefig_safe(path: str, dpi: int = 150):
    try:
        plt.savefig(path, dpi=dpi, bbox_inches='tight')
    finally:
        plt.close()

# -------------------------------------------------------------------------------------------------
# Fast Granger helpers
# -------------------------------------------------------------------------------------------------

def _zscore(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    m = np.nanmean(a)
    s = np.nanstd(a)
    if not np.isfinite(s) or s == 0:
        return a * 0.0
    return (a - m) / s


def quick_ccf_screen(y: pd.Series, x: pd.Series, max_lag: int) -> Tuple[float, int]:
    """Return (score, best_lag) where score = max abs corr for l=1..max_lag (X leads Y)."""
    yv = y.values.astype(float)
    xv = x.values.astype(float)
    best = 0.0; bestlag = 1
    for l in range(1, max_lag + 1):
        y_s = yv[l:]
        x_s = xv[:-l]
        if len(y_s) < 20:
            break
        mask = np.isfinite(y_s) & np.isfinite(x_s)
        if mask.sum() < 20:
            continue
        c = np.corrcoef(_zscore(y_s[mask]), _zscore(x_s[mask]))
        r = abs(c[0,1]) if c.shape == (2,2) else 0.0
        if r > best:
            best = r; bestlag = l
    return float(best), int(bestlag)


def _build_lag_df(y: pd.Series, x: pd.Series, Py: int, L: int) -> Tuple[pd.DataFrame, List[str], List[str]]:
    df = pd.DataFrame({'y': y})
    y_cols, x_cols = [], []
    for i in range(1, Py+1):
        col = f'y_lag{i}'; df[col] = y.shift(i); y_cols.append(col)
    for j in range(1, L+1):
        col = f'x_lag{j}'; df[col] = x.shift(j); x_cols.append(col)
    df = df.dropna()
    return df, y_cols, x_cols


def granger_prefix_wald(y: pd.Series, x: pd.Series, Py: int, L: int) -> Tuple[List[float], List[float]]:
    """Fit OLS once with all lags, then compute prefix Wald F-tests for X lags 1..L."""
    try:
        df, y_cols, x_cols = _build_lag_df(y, x, Py, L)
        if len(df) < max(50, Py + L + 5):
            return [np.nan]*L, [np.nan]*L
        Y = df['y'].values
        X = sm.add_constant(df[y_cols + x_cols].values, has_constant='add')
        res = sm.OLS(Y, X).fit()
        k = X.shape[1]
        x_start = 1 + len(y_cols)
        pvals, fvals = [], []
        for l in range(1, L+1):
            R = np.zeros((l, k))
            for r in range(l):
                R[r, x_start + r] = 1.0
            try:
                ft = res.f_test(R)
                pvals.append(float(ft.pvalue))
                fvals.append(float(np.nan if ft.fvalue is None else np.asarray(ft.fvalue).ravel()[0]))
            except Exception:
                pvals.append(np.nan); fvals.append(np.nan)
        return pvals, fvals
    except Exception:
        return [np.nan]*L, [np.nan]*L


def granger_single_lag(y: pd.Series, x: pd.Series, Py: int, lag: int) -> Tuple[float, float]:
    try:
        df = pd.DataFrame({'y': y})
        for i in range(1, Py+1):
            df[f'y_lag{i}'] = y.shift(i)
        df['x_lag'] = x.shift(lag)
        df = df.dropna()
        if len(df) < max(40, Py + 6):
            return np.nan, np.nan
        Y = df['y'].values
        X = sm.add_constant(df.drop(columns=['y']).values, has_constant='add')
        res = sm.OLS(Y, X).fit()
        k = X.shape[1]
        R = np.zeros((1, k)); R[0, -1] = 1.0
        ft = res.f_test(R)
        p = float(ft.pvalue); F = float(np.asarray(ft.fvalue).ravel()[0])
        return p, F
    except Exception:
        return np.nan, np.nan


def _worker_pair_full(args):
    (X_name, Y_name, series_X, series_Y, Py, L) = args
    pvals, fvals = granger_prefix_wald(series_Y, series_X, Py, L)
    arr = np.array(pvals, dtype=float)
    return (X_name, Y_name, float(np.nanmin(arr)), int(np.nanargmin(arr)+1) if np.isfinite(arr).any() else None, pvals, fvals)


def _worker_pair_single(args):
    (X_name, Y_name, series_X, series_Y, Py, bestlag) = args
    p, F = granger_single_lag(series_Y, series_X, Py, bestlag)
    return (X_name, Y_name, p, bestlag, [np.nan]*max(0,bestlag-1) + [p], [np.nan]*max(0,bestlag-1) + [F])

# -------------------------------------------------------------------------------------------------
# ARIMA top-level worker (fixes pickling error)
# -------------------------------------------------------------------------------------------------

def arima_test_worker(args):
    """Top-level worker for ARIMA test plots (picklable).
    args = (series_idx_values, series_values, label, out_png, model_path, model_dir)
    Returns a small dict summarizing metrics or status.
    """
    (series_idx_values, series_values, label, out_png, model_path, model_dir) = args
    import numpy as _np
    import pandas as _pd
    from statsmodels.tsa.arima.model import ARIMA as _ARIMA
    from sklearn.metrics import mean_squared_error as _mse, r2_score as _r2
    import matplotlib.pyplot as _plt
    import joblib as _joblib
    try:
        series = _pd.Series(series_values, index=_pd.to_datetime(series_idx_values)).dropna()
        if len(series) < 200:
            return {'status': 'short', 'var': label}
        n = len(series); n_test = max(100, int(n*0.3))
        tr, te = series.iloc[:-n_test], series.iloc[-n_test:]
        model = None; order_used = None
        if model_path and os.path.exists(model_path):
            try:
                model = _joblib.load(model_path); order_used = 'reused'
                fc = model.forecast(steps=len(te))
            except Exception:
                model = None
        if model is None:
            best_aic, best_order, best_model = _np.inf, None, None
            for p in range(0,3):
                for d in range(0,2):
                    for q in range(0,3):
                        try:
                            m = _ARIMA(tr.astype(float), order=(p,d,q)).fit()
                            if m.aic < best_aic:
                                best_aic, best_order, best_model = m.aic, (p,d,q), m
                        except Exception:
                            continue
            if best_model is None:
                return {'status': 'fit_fail', 'var': label}
            fc = best_model.forecast(steps=len(te))
            order_used = str(best_order)
            try: _joblib.dump(best_model, os.path.join(model_dir, f'ARIMA_model_{label}_autotrain.joblib'))
            except Exception: pass
        mse = _mse(te.values, _np.array(fc)); r2 = _r2(te.values, _np.array(fc))
        _plt.figure(figsize=(14,4))
        _plt.plot(te.index, te.values, label=f'Actual — {label}')
        _plt.plot(te.index, fc, label=f'ARIMA {order_used} — MSE={mse:.3f}, R²={r2:.3f}', linestyle='--')
        _plt.title(f'ARIMA test prediction — {label}')
        _plt.xlabel('Time'); _plt.ylabel(label); _plt.legend(); _plt.grid(True, linestyle=':')
        _plt.savefig(out_png, dpi=150, bbox_inches='tight'); _plt.close()
        return {'status': 'ok', 'var': label, 'mse': float(mse), 'r2': float(r2)}
    except Exception as e:
        return {'status': 'error', 'var': label, 'msg': str(e)}

# -------------------------------------------------------------------------------------------------
# Main trainer class
# -------------------------------------------------------------------------------------------------
class ModelTrainer:
    def __init__(self, data_path: str = None,
                 max_lag: int = 48, y_lags: int = 8,
                 top_k_per_target: int = 6, top_k_for_edc: int = 8,
                 resample_minutes: Optional[int] = None,
                 n_jobs: Optional[int] = None):
        self.data_path = find_dataset(data_path)
        self.data_mtime = get_file_mtime(self.data_path)
        self.max_lag = int(max_lag)
        self.y_lags = int(y_lags)
        self.top_k_per_target = int(top_k_per_target)
        self.top_k_for_edc = int(top_k_for_edc)
        self.resample_minutes = resample_minutes
        self.n_jobs = n_jobs or max(1, os.cpu_count() - 1)

        df = pd.read_csv(self.data_path)
        if 'time' not in df.columns:
            raise ValueError("CSV missing 'time' column")
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time').reset_index(drop=True)
        df.replace('No Data', np.nan, inplace=True)
        for c in df.columns:
            if c != 'time':
                df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.ffill().bfill()

        if self.resample_minutes:
            dfi = df.set_index('time')
            df = dfi.resample(f'{self.resample_minutes}T').mean().ffill().bfill().reset_index()

        self.df = df

        # Column names
        self.col_EDC = 'EDC'
        self.col_STEAM = 'LVCM2-FC503AS.PV'
        self.col_FEED_FLOW = 'LVCM2-FC503F'
        self.col_FEED_TEMP = 'LVCM-TI-C503A-I.PV'
        self.col_TOP_TEMP = 'LVCM2-TC503T'
        self.col_BOTTOM_TEMP = 'LVCM2-TC503B'
        self.col_TOP_PRESS = 'LVCM-PI-C503A-T.PV'
        self.col_BOTTOM_PRESS = 'LVCM-PI-C503A-B.PV'
        self.col_LEVEL = 'LVCM2-LC503'

        # English aliases for plots
        self.alias = {
            self.col_FEED_TEMP: 'Feed Temperature',
            self.col_BOTTOM_TEMP: 'Bottom Temperature',
            self.col_TOP_TEMP: 'Top Temperature',
            self.col_LEVEL: 'Level',
            self.col_FEED_FLOW: 'Feed Flow',
            self.col_TOP_PRESS: 'Top Pressure',
            self.col_BOTTOM_PRESS: 'Bottom Pressure',
            self.col_STEAM: 'Steam Usage',
            self.col_EDC: 'EDC',
        }

        preferred_order = [
            self.col_FEED_TEMP, self.col_BOTTOM_TEMP, self.col_TOP_TEMP, self.col_LEVEL,
            self.col_FEED_FLOW, self.col_TOP_PRESS, self.col_BOTTOM_PRESS, self.col_STEAM, self.col_EDC
        ]
        self.study_cols = [c for c in preferred_order if c in df.columns]
        self.rtmps_cols = [c for c in df.columns if c not in ['time', self.col_EDC]]

    # --------------------- A. Raw plots ---------------------
    def plot_raw_two_figures(self):
        outA = os.path.join(FIG_DIR, 'fig_raw_A_timeseries.png')
        outB = os.path.join(FIG_DIR, 'fig_raw_B_timeseries.png')
        if os.path.exists(outA) and os.path.exists(outB):
            print('[Raw] A/B plots exist. Skipping.')
            return
        dfi = self.df.set_index('time')
        left_A = [self.col_FEED_TEMP, self.col_BOTTOM_TEMP, self.col_TOP_TEMP, self.col_LEVEL, self.col_FEED_FLOW]
        left_A = [v for v in left_A if v in dfi.columns]
        if left_A and self.col_EDC in dfi.columns and not os.path.exists(outA):
            plt.figure(figsize=(14,5))
            for v in left_A:
                plt.plot(dfi.index, dfi[v], label=self.alias.get(v, v), linewidth=1)
            ax1 = plt.gca(); ax2 = ax1.twinx()
            ax2.plot(dfi.index, dfi[self.col_EDC], label='EDC', linewidth=1.2, alpha=0.8, linestyle='--')
            ax1.set_title('Raw data (Temps/Level/Feed flow) + EDC (right axis) — Figure A')
            ax1.set_xlabel('Time'); ax1.set_ylabel('Process values'); ax2.set_ylabel('EDC (ppm)')
            ax1.legend(loc='upper left', ncol=2)
            savefig_safe(outA); print('[Raw] Saved:', outA)
        left_B = [self.col_TOP_PRESS, self.col_BOTTOM_PRESS, self.col_STEAM]
        left_B = [v for v in left_B if v in dfi.columns]
        if left_B and self.col_EDC in dfi.columns and not os.path.exists(outB):
            plt.figure(figsize=(14,5))
            for v in left_B:
                plt.plot(dfi.index, dfi[v], label=self.alias.get(v, v), linewidth=1)
            ax1 = plt.gca(); ax2 = ax1.twinx()
            ax2.plot(dfi.index, dfi[self.col_EDC], label='EDC', linewidth=1.2, alpha=0.8, linestyle='--')
            ax1.set_title('Raw data (Pressures/Steam) + EDC (right axis) — Figure B')
            ax1.set_xlabel('Time'); ax1.set_ylabel('Process values'); ax2.set_ylabel('EDC (ppm)')
            ax1.legend(loc='upper left')
            savefig_safe(outB); print('[Raw] Saved:', outB)

    # --------------------- B. Fast Granger (screen + single-fit) ---------------------
    def granger_fast_matrix_and_top4(self):
        heatmap_png = os.path.join(FIG_DIR, 'fig_granger_heatmap.png')
        top4_png = os.path.join(FIG_DIR, 'fig_granger_top4_lag_curves.png')
        cache_path = os.path.join(MODEL_DIR, 'granger_matrix_fast.joblib')

        # Cache check
        if os.path.exists(heatmap_png) and os.path.exists(cache_path):
            meta = joblib.load(cache_path)
            if meta.get('data_mtime') == get_file_mtime(self.data_path) and \
               meta.get('params') == (self.max_lag, self.y_lags, self.top_k_per_target, self.top_k_for_edc, self.resample_minutes) and \
               meta.get('cols') == self.study_cols:
                print('[Granger] Using cached fast matrix.')
                if not os.path.exists(top4_png) and 'edc_records' in meta:
                    self._plot_top4_curves_from_records(meta['edc_records'], top4_png)
                # Still re-annotate p-values if heatmap exists? Cache already has matrix; we assume saved figure already annotated.
                return meta.get('matrix')

        dfi = self.df.set_index('time')[self.study_cols].dropna(how='all')
        cols = self.study_cols
        k = len(cols)
        if k < 2:
            print('[Granger] Not enough variables. Skipping.')
            return None

        # 1) SCREENING by quick cross-correlation (X leads Y)
        print('[Granger] Screening pairs by cross-correlation…')
        screen_scores = { (X,Y): (0.0, 1) for Y in cols for X in cols if X!=Y }
        for Y in cols:
            y = dfi[Y].astype(float)
            for X in cols:
                if X == Y: continue
                x = dfi[X].astype(float)
                score, lag = quick_ccf_screen(y, x, self.max_lag)
                screen_scores[(X,Y)] = (score, lag)

        # pick top-k per target Y; ensure EDC gets top_k_for_edc
        keep_pairs = set()
        for Y in cols:
            ranked = sorted([(X, screen_scores[(X,Y)][0]) for X in cols if X!=Y], key=lambda t:-np.nan_to_num(t[1]))
            take = self.top_k_for_edc if Y == self.col_EDC else self.top_k_per_target
            keep = [X for X,_ in ranked[:take]]
            for X in keep:
                keep_pairs.add((X,Y))

        # 2) Compute full prefix-Wald for kept pairs, and cheap single-lag for others
        print('[Granger] Running workers (full for kept pairs; single-lag for the rest)…')
        results: Dict[Tuple[str,str], Tuple[float,int,List[float],List[float]]] = {}
        edc_records: Dict[str, Tuple[List[float], List[float]]] = {}

        tasks = []
        with ProcessPoolExecutor(max_workers=self.n_jobs) as exe:
            # full
            for (X,Y) in keep_pairs:
                tasks.append(exe.submit(_worker_pair_full, (X, Y, dfi[X].astype(float), dfi[Y].astype(float), self.y_lags, self.max_lag)))
            # single-lag
            for (X,Y), (score, bestlag) in screen_scores.items():
                if (X,Y) in keep_pairs: continue
                tasks.append(exe.submit(_worker_pair_single, (X, Y, dfi[X].astype(float), dfi[Y].astype(float), self.y_lags, int(bestlag))))

            for fut in as_completed(tasks):
                X, Y, min_p, best_lag, pvals, fvals = fut.result()
                results[(X,Y)] = (min_p, best_lag, pvals, fvals)
                if Y == self.col_EDC:
                    edc_records[X] = (pvals, fvals)

        # 3) Assemble matrix and plots
        M = np.full((k,k), np.nan)
        for j, Y in enumerate(cols):
            for i, X in enumerate(cols):
                if X == Y: continue
                tup = results.get((X,Y))
                if tup is None: continue
                M[j,i] = tup[0]

        # heatmap with p-value labels
        M_plot = np.clip(M.copy(), 1e-300, 1.0)
        plt.figure(figsize=(max(10, k*1.4), max(7, k*1.1)))
        im = plt.imshow(-np.log10(M_plot), aspect='auto')
        cbar = plt.colorbar(im, label='-log10(p-value) (min across lags; full for screened pairs, single-lag otherwise)')
        xt = [self.alias.get(c,c) for c in cols]; yt = [self.alias.get(c,c) for c in cols]
        plt.xticks(range(k), xt, rotation=45, ha='right'); plt.yticks(range(k), yt)
        plt.xlabel('X (cause)'); plt.ylabel('Y (effect)')
        plt.title('Granger causality — fast-screen (prefix Wald for kept pairs)')
        # annotate p-values (off-diagonal only)
        clim = im.get_clim(); vmin, vmax = clim[0], clim[1]
        for j in range(k):
            for i in range(k):
                if i == j: continue
                p = M[j, i]
                if not np.isfinite(p):
                    continue
                txt = f"{p:.1e}" if p < 1e-3 else f"{p:.3f}"
                val = -np.log10(max(p, 1e-300))
                # choose white text on dark cells
                color = 'white' if (val > (vmax * 0.6)) else 'black'
                plt.text(i, j, txt, ha='center', va='center', fontsize=7, color=color)
        savefig_safe(heatmap_png); print('[Granger] Saved:', heatmap_png)

        # top-4 curves for Y=EDC (ensure curves exist → if a pair only had single-lag, compute full now)
        if self.col_EDC in cols:
            ranking = sorted([(x, np.nanmin(np.array(p))) for x,(p,f) in edc_records.items()], key=lambda t: np.nan_to_num(t[1]))
            need_full = [x for x,_ in ranking[:4] if (x,self.col_EDC) not in keep_pairs]
            if need_full:
                with ProcessPoolExecutor(max_workers=min(self.n_jobs, len(need_full))) as exe2:
                    futs = [exe2.submit(_worker_pair_full, (x, self.col_EDC, dfi[x].astype(float), dfi[self.col_EDC].astype(float), self.y_lags, self.max_lag)) for x in need_full]
                    for fut in as_completed(futs):
                        X, Y, min_p, best_lag, pvals, fvals = fut.result()
                        edc_records[X] = (pvals, fvals)
                        results[(X,Y)] = (min_p, best_lag, pvals, fvals)

            self._plot_top4_curves_from_records(edc_records, top4_png)

        joblib.dump({
            'data_mtime': get_file_mtime(self.data_path),
            'params': (self.max_lag, self.y_lags, self.top_k_per_target, self.top_k_for_edc, self.resample_minutes),
            'cols': cols,
            'matrix': M,
            'edc_records': edc_records,
            'screen_scores': screen_scores,
            'kept_pairs': list(keep_pairs),
        }, cache_path)
        return M

    def _plot_top4_curves_from_records(self, edc_records: Dict[str, Tuple[List[float], List[float]]], out_png: str):
        if not edc_records:
            return
        ranking = []
        for x, (pvals, _fvals) in edc_records.items():
            arr_p = np.array(pvals, dtype=float)
            if arr_p.size == 0:
                continue
            ranking.append((x, np.nanmin(arr_p)))
        if not ranking:
            return
        ranking.sort(key=lambda t: np.nan_to_num(t[1]))
        top4 = [x for x,_ in ranking[:4]]

        fig, axes = plt.subplots(2, 2, figsize=(14,8), sharex=True)
        axes = axes.ravel()
        for i, x in enumerate(top4):
            pvals, fvals = edc_records.get(x, ([], []))
            lags = range(1, 1+len(pvals))
            ax1 = axes[i]
            ax1.plot(lags, fvals, label='F-stat', linewidth=1.3)
            ax1.set_ylabel('F-stat (left)')
            ax1.set_title(f'Lag scan: {self.alias.get(x,x)} → EDC')
            ax2 = ax1.twinx()
            ax2.plot(lags, pvals, linestyle='--', alpha=0.8, label='p-value')
            ax2.set_ylabel('p-value (right)')
            ax1.grid(True, linestyle=':')
        for ax in axes: ax.set_xlabel('lag (10-min steps)')
        fig.tight_layout(); savefig_safe(out_png); print('[Granger] Saved:', out_png)

    # --------------------- C. RF Top-10 ---------------------
    def create_lag_features(self, df: pd.DataFrame, target_col: str = 'EDC', max_lag: int = 48) -> pd.DataFrame:
        if 'time' not in df.columns or target_col not in df.columns:
            raise ValueError("create_lag_features requires 'time' and target")
        lagged = df.copy(); numeric_cols = [c for c in df.columns if c != 'time']
        feats = [c for c in numeric_cols if c != target_col]
        for lag in range(1, max_lag + 1):
            for var in feats:
                lagged[f'{var}_lag{lag}'] = df[var].shift(lag)
        lagged = lagged.dropna().reset_index(drop=True)
        return lagged

    def rf_feature_importance_top10_plot(self):
        out_png = os.path.join(FIG_DIR, 'fig_rf_top10_lag_importances.png')
        cache_json = os.path.join(MODEL_DIR, 'rf_top10_importances.json')
        if os.path.exists(out_png) and os.path.exists(cache_json):
            print('[RF] Top-10 figure and cache exist. Skipping.')
            return
        have_cols = [c for c in [self.col_EDC] + self.rtmps_cols if c in self.df.columns]
        df = self.df[['time'] + have_cols].copy()
        lagged = self.create_lag_features(df, target_col=self.col_EDC, max_lag=self.max_lag)
        if lagged.empty:
            print('[RF] Empty lagged frame. Skipping.')
            return
        X = lagged.drop(columns=['time', self.col_EDC]); y = lagged[self.col_EDC]
        n = len(lagged); idx = int(n*0.7)
        X_tr, y_tr = X.iloc[:idx], y.iloc[:idx]
        rf = RandomForestRegressor(n_estimators=50, random_state=42, warm_start=True, n_jobs=-1)
        for trees in [50, 100, 150]:
            rf.set_params(n_estimators=trees); rf.fit(X_tr, y_tr)
        imps = rf.feature_importances_
        names = []
        for f in X.columns:
            if '_lag' in f:
                base, lag = f.split('_lag',1)
                names.append(self.alias.get(base, base) + '_lag' + lag)
            else:
                names.append(self.alias.get(f, f))
        names = np.array(names)
        top = np.argsort(imps)[::-1][:10]
        plt.figure(figsize=(10,5)); y_pos = np.arange(len(top))
        plt.barh(y_pos, imps[top]); plt.gca().invert_yaxis(); plt.yticks(y_pos, names[top])
        plt.xlabel('Feature importance'); plt.title('Top-10 lagged RTMPS for EDC (RF)')
        savefig_safe(out_png); print('[RF] Saved:', out_png)
        with open(cache_json, 'w', encoding='utf-8') as f:
            json.dump({'features': names[top].tolist(), 'importances': [float(v) for v in imps[top]],
                       'data_mtime': get_file_mtime(self.data_path)}, f, ensure_ascii=False, indent=2)

    # --------------------- D. ARIMA test plots (now uses top-level worker) ---------------------
    def _find_existing_arima_model_path(self, col_raw: str) -> Optional[str]:
        latest, mt = None, -1
        if not os.path.exists(MODEL_DIR): return None
        for root, _, files in os.walk(MODEL_DIR):
            for fn in files:
                if fn.endswith('.joblib') and (fn.startswith('ARIMA_model_') or fn.startswith('next_ARIMA_model_')):
                    if col_raw in fn:
                        p = os.path.join(root, fn); t = get_file_mtime(p)
                        if t > mt: latest, mt = p, t
        return latest

    def arima_test_plots_for_vars(self):
        targets = [self.col_FEED_FLOW, self.col_FEED_TEMP, self.col_STEAM,
                   self.col_BOTTOM_TEMP, self.col_TOP_TEMP,
                   self.col_BOTTOM_PRESS, self.col_TOP_PRESS, self.col_LEVEL]
        dfi = self.df.set_index('time')
        tasks = []; results = []
        with ProcessPoolExecutor(max_workers=self.n_jobs) as exe:
            for v in targets:
                if v not in dfi.columns: continue
                out_png = os.path.join(FIG_DIR, f'fig_arima_test_{self.alias.get(v,v)}.png')
                if os.path.exists(out_png):
                    print(f'[ARIMA] {self.alias.get(v,v)} exists. Skipping.')
                    continue
                series = dfi[v].dropna()
                if len(series) < 200: continue
                existing = self._find_existing_arima_model_path(v)
                args = (series.index.values.astype('datetime64[ns]'), series.values.astype(float),
                        self.alias.get(v,v), out_png, existing, MODEL_DIR)
                tasks.append(exe.submit(arima_test_worker, args))
            for fut in as_completed(tasks):
                results.append(fut.result())
        with open(os.path.join(MODEL_DIR, 'arima_test_summary.json'), 'w', encoding='utf-8') as f:
            json.dump({'results': results, 'data_mtime': get_file_mtime(self.data_path)}, f, ensure_ascii=False, indent=2)

    # --------------------- E. EDC RF test & combined ---------------------
    def edc_incremental_rf_test_plot(self):
        out_png = os.path.join(FIG_DIR, 'fig_edc_incremental_test.png')
        out_npz = os.path.join(MODEL_DIR, 'edc_incremental_test.npz')
        if os.path.exists(out_png) and os.path.exists(out_npz):
            print('[EDC-RF] Plot/cache exist. Skipping.')
            return
        have_cols = [c for c in [self.col_EDC] + self.rtmps_cols if c in self.df.columns]
        df = self.df[['time'] + have_cols].copy()
        lagged = self.create_lag_features(df, target_col=self.col_EDC, max_lag=self.max_lag)
        if lagged.empty:
            print('[EDC-RF] Empty lag frame. Skipping.')
            return
        X = lagged.drop(columns=['time', self.col_EDC]); y = lagged[self.col_EDC]
        n = len(lagged); idx = int(n*0.7)
        X_tr, y_tr = X.iloc[:idx], y.iloc[:idx]
        X_te, y_te = X.iloc[idx:], y.iloc[idx:]
        rf = RandomForestRegressor(n_estimators=50, random_state=42, warm_start=True, n_jobs=-1)
        for trees in [50, 100, 150, 200]:
            rf.set_params(n_estimators=trees); rf.fit(X_tr, y_tr)
        yhat = rf.predict(X_te)
        mse = mean_squared_error(y_te, yhat); r2 = r2_score(y_te, yhat)
        t_axis = lagged['time'].iloc[idx:]
        plt.figure(figsize=(14,4))
        plt.plot(t_axis, y_te.values, label='Actual — EDC')
        plt.plot(t_axis, yhat, label=f'RF — MSE={mse:.3f}, R²={r2:.3f}', linestyle='--')
        plt.title('EDC test prediction — RF with lagged RTMPS')
        plt.xlabel('Time'); plt.ylabel('EDC (ppm)')
        plt.legend(); plt.grid(True, linestyle=':')
        savefig_safe(out_png)
        np.savez_compressed(out_npz, t=np.array(t_axis.values.astype('datetime64[ns]')), y=y_te.values, yhat=yhat,
                            mse=float(mse), r2=float(r2))

    def combined_varima_rf_performance_plot(self):
        out_png = os.path.join(FIG_DIR, 'fig_varima_rf_test.png')
        if os.path.exists(out_png):
            print('[Combo] Combined figure exists. Skipping.')
            return
        self.edc_incremental_rf_test_plot()
        edc_npz = os.path.join(MODEL_DIR, 'edc_incremental_test.npz')
        if not os.path.exists(edc_npz):
            print('[Combo] Missing EDC cache. Skipping combined figure.')
            return
        data = np.load(edc_npz, allow_pickle=True)
        t_edc = pd.to_datetime(data['t']); y_edc = data['y']; yhat_edc = data['yhat']
        mse_edc = float(data.get('mse', np.nan)); r2_edc = float(data.get('r2', np.nan))

        dfi = self.df.set_index('time')
        if self.col_STEAM not in dfi.columns: return
        s = dfi[self.col_STEAM].dropna(); N = len(s)
        if N < 200: return
        n_test = max(100, int(N*0.3)); tr, te = s.iloc[:-n_test], s.iloc[-n_test:]
        best_aic, best_order, best_model = np.inf, None, None
        for p in range(0,3):
            for d in range(0,2):
                for q in range(0,3):
                    try:
                        m = ARIMA(tr.astype(float), order=(p,d,q)).fit()
                        if m.aic < best_aic: best_aic, best_order, best_model = m.aic, (p,d,q), m
                    except Exception: continue
        if best_model is None: return
        fc = best_model.forecast(steps=len(te))
        mse_steam = mean_squared_error(te.values, np.array(fc)); r2_steam = r2_score(te.values, np.array(fc))
        try: joblib.dump(best_model, os.path.join(MODEL_DIR, f'ARIMA_model_{self.col_STEAM}_autotrain.joblib'))
        except Exception: pass

        fig, axes = plt.subplots(2,1, figsize=(14,8), sharex=False)
        axes[0].plot(t_edc, y_edc, label='Actual — EDC')
        axes[0].plot(t_edc, yhat_edc, label=f'RF — MSE={mse_edc:.3f}, R²={r2_edc:.3f}', linestyle='--')
        axes[0].set_title('EDC — RF (test)'); axes[0].set_ylabel('EDC (ppm)'); axes[0].legend(); axes[0].grid(True, linestyle=':')
        axes[1].plot(te.index, te.values, label='Actual — Steam Usage')
        axes[1].plot(te.index, fc, label=f'ARIMA {best_order} — MSE={mse_steam:.3f}, R²={r2_steam:.3f}', linestyle='--')
        axes[1].set_title('Steam Usage — ARIMA (test)'); axes[1].set_xlabel('Time'); axes[1].set_ylabel('Steam Usage')
        axes[1].legend(); axes[1].grid(True, linestyle=':')
        fig.tight_layout(); savefig_safe(out_png)

    # --------------------- Entry ---------------------
    def run(self):
        self.plot_raw_two_figures()
        self.granger_fast_matrix_and_top4()
        self.rf_feature_importance_top10_plot()
        self.arima_test_plots_for_vars()
        self.edc_incremental_rf_test_plot()
        self.combined_varima_rf_performance_plot()
        print('\n[Done] All plots written; fast-screen Granger used.')


if __name__ == '__main__':
    # Tip: if you see CPU oversubscription, set these **before** importing numpy/scipy/statsmodels:
    #   os.environ['OMP_NUM_THREADS'] = '1'
    #   os.environ['MKL_NUM_THREADS'] = '1'
    trainer = ModelTrainer(
        data_path=None,
        max_lag=48,     # up to 8 hours of 10-min lags
        y_lags=8,       # Y autoregressive lags
        top_k_per_target=6,
        top_k_for_edc=8,
        resample_minutes=None,
        n_jobs=None,
    )
    trainer.run()
