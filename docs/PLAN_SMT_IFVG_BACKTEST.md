# Plan: Backtest the "NY open SMT + IFVG" strategy

Goal: test, with explicit mechanical rules, the Instagram claim of ~70% win rate at 1:2 to 1:3 RR
(~$3,000/day) for: HTF bias -> LTF SMT divergence -> inverse FVG retrace entry -> resting-liquidity target.
This is a research exercise, not trading advice.

## Step 1 - Data
Pull 5-minute NQ=F and ES=F (yfinance, tz America/New_York) plus daily bars for bias.
Known limit: yfinance serves only the last ~60 days of 5m data (~40 sessions), so the sample is small and
cannot confirm or refute a 70% win rate by itself; the report must show Wilson confidence intervals.
Acceptance: both series aligned on timestamp, no duplicate indices.

## Step 2 - Rule definitions (all parameterised, defaults below)
- Bias (09:25 ET snapshot): price in lower half of previous-day range -> long only; upper half -> short only.
- Window: entries only 09:30-11:30 ET; one trade per day; flat by 12:00 ET.
- SMT: bar t's low is below the prior N=12 bars' low on NQ while ES's low is not (bullish); mirrored for
  highs (bearish). Must agree with bias.
- IFVG: a 3-bar bearish FVG (low[i-2] > high[i]) later closed through by a candle close above its top becomes
  a bullish IFVG (mirrored for shorts). Must form within K=12 bars after the SMT bar.
- Entry: limit at the IFVG top on retrace; filled only if price trades there after the IFVG forms.
- Stop: beyond the SMT extreme +/- 1 tick. Target variants: fixed 2R, fixed 3R, nearest resting liquidity
  (prior swing high/low in the session or previous-day high/low) requiring at least 1R.
- Costs: 1 tick slippage each side, $4.50 round trip per micro contract. If stop and target are both hit in
  one bar, count the stop (conservative).
Acceptance: rules are pure functions with unit tests on synthetic bars.

## Step 3 - Engine and metrics
Per target variant: trades, win rate with 95% Wilson CI, avg R, expectancy, profit factor, max drawdown.
Acceptance: deterministic output; tests pass.

## Step 4 - Null baseline
Random entries in the same window with the same stop distances and target multiple, 1000 draws, to see
whether the setup beats chance. Acceptance: report percentile of the strategy's expectancy vs the null.

## Step 5 - Verdict
State plainly whether the data supports the claim, with the sample-size caveat. Longer paid data
(Databento / Polygon) is needed for any serious conclusion.
