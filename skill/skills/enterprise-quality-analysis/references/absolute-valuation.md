# 绝对估值：六年现金回本
计算前读取本篇；默认独立重建。六年、趋势上限及归属代理是方法约定，不是会计标准；不是DCF、公允价值、目标价或收益保证。

## 输入与归属
P、MV为同日、相同股份经济权益的价格和市值，均有限且>0；金额统一币种量级。多类股份须桥接完整权益或可核验每股分配，不能让某类市值承接集团全部现金。
C=未受限现金，A=一年内可变现且不重叠的金融资产，B_debt=有息债务；明确租赁负债和已扣项，不额外机械打折现金、不加应收或扣经营应付。未知项目不是零。
E为归母权益，N为少数股东权益；E>0，N缺失只有同期间总权益与E核对相等才用零。
```text
alpha = E / (E + max(N, 0))
FCF_ordinary = (OCF - Capex) * alpha
FCF_conservative = (OCF - Capex - Lease_cash_not_already_deducted) * alpha
K = (C + A - B_debt) * alpha
```
0<alpha<=1，是权益代理而非法律持股/可上划证明；年度FCF和现金分别用对应期间alpha。已归母FCF不再乘，直接归属现金另标变体不重复折减。K可为负。Capex用现金支付正数；普通与保守FCF扣除不同须列桥接。特殊重资产平滑仅在明确选择时读[兼容](compatibility.md)。

## 正常化与最新约束
F1…F5为最近五个完整可比年度归母FCF，新到旧，负年份保留：
```text
M5 = median(F1, F2, F3, F4, F5)
A3 = (F1 + F2 + F3) / 3
F_norm = min(M5, A3)
```
沿用既有特殊约定：M5、A3恰有一项为零时取另一项，两项都零则零；缺年不能填零触发例外。五年不足可交标注的简化敏感性结果，不声称标准门槛通过，也不阻断质量研究；取满五年不保证覆盖周期。

L、L_prev为最新及上年同类、归母且可比的年化FCF，默认优先真实TTM：
```text
TTM = FY_previous + YTD_current - YTD_previous_comparable
F0 = max(0, min(F_norm, max(0, L)))
raw_delta = L - L_prev
delta_base = max(-0.10 * F0, min(0.10 * F0, raw_delta))
```
仅F0、L、L_prev均正才用最后一式；L_prev缺失或三者任一非正则delta_base=0，说明原因。L或F_norm缺失不能借平坦回退补齐。不得静默改用累计年化代理；明确复现才读兼容参考，代理不是TTM或预测。

## 经营判断进入现金路径
普通减速/正常季节变化不自动下修。确认非季节性实质失速或衰退，说明事件到年度现金的传导，并选有依据的年度线性变化率g；g以小数表示且<=0，不是季度跌幅乘四。没有可靠幅度时仅用g=0构造停止增长的参考上界，不冒充已量化衰退。
```text
delta_used = delta_base
delta_used_if_material_stalling_or_decline = min(delta_base, F0 * g)
F(t) = max(0, F0 + t * delta_used), t = 1..6
```
激活时使用第二式作为delta_used；不抬高原有更差路径。每年为固定金额变化，不复利；当期基数也需核对是否仍适用。有可追溯年度情景基数时单列重建变体，不从短期营收跌幅机械折减FCF。负现金流截零只是回收约定，必须另列真实消耗、资金和融资压力，不能靠现金底座宣称安全。

## 覆盖、回本与参考价
```text
R(n) = K + sum(F(t) for t = 1..n)
Coverage(n) = R(n) / MV
FlatCoverage(n) = (K + n * F0) / MV
SupportMV(n) = max(0, R(n))
SupportPrice(n) = P * SupportMV(n) / MV
Payback = k - 1 + (MV - R(k - 1)) / F(k)
```
给5年和6年平坦/趋势覆盖及趋势参考价。K>=MV时Payback=0，否则k为首次覆盖年；六年内未覆盖就如此说明，不编造第七年。只将参考市值截零，K及R保留原值。跨日期重算不得叠加已支付股息与旧现金。

适用、输入完整可靠且Coverage(6)>=1时仅表示绝对回本价格条件通过；<1是不够明显便宜，不等于证明昂贵。缺关键数据为未知，简化变体不冒充标准结果；银行、保险、开发商等不适用时不强套。五年覆盖、平坦覆盖及正FCF年数是解释，不增加硬门槛。
即使数值通过，仍需[穿透回报](lookthrough-return.md)及企业/分红前提成立；未量化下行上界不作为已验证的买入依据。保留未调整输入、所选情景和原/新结果，刷新时从原值重算，不重复扣减。
