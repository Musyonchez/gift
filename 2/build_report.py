import pandas as pd
from docx import Document
from docx.shared import Pt, Inches

hm = pd.read_csv("holdout_metrics.csv").sort_values("RMSE")
rm = pd.read_csv("rolling_metrics.csv").sort_values("mean RMSE")
fin = pd.read_csv("final_forecast_24m.csv", parse_dates=[0], index_col=0)
doc = Document()
doc.styles['Normal'].font.name = 'Calibri'
doc.styles['Normal'].font.size = Pt(11)
H = doc.add_heading
P = doc.add_paragraph


def fig(f, cap, w=6.0):
    doc.add_picture(f, width=Inches(w))
    c = P(cap)
    c.runs[0].italic = True


def table(df, cols=None, fmt=1):
    cols = cols or list(df.columns)
    t = doc.add_table(rows=1, cols=len(cols))
    t.style = 'Light Grid Accent 1'
    for i, c in enumerate(cols):
        t.rows[0].cells[i].text = str(c)
    for _, r in df.iterrows():
        cs = t.add_row().cells
        for i, c in enumerate(cols):
            v = r[c]
            cs[i].text = f"{v:.{fmt}f}" if isinstance(v, float) else str(v)


def bullets(items):
    for it in items:
        P(it, style='List Bullet')


doc.add_heading('Forecasting the Global Tea Price: A Time Series Study from a Kenyan Export Perspective', 0)
P('STA 3050: Time Series Analysis and Forecasting | Term Paper. Companion files: Tea_Price_Dashboard.html (interactive dashboard), ts_analysis.py (all code), tea_price_monthly.csv (data).')

H('1. Summary of findings', 1)
bullets([
    'The tea price is a persistent, non-stationary series (ADF p = 0.26 on the level). One regular difference of the log price makes it stationary (ADF p < 0.001, KPSS not rejected).',
    'There is a real but weak seasonal pattern: prices are about 4.5% below the yearly average in May and June and 3 to 4% above it in February and September (ANOVA p < 0.001), yet seasonality explains little compared with the trend (STL strength 0.14 versus 0.90).',
    'Monthly price changes are only weakly predictable. The best ARIMA model is ARIMA(2,1,3) on the log price; its 24-month forecast is nearly flat at about 274 US cents/kg, with a wide 80% interval of 183 to 411 at 24 months.',
    'On a 36-month hold-out, gradient boosting on lagged returns had the lowest RMSE (32.7 against 47.7 for the naive forecast, -31%). Across eight rolling 12-month forecast origins, however, Holt-Winters was best (27.1 against 30.0 for naive, -10%) and gradient boosting was close behind (28.3). Gains over a naive forecast are modest and smaller than the spread across origins (standard deviation about 16 to 19), so I treat the ranking as tentative.',
    'Volatility clusters (ARCH test p < 0.001) and the residuals are not normal (Jarque-Bera p = 0.009), so the ARIMA intervals are approximate.'])

H('2. Area of interest and justification (WHY)', 1)
P('Tea is one of Kenya\'s largest export earners and Kenya is among the world\'s leading exporters of black tea, sold mainly through the Mombasa auction. Smallholder farmers, factories and the Treasury are all exposed to the world price, which cannot be controlled. Time series methods are suited to this problem because (i) the data are ordered monthly observations with strong dependence over time, (ii) planning decisions (factory payments, bonus to farmers, budget projections, forward contracts) need a forecast and a measure of its uncertainty, and (iii) the course tools (stationarity, differencing, ACF/PACF, exponential smoothing, ARIMA, decomposition, spectral analysis) answer the questions of trend, seasonality and predictability directly.')
P('Questions: Q1. How has the price behaved, and is there a seasonal pattern? Q2. Is the series stationary, and what does its autocorrelation structure suggest? Q3. Which forecasting model is most accurate, and does a machine-learning model beat classical time series models? Q4. What is the price outlook for the next 24 months and how uncertain is it?')

