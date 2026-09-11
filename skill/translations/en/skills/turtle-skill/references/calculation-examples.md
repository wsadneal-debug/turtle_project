# Synthetic cases: arithmetic and reasoning boundaries
All figures are fictional, in one currency's millions except P. No case prescribes a real company's conclusion; passing arithmetic does not establish actual model behavior.

## Baseline recovery and shared capacity
```text
P=10; MV=800; C=300; A=20; B_debt=100; alpha=0.8
F1=100; F2=90; F3=80; F4=70; F5=60; L=90; L_prev=70
M5=80; A3=90; F_norm=80; K=176; F0=80; delta_base=8
F_path=[88,96,104,112,120,128]
R5=696; R6=824; Coverage6=1.03; FlatCoverage6=0.82
Payback=5.8125; SupportPrice5=8.70; SupportPrice6=10.30
O=80; D=60; B_buyback=30; tau=0.2
D_alloc=60; B_alloc=20; ShareholderCash_net=68; GG=8.5
II=5; KK=3.5; ObservePrice=17; HeavyPrice=8.5; StandardPrice=12.75
```
Only numerical price conditions are demonstrated, not stable fundamentals/sustainable dividends. Counting all buybacks yields a wrong9.75%, substituting FCF yield gives10%, and releasing capacity after dividend tax is also wrong.

## A half year hiding a quarter, versus seasonality
```text
Q1_prior=90; H1_prior=200; Q1_current=130; H1_current=220
Q2_prior=110; Q2_current=90
H1_YoY_pct=10; Q2_YoY_pct=-18.181818; Q2_QoQ_pct=-30.769231
Seasonal_Q1_prior=180; Seasonal_Q2_prior=90
Seasonal_Q1_current=200; Seasonal_Q2_current=100
Seasonal_QoQ_pct=-50; Seasonal_Q2_YoY_pct=11.111111
```
The first needs investigation of the quarterly reversal, not just H1 growth. If historical/operating evidence supports the second's seasonality, -50% does not mechanically trigger decline. Missing Q1 forbids H1/2; YoY-growth-only updates cannot establish amount-based QoQ.

## Small-business scaling and direct non-revenue effects
```text
AffectedRevenueShare=0.03; BusinessRevenueChange_pct=50
GroupRevenueImpact_pct=1.5
```
With matching periods and other businesses unchanged, group revenue grows1.5%, not50%. New businesses need absolute increments. Cost savings can directly affect profit and capital expenditure can consume cash before revenue, without a forced revenue step.

## Independently supported annual downside
Here g/capacity are assumed supported by separate annual research, not derived from the quarterly decline above:
```text
g=-0.20; delta_used=-16; F_path=[64,48,32,16,0,0]
R6=336; Coverage6=0.42; SupportPrice6=4.20
O_forward=56; D_forward=60; B_forward=30; tau=0.2
D_alloc=56; B_alloc=0; ShareholderCash_net=44.8; GG_forward=5.6
```
Capacity already limits distribution; do not cut GG another20%. Failed fundamentals cannot become a strategy opportunity through a cheap downside reference price. An unquantified g permits only a no-positive-extrapolation upper bound, not verified value.

## Two commitment counterexamples
```text
raw_fcf=[40,-20,50]; F_rec=0; U=30; n=3; TermCapacity=30
D_current=40; B_current=20; FCF_parent_current=25; F_rec=25; U=65; n=3
O_current=65; CurrentDemand=60; TermCapacity=140; RemainingDemand=180
CurrentSupported=True; TermSupported=False
```
Never delete negative years. Buyback-only commitments retain ordinary dividends: full demand is not just buybacks60. U is not added every year; current sufficiency is not full-term sufficiency, and the schedule must work too. Fixed commitments with genuine full-term coverage are not mechanically cut by revenue deterioration.

## Retained edges
Missing L_prev permits flat projection; missing L/F_norm prevents standard passage. Keep negative K; K>=MV pays back at zero years. M5=0/A3=10 yields10, not zero-filled missing years. Known O=0 with complete events yields GG=0; unknown events do not. GG=5.5 against[5,6] is conditional, not an assumed5% requirement; StandardPrice is a price midpoint.
No MCP, offline restrictions or unverifiable adjustments permit a skip, not normal status. Constant-price100% percentiles are not meaningful high-position evidence. Separate business/dividend prerequisites and absolute/return conditions; missing evidence does not automatically imply C quality.
