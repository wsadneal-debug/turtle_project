# 合成案例：检验算术与推理边界
全部数字虚构，金额同一币种百万元，P除外。案例不预设任何真实公司的结论，算式通过不证明真实模型会正确执行。

## 基线回本与共享容量
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
此处只证明两项数值条件，未证明企业稳定或分红可持续。错误全算回购会得9.75%，误用FCF收益率会得10%；先扣股息税再释放容量同样错误。

## 半年掩盖季度与正常季节
```text
Q1_prior=90; H1_prior=200; Q1_current=130; H1_current=220
Q2_prior=110; Q2_current=90
H1_YoY_pct=10; Q2_YoY_pct=-18.181818; Q2_QoQ_pct=-30.769231
Seasonal_Q1_prior=180; Seasonal_Q2_prior=90
Seasonal_Q1_current=200; Seasonal_Q2_current=100
Seasonal_QoQ_pct=-50; Seasonal_Q2_YoY_pct=11.111111
```
第一组必须研究季度反转，不可只写H1增长；第二组若历史与经营证据支持同样淡旺季，不因-50%机械进入衰退。缺Q1则不准H1除二；只有同比增速公告不能算绝对环比。

## 小业务缩放与非营收事件
```text
AffectedRevenueShare=0.03; BusinessRevenueChange_pct=50
GroupRevenueImpact_pct=1.5
```
在其他业务不变、同一期间下只是集团营收+1.5%，不是+50%。新业务需估绝对增量；成本节约可直接影响利润，资本支出可先消耗现金，不强迫二者先转收入。

## 独立年度下行情景
以下g和现金容量是假设已被单独年度研究支持的情景，不由上面的季度降幅推算：
```text
g=-0.20; delta_used=-16; F_path=[64,48,32,16,0,0]
R6=336; Coverage6=0.42; SupportPrice6=4.20
O_forward=56; D_forward=60; B_forward=30; tau=0.2
D_alloc=56; B_alloc=0; ShareholderCash_net=44.8; GG_forward=5.6
```
分配已受容量限制，不能再给GG扣一次20%。基本面不成立时，无论下行参考价多低都不是策略内买入机会；无法量化g时停止正向外推仅得上界，不称已验证价值。

## 多年承诺的两个反例
```text
raw_fcf=[40,-20,50]; F_rec=0; U=30; n=3; TermCapacity=30
D_current=40; B_current=20; FCF_parent_current=25; F_rec=25; U=65; n=3
O_current=65; CurrentDemand=60; TermCapacity=140; RemainingDemand=180
CurrentSupported=True; TermSupported=False
```
负年份不能删除；仅回购承诺也保留普通股息，全期需求不是回购60。U不能每年重复加，当前足够不代表全期足够；时间表也要满足。固定额承诺若确有全期覆盖，不机械按营收跌幅减额。

## 必留边界
L_prev缺失可平坦，L或F_norm缺失不能标准通过；K负值保留，K>=MV回本为零；M5=0且A3=10取10，缺年不填零；O=0且事件完整GG=0，未知事件不是零。要求区间[5,6]且GG=5.5只能条件成立，不默选5；价阶标准价是价格中点。
无行情MCP、离线禁止联网或复权不可核验时可跳过，不能写正常；恒定收盘的100%分位没有高位含义。质量与分红前提、绝对价格条件和回报条件分别判断，证据不足不自动给企业C。
