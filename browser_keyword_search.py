#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 浏览器关键词搜索工具

这个脚本配合 OpenClaw browser 工具使用：
1. 定义 20 个风险关键词
2. 生成搜索 URL 列表
3. 接收浏览器截图/快照结果
4. 解析并保存为 JSON 供 keyword_crawler.py 使用

使用方法：
1. 使用 browser 工具依次访问每个关键词的搜索 URL
2. 使用 browser snapshot 获取搜索结果
3. 将结果传递给此脚本解析
4. 运行 keyword_crawler.py 入库
"""

import json
import re
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

WORKSPACE = Path('/home/yxy/.openclaw/workspace/hk_risk_news')

# 20 个风险关键词
RISK_KEYWORDS = [
    # 监管处罚类
    '立案调查', '行政处罚', '监管函', '问询函',
    # 审计问题类
    '审计师辞任', '无法表示意见', '财报延期',
    # 债务违约类
    '债务违约', '债券违约', '无法兑付', '债务逾期',
    # 经营风险类
    '破产清算', '资产冻结', '重大亏损',
    # 高管变动类
    '实控人被捕', '董事长辞职', '被调查',
    # 停牌风险类
    '停牌', '暂停上市', '终止上市'
]

# 关键词到风险类型的映射
KEYWORD_TO_RISK_TYPE = {
    '立案调查': '监管处罚',
    '行政处罚': '监管处罚',
    '监管函': '监管处罚',
    '问询函': '监管处罚',
    '审计师辞任': '审计问题',
    '无法表示意见': '审计问题',
    '财报延期': '审计问题',
    '债务违约': '债务违约',
    '债券违约': '债务违约',
    '无法兑付': '债务违约',
    '债务逾期': '债务违约',
    '破产清算': '经营风险',
    '资产冻结': '经营风险',
    '重大亏损': '经营风险',
    '实控人被捕': '高管变动',
    '董事长辞职': '高管变动',
    '被调查': '高管变动',
    '停牌': '停牌风险',
    '暂停上市': '停牌风险',
    '终止上市': '停牌风险'
}

# 风险等级映射
RISK_LEVEL_MAP = {
    '监管处罚': 'HIGH',
    '债务违约': 'HIGH',
    '停牌风险': 'HIGH',
    '审计问题': 'MEDIUM',
    '经营风险': 'MEDIUM',
    '高管变动': 'MEDIUM'
}

# 搜索 URL 模板
EASTMONEY_SEARCH_URL_TEMPLATE = 'https://so.eastmoney.com/news/s?keyword={keyword}'
YICAI_SEARCH_URL_TEMPLATE = 'https://www.yicai.com/search?keys={keyword}'

# 搜索源配置
SEARCH_SOURCES = [
    {
        'name': '东方财富网',
        'url_template': EASTMONEY_SEARCH_URL_TEMPLATE,
        'domain': 'eastmoney.com',
        'wait_ms': 5000  # 搜索间隔 5 秒
    },
    {
        'name': '第一财经',
        'url_template': YICAI_SEARCH_URL_TEMPLATE,
        'domain': 'yicai.com',
        'wait_ms': 5000  # 搜索间隔 5 秒
    }
]


def get_search_urls():
    """生成所有关键词的搜索 URL（多搜索源）"""
    from urllib.parse import quote
    
    urls = {
        '东方财富网': {},
        '第一财经': {}
    }
    
    for keyword in RISK_KEYWORDS:
        encoded_keyword = quote(keyword)
        urls['东方财富网'][keyword] = f'https://so.eastmoney.com/news/s?keyword={encoded_keyword}'
        urls['第一财经'][keyword] = f'https://www.yicai.com/search?keys={encoded_keyword}'
    
    return urls


def parse_snapshot_results(snapshot_data, keyword):
    """
    解析浏览器 snapshot 返回的结果
    
    snapshot_data 格式示例:
    {
        "links": [
            {"ref": "e20", "text": "北京对哈啰违规超量投放共享单车进行立案调查", "url": "http://biz.eastmoney.com/..."},
            ...
        ]
    }
    """
    results = []
    
    if isinstance(snapshot_data, dict):
        # 处理 links
        links = snapshot_data.get('links', [])
        for link in links:
            text = link.get('text', '')
            url = link.get('url', '') or link.get('href', '')
            
            # 过滤掉非新闻链接（如分页、导航等）
            if not text or not url:
                continue
            if 'eastmoney.com' not in url:
                continue
            if '/a/' not in url and '/news/' not in url:
                continue
            
            results.append({
                'title': text,
                'url': url
            })
    
    return results


def parse_search_page(html_or_text, keyword):
    """
    从搜索页面 HTML 或文本中解析搜索结果
    
    返回格式:
    [
        {'title': '...', 'url': '...'},
        ...
    ]
    """
    results = []
    
    # 匹配新闻标题和链接
    # 东方财富搜索结果格式：<a href="http://finance.eastmoney.com/a/202604113702012257.html">标题</a>
    pattern = r'<a[^>]+href=["\']([^"\']*eastmoney\.com/a/[^"\']+)["\'][^>]*>([^<]+)</a>'
    
    for match in re.finditer(pattern, html_or_text, re.IGNORECASE):
        url = match.group(1)
        title = match.group(2).strip()
        
        if title and url:
            results.append({
                'title': title,
                'url': url
            })
    
    return results


def save_search_results(all_results):
    """保存搜索结果到 JSON 文件"""
    crawl_date = datetime.now().strftime('%Y-%m-%d')
    output_file = WORKSPACE / f'keyword_search_{crawl_date.replace("-", "")}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    return output_file


def generate_prompt_for_agent():
    """
    生成给 AI Agent 的提示词，指导其使用浏览器工具进行搜索
    
    这个提示词可以直接用在 cron 任务中
    """
    urls = get_search_urls()
    
    prompt = """# 港股风险新闻监控 - 浏览器搜索任务（多搜索源）

