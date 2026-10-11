"""Builds the interactive dashboard (single self-contained HTML file) from the CSV/JSON outputs of ts_analysis.py."""
import json
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs
from plotly.subplots import make_subplots
from statsmodels.tsa.stattools import acf, pacf

y = pd.read_csv("series_for_dashboard.csv", parse_dates=[0], index_col=0)["actual"]
fin = pd.read_csv("final_forecast_24m.csv", parse_dates=[0], index_col=0)
ho = pd.read_csv("holdout_forecasts.csv", parse_dates=[0], index_col=0)
hm = pd.read_csv("holdout_metrics.csv")
rm = pd.read_csv("rolling_metrics.csv")
stl = pd.read_csv("stl_components.csv", parse_dates=[0], index_col=0)
R = json.load(open("results.json"))
GREEN, RED, ORANGE, BLUE, GREY = "#2a7f3b", "#c0392b", "#e67e22", "#2980b9", "#7f8c8d"
LAYOUT = dict(template="plotly_white", margin=dict(l=50, r=20, t=50, b=40), font=dict(family="Segoe UI, Arial", size=13), legend=dict(orientation="h", y=-0.2))
figs = {}

# 1 overview
ma = y.rolling(12).mean()
f = go.Figure()
f.add_trace(go.Scatter(x=y.index, y=y, name="Monthly price", line=dict(color=GREEN, width=1.3), hovertemplate="%{x|%b %Y}: %{y:.1f} c/kg"))
f.add_trace(go.Scatter(x=ma.index, y=ma, name="12-month average", line=dict(color=RED, width=2.2)))
f.update_layout(title="Global tea price (US cents/kg), monthly", yaxis_title="US cents per kg", **LAYOUT)
f.update_xaxes(rangeslider_visible=True, rangeselector=dict(buttons=[dict(count=5, label="5y", step="year", stepmode="backward"), dict(count=10, label="10y", step="year", stepmode="backward"), dict(count=20, label="20y", step="year", stepmode="backward"), dict(step="all", label="All")]))
figs["overview"] = f

# yearly bars + change
ya = y.resample("YS").mean()
f = make_subplots(rows=1, cols=2, subplot_titles=("Annual average price", "Year-on-year change (%)"))
f.add_trace(go.Bar(x=ya.index.year, y=ya.values, marker_color=GREEN, name="Annual mean", hovertemplate="%{x}: %{y:.1f}"), 1, 1)
yoy = ya.pct_change() * 100
f.add_trace(go.Bar(x=yoy.index.year, y=yoy.values, marker_color=[RED if v < 0 else GREEN for v in yoy.values], name="YoY %", hovertemplate="%{x}: %{y:.1f}%"), 1, 2)
f.update_layout(showlegend=False, **{k: v for k, v in LAYOUT.items() if k != "legend"})
figs["annual"] = f

# 2 seasonality
ratio = (y / y.rolling(12, center=True).mean()).dropna()
mn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
f = go.Figure()
for m in range(1, 13):
    f.add_trace(go.Box(y=ratio[ratio.index.month == m], name=mn[m - 1], marker_color=GREEN, boxpoints=False, showlegend=False))
f.add_hline(y=1, line_dash="dash", line_color="black")
f.update_layout(title="Seasonal ratio by month (price / centred 12-month mean)", yaxis_title="ratio", **LAYOUT)
figs["season_box"] = f
pv = y.to_frame("p").assign(year=y.index.year, month=y.index.month).pivot(index="year", columns="month", values="p")
f = go.Figure(go.Heatmap(z=pv.values, x=mn, y=pv.index, colorscale="YlGn", colorbar=dict(title="c/kg"), hovertemplate="%{y} %{x}: %{z:.0f}"))
f.update_layout(title="Price heat-map (year x month)", yaxis_autorange="reversed", **LAYOUT)
figs["season_heat"] = f

