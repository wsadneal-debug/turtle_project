#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从东方财富获取全部A股股票列表
"""

import json
import subprocess
import sys
from pathlib import Path

OUTPUT_FILE = Path('/home/yxy/.openclaw/workspace/hk_risk_news/data/all_a_stocks.json')

def fetch_a_stocks():
    """使用curl获取A股列表"""
    
    # 东方财富A股列表API（全部市场）
    url = 'https://push2.eastmoney.com/api/qt/clist/get'
    
    # 分批获取（每次500只）
    all_stocks = []
    
    for page in range(1, 15):  # 15页 × 500只 = 7500只（覆盖全部A股）
        params = {
            'pn': page,
            'pz': 500,
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # 深市+沪市
            'fields': 'f12,f14,f116'  # 代码、名称、行业
        }
        
        param_str = '&'.join([f'{k}={v}' for k, v in params.items()])
        full_url = f'{url}?{param_str}'
        
        print(f"获取第 {page} 页...")
        
        # 使用curl（绕过Python SSL问题）
        result = subprocess.run(
            ['curl', '-s', '--max-time', '30', full_url],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or not result.stdout:
            print(f"  第 {page} 页失败: {result.stderr}")
            continue
        
        try:
            data = json.loads(result.stdout)
            diff = data.get('data', {}).get('diff', [])
            
            if not diff:
                print(f"  第 {page} 页无数据，停止")
                break
            
            for item in diff:
                code = item.get('f12', '')
                name = item.get('f14', '')
                
                if code and name and len(code) == 6:
                    # 判断市场
                    if code.startswith(('00', '30')):
                        market = 'SZ'
                    elif code.startswith('6'):
                        market = 'SH'
                    else:
                        continue
                    
                    all_stocks.append({
                        'code': f'{code}.{market}',
                        'name': name,
                        'industry': ''
                    })
            
            print(f"  ✓ 已获取 {len(all_stocks)} 只")
            
        except json.JSONDecodeError as e:
            print(f"  第 {page} 页JSON解析失败: {e}")
            continue
    
    return all_stocks

def main():
    print("=" * 60)
    print("获取全部A股股票列表")
    print("=" * 60)
    
    stocks = fetch_a_stocks()
    
    if stocks:
        # 保存
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(stocks, f, ensure_ascii=False)
        
        print(f"\n✅ 共获取 {len(stocks)} 只A股")
        print(f"✅ 已保存到: {OUTPUT_FILE}")
        
        # 显示前20只
        print("\n前20只股票:")
        for s in stocks[:20]:
            print(f"  {s['code']} {s['name']}")
    else:
        print("\n❌ 获取失败")
        sys.exit(1)

if __name__ == "__main__":
    main()