请使用 OpenClaw browser 工具完成以下任务：

## 任务说明
依次访问东方财富网和第一财经搜索页面，搜索 20 个风险关键词，抓取搜索结果。

## 搜索源 (2 个)
1. **东方财富网**: https://so.eastmoney.com/news/s?keyword={关键词}
2. **第一财经**: https://www.yicai.com/search?keys={关键词}

## 关键词列表 (20 个)

### 监管处罚类 (4 个)
- 立案调查
- 行政处罚  
- 监管函
- 问询函

### 审计问题类 (3 个)
- 审计师辞任
- 无法表示意见
- 财报延期

### 债务违约类 (4 个)
- 债务违约
- 债券违约
- 无法兑付
- 债务逾期

### 经营风险类 (3 个)
- 破产清算
- 资产冻结
- 重大亏损

### 高管变动类 (3 个)
- 实控人被捕
- 董事长辞职
- 被调查

### 停牌风险类 (3 个)
- 停牌
- 暂停上市
- 终止上市

## 执行步骤

### 对每个关键词，依次搜索 2 个搜索源：

#### 搜索源 1：东方财富网
1. **导航到搜索页面**
   ```
   browser(action="navigate", profile="openclaw", url="https://so.eastmoney.com/news/s?keyword={URL 编码的关键词}")
   ```

2. **等待页面加载（5 秒）**
   ```
   browser(action="act", request={"kind": "wait", "timeMs": 5000})
   ```

3. **获取搜索结果**
   ```
   browser(action="snapshot", profile="openclaw", interactive=True)
   ```

4. **提取链接信息**
   从 snapshot 结果中提取所有 eastmoney.com/a/ 开头的新闻链接，记录标题和 URL

#### 搜索源 2：第一财经
1. **导航到搜索页面**
   ```
   browser(action="navigate", profile="openclaw", url="https://www.yicai.com/search?keys={URL 编码的关键词}")
   ```

2. **等待页面加载（5 秒）**
   ```
   browser(action="act", request={"kind": "wait", "timeMs": 5000})
   ```

3. **获取搜索结果**
   ```
   browser(action="snapshot", profile="openclaw", interactive=True)
   ```

4. **提取链接信息**
   从 snapshot 结果中提取所有 yicai.com 开头的新闻链接，记录标题和 URL

## 输出格式

将结果保存为 JSON 格式：
```json
{
  "crawl_date": "2026-04-15",
  "crawl_time": "2026-04-15 18:00:00",
  "立案调查": [
    {"title": "某某公司被立案调查", "url": "http://finance.eastmoney.com/a/..."},
    ...
  ],
  "行政处罚": [...],
  ...
}
```

## 注意事项
- **搜索间隔**: 每次搜索后等待 5 秒再获取 snapshot（避免页面未加载完成）
- **东方财富网**: 只提取 eastmoney.com/a/ 开头的新闻链接
- **第一财经**: 只提取 yicai.com/search/ 或 yicai.com/news/ 开头的新闻链接
- **去重**: 数据库基于 URL 自动去重，已存在的记录不会重复入库
- **错误处理**: 如果某个搜索源失败，继续下一个

## 完成后
运行以下命令处理结果并入库：
```bash
python3 /home/yxy/.openclaw/workspace/hk_risk_news/keyword_crawler.py
```
"""
    return prompt


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='港股风险新闻监控 - 浏览器关键词搜索工具')
    parser.add_argument('--urls', action='store_true', help='输出所有搜索 URL')
    parser.add_argument('--prompt', action='store_true', help='输出 Agent 提示词')
    parser.add_argument('--test', action='store_true', help='测试模式')
    
    args = parser.parse_args()
    
    if args.urls:
        urls = get_search_urls()
        for keyword, url in urls.items():
            print(f"{keyword}: {url}")
    
    elif args.prompt:
        print(generate_prompt_for_agent())
    
    elif args.test:
        # 测试数据
        test_data = {
            'crawl_date': '2026-04-15',
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '立案调查': [
                {'title': '广安爱众：董事李常兵被立案调查并实施留置', 'url': 'http://finance.eastmoney.com/a/202604113702012257.html'},
                {'title': '300152，相关股东被证监会立案调查！', 'url': 'http://finance.eastmoney.com/a/202604103701681937.html'}
            ],
            '债务违约': [
                {'title': '融创房地产集团：子公司新增一笔 1.23 亿元债务违约', 'url': 'http://finance.eastmoney.com/a/20260326386020384.html'}
            ]
        }
        output_file = save_search_results(test_data)
        print(f"✅ 测试数据已保存到：{output_file}")
    
    else:
        # 默认输出 URL 列表
        urls = get_search_urls()
        print("# 港股风险新闻监控 - 20 个关键词搜索 URL\n")
        for keyword, url in urls.items():
            print(f"- {keyword}: {url}")


if __name__ == '__main__':
    main()