# 3 decomposition
f = make_subplots(rows=3, cols=1, shared_xaxes=True, subplot_titles=("Trend (price scale)", "Seasonal component (log scale)", "Remainder (log scale)"), vertical_spacing=0.08)
f.add_trace(go.Scatter(x=stl.index, y=stl.trend, line=dict(color=RED)), 1, 1)
f.add_trace(go.Scatter(x=stl.index, y=stl.seasonal, line=dict(color=GREEN)), 2, 1)
f.add_trace(go.Scatter(x=stl.index, y=stl.resid, line=dict(color=GREY)), 3, 1)
f.update_layout(height=640, showlegend=False, title=f"STL decomposition: trend strength {R['trend_strength']:.2f}, seasonal strength {R['seasonal_strength']:.2f}", **{k: v for k, v in LAYOUT.items() if k != "legend"})
figs["stl"] = f

# 4 ACF / PACF
d1 = np.log(y).diff().dropna()
a, p = acf(d1, nlags=36), pacf(d1, nlags=36)
ci = 1.96 / np.sqrt(len(d1))
f = make_subplots(rows=1, cols=2, subplot_titles=("ACF of monthly log-returns", "PACF of monthly log-returns"))
f.add_trace(go.Bar(x=list(range(1, 37)), y=a[1:], marker_color=BLUE), 1, 1); f.add_trace(go.Bar(x=list(range(1, 37)), y=p[1:], marker_color=BLUE), 1, 2)
for c in (1, 2):
    for s in (ci, -ci): f.add_hline(y=s, line_dash="dot", line_color=RED, row=1, col=c)
f.update_layout(showlegend=False, **{k: v for k, v in LAYOUT.items() if k != "legend"})
figs["acf"] = f

# 5 models
hm = hm.sort_values("RMSE")
f = go.Figure(go.Bar(y=hm["model"], x=hm["RMSE"], orientation="h", marker_color=[GREEN if i == 0 else GREY for i in range(len(hm))], hovertemplate="%{y}: RMSE %{x:.1f}"))
f.update_layout(title="Hold-out RMSE, last 36 months (lower is better)", xaxis_title="RMSE (US cents/kg)", yaxis_autorange="reversed", height=430, **{k: v for k, v in LAYOUT.items() if k != "legend"}); f.update_layout(margin=dict(l=250, r=20, t=50, b=40))
figs["rmse"] = f
rm = rm.sort_values("mean RMSE")
f = go.Figure(go.Bar(y=rm["model"], x=rm["mean RMSE"], error_x=dict(type="data", array=rm["std"]), orientation="h", marker_color=[GREEN if i == 0 else GREY for i in range(len(rm))]))
f.update_layout(title="Rolling-origin 12-month RMSE (8 origins, mean +/- std across origins)", xaxis_title="RMSE (US cents/kg)", yaxis_autorange="reversed", height=380, **{k: v for k, v in LAYOUT.items() if k != "legend"}); f.update_layout(margin=dict(l=150, r=20, t=50, b=40))
figs["rolling"] = f
f = go.Figure()
f.add_trace(go.Scatter(x=y.loc["2021":].index, y=y.loc["2021":], name="Actual", line=dict(color="black", width=2)))
cols = [BLUE, ORANGE, RED, "#8e44ad", GREY, "#16a085", "#d35400", "#2c3e50", "#7f8c8d", "#27ae60"]
for i, c in enumerate(ho.columns):
    f.add_trace(go.Scatter(x=ho.index, y=ho[c], name=c, line=dict(color=cols[i % len(cols)], width=1.6), visible=True if c in ("Gradient boosting (lags)", "Naive (last value)", "Holt-Winters (damped, mult. seasonal)") else "legendonly"))
f.update_layout(title="Hold-out forecasts (click legend to show/hide models)", yaxis_title="US cents per kg", legend=dict(orientation="h", y=-0.25), margin=dict(l=50, r=20, t=50, b=40), template="plotly_white", height=470)
f.add_vline(x=ho.index[0], line_dash="dash", line_color="red")
figs["holdout"] = f

