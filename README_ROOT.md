# Turtle Project - 龟龟项目

🐢 **智能投资决策系统**

---

## 📁 项目结构

```
turtle_project/
├── prompts/                 # 【最高优先级】项目提示词配置
│   ├── README.md            # 提示词使用说明
│   ├── ARCHITECTURE_PROMPT.md
│   ├── A_STOCK_DATA_PROMPT.md
│   ├── B_COMPUTE_PROMPT.md
│   ├── B_SCORING_PROMPT.md
│   ├── C_DAILY_SCAN_PROMPT.md
│   ├── D_SCAN_PUBLISH_PROMPT.md
│   ├── E_DAILY_PIPELINE_PROMPT.md
│   ├── F_BACKTEST_PROMPT.md
│   └── G_SIMULATED_PORTFOLIO_PROMPT.md
│
├── hk-risk-news/            # 港股风险新闻监控系统
│   ├── core/                # 核心代码
│   ├── scripts/             # 辅助脚本
│   ├── docs/                # 项目文档
│   ├── legacy/              # 历史代码
│   └── README.md            # 子系统说明
│
├── data/                    # 数据目录
├── logs/                    # 日志目录
└── output/                  # 输出目录
```

---

## 🔮 Prompts - 项目提示词配置

**优先级：最高** ⭐⭐⭐⭐⭐

`prompts/` 目录包含整个项目的核心提示词配置，指导 AI 助手如何理解和执行项目任务。

### 提示词列表

| 文件 | 用途 |
|------|------|
| `README.md` | 提示词文档说明 |
| `ARCHITECTURE_PROMPT.md` | 项目架构提示词 |
| `A_STOCK_DATA_PROMPT.md` | A 股数据提示词 |
| `B_COMPUTE_PROMPT.md` | 计算提示词 |
| `B_SCORING_PROMPT.md` | 评分提示词 |
| `C_DAILY_SCAN_PROMPT.md` | 每日扫描提示词 |
| `D_SCAN_PUBLISH_PROMPT.md` | 扫描发布提示词 |
| `E_DAILY_PIPELINE_PROMPT.md` | 每日流水线提示词 |
| `F_BACKTEST_PROMPT.md` | 回测提示词 |
| `G_SIMULATED_PORTFOLIO_PROMPT.md` | 模拟组合提示词 |

### 使用说明

1. **AI 助手启动时首先读取** `prompts/README.md`
2. 根据任务类型加载对应的提示词文件
3. 遵循提示词中的指导和规范执行任务

---

## 📰 子系统

### 1. 港股风险新闻监控系统 (hk-risk-news/)

🔴 **自动监控 A/H 股市场风险新闻，智能识别风险股票**

**功能**:
- 20 个风险关键词搜索
- 多搜索源支持（东方财富网、第一财经）
- A+H 股市场覆盖（7876 条股票别名）
- 智能股票映射
- 自动去重入库
- 定时自动执行（每天 18:00）

**文档**: [hk-risk-news/README.md](hk-risk-news/README.md)

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone git@github.com-myrepo:wsadneal-debug/turtle_project.git
cd turtle_project
```

### 2. 阅读提示词文档

```bash
cat prompts/README.md
```

### 3. 进入子系统

```bash
# 港股风险新闻监控系统
cd hk-risk-news
cat README.md
```

---

## 📋 目录说明

| 目录 | 用途 | 权限 |
|------|------|------|
| `prompts/` | 项目提示词配置 | 🔒 只读，核心配置 |
| `hk-risk-news/` | 港股风险新闻系统 | ✅ 可修改 |
| `data/` | 数据文件 | 📝 运行时生成 |
| `logs/` | 日志文件 | 📝 运行时生成 |
| `output/` | 输出文件 | 📝 运行时生成 |

---

## 🔐 提示词优先级

```
最高优先级 → prompts/
            ↓
        指导整个项目
            ↓
    各子系统遵循提示词规范
```

**重要**: 
- `prompts/` 目录下的文件是项目的核心配置
- 所有 AI 助手必须首先读取并遵循这些提示词
- 修改提示词需要谨慎，影响整个项目行为

---

## 📖 详细文档

- **项目提示词**: [prompts/README.md](prompts/README.md)
- **港股风险新闻系统**: [hk-risk-news/README.md](hk-risk-news/README.md)
- **部署指南**: [hk-risk-news/docs/DEPLOYMENT_CHECKLIST.md](hk-risk-news/docs/DEPLOYMENT_CHECKLIST.md)

---

## 🤝 贡献指南

1. **修改提示词**: 需谨慎，影响整个项目
2. **添加子系统**: 在根目录创建新目录
3. **遵循规范**: 遵循 `prompts/` 中的指导

---

## 📄 许可证

MIT License

---

*最后更新：2026-04-15*