H('3. Data (mining the dataset)', 1)
P('Source: the IMF "Global price of Tea" series, distributed by the Federal Reserve Bank of St. Louis (FRED code PTEAUSDM), downloaded with the date of this analysis. It is monthly, in US cents per kilogram, from January 1992 to July 2026: 415 observations and no missing values. The IMF series is an average of the Mombasa, Colombo and Calcutta auction prices, so it is a benchmark for the world market that Kenya sells into, not the Mombasa price alone. The price is in nominal US dollars, so it contains inflation and exchange-rate effects.')
P('Summary statistics: mean 256.3, standard deviation 60.1, minimum 143.4 (July 1995), median 252.5, maximum 403.0 (July 2015). Skewness is 0.28 and excess kurtosis -0.92 (a flat-topped distribution, with the price spending time at several different levels). Annual averages: 199.7 (1992), 248.1 (2000), 269.5 (2008), 346.2 (2011), 237.9 (2014), 253.9 (2020), 277.9 (2022), 316.8 (2025). The latest observation is 273.1 (July 2026).')
fig('figs/fig1_series.png', 'Figure 1: Monthly tea price (top, with 12-month moving average) and its logarithm (bottom).')

H('4. Exploratory data analysis', 1)
H('4.1 Trend and seasonality', 2)
P('The series wanders around long swings rather than returning to a fixed mean: a rise to a peak in 2011 and July 2015, and a fall after. The seasonal ratio (price divided by its centred 12-month mean) shows the highest averages in February (1.034), September (1.039) and October (1.026) and the lowest in May (0.956) and June (0.955). A one-way ANOVA across calendar months gives F = 7.02 (p < 0.001) and a Kruskal-Wallis test agrees (H = 72.1, p < 0.001), so the seasonal pattern is statistically real. Its size, however, is small compared with the multi-year swings.')
fig('figs/fig2_seasonal.png', 'Figure 2: Seasonal ratio by calendar month (left) and a year-by-month heat-map of the price (right).', 6.3)
H('4.2 Decomposition', 2)
P('An STL decomposition of the log price (period 12, robust fitting) gives a trend strength of 0.896 and a seasonal strength of 0.139 (measures defined as 1 minus the remainder variance divided by the variance of trend plus remainder, or of seasonal plus remainder). The series is therefore mostly trend-like (slowly moving level) with a minor seasonal component. A multiplicative seasonal form was used in Holt-Winters since the price swings grow with the level.')
fig('figs/fig3_stl.png', 'Figure 3: STL decomposition of the log tea price.', 6.0)
H('4.3 Frequency-domain view', 2)
P('The periodogram of the monthly log-returns (Figure 4) has its largest peaks at 2.0 cycles per year (a 6-month period; power 0.0078) and at 3.07 cycles per year (3.9 months). There is no dominant 12-month peak, which is consistent with the weak annual seasonality above; the 6-month component is a harmonic of the annual pattern (the twice-per-year highs in February and September to October). Peaks of this size in a short sample should be read with care, since a periodogram is noisy.')
fig('figs/fig4_periodogram.png', 'Figure 4: Periodogram of monthly log-returns.', 5.0)

H('5. Stationarity and autocorrelation tests', 1)
t = pd.DataFrame([
    ('Level', -2.063, 0.2598, 2.061, '<= 0.01', 'non-stationary'),
    ('Log level', -1.995, 0.2889, 2.171, '<= 0.01', 'non-stationary'),
    ('First difference of level', -9.073, 0.0000, 0.036, '>= 0.10', 'stationary'),
    ('First difference of log', -8.788, 0.0000, 0.043, '>= 0.10', 'stationary'),
    ('Seasonal difference (12) of log', -4.742, 0.0001, 0.038, '>= 0.10', 'stationary')],
    columns=['Series', 'ADF stat', 'ADF p', 'KPSS stat', 'KPSS p', 'Conclusion'])
table(t, fmt=3)
P('')
P('ADF has a unit root as its null and KPSS has stationarity as its null; the two tests agree. The level and its log are non-stationary, so I used d = 1 on the log price (the log stabilises the growing variance). The Ljung-Box test on the differenced log series rejects white noise (Q(12) = 70.5, Q(24) = 84.2, p < 0.001), so there is exploitable short-term dependence: the ACF of the differences at lags 1 to 3 is 0.164, -0.196 and -0.171, and the PACF is 0.164, -0.230 and -0.103 (Figure 5). That pattern suggests an ARMA(2,q) structure for the differences, which matches the model chosen below. The annualised volatility of monthly log-returns is 23.0%, and an ARCH-LM test (p < 0.001) shows volatility clustering.')
fig('figs/fig5_acf_pacf.png', 'Figure 5: ACF and PACF of the log price (top) and of its first difference (bottom).', 6.3)

