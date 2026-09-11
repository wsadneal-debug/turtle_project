# 条件分支：只有明确复现或选择变体才读取
默认不加载，不静默切换，不混称独立重建与既有系统逐值等价；原系统数据、资格或工具不可用就注明，不能编造。

## 累计年化代理
```text
Annualized_Q1 = Q1_YTD * 4
Annualized_H1 = H1_YTD * 2
Annualized_9M = 9M_YTD * 4 / 3
Annualized_FY = FY
```
本年和上年同窗口分别按对应归属换算，明示“累计年化代理”，不是TTM，不是季节调整或未来预测。缺真实TTM不能悄悄用此分支宣称标准通过。

## 重资产平滑上游变体
```text
adjusted_OCF = min(OCF_current, 1.5 * mean_OCF_5y)
adjusted_Capex = max(Capex_current, mean_Capex_5y)
heavy_FCF = adjusted_OCF - adjusted_Capex
```
再按实际归属处理；只有原输入明确采用该口径才复现，不能重复平滑已调整数，五年缺值不能补零。

## 合并容量与原生普通股息缩放
```text
O0_legacy_consolidated_proxy = max(0, OCF_annual - Capex_annual)
GG_native = g_ordinary * min(1, max(0, F_parent) / D_year), if D_year > 0
```
仅用户明确要求复现旧路径时使用。合并代理不保证全部属于上市公司股东。g_ordinary为普通TTM税后事件回报，D_year为最近财务行普通股息现金额，F_parent为同财务行归母FCF；期间可能不同，不等于默认用D_TTM共享容量的公式。D_year=0时旧分支不缩放，但不能据此证明TTM分红有覆盖；缺分母不是0。

明确选择直接最新现金能力法时，列最新归母期间和口径，不冒充年报容量的60%/85%更新规则。年度现金假设和股息假设仍需一致，主线的季节性、事件推演及基本面前提不因选择兼容分支而取消。

## 复现与当前决策分开
严格复现旧报告时保留旧输入、公式及结果，单列当前主线要求的纠正/情景，不悄悄改旧数，也不把忠实复现当作当前策略资格。说明差异来自数据、币种、归属、窗口、情景还是算法；不需要旧模式时返回默认参考。
