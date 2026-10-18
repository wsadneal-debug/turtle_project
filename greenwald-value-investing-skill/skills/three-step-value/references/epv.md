# 正常盈利能力价值（EPV）

## 研究顺序与口径

在不依赖增长的当前经营规模上，估计足以维持竞争地位的正常年度可分配盈利。用已有长期可比序列判断收入、正常利润率及周期位置，用当前规模算盈利；说明参考/采用年份、历史位置、结构变化和局限。两份年报不等于两个经济周期，10年数据也不自动证明周期正常化；不硬凑年限。TTM只是符合可比累计期间的算术参考。

费用调整双向：反复发生的“一次性”支出保留正常负担；研发、培训、营销仅加回可避免扩张部分，维持经营所必需的费用不因“零增长”消失。保留股权激励成本或一致稀释；利润率已处理的费用不再列调整。维护按全新功能成本和更新周期，不能用当前经济净值乘折旧率；新增营运资金与增长投入区分。

租赁优先选择一致的经营租金口径：EBIT加回已扣使用权折旧及其他已扣租金，再扣完整正常租金；其他折旧加回不含同一ROU。核心租金已承担的同范围租赁债务不重复扣；非核心/剥离业务未覆盖义务可明确`covered_by_core_rent=false`保留。融资口径则同步维护、税、债务与资本成本，不能在各桥混搭。

经营税不含融资利息税盾；账面折旧、税务折旧和维护现金分开。维护付款不是自动当期全额抵税，税后加回折旧不自动增加税基。PPA不可扣税摊销等重大差异若未在税率吸收才列税差；有限旧税益另做有限现值。资本成本依据币种、风险和资本结构，不设统一8%/10%。

核心EPV加同口径非经营/超额资源、扣实际融资债务及外部权益，形成归母桥。现金核总分和必要留存；少数权益若按全部子公司盈利估值乘外部份额，不能将已持有份额再乘一次。资产法NCI不能直接当盈利法NCI。经营应付已在经营占用中，不全部当融资债务再扣。有限税益、旧现金汇出税与未来年度税不要混淆。

重大受限或圈存资金是否可加回，按限制目的、可释放条件与时点判断；若经营持续需要同额替代资本，说明可释放净额及假设。对应债务、担保或履约义务与资金成对处理：已按净额或经营现金流承担的同一负担不重复扣。受限不代表价值为零，也不代表立即可分配，不机械全额剔除或全额加回；缺细分时允许合理估计。

对附注拆出的重大现金、存款、金融资产和债务，沿现有`reason`、`adoptions`或`review`简述每项计入何处或为何排除；剔除收益后，相关本金仍须判断是否应进入归母桥，已在经营盈利中计价的资源不再加一次。

剔除衍生工具收益不消灭相关衍生负债，省略不相关递延税资产也不使递延所得税负债自动归零。简述结算现金流、税款与存量义务如何匹配；已在正常现金流或其他净额中承担的部分不重复扣，按重大性估计或合并，不机械补全或全额照扣账面数。

先独立选择盈利/维护/税/资本成本并完成EPV初算，复核时才对照明确选定资产运行的最终计算及明细，核查重大资源和义务的去向并解释差别；不从资产总值倒推EPV，也不把经营项目机械全搬入归母桥。便携prepare仅提供成本/权属参照，不假定已自动绑定资产总值或完成比较。日期、币种、归母范围、租赁、完整性一致才算数值差距；否则定性并列。高EPV/资产比不自动证明护城河，不平均或相加。

## 内部参数合同

完整合成例`assets/epv-synthetic.json`可直接运行。顶层：`method="epv"`、currency、valuation_date、scope="parent_common"、shares、premise、summary、earnings、maintenance、tax、capital_cost、equity_adjustments。另建议明确`financial_position_date`（股权桥存量日）、`equity_basis`（股息和期后调整范围），不要把研究截止日当成存量已滚动更新。

| 对象 | 支持字段和模式 |
|---|---|
| earnings | revenue、margin（小数）、ebit_adjustments:[{id,value,reason,sources}]有符号税前调整、da_addback、working_capital_addition、lease、reason |
| earnings.lease | mode=none/operating/financing；operating须rou_depreciation_in_ebit、rent_expense_in_ebit、normalized_rent，均完整年度金额 |
| maintenance | mode=direct,value；或mode=components,items:[{id,name,gross_cost,residual,life_years,reason,sources,include}]；分项有value时优先完整年度金额，否则(全新成本−残值)/周期。没有net_asset_value计算路径 |
| tax | mode=rate,rate；或mode=direct,value；两者均可adjustments:[{id,value,reason,sources}]，正税差增税，负税差减税 |
| capital_cost | mode=direct,currency,wacc；或mode=components,currency,equity_cost,debt_weight,debt_cost,tax_shield。无债务时不强求debt_cost。as_of/reason/sources说明依据，不同时混两种模式 |
| equity_adjustments | [{id,name,kind,value,include,reason,sources}]；金额非负，由kind确定方向。parent_id表示同一权利父子，只选一层。reflected_in_earnings=true排除已计价资源，但不免扣真实融资/优先本金 |

允许调整种类：增加`excess_cash/nonoperating_asset/associate/tax_benefit/lease_advantage`；扣减`financing_debt/legacy_liability/transition_cost/nci/preferred/lease_debt`。`operating_asset/operating_payable/lease_right`仅作排除参照。operating租赁中lease_debt默认已覆盖而排除，明确未覆盖才用`covered_by_core_rent=false`。若资产已按减债净额估值，不再另扣债务。

股权行value为空时可选简单计算：

- `calculation=equity_epv, earnings, equity_cost, ownership`：被投企业全部股东税后年度可分配收益/股权成本×实际份额，不再扣集团税。
- `calculation=present_value, rate, cashflows:[{amount,years}]`：有限期逐笔现值。
- `calculation=ownership, equity_value, ownership`：被投企业股权价值×份额。

EPV无资产法通用fact_ref；正常化参数与原事实分开，sources连回事实。所有金额基本单位、比例小数。可选`history_analysis`、`annual_comparison`、`materials_read`、`assumptions`、`adoptions`、`competitive_advantage`保留研究，无必填证据树。

## 算术与情景

基础EBIT＝revenue×margin；加税前调整，经营租赁再按上表调整。年度可分配盈利E＝正常EBIT＋其他折旧加回−年度维护−正常经营现金税−维持所需营运资本增加。rate税＝max(正常EBIT,0)×rate＋税差。核心EPV＝E/WACC，再加减股权桥得到归母价值和每股值。程序输出earnings_bridge/equity_bridge；决定性金额缺失不伪称完整EPV。

`scenarios=[{name,reason,earnings:{变更},maintenance:{变更},tax:{变更},capital_cost:{变更},shares:可选,equity_values:{已有行id:新金额}}]`。同mode浅合并，切mode提供完整新块；lease/adjustments列表完整替换。重要维护/税/NCI联动要配对。`sensitivity={margins:[...],waccs:[...]}`真实重算网格，固定其余条件，不替代联合压力情景。未知字段不当成功执行。

合成教学例：正常EBIT2亿元，加回0.3亿，维护0.4亿，税0.5亿，E=1.4亿；教学WACC10%得核心14亿，净股权调整−1.5亿，归母12.5亿、每股12.5元。此处10%不是市场默认利率。
