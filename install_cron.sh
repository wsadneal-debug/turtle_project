#!/bin/bash
#
# 港股风险新闻监控 - 定时任务安装脚本
#
# 功能：
# 1. 创建日志目录
# 2. 初始化数据库
# 3. 配置 crontab 定时任务
# 4. 验证配置
#

set -e

WORKSPACE="/home/yxy/.openclaw/workspace/hk_risk_news"
LOG_DIR="$WORKSPACE/logs"
SCHEDULER="$WORKSPACE/scheduler.py"
CRON_FILE="/tmp/hk_risk_cron.txt"

echo "============================================================"
echo "📦 港股风险新闻监控 - 定时任务安装"
echo "============================================================"

# 1. 创建日志目录
echo ""
echo "📁 创建日志目录..."
mkdir -p "$LOG_DIR"
echo "✅ 日志目录：$LOG_DIR"

# 2. 初始化数据库
echo ""
echo "🗄️  初始化数据库..."
python3 "$SCHEDULER" --init
echo "✅ 数据库初始化完成"

# 3. 创建 crontab 配置
echo ""
echo "⏰ 配置 crontab 定时任务..."

cat > "$CRON_FILE" << EOF
# 港股风险新闻监控 - 每天 18:00 执行（搜索截至昨天 18:00 的信息）
0 18 * * * cd $WORKSPACE && /usr/bin/python3 $SCHEDULER --cron >> $LOG_DIR/cron.log 2>&1
EOF

# 备份现有 crontab
if crontab -l > /dev/null 2>&1; then
    echo "📋 备份现有 crontab..."
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt
fi

# 安装新的 crontab
echo "📝 写入新的 crontab 配置..."
crontab "$CRON_FILE"

echo "✅ Crontab 配置完成"

# 4. 验证配置
echo ""
echo "🔍 验证配置..."
echo ""
echo "当前 crontab 配置:"
echo "------------------------------------------------------------"
crontab -l
echo "------------------------------------------------------------"

# 5. 测试执行
echo ""
echo "🧪 测试执行（立即运行一次）..."
python3 "$SCHEDULER" --run

# 6. 显示使用说明
echo ""
echo "============================================================"
echo "✅ 安装完成！"
echo "============================================================"
echo ""
echo "📋 配置信息:"
echo "  - 执行时间：每天 15:30"
echo "  - 脚本位置：$SCHEDULER"
echo "  - 日志目录：$LOG_DIR"
echo "  - 数据库：$WORKSPACE/risk_stocks.db"
echo ""
echo "🔧 管理命令:"
echo "  # 查看 crontab 配置"
echo "  crontab -l"
echo ""
echo "  # 立即手动执行一次"
echo "  python3 $SCHEDULER --run"
echo ""
echo "  # 查看最新日志"
echo "  tail -f $LOG_DIR/scheduler.log"
echo ""
echo "  # 查看 cron 日志"
echo "  tail -f $LOG_DIR/cron.log"
echo ""
echo "  # 编辑 crontab"
echo "  crontab -e"
echo ""
echo "  # 删除定时任务"
echo "  crontab -r"
echo ""
echo "============================================================"

# 清理临时文件
rm -f "$CRON_FILE"
