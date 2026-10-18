# Turtle Project · 龟龟项目

面向 A 股与港股研究的企业分析方法、风险新闻工具和项目架构文档。

当前公开内容包括 **龟龟skill 5.2.2（中文 / English）**、风险新闻工具源码，以及数据同步、计算、评分、扫描和回测等模块的设计说明。仓库并未包含架构文档所描述的全部运行系统；各部分的使用方式与完成状态见下文。

## 从这里开始

| 你想做什么 | 入口 |
|---|---|
| 使用中文 Skill 分析企业 | [中文说明](skill/README.md) · [中文 ZIP](skill/turtle-skill-v5.2.2-zh-CN.zip) |
| Use the English analysis Skill | [English guide](skill/translations/en/README.md) · [English ZIP](skill/turtle-skill-v5.2.2-en.zip) |
| 查看分析方法本体 | [中文入口](skill/skills/turtle-skill/SKILL.md) · [English entry](skill/translations/en/skills/turtle-skill/SKILL.md) |
| 了解风险新闻工具 | [模块说明](hk-risk-news/README.md) · [核心源码](hk-risk-news/core/) |
| 阅读整体架构和模块设计 | [文档索引](prompts/README.md) · [总架构](prompts/ARCHITECTURE_PROMPT.md) |

## 龟龟skill 5.2.2

先研究经营，再判断价格。基础研究采用六个经营问题与一次价格后裁决，选定最可能的经营基准；现金回本默认采用正常化历史平均＋经营及资本项目阶段调整，六年归母现金直接入算，保留负现金。合理估计须披露依据与限制，账面权益代理不等于法律持股或可上划现金。

另附可单独安装的 `turtle-due-diligence`（尽调方法V2.3），包含十方向60题、质询、三种情景及五项裁决。额外尽调默认关闭，用户明确启用后执行。宿主支持且用户授权时可派有限子代理处理决定性缺口，由主模型综合；无需固定模型、私有数据库或付费数据接口。

### 安装与使用

选择一种语言，解压后将所需完整Skill目录放入宿主支持的位置，保留references和scripts，不要只复制SKILL.md。完整套件含基础研究与可选尽调；只需要尽调时也可选独立包。

| 安装包 | 中文 | English |
|---|---|---|
| 基础研究＋可选尽调 | [下载](skill/turtle-skill-v5.2.2-zh-CN.zip) | [Download](skill/turtle-skill-v5.2.2-en.zip) |
| 独立尽调 | [下载](skill/turtle-due-diligence-v5.2.2-zh-CN.zip) | [Download](skill/turtle-due-diligence-v5.2.2-en.zip) |

示例：

> 使用 turtle-skill 分析指定企业，注明截止日和来源；本次启用 turtle-due-diligence 完整尽调。允许在明确预算内派子代理查证细分问题，主模型综合。正文先给结论，完整问答和计算留在附录。

只研究附件可明确“不联网”；不启用尽调也可独立完成基础研究。Skill不自带数据、模型额度或交易权限。双语入口同名，避免重复安装。

### 版本与验证

当前基础方法/包版本 **5.2.2（2026-10-18修正）**，尽调方法 **2.3**。详见[中文变更记录](skill/CHANGELOG.md)及[English changelog](skill/translations/en/CHANGELOG.md)。旧0.4.0 ZIP保留作历史存档。

完整语言套件各35文件，独立尽调各15文件。离线Skill测试105项通过、2项历史归档缺失跳过；检查双语公式、四份脚本、引用、自包含解压运行和ZIP源码一致性。真实合成案例测试覆盖阶段付款、归属与负现金；完整公开资料试跑仍存在营运资金正常化、项目付款解释和口径审阅问题，不能将技术完成当作结论正确或收益保证。

本次发布仅包含方法、脚本、公开说明和合成算例，已检查新增文件及ZIP内容；未上传公司研究底稿、数据库、模型日志、账户凭据、本机路径或会话标识。此检查不声称清理了仓库所有历史提交。旧数值接口需显式使用 `legacy_cash_path`，默认 `cash_path` 接受六年 `annual_fcf`。

## 风险新闻工具

[hk-risk-news/](hk-risk-news/) 保留了关键词搜索辅助、新闻解析、股票名称映射、去重入库、数据库管理和调度脚本，另有部署记录及历史实现。

这是需要适配环境的工具源码。部分脚本仍采用固定工作目录，并依赖外部浏览器能力、股票别名数据和本地数据库；提供 `.env.example` 不代表所有入口已读取该配置。旧说明中的覆盖数量与运行记录不代表新环境已经具备相同数据或完成部署。

建议先阅读[模块说明](hk-risk-news/README.md)、[部署说明](hk-risk-news/docs/DEPLOYMENT.md)及对应源码，再配置独立研究环境。部分初始化路径包含重建表逻辑，运行前应核对目标数据库。克隆仓库不会自动安装定时任务，本次文档更新也未执行新闻采集或验证其在线数据源。

## 架构与模块文档

[prompts/](prompts/) 描述更广的股票研究框架：数据同步、统一计算、评分、每日扫描、发布、回测和模拟组合。其中的模块名与流程用于说明设计，不意味着对应完整代码已在本仓库公开。

主要原则是原始数据同步、统一计算落库、消费端读取统一结果，各模块保持明确职责。阅读时先看[总架构](prompts/ARCHITECTURE_PROMPT.md)，再按[索引](prompts/README.md)选择模块文档。独立企业分析 Skill 的现行方法以其自身入口及参考为准。

## 仓库结构

```text
turtle_project/
├── README.md                # 总说明与使用入口
├── README_ROOT.md           # 兼容旧链接的索引
├── skill/                   # 中文方法源码及双语 ZIP
│   ├── skills/turtle-skill/
│   └── translations/en/     # 英文完整源码
├── hk-risk-news/
│   ├── core/                # 新闻处理、映射、数据库和调度
│   ├── scripts/             # 批处理与调度安装脚本
│   ├── docs/                # 模块说明和历史部署记录
│   ├── examples/            # 配置示例
│   └── legacy/              # 历史实现
├── prompts/                 # 架构和模块设计说明
├── data/                    # 占位目录
├── logs/                    # 占位目录
└── output/                  # 占位目录
```

### 获取当前 Skill 分支

```bash
git clone --branch 龟龟skill https://github.com/wsadneal-debug/turtle_project.git
cd turtle_project
```

上述分支包含 5.2.2 双语 Skill 和本说明。只使用 Skill 时，直接下载上方对应语言的 ZIP 即可，无需安装新闻工具的 Python 依赖。

## 维护与许可说明

提交修改时请注明影响的模块、方法版本和实际验证结果。双语方法修改应同步核对公式与引用；研究输入、输出、账户凭据及运行数据库应保留在发布包之外。

旧版仓库说明标注 MIT，但当前文件树未提供对应的 `LICENSE` 正文；Skill 包也保留了许可由所有者决定的说明。本次更新不新增或变更许可授权，具体授权范围仍需由所有者明确。

文档更新日期：2026-10-18。
