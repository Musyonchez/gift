"""STA 3050 Term Paper: forecasting the global (Kenya-benchmark) tea price.
Data: IMF/FRED PTEAUSDM, monthly, US cents per kg, 1992-01 to 2026-07 (tea_price_monthly.csv).
Run: python ts_analysis.py  -> prints results (results.txt), saves figures to figs/, results.json
"""
import json, os, time, warnings
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal, stats
from statsmodels.tsa.stattools import adfuller, kpss, acf, pacf
from statsmodels.tsa.seasonal import STL, seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
warnings.filterwarnings("ignore")
SEED = 42
np.random.seed(SEED)
sns.set_theme(style="whitegrid")
os.makedirs("figs", exist_ok=True)
R = {}  # results store

df = pd.read_csv("tea_price_monthly.csv", parse_dates=[0], index_col=0)
y = df["PTEAUSDM"].asfreq("MS")
y.name = "tea_price"
print("=== 1. DATA ===")
print("Observations:", len(y), "| from", y.index.min().date(), "to", y.index.max().date(), "| missing:", int(y.isna().sum()))
print(y.describe().round(2).to_string())
R["n"] = len(y)
yr = y.resample("YS").mean()
print("\nAnnual mean price (cents/kg), selected years:")
print(yr.loc[[pd.Timestamp(f"{k}-01-01") for k in [1992, 2000, 2008, 2011, 2014, 2020, 2022, 2025]]].round(1).to_string())
print("Largest monthly value: %s %.1f | Smallest: %s %.1f" % (y.idxmax().date(), y.max(), y.idxmin().date(), y.min()))
print("Skewness %.3f, excess kurtosis %.3f" % (stats.skew(y), stats.kurtosis(y)))

# ---------- EDA figures
fig, ax = plt.subplots(2, 1, figsize=(10, 6.5))
ax[0].plot(y, color="#2a7f3b", lw=1.1, label="Monthly price")
ax[0].plot(y.rolling(12).mean(), color="#c0392b", lw=1.8, label="12-month moving average")
ax[0].set_title("Fig 1a: Global tea price, monthly (US cents/kg)"); ax[0].set_ylabel("US cents per kg"); ax[0].legend()
ax[1].plot(np.log(y), color="#2a7f3b", lw=1.1)
ax[1].set_title("Fig 1b: Log of tea price"); ax[1].set_ylabel("log(price)"); ax[1].set_xlabel("Date")
plt.tight_layout(); plt.savefig("figs/fig1_series.png", dpi=150); plt.close()

# seasonal view
tmp = y.to_frame(); tmp["year"] = tmp.index.year; tmp["month"] = tmp.index.month
ratio = (y / y.rolling(12, center=True).mean()).dropna()  # seasonal ratio
rm = ratio.groupby(ratio.index.month).agg(["mean", "std"])
print("\nAverage seasonal ratio (price / centred 12-month mean) by month:")
print(rm.round(4).to_string())
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
sns.boxplot(x=ratio.index.month, y=ratio.values, ax=ax[0], color="#8fd19e")
ax[0].axhline(1, color="k", lw=0.8); ax[0].set_title("Fig 2a: Seasonal ratio by calendar month"); ax[0].set_xlabel("Month"); ax[0].set_ylabel("Price / 12-month centred mean")
pv = tmp.pivot(index="year", columns="month", values="tea_price")
sns.heatmap(pv, cmap="YlGn", ax=ax[1], cbar_kws={"label": "cents/kg"}); ax[1].set_title("Fig 2b: Price heat-map (year x month)")
plt.tight_layout(); plt.savefig("figs/fig2_seasonal.png", dpi=150); plt.close()
# F-test (ANOVA) for monthly seasonality on detrended ratio
groups = [g.values for _, g in ratio.groupby(ratio.index.month)]
F, p = stats.f_oneway(*groups)
print("One-way ANOVA of seasonal ratio across months: F=%.3f, p=%.4f" % (F, p))
R["anova_p"] = float(p)
kw = stats.kruskal(*groups); print("Kruskal-Wallis: H=%.3f, p=%.4f" % kw)

