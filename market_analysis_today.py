#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今日A股大盘分析
使用AKShare获取最新数据进行分析
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def get_market_overview():
    """获取大盘概览数据"""
    try:
        print("正在获取主要指数数据...")
        
        # 使用新浪数据源获取指数数据
        sh_real = ak.stock_zh_index_spot_sina()
        
        if not sh_real.empty:
            # 筛选主要指数
            sh_index = sh_real[sh_real['名称'] == '上证指数']
            sz_index = sh_real[sh_real['名称'] == '深证成指']  
            cy_index = sh_real[sh_real['名称'] == '创业板指']
            
            market_data = {
                "上证指数": sh_index,
                "深证成指": sz_index,
                "创业板指": cy_index
            }
            return market_data
        else:
            return None
            
    except Exception as e:
        print(f"获取大盘数据失败: {e}")
        return None

def get_market_trading_info():
    """获取市场成交信息"""
    try:
        print("正在获取市场成交数据...")
        
        # 获取A股实时数据
        all_stocks = ak.stock_zh_a_spot_em()
        
        if all_stocks.empty:
            return None
            
        # 计算总成交额（单位：亿元）
        total_volume = all_stocks['成交额'].sum() / 1e8 if '成交额' in all_stocks.columns else 0
        
        # 获取涨跌家数统计
        up_count = len(all_stocks[all_stocks['涨跌幅'] > 0]) if '涨跌幅' in all_stocks.columns else 0
        down_count = len(all_stocks[all_stocks['涨跌幅'] < 0]) if '涨跌幅' in all_stocks.columns else 0
        flat_count = len(all_stocks[all_stocks['涨跌幅'] == 0]) if '涨跌幅' in all_stocks.columns else 0
        
        # 计算涨停和跌停家数
        limit_up = len(all_stocks[all_stocks['涨跌幅'] >= 9.9]) if '涨跌幅' in all_stocks.columns else 0
        limit_down = len(all_stocks[all_stocks['涨跌幅'] <= -9.9]) if '涨跌幅' in all_stocks.columns else 0
        
        trading_info = {
            "总成交额(亿元)": round(total_volume, 2),
            "上涨家数": up_count,
            "下跌家数": down_count, 
            "平盘家数": flat_count,
            "涨停家数": limit_up,
            "跌停家数": limit_down,
            "涨跌比": round(up_count / down_count, 2) if down_count > 0 else float('inf')
        }
        
        return trading_info
        
    except Exception as e:
        print(f"获取成交数据失败: {e}")
        return None

def get_hot_sectors():
    """获取热点板块数据"""
    try:
        print("正在获取热点板块数据...")
        
        # 获取行业板块数据
        sector_df = ak.stock_board_industry_name_em()
        
        if not sector_df.empty and '涨跌幅' in sector_df.columns:
            # 按涨跌幅排序，取前10名
            top_sectors = sector_df.nlargest(10, '涨跌幅')[['板块名称', '涨跌幅', '总市值', '换手率']]
            return top_sectors
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"获取板块数据失败: {e}")
        return None

def get_concept_sectors():
    """获取概念板块数据"""
    try:
        print("正在获取概念板块数据...")
        
        # 获取概念板块数据
        concept_df = ak.stock_board_concept_name_em()
        
        if not concept_df.empty and '涨跌幅' in concept_df.columns:
            # 按涨跌幅排序，取前10名
            top_concepts = concept_df.nlargest(10, '涨跌幅')[['板块名称', '涨跌幅', '总市值', '换手率']]
            return top_concepts
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"获取概念板块数据失败: {e}")
        return None

def analyze_market():
    """执行完整的大盘分析"""
    print("=== 今日A股大盘分析 ===")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 获取大盘数据
    market_data = get_market_overview()
    trading_info = get_market_trading_info()
    hot_sectors = get_hot_sectors()
    concept_sectors = get_concept_sectors()
    
    # 分析主要指数
    if market_data:
        print("\n【主要指数表现】")
        for name, data in market_data.items():
            if data is not None and not data.empty:
                index_data = data.iloc[0]
                current_price = index_data.get('最新价', index_data.get('当前价', 'N/A'))
                change_pct = index_data.get('涨跌幅', 0)
                change_amount = index_data.get('涨跌额', 0)
                volume = index_data.get('成交量', index_data.get('成交额', 'N/A'))
                
                print(f"{name}:")
                print(f"  当前点位: {current_price}")
                print(f"  涨跌幅: {change_pct}%")
                print(f"  涨跌额: {change_amount}")
                print(f"  成交量: {volume}")
                print()
    
    # 分析成交情况
    if trading_info:
        print("【市场成交概况】")
        for key, value in trading_info.items():
            print(f"{key}: {value}")
        print()
    
    # 分析热点行业板块
    if hot_sectors is not None and not hot_sectors.empty:
        print("【热点行业板块TOP10】")
        print(hot_sectors.to_string(index=False))
        print()
    
    # 分析热点概念板块
    if concept_sectors is not None and not concept_sectors.empty:
        print("【热点概念板块TOP10】")
        print(concept_sectors.to_string(index=False))
        print()
    
    # 市场分析总结
    print("【市场分析总结】")
    if trading_info:
        total_turnover = trading_info.get("总成交额(亿元)", 0)
        up_ratio = trading_info.get("涨跌比", 0)
        limit_up = trading_info.get("涨停家数", 0)
        limit_down = trading_info.get("跌停家数", 0)
        
        print(f"今日两市成交额约{total_turnover}亿元，", end="")
        if up_ratio > 1:
            print("市场呈现普涨格局，", end="")
        elif up_ratio < 1:
            print("市场跌多涨少，", end="")
        else:
            print("市场涨跌互现，", end="")
        print(f"涨停{limit_up}家，跌停{limit_down}家。")
    
    # 热点分析
    if hot_sectors is not None and not hot_sectors.empty:
        top_sector = hot_sectors.iloc[0]
        print(f"行业板块中，{top_sector['板块名称']}领涨，涨幅{top_sector['涨跌幅']:.2f}%。")
    
    if concept_sectors is not None and not concept_sectors.empty:
        top_concept = concept_sectors.iloc[0]
        print(f"概念板块中，{top_concept['板块名称']}表现活跃，涨幅{top_concept['涨跌幅']:.2f}%。")
    
    # 生成分析报告
    report = {
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "主要指数": {},
        "成交概况": trading_info,
        "热点行业板块": hot_sectors.to_dict('records') if hot_sectors is not None else [],
        "热点概念板块": concept_sectors.to_dict('records') if concept_sectors is not None else []
    }
    
    # 保存指数数据到报告
    if market_data:
        for name, data in market_data.items():
            if data is not None and not data.empty:
                report["主要指数"][name] = data.iloc[0].to_dict()
    
    return report

if __name__ == "__main__":
    try:
        report = analyze_market()
        
        # 保存报告到文件
        report_file = f"report/market_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n分析报告已保存至: {report_file}")
        
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()