H('6. Models and accuracy', 1)
P('Design. The last 36 months (August 2023 to July 2026) were kept as a hold-out; every model was fitted on January 1992 to July 2023 (379 observations) only, with parameters and orders chosen on the training data. Forecasts are multi-step (36 months ahead from one origin). Accuracy metrics are MAE, RMSE, MAPE and sMAPE. To avoid relying on one split, I also ran a rolling-origin evaluation with eight yearly origins and a 12-month horizon. Random seed 42.')
P('Models: naive (last value), seasonal naive, drift, simple exponential smoothing, damped Holt, damped-trend multiplicative Holt-Winters, ARIMA (order chosen by AIC over a p, q grid with d = 1, on the log price) and a seasonal ARIMA, plus three machine-learning regressors (random forest, gradient boosting and ridge regression) that use the previous 12 monthly log-returns, moving averages, a deviation from the 12-month mean and sine/cosine month terms as features and forecast recursively. The ARIMA grid selected ARIMA(2,1,3) by AIC (-992.7); BIC prefers the simpler ARIMA(2,1,0). The seasonal ARIMA(2,1,1)(1,0,1)12 improved AIC only slightly (-994.4).')
H('6.1 Hold-out results (36 months)', 2)
table(hm[['model', 'MAE', 'RMSE', 'MAPE', 'sMAPE']].rename(columns={'model': 'Model'}), fmt=2)
P('')
P('Gradient boosting has the lowest error (RMSE 32.7, MAPE 8.5%), followed by ridge regression (40.2), SARIMA (42.2) and Holt-Winters (42.8). The naive forecast has RMSE 47.7 (MAPE 13.2%), and the chosen ARIMA(2,1,3) is no better than naive (47.8): a model of price changes with a small autocorrelation forecasts an almost flat line. The random forest (47.6) and the seasonal naive (50.8) do not beat naive. Diebold-Mariano tests against the naive forecast (squared error, Bartlett variance, 12-month lag) favour gradient boosting (p = 0.004), SARIMA (p < 0.001), ridge (p < 0.001), Holt-Winters (p < 0.001) and drift (p = 0.004), but with only 36 overlapping monthly errors from one forecast origin these p-values are optimistic and I interpret them cautiously.')
fig('figs/fig6_holdout.png', 'Figure 6: Hold-out forecasts for four representative models against the actual price.', 6.0)
H('6.2 Rolling-origin results (12-month horizon, 8 origins)', 2)
table(rm.rename(columns={'model': 'Model'}), fmt=2)
P('')
P('Over eight different forecast origins the ordering changes: Holt-Winters has the lowest mean RMSE (27.1), then gradient boosting (28.3), ARIMA (29.4), drift (29.8), damped Holt (30.0), naive (30.0) and random forest (31.1). The standard deviation across origins is 16 to 19 for every model, much larger than the gaps between models, which means that the choice of origin matters more than the choice of model. The honest conclusion is that none of the models is clearly better than the naive forecast by a wide margin; the most reliable gains are about 10% in RMSE.')
H('6.3 Diagnostics of the ARIMA model', 2)
P('Fitted ARIMA(2,1,3) on log price (training data): AR(1) = 1.050, AR(2) = -0.781, MA(1) = -0.874, MA(2) = 0.427, MA(3) = 0.197, all significant at the 1% level; residual variance 0.0041. Ljung-Box tests on residuals do not reject white noise (Q(12) p = 0.079, Q(24) p = 0.165), so the autocorrelation is captured. The residuals are slightly heavy-tailed (excess kurtosis 0.76, Jarque-Bera p = 0.009) and show ARCH effects (p < 0.001), meaning that variance changes through time and the constant-variance intervals are only approximate. On the hold-out the nominal 80% and 95% intervals contained 86% and 100% of the actual values (36 months, so the coverage figures are rough).')
fig('figs/fig7_diagnostics.png', 'Figure 7: ARIMA residual diagnostics: residuals, ACF, histogram and normal Q-Q plot.', 6.0)