# ---------- decomposition
stl = STL(np.log(y), period=12, robust=True).fit()
tr_str = max(0, 1 - stl.resid.var() / (stl.trend + stl.resid).var())
se_str = max(0, 1 - stl.resid.var() / (stl.seasonal + stl.resid).var())
print("\nSTL (log scale): strength of trend = %.3f, strength of seasonality = %.3f" % (tr_str, se_str))
R["trend_strength"], R["seasonal_strength"] = float(tr_str), float(se_str)
fig = stl.plot(); fig.set_size_inches(10, 7); fig.suptitle("Fig 3: STL decomposition of log tea price", y=1.0)
plt.tight_layout(); plt.savefig("figs/fig3_stl.png", dpi=150); plt.close()
# ---------- spectral
f, pxx = signal.periodogram(np.log(y).diff().dropna().values, fs=12)  # cycles per year, differenced log
top = np.argsort(-pxx)[:5]
print("\nPeriodogram of log-differences (cycles/year -> period in months), top 5 peaks:")
for i in top: print("  freq %.3f cyc/yr  period %.1f months  power %.5f" % (f[i], 12 / f[i] if f[i] > 0 else np.inf, pxx[i]))
fig, ax = plt.subplots(figsize=(8, 3.5)); ax.plot(f, pxx, color="#2a7f3b"); ax.set_xlabel("Frequency (cycles per year)"); ax.set_ylabel("Power")
ax.set_title("Fig 4: Periodogram of monthly log-returns of the tea price"); plt.tight_layout(); plt.savefig("figs/fig4_periodogram.png", dpi=150); plt.close()

# ---------- stationarity
print("\n=== 2. STATIONARITY TESTS ===")
def tests(s, name):
    a = adfuller(s.dropna(), autolag="AIC")
    k = kpss(s.dropna(), regression="c", nlags="auto")
    print("%-26s ADF stat %7.3f p=%.4f | KPSS stat %6.3f p=%s" % (name, a[0], a[1], k[0], ("%.3f" % k[1]) if 0.01 < k[1] < 0.1 else ("<=0.01" if k[1] <= 0.01 else ">=0.10")))
    return dict(adf_stat=float(a[0]), adf_p=float(a[1]), kpss_stat=float(k[0]), kpss_p=float(k[1]))
ly = np.log(y)
R["stationarity"] = {"level": tests(y, "Level"), "log level": tests(ly, "Log level"), "diff(log)": tests(ly.diff(), "First difference of log"),
                     "diff(level)": tests(y.diff(), "First difference of level"), "seasonal diff(log)": tests(ly.diff(12), "Seasonal diff (12) of log")}
fig, ax = plt.subplots(2, 2, figsize=(11, 6))
plot_acf(ly, lags=48, ax=ax[0, 0], title="Fig 5a: ACF of log price"); plot_pacf(ly, lags=48, ax=ax[0, 1], title="Fig 5b: PACF of log price", method="ywm")
plot_acf(ly.diff().dropna(), lags=48, ax=ax[1, 0], title="Fig 5c: ACF of first difference of log price"); plot_pacf(ly.diff().dropna(), lags=48, ax=ax[1, 1], title="Fig 5d: PACF of first difference of log price", method="ywm")
plt.tight_layout(); plt.savefig("figs/fig5_acf_pacf.png", dpi=150); plt.close()
d1 = ly.diff().dropna()
lb = acorr_ljungbox(d1, lags=[12, 24], return_df=True)
print("Ljung-Box on first difference of log (autocorrelation present if p small):\n", lb.round(4).to_string())
print("ACF of differenced log, lags 1-6:", np.round(acf(d1, nlags=6)[1:], 3), " PACF lags 1-6:", np.round(pacf(d1, nlags=6)[1:], 3))
print("Annualised volatility of monthly log-returns: %.1f%%" % (d1.std() * np.sqrt(12) * 100))
# ARCH effect check
from statsmodels.stats.diagnostic import het_arch
print("ARCH-LM test on log-returns: LM p=%.4f" % het_arch(d1, nlags=6)[1])

