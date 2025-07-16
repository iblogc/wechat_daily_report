#!/usr/bin/env python3
"""
测试时间范围功能
"""
import sys
import os
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.wechat_client import WeChatAPIClient

def test_time_range():
    """测试时间范围计算"""
    client = WeChatAPIClient()
    
    # 测试不同的报告日期
    test_dates = [
        "2025-07-15",
        "2025-07-16", 
        "2025-07-14"
    ]
    
    for report_date in test_dates:
        print(f"\n📅 测试报告日期: {report_date}")
        
        # 解析报告日期
        report_dt = datetime.strptime(report_date, '%Y-%m-%d')
        
        # 计算时间范围：当天5点到第二天5点
        start_time = report_dt.replace(hour=5, minute=0, second=0, microsecond=0)
        end_time = (report_dt + timedelta(days=1)).replace(hour=5, minute=0, second=0, microsecond=0)
        
        print(f"⏰ 时间范围: {start_time} 到 {end_time}")
        print(f"📊 覆盖时间: {start_time.strftime('%Y-%m-%d %H:%M')} ~ {end_time.strftime('%Y-%m-%d %H:%M')}")
        
        # 格式化时间范围
        start_date = start_time.strftime('%Y-%m-%d %H:%M')
        end_date = end_time.strftime('%Y-%m-%d %H:%M')
        
        if start_date == end_date:
            time_range = start_date
            print(f"🔍 API时间范围参数: {time_range}")
        else:
            time_range = f"{start_date}~{end_date}"
            print(f"🔍 API时间范围参数: {time_range}")

if __name__ == "__main__":
    test_time_range()