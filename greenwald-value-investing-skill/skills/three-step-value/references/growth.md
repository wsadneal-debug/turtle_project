# 给定价格下的成长回报

## 先判断适用性

阅读明确选定EPV与已有资产成本/权属解释，核对新变化，复用正常盈利、维护、税和资本成本；不重做全公司EPV。缺资产总值不强制补跑，EPV/资产差额不是优势证据。判断实际产品/地域/客群市场、强竞争者难以复制的成本或客户障碍、优势持续性及最强反证、新增投入是否仍在保护内且有望超过匹配资本成本。行业竞争激烈不自动否定局部优势，品牌、高利润率和优秀管理也不自动证明壁垒。

有机增长率及支持它的投入须对应受保护的业务范围。保留集团EPV基础时，把受保护业务与其他业务的收入增量分别汇总、除以同范围集团S，得到集团收入增长率；盈利增量分别汇总、除以集团E，得到集团盈利增长率。收入权重与盈利权重分开，盈利须与E的税、维护及资本范围可比；权重可合理粗估并简述依据，亏损或总部费用重大时用增量桥解释，不强套正权重。I按同一组业务的收入增量及资本需求汇总后用direct，或给与此汇总等效的集团intensity；不能直接用核心业务增长率乘集团S。沿现有reason/assumptions说明即可，不增字段或必填表。

纯合成例：受保护业务占同口径集团盈利60%，该业务盈利增长5%，其余盈利不变，则集团盈利g约为60%×5%＋40%×0%=3%，不能直接填5%。这不意味着它也占收入60%；集团收入增长及I须另按收入构成和各业务资本需求估计。保留集团E、S、B、M和匹配资本成本，无须为了局部优势单独估子公司买价，也不能把局部E除以整个集团M。

剩余资金可投其他业务，按实际投向单独估计F，包括F低于1的毁值情形。集团混合增长不能自动套用局部优势，新增市场或其他业务也不自动享有同一投资回报。无法合理解释集团映射时可选择skip/defer；不为凑全集团数值强行计算。

轻量`growth_route={action,reason}`：

- `evaluate`：支持或有据条件支持受保护的成长；仅部分业务适用时解释其如何进入集团增长与投入，沿用冻结集团基础。确需改估值范围时才按下节adjusted成对调整盈利、投资、资本成本、资源和买价。
- `skip`：明确不适用，直接简短结论结束，不强求报价、因子或衰减数值。
- `investigate`：只有一个决定性疑点时定向核查一次，然后由宿主综合为evaluate/skip/defer，不循环派题。
- `defer`：无法合理限定关键适用性，本轮不采用成长溢价；未知不能写成已证明无优势。

skip/defer都是正常研究收尾，不是投资否决，也不是估算成长价值为零。毁值扩张和资金侵蚀保留在`capital_allocation_risk/upstream_implications`；影响旧正常盈利时说明需要更新，不覆盖原EPV或称其保证底价。结论短对象可为`{"method":"growth","growth_route":{"action":"skip","reason":"经济原因"},"franchise":{"status":"unsupported","reason":"依据"},"summary":"结论","sources":[]}`。不强填数表；已初算后撤回要说明初算未最终采用。

## 冻结EPV和用户价格

用`growth --epv-run 明确目录`准备独立目录，源EPV先纯计算，再冻结基础、报告、日期和局限。`basis_mode=reuse_epv`由宿主绑定冻结basis，模型不能暗改。确有范围、期后变化或有据修正时用`adjusted`，给完整basis和`basis_change_reason`，展示原新差别，不写回源。`explicit`仅用于无源EPV的明确人工/合成input，已有源时不能借它绕过变化说明。

request仅`price`、`price_grid`、`policy`、`question`、`notes`。用户给定的价格/政策在本轮冻结；明确price={}或value=null保留缺价，不绕过冻结另搜。未给价格可实际查证并注明时间/币种/汇率；查不到仍交经营与资金判断，缺价不当0。新增研究日不代表源股权桥存量已更新。

## evaluate参数合同

顶层：method=growth、basis_mode、currency、summary、growth_route、franchise、distribution、organic、active、decay、price、policy，可附sources/assumptions/adoptions/materials_read/unmeasured/review及上述风险。

| 参数 | 字段/意义 |
|---|---|
| basis | currency,unit=currency,scope=enterprise或equity,revenue=S,earnings_power=E,equity_adjustment=B,capital_cost,capital_cost_basis=wacc或equity_cost,shares；另有valuation_date/financial_position_date/reason。E已扣维护、未扣成长投入，B为同范围核心到归母净桥 |
| franchise | status=supported/conditional/unsupported/not_assessed及reason；可用market/protection/durability/growth_scope/incremental_returns/counterevidence短答，不逐栏补研 |
| distribution | mode=ratio,value为小数（D=E×value）；或mode=direct,value为年度D，reason说明可持续性 |
| organic | revenue_growth、earnings_growth小数、investment、reason；收入/盈利增速分别有依据，不默认经营杠杆溢价 |
| organic.investment | mode=direct,value为年度增量投入；或mode=intensity,working_capital,fixed_capital,expensed_growth，后者I=S×收入增长×(两项资本系数之和)+额外费用化投入，各项明确为0才填0 |
| active | mode=direct,factor=F；或mode=return_ratio,incremental_return,capital_cost,scope；或mode=allocations,items:[{share,factor,reason}]且share合计1 |
| active可选极端 | mode=repeat,initial_factor,payout_ratio；F=payout×initial_factor/[1−(1−payout)×initial_factor]，分母非正不输出无限值，非默认 |
| decay | 见下节四种模式；必须实质考虑经济衰减，数字可选 |
| price | mode=market_cap或per_share,value,currency,date,sources；异币另有fx_to_valuation（1报价币兑换多少计价币）、fx_date |
| 分股类price | mode=share_classes,quotes:[{label,shares,value,currency,date,fx_to_valuation,fx_date}]，股类无重叠且覆盖同口径普通股数 |
| policy | 可选additional_margin；qualitative时可选qualitative_decay_buffer。比例小数，明确政策而非公司事实；无统一门槛，不擅改冻结policy |