# ---------- 3. MODELS
print("\n=== 3. FORECASTING (hold-out: last 36 months) ===")
H = 36
train, test = y.iloc[:-H], y.iloc[-H:]
print("Train: %s to %s (%d) | Test: %s to %s (%d)" % (train.index[0].date(), train.index[-1].date(), len(train), test.index[0].date(), test.index[-1].date(), len(test)))

def metrics(actual, fc, name, extra=None):
    a, f_ = np.asarray(actual), np.asarray(fc)
    e = a - f_
    d = dict(model=name, MAE=np.mean(np.abs(e)), RMSE=np.sqrt(np.mean(e ** 2)), MAPE=np.mean(np.abs(e / a)) * 100)
    d["sMAPE"] = np.mean(2 * np.abs(e) / (np.abs(a) + np.abs(f_))) * 100
    if extra: d.update(extra)
    return d

fcs, rows, fits = {}, [], {}
t_model = {}
def add(name, fc, t0, extra=None):
    fcs[name] = pd.Series(np.asarray(fc), index=test.index); t_model[name] = time.time() - t0
    rows.append(metrics(test, fc, name, extra))

t0 = time.time(); add("Naive (last value)", np.repeat(train.iloc[-1], H), t0)
t0 = time.time(); add("Seasonal naive", np.tile(train.iloc[-12:].values, H // 12 + 1)[:H], t0)
t0 = time.time(); add("Drift", train.iloc[-1] + (train.iloc[-1] - train.iloc[0]) / (len(train) - 1) * np.arange(1, H + 1), t0)
t0 = time.time(); m = SimpleExpSmoothing(train, initialization_method="estimated").fit(); fits["SES"] = m; add("Simple exp. smoothing", m.forecast(H), t0)
t0 = time.time(); m = ExponentialSmoothing(train, trend="add", damped_trend=True, initialization_method="estimated").fit(); fits["Holt"] = m; add("Holt (damped trend)", m.forecast(H), t0)
t0 = time.time(); m = ExponentialSmoothing(train, trend="add", damped_trend=True, seasonal="mul", seasonal_periods=12, initialization_method="estimated").fit(); fits["HW"] = m; add("Holt-Winters (damped, mult. seasonal)", m.forecast(H), t0)
print("Holt-Winters params: alpha=%.3f beta=%.3f gamma=%.3f phi=%.3f" % tuple(m.params[k] for k in ["smoothing_level", "smoothing_trend", "smoothing_seasonal", "damping_trend"]))

# ARIMA order selection by AIC on log train (grid)
print("\nARIMA order search on log(train), AIC (d fixed at 1 per stationarity tests):")
best = []
ly_tr = np.log(train)
for p_ in range(0, 4):
    for q_ in range(0, 4):
        try:
            r = SARIMAX(ly_tr, order=(p_, 1, q_), trend="n").fit(disp=False)
            best.append((r.aic, r.bic, p_, q_))
        except Exception:
            pass
best.sort(); print("  top 5 by AIC (aic, bic, p, q):", [tuple(round(v, 1) if i < 2 else v for i, v in enumerate(b)) for b in best[:5]])
aic_p, aic_q = best[0][2], best[0][3]
bic_sorted = sorted(best, key=lambda b: b[1]); print("  best by BIC: p=%d q=%d" % (bic_sorted[0][2], bic_sorted[0][3]))
t0 = time.time(); ar = SARIMAX(ly_tr, order=(aic_p, 1, aic_q), trend="n").fit(disp=False); fits["ARIMA"] = ar
add("ARIMA(%d,1,%d) on log" % (aic_p, aic_q), np.exp(ar.get_forecast(H).predicted_mean), t0)
# seasonal ARIMA candidates
sar_best = []
for (P, Q) in [(0, 1), (1, 0), (1, 1), (0, 0)]:
    for (p_, q_) in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (2, 1)]:
        try:
            r = SARIMAX(ly_tr, order=(p_, 1, q_), seasonal_order=(P, 0 if P + Q == 0 else 0, Q, 12) if P + Q else (0, 0, 0, 0), trend="n").fit(disp=False, maxiter=200)
            sar_best.append((r.aic, p_, q_, P, Q))
        except Exception:
            pass
sar_best.sort(); print("Seasonal-ARIMA search (aic, p, q, P, Q) top 5:", [tuple(round(v, 1) if i == 0 else v for i, v in enumerate(b)) for b in sar_best[:5]])
_, sp, sq, sP, sQ = sar_best[0]
t0 = time.time(); sr = SARIMAX(ly_tr, order=(sp, 1, sq), seasonal_order=(sP, 0, sQ, 12) if sP + sQ else (0, 0, 0, 0), trend="n").fit(disp=False, maxiter=200); fits["SARIMA"] = sr
add("SARIMA(%d,1,%d)(%d,0,%d)12 on log" % (sp, sq, sP, sQ), np.exp(sr.get_forecast(H).predicted_mean), t0)
print("Seasonal-ARIMA best vs plain ARIMA AIC: %.1f vs %.1f" % (sar_best[0][0], ar.aic))

# ML: lag-feature regressors, recursive multi-step on log-returns -> price
def feats(s_log, n_lag=12):
    d = s_log.diff()
    X = pd.concat({f"lag{k}": d.shift(k) for k in range(1, n_lag + 1)}, axis=1)
    X["ma3"] = d.shift(1).rolling(3).mean(); X["ma12"] = d.shift(1).rolling(12).mean()
    X["dev12"] = (s_log.shift(1) - s_log.shift(1).rolling(12).mean())
    X["m_sin"] = np.sin(2 * np.pi * s_log.index.month / 12); X["m_cos"] = np.cos(2 * np.pi * s_log.index.month / 12)
    return X
def recursive(model, s_log_train, H, n_lag=12):
    hist = s_log_train.copy(); out = []
    for i in range(H):
        nxt_idx = hist.index[-1] + pd.offsets.MonthBegin(1)
        h2 = pd.concat([hist, pd.Series([np.nan], index=[nxt_idx])])
        x = feats(h2, n_lag).iloc[[-1]]
        step = model.predict(x.values)[0]
        val = hist.iloc[-1] + step
        hist.loc[nxt_idx] = val; out.append(val)
    return np.exp(np.array(out))
X_all = feats(ly_tr); target = ly_tr.diff(); ok = X_all.dropna().index.intersection(target.dropna().index)
for nm, mdl in [("Random forest (lags)", RandomForestRegressor(300, min_samples_leaf=5, random_state=SEED, n_jobs=1)),
                ("Gradient boosting (lags)", GradientBoostingRegressor(n_estimators=200, max_depth=2, learning_rate=0.05, subsample=0.8, random_state=SEED)),
                ("Ridge (lags)", Ridge(alpha=1.0))]:
    t0 = time.time(); mdl.fit(X_all.loc[ok].values, target.loc[ok].values); fits[nm] = mdl
    add(nm, recursive(mdl, ly_tr.copy(), H), t0)
res = pd.DataFrame(rows).set_index("model")
res["fit_time_s"] = pd.Series(t_model)
print("\nHold-out accuracy (36 months):")
print(res.round(3).sort_values("RMSE").to_string())
R["holdout"] = res.round(4).reset_index().to_dict("records")

# Diebold-Mariano (squared error) vs Naive for top models
def dm(a, f1, f2, h=1):
    e1, e2 = a - f1, a - f2; d = e1 ** 2 - e2 ** 2; n = len(d)
    var = np.var(d, ddof=0); g = [np.mean((d[k:] - d.mean()) * (d[:-k] - d.mean())) for k in range(1, h)]
    v = (var + 2 * sum(g)) / n; st = d.mean() / np.sqrt(v); return st, 2 * (1 - stats.norm.cdf(abs(st)))
best_name = res["RMSE"].idxmin(); print("\nBest RMSE on hold-out:", best_name)
for nm in res.index:
    if nm != "Naive (last value)":
        s_, p_ = dm(test.values, fcs[nm].values, fcs["Naive (last value)"].values, h=12)
        print("  DM test vs Naive: %-40s stat %6.2f p=%.3f" % (nm, s_, p_))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(y.loc["2018":], color="k", lw=1.2, label="Actual")
for nm, col in [("Naive (last value)", "#999999"), ("Holt-Winters (damped, mult. seasonal)", "#e67e22"), (res.index[res.index.str.startswith("ARIMA")][0], "#2980b9"), ("Random forest (lags)", "#8e44ad")]:
    ax.plot(fcs[nm], lw=1.6, label=nm, color=col)
ax.axvline(test.index[0], color="r", ls="--", lw=0.8); ax.set_title("Fig 6: Hold-out forecasts vs actual (last 36 months)"); ax.set_ylabel("US cents per kg"); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig("figs/fig6_holdout.png", dpi=150); plt.close()

# ---------- rolling-origin evaluation (12-month horizon, 8 origins, yearly)
print("\n=== 4. ROLLING-ORIGIN EVALUATION (horizon 12, 8 origins) ===")
origins = [len(y) - 12 * k for k in range(8, 0, -1)]
roll = {k: [] for k in ["Naive", "Drift", "Holt (damped)", "Holt-Winters", "ARIMA(%d,1,%d)" % (aic_p, aic_q), "Random forest"]}
for o in origins:
    tr_, te_ = y.iloc[:o], y.iloc[o:o + 12]
    if len(te_) < 12: continue
    a = te_.values
    roll["Naive"].append(np.sqrt(np.mean((a - tr_.iloc[-1]) ** 2)))
    dr = tr_.iloc[-1] + (tr_.iloc[-1] - tr_.iloc[0]) / (len(tr_) - 1) * np.arange(1, 13); roll["Drift"].append(np.sqrt(np.mean((a - dr) ** 2)))
    hm = ExponentialSmoothing(tr_, trend="add", damped_trend=True, initialization_method="estimated").fit(); roll["Holt (damped)"].append(np.sqrt(np.mean((a - hm.forecast(12).values) ** 2)))
    hw = ExponentialSmoothing(tr_, trend="add", damped_trend=True, seasonal="mul", seasonal_periods=12, initialization_method="estimated").fit(); roll["Holt-Winters"].append(np.sqrt(np.mean((a - hw.forecast(12).values) ** 2)))
    ar_ = SARIMAX(np.log(tr_), order=(aic_p, 1, aic_q), trend="n").fit(disp=False); roll["ARIMA(%d,1,%d)" % (aic_p, aic_q)].append(np.sqrt(np.mean((a - np.exp(ar_.get_forecast(12).predicted_mean.values)) ** 2)))
    lt = np.log(tr_); Xa = feats(lt); tg = lt.diff(); ok_ = Xa.dropna().index.intersection(tg.dropna().index)
    rf = RandomForestRegressor(300, min_samples_leaf=5, random_state=SEED, n_jobs=1).fit(Xa.loc[ok_].values, tg.loc[ok_].values)
    roll["Random forest"].append(np.sqrt(np.mean((a - recursive(rf, lt.copy(), 12)) ** 2)))
rr = pd.DataFrame({k: [np.mean(v), np.std(v), np.min(v), np.max(v)] for k, v in roll.items()}, index=["mean RMSE", "std", "min", "max"]).T
print(rr.round(2).sort_values("mean RMSE").to_string())
R["rolling"] = rr.round(3).reset_index().rename(columns={"index": "model"}).to_dict("records")

# ---------- residual diagnostics of ARIMA
print("\n=== 5. DIAGNOSTICS (ARIMA on training log data) ===")
resid = ar.resid.iloc[1:]
lb = acorr_ljungbox(resid, lags=[12, 24], return_df=True)
print("Ljung-Box on residuals:\n", lb.round(4).to_string())
jb = stats.jarque_bera(resid); print("Jarque-Bera: stat=%.2f p=%.4g (skew %.2f, kurt %.2f)" % (jb[0], jb[1], stats.skew(resid), stats.kurtosis(resid)))
print("ARCH-LM on residuals: p=%.4f" % het_arch(resid, nlags=6)[1])
print(ar.summary().tables[1])
R["arima_diag"] = dict(lb12_p=float(lb["lb_pvalue"].iloc[0]), lb24_p=float(lb["lb_pvalue"].iloc[1]), jb_p=float(jb[1]))
fig, ax = plt.subplots(2, 2, figsize=(10, 6.5))
ax[0, 0].plot(resid); ax[0, 0].set_title("Fig 7a: ARIMA residuals"); plot_acf(resid, lags=36, ax=ax[0, 1], title="Fig 7b: ACF of residuals")
sns.histplot(resid, kde=True, ax=ax[1, 0], color="#2a7f3b"); ax[1, 0].set_title("Fig 7c: Residual histogram"); stats.probplot(resid, plot=ax[1, 1]); ax[1, 1].set_title("Fig 7d: Normal Q-Q plot")
plt.tight_layout(); plt.savefig("figs/fig7_diagnostics.png", dpi=150); plt.close()

# ---------- final forecast
print("\n=== 6. FINAL FORECAST (best simple model refit on all data) ===")
H2 = 24
cand = {"ARIMA": SARIMAX(np.log(y), order=(aic_p, 1, aic_q), trend="n").fit(disp=False)}
fc = cand["ARIMA"].get_forecast(H2); ci = np.exp(fc.conf_int(alpha=0.2)); ci95 = np.exp(fc.conf_int(alpha=0.05))
fidx = pd.date_range(y.index[-1] + pd.offsets.MonthBegin(1), periods=H2, freq="MS")
final = pd.DataFrame({"forecast": np.exp(fc.predicted_mean.values), "lo80": ci.iloc[:, 0].values, "hi80": ci.iloc[:, 1].values, "lo95": ci95.iloc[:, 0].values, "hi95": ci95.iloc[:, 1].values}, index=fidx)
hw_full = ExponentialSmoothing(y, trend="add", damped_trend=True, seasonal="mul", seasonal_periods=12, initialization_method="estimated").fit()
final["holt_winters"] = hw_full.forecast(H2).values
print(final.round(1).iloc[[0, 5, 11, 17, 23]].to_string())
final.to_csv("final_forecast_24m.csv")
# empirical interval coverage of the ARIMA 80/95% intervals on the hold-out
fh = ar.get_forecast(H); c80 = np.exp(fh.conf_int(alpha=0.2)); c95 = np.exp(fh.conf_int(alpha=0.05))
cov80 = np.mean((test.values >= c80.iloc[:, 0].values) & (test.values <= c80.iloc[:, 1].values)); cov95 = np.mean((test.values >= c95.iloc[:, 0].values) & (test.values <= c95.iloc[:, 1].values))
print("Hold-out coverage of nominal 80%% interval: %.0f%%, 95%% interval: %.0f%%" % (cov80 * 100, cov95 * 100))
fig, ax = plt.subplots(figsize=(10, 5)); ax.plot(y.loc["2015":], color="k", lw=1.2, label="Actual")
ax.plot(final.forecast, color="#c0392b", lw=2, label="ARIMA forecast"); ax.fill_between(final.index, final.lo95, final.hi95, color="#c0392b", alpha=0.15, label="95% interval"); ax.fill_between(final.index, final.lo80, final.hi80, color="#c0392b", alpha=0.3, label="80% interval")
ax.plot(final.holt_winters, color="#e67e22", ls="--", label="Holt-Winters"); ax.set_title("Fig 8: 24-month forecast of the tea price"); ax.set_ylabel("US cents per kg"); ax.legend()
plt.tight_layout(); plt.savefig("figs/fig8_final_forecast.png", dpi=150); plt.close()

# save for dashboard
pd.DataFrame({"actual": y}).to_csv("series_for_dashboard.csv")
pd.DataFrame(fcs).to_csv("holdout_forecasts.csv")
res.reset_index().to_csv("holdout_metrics.csv", index=False)
rr.reset_index().rename(columns={"index": "model"}).to_csv("rolling_metrics.csv", index=False)
pd.DataFrame({"trend": np.exp(stl.trend), "seasonal": stl.seasonal, "resid": stl.resid}).to_csv("stl_components.csv")
R["best_name"] = best_name; R["arima_order"] = [aic_p, 1, aic_q]; R["cov80"] = float(cov80); R["cov95"] = float(cov95)
json.dump(R, open("results.json", "w"), indent=1, default=float)
print("\nDone.")
