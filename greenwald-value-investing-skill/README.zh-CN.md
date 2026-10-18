# 格林沃尔特-价值投资 Skill

[English](README.md)

可独立安装的 AI skill，用资产再生产价值、正常盈利能力价值（EPV）和给定价格下的成长回报，手动研究少量 A 股、港股非金融企业。宿主 AI 发现可用数据工具、阅读官方财报、提出估计并复核；随包 Python 仅用标准库完成确定性计算，两种语言共用相同算法。

- **资产再生产价值**：估计当前取得企业现有同等经营能力所需的经济成本，加上非经营资源、扣除义务及其他权益，得到归母普通股价值。
- **EPV**：在不依赖增长的当前经营规模上估计正常可分配盈利，明确维护、税、资本成本及经营价值到归母普通股的调整桥。
- **成长回报**：先判断持续竞争优势及受保护增长范围，再在适用时估计给定买价下的条件回报，分别考虑分配、有机增长、剩余资金投资和经济衰减；也可得出跳过或暂缓的结论。

三个方法独立，不相加、不平均，不把成长回报转成另一个价值总额。允许有理由并明确标注的估计，小项目缺口不自动阻断基准估值。算术完成不等于买入决定，资产/EPV也不是保证底价。

## 取得完整技能目录

源码已公开在 GitHub 的[格林沃尔特-价值投资-skill 分支](https://github.com/wsadneal-debug/turtle_project/tree/%E6%A0%BC%E6%9E%97%E6%B2%83%E5%B0%94%E7%89%B9-%E4%BB%B7%E5%80%BC%E6%8A%95%E8%B5%84-skill/greenwald-value-investing-skill)。

打开该分支，选择 **Code → Download ZIP**，解压下载文件后进入仓库内的 `greenwald-value-investing-skill/`。这里有中英文说明和 `skills/` 下的两个完整技能目录。不要把整个仓库作为一个 skill 安装，应按下文选择完整的语言目录；下载文件中还会包含远端仓库原有的其他项目文件。

## 选择语言并安装

- `skills/three-step-value`：中文指引、示例及宿主最终交付。
- `skills/three-step-value-en`：英文指引、UI、参考文件、合成示例及宿主最终交付。共用计算器生成的技术底稿 `report.md`、命令帮助/诊断、警告及部分自动生成 JSON 文字仍为中文；宿主据保存的实际计算结果用英文解释或翻译，不能宣称计算器已全英文。

将完整技能目录复制到目标 AI 助手支持的 skill 目录。例如使用常见 Codex 目录：

```bash
mkdir -p ~/.codex/skills
cp -R skills/three-step-value ~/.codex/skills/
```

使用尚不存在的目标目录，不合并覆盖旧安装。若单独提供语言 ZIP，解压后就是完整技能目录。两版名称不同，可同时安装，通常调用所需语言的一版。其他宿主须支持本地 skill 指引、文件读写和 Python 执行；可读文件的助手也能直接按该目录 `SKILL.md` 执行。

需要 Python 3.10+及本地文件读写，不需要 pip 安装、特定私人库、模型 CLI、API 凭据或计算器指定的付费供应商；宿主自身账号和工具的使用条件另计。联网/文档工具用来取得缺少的官方报告，有完整上传材料时可离线使用。不能执行脚本的纯聊天环境只能讨论方法，不能称已执行程序验算。

## 如何发起研究

> 使用 $three-step-value 完整研究我指定的企业。先发现可用金融数据和报告工具，并一次询问我是否有本地数据或财报；准备最近两份完整年报及其后最新季报或中报。三个结果独立，以通俗中文交付。

> 使用 $three-step-value，只做 EPV，使用这些年报和中报。区分披露事实、估计和实际 Python 计算。

> 复用这份明确选定的 EPV，在我给定的价格下研究成长回报。先判断持续竞争优势，半衰期数值可选，保留原 EPV。

宿主把已有来源适配为内部 JSON packet，不要求用户建立特定数据库。辅助器不自动从 PDF 识别财务事实，也不自行调用研究模型。具体参数合同和六步资产/EPV/成长命令见所选技能 `references/runtime.md`。产物写技能目录之外，每个方法使用新目录。

## 离线合成演示

从下载后的 `greenwald-value-investing-skill/` 目录运行，选择全新输出目录。全部为虚构教学参数，短文本不是完整真实年报；只验证实际程序入口，零模型、零网络：

```bash
skill=skills/three-step-value
work=/tmp/three-step-value-demo-zh
python3 "$skill/scripts/run.py" --help
python3 "$skill/scripts/run.py" prepare --packet "$skill/assets/packet-synthetic.json" --method asset --run-dir "$work/asset"
python3 "$skill/scripts/run.py" recalculate --run-dir "$work/asset" --valuation "$skill/assets/asset-synthetic.json"
python3 "$skill/scripts/run.py" prepare --packet "$skill/assets/packet-synthetic.json" --method epv --asset-run "$work/asset" --run-dir "$work/epv"
python3 "$skill/scripts/run.py" recalculate --run-dir "$work/epv" --valuation "$skill/assets/epv-synthetic.json"
python3 "$skill/scripts/run.py" growth --epv-run "$work/epv" --request "$skill/assets/growth-request-synthetic.json" --run-dir "$work/growth"
python3 "$skill/scripts/run.py" recalculate --run-dir "$work/growth" --valuation "$skill/assets/growth-synthetic.json"
```

教学结果：资产法归母17亿元、每股17元；EPV归母12.5亿元、每股12.5元；成长衰减前条件回报约13.0364%。基准定性衰减不产生已量化净回报。英文版参数及算术一致，改选 `skills/three-step-value-en` 并另建输出目录即可。

## 公开状态

本技能目录的源码已公开到上方 GitHub 分支，目前尚未选择或授予开源许可证，公开可见不等于已获得开源许可，不宣称 MIT 等未指定许可。本目录仅含技能说明、合成教学素材及必要计算代码；本次技能发布不含私人数据库、真实公司研究产物、凭据、内部日志或本地开发库的 Git 历史。