企业scope用经营E与WACC，权益scope用税后股东E及equity_cost；不把经营利润除股权总价。金融企业不能机械剥经营性债务；本包非金融初始范围以外先说明行业适配，不能静默切口径。

## 资金账和回报

全部股权买价Q，核心买价M=Q−B；B资源正，融资/外部权益负，不能加扣两次。B不是资产模块总额。单股价乘全部同权股数是统一价格假设，非A/H实际集团市值。M非正时作净资源兑现判断，不输出无限回报；B缺失不填0。高回报主要靠大额资源扣回形成小M时，解释资源归属、必要留存及兑现，可能改判才改变B作情景，不统一打折。

D为匹配资本范围的可持续净分配，企业范围不等于个人现金股息；D/M是回报项，D/Q仅量级参照。还债已计D不能在剩余积极投资给还债因子。支持有机增长的I先扣，维护不重扣，E已保留的费用不重扣；负收入增长不机械算资本释放。存量客户粘性不证明新市场受保护，不能仅降低增长率代替范围判断。

A=E−D−I；A<0披露资金缺口，不自动借钱、砍分配或截零。A=0无需F；A>0缺F保留已知项与真实有效情景，不为凑数循环调查。F为投入创造的**全部价值/投入**：1保值，低于1毁损，高于1创造；积极贡献A×F/M，净创造A×(F−1)仅解释，不再相加。低息留存须考虑本金最终分配/永久留存，不能仅用利率/资本成本毁掉本金；同一提效不同时算有机增长与积极投资。

基准回报r=D/M＋有机盈利增速＋A×F/M，假设V≈M，是条件参照，非实际IRR。量化衰减只扣一次，净回报与资本成本之差用百分点，不是亏损概率。程序对0<净回报<资本成本且有机增速>0可做一次向下代理修正，不能反复上调或反解精确目标价。成长不输出growth_value/equity_value/target_price，不用市值−EPV称成长价值，不将三个模块相加。

## 衰减必须考虑，半衰期数字可选

按重大性分析优势持续性、逐步侵蚀或突发消失、支持/反证、失去优势后的盈利或残值及对价格判断的约束，不强填清单。可按机制、类比或自主假设粗估；数字无助或映射不合理时可直接有理由定性，无须先尝试报数或证明穷尽估计。半衰期不是企业寿命，失去超额回报不等于企业归零。

- `mode=deduct,rate,residual_fraction,reason`：年度扣减=rate×(1−残值比例)。
- `mode=half_life,half_life,convention,residual_fraction,reason`：正数年T，convention=rule72用0.72/T，constant_hazard用1−0.5^(1/T)，再乘(1−残值比例)。rate/T单个数值，区间放scenarios。残值0—1是估计，不默认为归零。
- `mode=embedded,reason`：明确已嵌入的净增长参数、侵蚀幅度和覆盖范围，不把历史利润率保守当已覆盖未来突发消失。该模式不附rate/half_life/residual_fraction。
- `mode=qualitative,reason`：说明选择理由、关键风险、优势丧失后的盈利/残值与条件约束；不附上述数值扣减字段。可保留衰减前回报和有理由的条件判断，缺半衰期不自动skip/defer。必要时用已有情景压力对照，压力不是事实，不为填字段补研。

`gross_gap`在其他参数固定时只是盈亏平衡年度扣减参照，不能倒推实际半衰期或凭差额证明风险已覆盖。qualitative buffer是额外要求的政策门槛，不是实际衰减；缺少风险与补偿的合理联系，不能仅因通过buffer称净回报已验证或安全边际成立。未设additional_margin不生成“满足明确额外要求”的结论。

## 情景与合成例

`price_grid`是完整price对象列表，只变买价，固定经营假设。`scenarios=[{name,reason,basis/distribution/organic/active/decay/policy/price/franchise中的明确变更}]`，同块浅合并；price/decay/active或mode切换整块替换，嵌套investment完整提供。各行从基准独立实际重算；文字情景写discussion_only，缺关键参数写not_calculated，不能用基准数伪装执行。用户冻结值仍优先。

`assets/growth-synthetic.json`匹配CNY合成EPV，basis_mode=reuse_epv，完整三步演示可直接重算。E=1.4亿、D=0.84亿、有机投资500万、A=5100万，F=1.6；Q=15亿、B=−1.5亿、M=16.5亿，三项回报约5.0909%/3%/4.9455%，合计13.0364%。定性衰减保留净回报未知，不称风险调整后已验证收益；所有输入均是教学假设。

另一个方法校验例是原书表8-1：S=30亿美元、E=2.4亿、M=40亿、D=1.44亿、I=450万、A=9150万、F=1.6；三项3.6%/3.5%/3.66%，合计10.76%。不把它的USD价格与本包CNY EPV混用；书本案例值和资本成本都不是企业默认参数。
