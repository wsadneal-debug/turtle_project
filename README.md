# 格林沃尔特-价值投资 Skill

面向少量 A 股、港股非金融企业的中英文 AI 研究技能。以资产再生产价值、正常盈利能力价值（EPV）和给定价格下的成长回报，分别回答“复制现有经营资源要花多少”“当前正常经营能支持多少价值”“这个买价下的成长回报是否有合理依据”。

- **资产再生产价值**：估计当前取得现有同等经营能力的经济成本，加上非经营资源、扣除义务及其他权益，得到归母普通股价值。
- **EPV**：在不依赖增长的当前规模上，估计正常可分配盈利，明确维护投入、税、资本成本及归母股权调整。
- **成长回报**：先判断持续竞争优势及其保护范围，适用时再估计给定买价下的分配、有机增长与剩余资金投资回报，并考虑经济衰减；可以判断跳过或暂缓，不强求每家企业计算成长回报。

## 源码、说明与下载

- [完整技能源码目录](greenwald-value-investing-skill/)
- [中文说明与完整使用方法](greenwald-value-investing-skill/README.zh-CN.md)
- [English guide](greenwald-value-investing-skill/README.md)
- [中文技能源码](greenwald-value-investing-skill/skills/three-step-value/)
- [English skill source](greenwald-value-investing-skill/skills/three-step-value-en/)
- [网站下载页：中文及英文 ZIP](https://turtle-web-cke.pages.dev/download/)

在本分支选择 **Code → Download ZIP**，解压后可取得完整源码。安装时选一个完整语言技能目录；不能只复制 `SKILL.md`，也不要把整个仓库作为一个 skill 安装。

## 安装与环境

需要支持本地技能指引、文件读写和 Python 执行的 AI 助手，以及 **Python 3.10+**。以下从下载并解压后的仓库根目录执行，以常见 Codex 技能目录为例：

```bash
cd greenwald-value-investing-skill
mkdir -p ~/.codex/skills
cp -R skills/three-step-value ~/.codex/skills/
```

英文版将最后一行改为：

```bash
cp -R skills/three-step-value-en ~/.codex/skills/
```

使用尚不存在的安装目标，不合并覆盖旧版；其他宿主使用其支持的技能目录。两版名称不同，可以同时安装。若从网站取得单语言 ZIP，解压后的完整目录可直接放入技能目录。

宿主 AI 负责发现可用 MCP/金融数据/报告工具、阅读报告、提出假设、综合和复核；随包 Python 只用标准库执行确定性计算并生成技术底稿，无需 pip 安装、特定私人数据库、模型 CLI 或计算器指定的 API 凭据。宿主工具与账号自身的条件另计。可从官方公开报告、用户上传文件开始，也可只读使用用户明确提供的数据库或资料目录，不要求建立特定私库。辅助程序不会自动从 PDF 识别财务事实，也不会自行调用研究模型；没有脚本执行能力时，不能声称已完成程序验算。

## 示例请求

> 使用 $three-step-value 研究我指定的企业。先发现可用数据和报告工具，并一次询问我是否有本地数据库或财报目录。准备最近两份完整年报及其后最新季报或中报，三个方法分别研究、计算和交付。

> 使用 $three-step-value，只做 EPV，资料是这些年报和中报。区分披露事实、正常化估计与实际 Python 计算。

> 复用这份明确选定的 EPV，在我给定的价格下研究成长回报。先判断持续竞争优势；半衰期数字可选，保留原 EPV。

> Use $three-step-value-en to research my chosen business, run the required Python calculations, and explain the independent results in English.

中文和英文版的参数合同与算法相同。英文版已提供英文指引、界面说明、参考材料及合成教学示例，并要求宿主以英文交付；共用计算器的 `report.md`、警告、命令帮助/诊断及部分生成文字仍为中文，宿主依据保存的实际数值解释或翻译，不宣称计算器已全英文。

## 结果与边界

三个方法的结果独立，不相加、不平均；不把市值减 EPV 当成成长价值，也不将成长回报换成第三个总价值。允许有依据的粗估、类比和自主假设，但须与披露事实分开；小项目缺口不自动阻断资产或 EPV 基准估值。

成长适用性与回报计算分别说明。衰减可以定性分析；未量化时，衰减前条件回报不能冒称已验证的净回报，净回报未知就保留未知。教学示例不是真实企业估值。研究完成、算术完成、方法适用与买入决定并不相同，资产价值与 EPV 也不是保证底价。

源码已经公开，**开源许可证尚未选定**；公开可见不等于已授予 MIT 或其他未指定的开源许可。