H('7. Forecast for August 2026 to July 2028', 1)
sel = fin.iloc[[0, 5, 11, 17, 23]].copy()
sel.insert(0, 'Month', [d.strftime('%b %Y') for d in sel.index])
table(sel[['Month', 'forecast', 'lo80', 'hi80', 'lo95', 'hi95', 'holt_winters', 'gradient_boosting']].rename(columns={'forecast': 'ARIMA', 'lo80': '80% low', 'hi80': '80% high', 'lo95': '95% low', 'hi95': '95% high', 'holt_winters': 'Holt-Winters', 'gradient_boosting': 'Grad. boosting'}), fmt=1)
P('')
P('The ARIMA model refitted on all 415 observations forecasts a level of about 274 US cents/kg for the whole horizon (the latest price is 273.1), with an 80% interval that widens from 253 to 297 after one month to 183 to 411 after 24 months. Holt-Winters and gradient boosting forecast a slightly higher level with a mild seasonal rhythm (about 273 to 295). I present the ARIMA path as the central forecast because it has a proper prediction interval, and the other two as scenarios. In practice this means: expect prices near current levels with no confident prediction of direction, and plan for a large range of outcomes.')
fig('figs/fig8_final_forecast.png', 'Figure 8: 24-month forecast with 80% and 95% intervals.', 6.0)

H('8. Interactive dashboard', 1)
P('Tea_Price_Dashboard.html is a single self-contained file (open it in any browser, no internet needed). It has summary indicator cards and six tabs: overview (zoomable series with range buttons and slider and annual changes), seasonality (box plots and heat-map), decomposition (STL), stationarity (test table and ACF/PACF), model comparison (hold-out and rolling-origin errors and a hold-out forecast chart in which models can be switched on and off from the legend) and forecast (fan chart with 80% and 95% intervals and two alternative scenarios), each with a short interpretation.')

H('9. Limitations', 1)
bullets([
    'The series is the world benchmark and not the Mombasa auction price or the price received by farmers; it is nominal and in US dollars, so shilling and inflation effects are not separated.',
    'It is a univariate analysis. Weather (rainfall and drought in the Kenyan highlands), supply, exchange rates and demand (Pakistan, Egypt, UK) are likely drivers and were not modelled; a regression with these variables or a dynamic regression model would be a natural next step.',
    'Accuracy conclusions rest on one 36-month hold-out and eight overlapping origins, and the gains over naive are modest and uncertain. Hyper-parameters of the machine-learning models were not tuned.',
    'Residuals show volatility clustering and non-normality; a GARCH or bootstrap interval would be more accurate for risk planning.'])

H('10. Conclusions and recommendations', 1)
P('The tea price is a trending, only weakly predictable series with a small seasonal effect. Differenced log prices have short-term autocorrelation that an ARIMA(2,1,3) captures, but its point forecasts hardly improve on a naive forecast; Holt-Winters and gradient boosting give 10% to 30% lower errors in the tests, with the caution above. For planning I recommend using the central forecast (about 274 cents/kg) together with the wide intervals, reviewing the models each month as new data arrive, and building the budget or contracts around the range 180 to 410 rather than a single number.')

H('11. Reproducibility and AI-use note', 1)
P('Run ts_analysis.py (produces results.txt-style output, figs/ and the CSV files), then build_dashboard.py and build_report.py. Python packages: pandas, numpy, scipy, statsmodels, scikit-learn, matplotlib, seaborn, plotly. The code, dashboard and a draft of this report were produced with Claude Code (Anthropic, Claude Sonnet 5.5); the figures in the text come from the script output. You should check it and edit this note to reflect your own work and what you can explain.')

H('References', 1)
for r in [
    'International Monetary Fund. Global price of Tea (Mombasa, Colombo and Calcutta auctions), US cents per kilogram [PTEAUSDM]. Retrieved from FRED, Federal Reserve Bank of St. Louis, https://fred.stlouisfed.org/series/PTEAUSDM.',
    'Chatfield, C. (2016). The Analysis of Time Series (7th ed.). CRC Press.',
    'Shumway, R. H. and Stoffer, D. S. (2016). Time Series Analysis and its Applications with R Examples (3rd ed.). Springer.',
    'Hyndman, R. J. and Athanasopoulos, G. Forecasting: Principles and Practice (3rd ed.). OTexts, https://otexts.com/fpp3/.',
    'Diebold, F. X. and Mariano, R. S. (1995). Comparing predictive accuracy. Journal of Business and Economic Statistics, 13(3), 253-263.',
    'Cleveland, R. B., Cleveland, W. S., McRae, J. E. and Terpenning, I. (1990). STL: a seasonal-trend decomposition procedure based on loess. Journal of Official Statistics, 6(1), 3-73.']:
    P(r, style='List Bullet')
doc.save('Term_Paper_Tea_Price_Forecasting.docx')