# 6 forecast
f = go.Figure()
f.add_trace(go.Scatter(x=y.loc["2015":].index, y=y.loc["2015":], name="Actual", line=dict(color="black", width=1.6)))
f.add_trace(go.Scatter(x=list(fin.index) + list(fin.index[::-1]), y=list(fin.hi95) + list(fin.lo95[::-1]), fill="toself", fillcolor="rgba(192,57,43,0.15)", line=dict(width=0), name="95% interval", hoverinfo="skip"))
f.add_trace(go.Scatter(x=list(fin.index) + list(fin.index[::-1]), y=list(fin.hi80) + list(fin.lo80[::-1]), fill="toself", fillcolor="rgba(192,57,43,0.3)", line=dict(width=0), name="80% interval", hoverinfo="skip"))
f.add_trace(go.Scatter(x=fin.index, y=fin.forecast, name="ARIMA forecast", line=dict(color=RED, width=2.4)))
f.add_trace(go.Scatter(x=fin.index, y=fin.holt_winters, name="Holt-Winters", line=dict(color=ORANGE, dash="dash")))
f.add_trace(go.Scatter(x=fin.index, y=fin.gradient_boosting, name="Gradient boosting", line=dict(color=BLUE, dash="dot")))
f.update_layout(title="24-month forecast, August 2026 to July 2028", yaxis_title="US cents per kg", height=480, **LAYOUT)
figs["forecast"] = f

last, prev12 = y.iloc[-1], y.iloc[-13]
kpis = [("Latest price (Jul 2026)", f"{last:.0f} c/kg", ""), ("Change vs 12 months ago", f"{(last / prev12 - 1) * 100:+.1f}%", ""),
        ("All-time high", f"{y.max():.0f} c/kg", y.idxmax().strftime("%b %Y")), ("Typical monthly swing (st.dev.)", f"{np.exp(d1.std()) * 100 - 100:.1f}%", f"annualised {d1.std() * np.sqrt(12) * 100:.0f}%"),
        ("Forecast Jul 2027 (ARIMA)", f"{fin.forecast.iloc[11]:.0f} c/kg", f"80% range {fin.lo80.iloc[11]:.0f} to {fin.hi80.iloc[11]:.0f}"),
        ("Best hold-out model", "Gradient boosting", f"RMSE {hm.RMSE.min():.1f} vs naive {hm[hm.model.str.startswith('Naive')].RMSE.iloc[0]:.1f}")]
st = R["stationarity"]
stat_rows = "".join(f"<tr><td>{k}</td><td>{v['adf_stat']:.2f}</td><td>{v['adf_p']:.4f}</td><td>{v['kpss_stat']:.3f}</td><td>{'stationary' if v['adf_p'] < 0.05 and v['kpss_p'] > 0.05 else 'non-stationary'}</td></tr>" for k, v in st.items())
ho_rows = "".join(f"<tr><td>{r.model}</td><td>{r.MAE:.1f}</td><td>{r.RMSE:.1f}</td><td>{r.MAPE:.1f}%</td></tr>" for r in hm.itertuples())

