# GitHub 推送指南

## 当前状态

✅ **Git 仓库已初始化**
✅ **远程地址已配置**: `git@github.com-myrepo:wsadneal-debug/turtle_project.git`
✅ **SSH 密钥已生成**: `~/.ssh/repo_deploy_key`
✅ **代码已提交**: 60 个文件，10849 行代码

## ⚠️ 需要完成的步骤

### 方案一：使用 Deploy Key（推荐用于自动化）

1. **复制公钥内容**
   ```bash
   cat ~/.ssh/repo_deploy_key.pub
   ```
   
   输出：
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMxSq2r/mwwex/gJDiF0+m9alJp95cyYF56yK3RWpx+P deploy-key-for-your-repo
   ```

2. **添加到 GitHub 仓库**
   - 访问：https://github.com/wsadneal-debug/turtle_project/settings/keys
   - 点击 "Add deploy key"
   - 标题：`turtle_project_deploy_key`
   - 密钥：粘贴上面的公钥内容
   - ✅ 勾选 "Allow write access"
   - 点击 "Add key"

3. **测试连接**
   ```bash
   ssh -T git@github.com-myrepo
   ```
   应该看到：
   ```
   Hi wsadneal-debug/turtle_project! You've successfully authenticated, but GitHub does not provide shell access.
   ```

4. **推送代码**
   ```bash
   cd /home/yxy/.openclaw/workspace/hk_risk_news
   git push -u origin main
   ```

### 方案二：使用 GitHub CLI（最简单）

如果已安装 GitHub CLI：

```bash
# 登录 GitHub
gh auth login

# 推送代码
cd /home/yxy/.openclaw/workspace/hk_risk_news
git push -u origin main
```

### 方案三：使用 HTTPS + Token（备选）

```bash
# 更改远程地址为 HTTPS
git remote set-url origin https://github.com/wsadneal-debug/turtle_project.git

# 推送（会提示输入 token）
git push -u origin main
```

生成 Personal Access Token：
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成后复制 token
5. 推送时使用 token 作为密码

---

## 验证推送成功

推送成功后，访问：
https://github.com/wsadneal-debug/turtle_project

应该能看到：
- ✅ 60 个文件
- ✅ README_GITHUB.md 显示在项目首页
- ✅ 提交历史：Initial commit: HK Risk News Monitor v2.0

---

## 常见问题

### Q1: Permission denied (publickey)

**原因**: Deploy key 未添加到 GitHub 或权限不足

**解决**:
1. 确认公钥已添加到仓库 Settings → Deploy keys
2. 确认勾选了 "Allow write access"
3. 测试：`ssh -T git@github.com-myrepo`

### Q2: 仓库不存在

**解决**:
```bash
# 确认远程地址
git remote -v

# 如果错误，重新设置
git remote set-url origin git@github.com-myrepo:wsadneal-debug/turtle_project.git
```

### Q3: SSH 配置问题

**解决**:
```bash
# 检查 SSH 配置
cat ~/.ssh/config

# 应该是：
# Host github.com-myrepo
#  HostName github.com
#  User git
#  IdentityFile ~/.ssh/repo_deploy_key
#  IdentitiesOnly yes
```

---

## 推送后的后续步骤

1. **检查仓库**
   - 访问 https://github.com/wsadneal-debug/turtle_project
   - 确认文件完整
   - 确认 README 正确显示

2. **设置 GitHub Pages**（可选）
   - Settings → Pages
   - Source: main branch
   - 可以在线查看文档

3. **配置 GitHub Actions**（可选）
   - 添加自动测试
   - 添加自动部署

4. **邀请协作者**（如需要）
   - Settings → Collaborators
   - 添加协作者

---

## 当前提交摘要

```
Commit: 1ca8b3c
Branch: main
Files: 60
Lines: 10,849

核心功能:
- 20 个风险关键词搜索
- 多搜索源支持（东方财富网、第一财经）
- A+H 股市场覆盖（7876 条股票别名）
- 智能股票映射
- 自动去重入库
- 定时自动执行（每天 18:00）

已清理敏感信息:
- 数据库文件 (*.db)
- 日志文件 (logs/)
- 输出数据 (output/, data/, *.json)
- 个人配置文件 (.env, *.local.json)
```

---

*创建时间：2026-04-15*
