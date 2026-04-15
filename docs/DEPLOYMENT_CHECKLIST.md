# 📋 GitHub 上传前检查清单

⚠️ **重要**: 在上传到 GitHub 前，请务必完成以下检查，确保不泄露敏感信息！

---

## 🔒 敏感信息检查

### 1. 文件清理

- [ ] **数据库文件已删除**
  ```bash
  rm -f risk_stocks.db
  rm -f risk_stocks.db-journal
  ```

- [ ] **日志文件已删除**
  ```bash
  rm -rf logs/*.log
  rm -rf logs/*.json
  ```

- [ ] **输出数据已删除**
  ```bash
  rm -f keyword_search_*.json
  rm -f keyword_result_*.json
  rm -f unmapped_news_*.json
  rm -f verified_*.json
  rm -f crawl_*.json
  ```

- [ ] **缓存文件已删除**
  ```bash
  rm -rf __pycache__/
  rm -rf *.pyc
  ```

### 2. 配置文件检查

- [ ] **检查 config/ 目录**
  - 删除所有 `*.local.json` 文件
  - 删除所有包含实际路径的配置文件
  - 保留 `*.example.json` 模板文件

- [ ] **检查 .env 文件**
  - 删除 `.env` 文件（保留 `.env.example`）
  - 确保 `.env` 在 `.gitignore` 中

- [ ] **检查代码中的硬编码路径**
  ```bash
  # 搜索可能的本地路径
  grep -r "/home/" .
  grep -r "/Users/" .
  grep -r "C:\\Users\\" .
  grep -r "~/" .
  ```

### 3. 代码审查

- [ ] **检查是否有硬编码的 Token**
  ```bash
  grep -r "token" . --include="*.py" | grep -v ".pyc"
  grep -r "secret" . --include="*.py" | grep -v ".pyc"
  grep -r "password" . --include="*.py" | grep -v ".pyc"
  grep -r "api_key" . --include="*.py" | grep -v ".pyc"
  grep -r "webhook" . --include="*.py" | grep -v ".pyc"
  ```

- [ ] **检查是否有硬编码的 URL**
  ```bash
  # 保留公开的网站 URL（如 eastmoney.com）
  # 删除私有的 webhook URL
  ```

- [ ] **替换本地路径为环境变量**
  ```python
  # ❌ 不要这样写
  DB_PATH = '/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db'
  
  # ✅ 应该这样写
  import os
  DB_PATH = os.getenv('DB_PATH', 'risk_stocks.db')
  ```

### 4. .gitignore 验证

- [ ] **确认 .gitignore 包含以下规则**
  ```
  *.db
  *.sqlite
  logs/
  .env
  config/*.local.json
  output/
  data/
  keyword_*.json
  ```

- [ ] **测试 .gitignore 是否生效**
  ```bash
  git status
  # 确认敏感文件不在 "Changes to be committed" 列表中
  ```

### 5. Git 历史检查

- [ ] **检查 Git 历史中是否有敏感信息**
  ```bash
  # 查看历史提交
  git log --all --full-history -- "*.env"
  git log --all --full-history -- "*.db"
  
  # 如果有敏感信息已提交，需要清理历史
  # 参考：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
  ```

- [ ] **清理 Git 历史（如需要）**
  ```bash
  # 使用 BFG Repo-Cleaner
  java -jar bfg.jar --delete-files '*.db'
  java -jar bfg.jar --delete-files '*.env'
  
  # 或者使用 git filter-branch
  git filter-branch --force --index-filter \
    'git rm --cached --ignore-unmatch *.db *.env' \
    --prune-empty --tag-name-filter cat -- --all
  ```

### 6. 最终检查

- [ ] **运行 git status 确认**
  ```bash
  git status
  # 应该只看到代码文件和文档，没有敏感文件
  ```

- [ ] **运行 git diff 确认**
  ```bash
  git diff --cached
  # 确认没有敏感信息
  ```

- [ ] **检查文件大小**
  ```bash
  git count-objects -vH
  # 确认仓库大小合理（< 100MB）
  ```

---

## 📝 推荐的文件结构

上传到 GitHub 的应该是这样的结构：

```
hk-risk-news/
├── .gitignore              # ✅ 上传
├── .env.example            # ✅ 上传（模板）
├── README.md               # ✅ 上传
├── README_GITHUB.md        # ✅ 上传
├── DATABASE.md             # ✅ 上传
├── DEPLOYMENT.md           # ✅ 上传
├── CHANGELOG.md            # ✅ 上传
├── requirements.txt        # ✅ 上传
├── keyword_crawler.py      # ✅ 上传
├── browser_keyword_search.py  # ✅ 上传
├── scheduler.py            # ✅ 上传
├── stock_mapper.py         # ✅ 上传
├── database_manager.py     # ✅ 上传
├── config/
│   └── openclaw_cron.example.json  # ✅ 上传（模板）
├── scripts/                # ✅ 上传（如果有）
└── docs/                   # ✅ 上传（如果有）

# 以下文件 NOT 上传：
# - risk_stocks.db
# - logs/
# - output/
# - data/
# - .env
# - *.local.json
# - __pycache__/
```

---

## 🚀 上传步骤

### 1. 本地清理

```bash
cd /path/to/hk-risk-news

# 清理敏感文件
rm -f risk_stocks.db
rm -rf logs/
rm -rf output/
rm -rf data/
rm -f .env
rm -rf __pycache__/

# 验证清理
git status
```

### 2. 初始化 Git（如果还没有）

```bash
git init
git add .
git commit -m "Initial commit: HK Risk News Monitor"
```

### 3. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`hk-risk-news`
3. 可见性：Public 或 Private（根据需要）
4. **不要** 勾选 "Add a README file"
5. 点击 "Create repository"

### 4. 推送代码

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/hk-risk-news.git

# 推送代码
git branch -M main
git push -u origin main
```

### 5. 验证上传

1. 访问 GitHub 仓库页面
2. 检查文件列表
3. 确认没有敏感文件
4. 检查 README 是否正确显示

---

## ✅ 上传后检查

- [ ] 仓库页面显示正常
- [ ] README 正确渲染
- [ ] 没有敏感文件（.db, .env, logs 等）
- [ ] 代码文件完整
- [ ] 文档文件完整
- [ ] .gitignore 已上传
- [ ] .env.example 已上传

---

## 🔐 安全最佳实践

1. **永远不要上传**:
   - 数据库文件（*.db, *.sqlite）
   - 环境变量文件（.env）
   - 日志文件（*.log）
   - 包含 token 的配置文件
   - 个人数据文件

2. **使用环境变量**:
   - 所有配置通过环境变量或配置文件加载
   - 提供 `.example` 模板文件
   - 在文档中说明如何配置

3. **定期审查**:
   - 定期检查 Git 历史
   - 使用工具扫描敏感信息
   - 更新 .gitignore

4. **使用 GitHub Secrets**（如果使用 GitHub Actions）:
   - 不要在代码中硬编码 token
   - 使用 GitHub Secrets 存储敏感信息

---

## 🛠️ 有用的工具

### 检测敏感信息

```bash
# 安装 truffleHog
pip install truffleHog

# 扫描仓库
trufflehog .
```

### 检查大文件

```bash
# 找出大文件
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 | \
  cut -c 1-12,41- | \
  $(command -v gnumfmt || echo numfmt) --field=2 --to=iec-i --suffix=B --padding=7
```

---

*最后更新：2026-04-15*