def div(k, h=None): return figs[k].to_html(full_html=False, include_plotlyjs=False, default_height=h or 450, div_id=f"fig_{k}")
html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kenya Tea Price Forecasting Dashboard</title>
<style>
:root{{--bg:#f6f8f5;--card:#fff;--ink:#1d2b20;--mute:#5d6b60;--g:#2a7f3b;--line:#dfe6dc}}
body{{margin:0;font-family:Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--ink)}}
header{{background:linear-gradient(120deg,#1e5e2c,#2a7f3b);color:#fff;padding:22px 28px}} header h1{{margin:0;font-size:24px}} header p{{margin:6px 0 0;opacity:.9;font-size:14px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;padding:16px 28px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}} .kpi small{{color:var(--mute)}} .kpi b{{display:block;font-size:22px;margin:3px 0}}
nav{{display:flex;flex-wrap:wrap;gap:6px;padding:0 28px}} nav button{{border:1px solid var(--line);background:#fff;padding:9px 16px;border-radius:8px 8px 0 0;cursor:pointer;font-size:14px;color:var(--ink)}} nav button.on{{background:var(--g);color:#fff;border-color:var(--g)}}
section{{display:none;margin:0 28px 28px;background:var(--card);border:1px solid var(--line);border-radius:0 10px 10px 10px;padding:16px}} section.on{{display:block}}
.note{{background:#eef6ee;border-left:4px solid var(--g);padding:10px 14px;margin:10px 0;font-size:14px;border-radius:4px}}
table{{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0}} th,td{{border-bottom:1px solid var(--line);padding:6px 10px;text-align:left}} th{{background:#f0f5ef}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} @media(max-width:850px){{.two{{grid-template-columns:1fr}} header,.kpis,nav{{padding-left:14px;padding-right:14px}} section{{margin:0 14px 20px}}}}
footer{{padding:14px 28px;color:var(--mute);font-size:12px}}
</style><script>{get_plotlyjs()}</script></head><body>
<header><h1>Forecasting the Global Tea Price: a Kenya Export Perspective</h1>
<p>STA 3050 Term Paper dashboard | Monthly tea price (US cents/kg), Jan 1992 to Jul 2026, 415 observations | Source: IMF via FRED (PTEAUSDM)</p></header>
<div class="kpis">{"".join(f'<div class="kpi"><small>{a}</small><b>{b}</b><small>{c}</small></div>' for a, b, c in kpis)}</div>
<nav id="tabs"><button class="on" data-t="t1">1. Overview</button><button data-t="t2">2. Seasonality</button><button data-t="t3">3. Decomposition</button><button data-t="t4">4. Stationarity</button><button data-t="t5">5. Model comparison</button><button data-t="t6">6. Forecast</button></nav>
<section id="t1" class="on">{div('overview', 480)}<div class="note"><b>Why tea?</b> Tea is one of Kenya's largest export earners and Kenya is among the world's leading exporters of black tea, so the world price drives farmer incomes and foreign-exchange earnings. The series is the IMF's global tea price (an average of the Mombasa, Colombo and Calcutta auctions), not the Mombasa price alone. Use the range slider to zoom; the rise to the 2011 average (346 c/kg) and the July 2015 peak (403 c/kg) stand out.</div>{div('annual', 380)}</section>
<section id="t2">{div('season_box', 420)}{div('season_heat', 600)}<div class="note">Prices tend to be higher in January, February, September and October and lowest in May to June (about 4.5% below the yearly average). The monthly pattern is statistically significant (ANOVA p &lt; 0.001) but small compared with the year-to-year swings, so STL seasonal strength is only {R['seasonal_strength']:.2f} against {R['trend_strength']:.2f} for the trend.</div></section>
<section id="t3">{div('stl', 650)}</section>
<section id="t4"><table><tr><th>Series</th><th>ADF statistic</th><th>ADF p-value</th><th>KPSS statistic</th><th>Verdict (ADF + KPSS)</th></tr>{stat_rows}</table>
<div class="note">The price level is non-stationary (ADF cannot reject a unit root; KPSS rejects stationarity), and one regular difference of the log price makes it stationary, so ARIMA models use d = 1. Monthly returns have small positive first-order autocorrelation (0.16) and negative lags 2 and 3, which is why an ARMA model on the differences fits slightly better than a pure random walk.</div>{div('acf', 400)}</section>
<section id="t5"><div class="two"><div>{div('rmse', 430)}</div><div>{div('rolling', 380)}<div class="note">On the single 36-month hold-out the gradient-boosting model wins, but across eight rolling 12-month origins Holt-Winters is best and all differences are small compared with the spread across origins (std about 17 to 19). Treat model rankings as tentative.</div></div></div>
{div('holdout', 480)}<table><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAPE</th></tr>{ho_rows}</table></section>
<section id="t6">{div('forecast', 500)}<div class="note">The ARIMA forecast is nearly flat at about 274 c/kg (a model of price changes cannot predict direction), with 80% intervals that widen from about -8%/+8% after one month to about -33%/+50% after 24 months. Hold-out coverage of the nominal 80% and 95% intervals was {R['cov80'] * 100:.0f}% and {R['cov95'] * 100:.0f}%. The Holt-Winters and gradient-boosting paths add a mild seasonal rhythm and a slightly higher level (about 285 to 295). Use them as scenarios, not as certainties.</div></section>
<footer>Built with Python (statsmodels, scikit-learn, plotly). Forecasts are statistical projections, not financial advice.</footer>
<script>
const btns=document.querySelectorAll('#tabs button');
btns.forEach(b=>b.addEventListener('click',()=>{{btns.forEach(x=>x.classList.remove('on'));document.querySelectorAll('section').forEach(s=>s.classList.remove('on'));b.classList.add('on');const s=document.getElementById(b.dataset.t);s.classList.add('on');s.querySelectorAll('.plotly-graph-div').forEach(g=>Plotly.Plots.resize(g));}}));
</script></body></html>"""
open("Tea_Price_Dashboard.html", "w", encoding="utf-8").write(html)
print("dashboard written", len(html) // 1024, "KB")
