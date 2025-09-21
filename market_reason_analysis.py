#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析今日A股整体下跌的原因
结合市场数据、新闻、外围市场等多维度分析
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import requests
from bs4 import BeautifulSoup

def get_market_news():
    """获取相关市场新闻"""
    print("正在搜索相关市场新闻...")
    
    news_items = []
    try:
        # 获取财经头条新闻
        news_df = ak.news_cctv(date=datetime.now().strftime("%Y%m%d"))
        if not news_df.empty:
            # 筛选与市场相关的新闻
            market_keywords = ['股市', 'A股', '下跌', '调整', '外围', '美股', '港股', '政策', '监管', '流动性', '经济']
            for _, news in news_df.head(20).iterrows():
                title = news.get('title', '')
                content = news.get('content', '')
                
                # 检查是否包含相关关键词
                if any(keyword in title or keyword in content for keyword in market_keywords):
                    news_items.append({
                        'title': title,
                        'content': content[:200] + '...' if len(content) > 200 else content,
                        'time': news.get('time', '')
                    })
    except Exception as e:
        print(f"获取新闻失败: {e}")
    
    return news_items

def get_us_market_performance():
    """获取美股表现"""
    print("正在获取美股数据...")
    
    try:
        # 获取美股主要指数
        sp500 = ak.stock_us_spot_daily(symbol=".INX")
        nasdaq = ak.stock_us_spot_daily(symbol=".IXIC")
        dow_jones = ak.stock_us_spot_daily(symbol=".DJI")
        
        us_market = {
            "标普500": {
                "最新价": sp500['close'].iloc[-1] if not sp500.empty else "N/A",
                "涨跌幅": ((sp500['close'].iloc[-1] - sp500['close'].iloc[-2]) / sp500['close'].iloc[-2] * 100) if len(sp500) >= 2 else 0
            },
            "纳斯达克": {
                "最新价": nasdaq['close'].iloc[-1] if not nasdaq.empty else "N/A",
                "涨跌幅": ((nasdaq['close'].iloc[-1] - nasdaq['close'].iloc[-2]) / nasdaq['close'].iloc[-2] * 100) if len(nasdaq) >= 2 else 0
            },
            "道琼斯": {
                "最新价": dow_jones['close'].iloc[-1] if not dow_jones.empty else "N/A",
                "涨跌幅": ((dow_jones['close'].iloc[-1] - dow_jones['close'].iloc[-2]) / dow_jones['close'].iloc[-2] * 100) if len(dow_jones) >= 2 else 0
            }
        }
        
        return us_market
        
    except Exception as e:
        print(f"获取美股数据失败: {e}")
        return None

def get_hk_market_performance():
    """获取港股表现"""
    print("正在获取港股数据...")
    
    try:
        # 获取恒生指数
        hk_index = ak.stock_hk_spot()
        if not hk_index.empty:
            hs_index = hk_index[hk_index['名称'] == '恒生指数']
            if not hs_index.empty:
                return {
                    "恒生指数": {
                        "最新价": hs_index.iloc[0].get('最新价', 'N/A'),
                        "涨跌幅": hs_index.iloc[0].get('涨跌幅', 0)
                    }
                }
        return None
        
    except Exception as e:
        print(f"获取港股数据失败: {e}")
        return None

def analyze_sector_rotation():
    """分析板块轮动情况"""
    print("正在分析板块轮动...")
    
    try:
        # 获取行业板块数据
        sector_df = ak.stock_board_industry_name_em()
        
        if not sector_df.empty:
            # 分析涨跌分布
            up_sectors = len(sector_df[sector_df['涨跌幅'] > 0])
            down_sectors = len(sector_df[sector_df['涨跌幅'] < 0])
            flat_sectors = len(sector_df[sector_df['涨跌幅'] == 0])
            
            # 获取表现最好和最差的板块
            best_sector = sector_df.loc[sector_df['涨跌幅'].idxmax()]
            worst_sector = sector_df.loc[sector_df['涨跌幅'].idxmin()]
            
            sector_analysis = {
                "上涨板块数": up_sectors,
                "下跌板块数": down_sectors,
                "平盘板块数": flat_sectors,
                "最好板块": {
                    "名称": best_sector['板块名称'],
                    "涨跌幅": best_sector['涨跌幅']
                },
                "最差板块": {
                    "名称": worst_sector['板块名称'],
                    "涨跌幅": worst_sector['涨跌幅']
                }
            }
            
            return sector_analysis
    except Exception as e:
        print(f"板块分析失败: {e}")
        return None

def get_market_sentiment():
    """分析市场情绪"""
    print("正在分析市场情绪...")
    
    sentiment_analysis = {
        "恐慌因素": [],
        "乐观因素": [],
        "中性因素": []
    }
    
    # 基于今日市场表现分析情绪
    try:
        # 获取主要指数数据
        sh_index = ak.stock_zh_index_spot_sina()
        sh_data = sh_index[sh_index['名称'] == '上证指数']
        
        if not sh_data.empty:
            change_pct = sh_data.iloc[0].get('涨跌幅', 0)
            
            if change_pct < -1:
                sentiment_analysis["恐慌因素"].append(f"上证指数下跌{abs(change_pct):.2f}%，跌幅较大")
            elif change_pct > 1:
                sentiment_analysis["乐观因素"].append(f"上证指数上涨{change_pct:.2f}%，表现强势")
            else:
                sentiment_analysis["中性因素"].append(f"上证指数微幅波动{change_pct:.2f}%，表现平稳")
        
        # 分析板块表现
        sector_df = ak.stock_board_industry_name_em()
        if not sector_df.empty:
            down_sectors = len(sector_df[sector_df['涨跌幅'] < -1])
            up_sectors = len(sector_df[sector_df['涨跌幅'] > 1])
            
            if down_sectors > up_sectors * 2:
                sentiment_analysis["恐慌因素"].append(f"超三分之二板块下跌，市场普跌明显")
            elif up_sectors > down_sectors * 2:
                sentiment_analysis["乐观因素"].append(f"超三分之二板块上涨，市场普涨明显")
            else:
                sentiment_analysis["中性因素"].append(f"板块表现分化，结构性行情明显")
        
    except Exception as e:
        print(f"情绪分析失败: {e}")
    
    return sentiment_analysis

def analyze_fund_flow():
    """分析资金流向"""
    print("正在分析资金流向...")
    
    try:
        # 获取北向资金流向
        north_flow = ak.stock_hsgt_north_net_flow_in_em()
        
        fund_analysis = {
            "北向资金": {
                "今日流向": "数据获取失败",
                "近期趋势": "数据获取失败"
            },
            "大单资金": {
                "流入板块": [],
                "流出板块": []
            }
        }
        
        if not north_flow.empty:
            latest_flow = north_flow.iloc[-1]
            fund_analysis["北向资金"]["今日流向"] = f"{latest_flow.get('今日净流入', 'N/A')}亿元"
        
        return fund_analysis
        
    except Exception as e:
        print(f"资金流向分析失败: {e}")
        return None

def generate_reason_analysis():
    """生成综合原因分析"""
    print("\n=== 今日A股下跌原因综合分析 ===")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取各项数据
    us_market = get_us_market_performance()
    hk_market = get_hk_market_performance()
    sector_analysis = analyze_sector_rotation()
    sentiment = get_market_sentiment()
    fund_flow = analyze_fund_flow()
    news = get_market_news()
    
    print("\n【外围市场影响】")
    if us_market:
        for index, data in us_market.items():
            print(f"{index}: {data['涨跌幅']:.2f}%")
    
    if hk_market:
        for index, data in hk_market.items():
            print(f"{index}: {data['涨跌幅']:.2f}%")
    
    print("\n【板块表现分析】")
    if sector_analysis:
        print(f"板块涨跌分布：上涨{sector_analysis['上涨板块数']}个，下跌{sector_analysis['下跌板块数']}个")
        print(f"表现最好：{sector_analysis['最好板块']['名称']} ({sector_analysis['最好板块']['涨跌幅']:.2f}%)")
        print(f"表现最差：{sector_analysis['最差板块']['名称']} ({sector_analysis['最差板块']['涨跌幅']:.2f}%)")
    
    print("\n【市场情绪分析】")
    if sentiment:
        for category, factors in sentiment.items():
            if factors:
                print(f"{category}：")
                for factor in factors:
                    print(f"  - {factor}")
    
    print("\n【相关市场新闻】")
    if news:
        for i, item in enumerate(news[:5], 1):
            print(f"{i}. {item['title']}")
            if item['content']:
                print(f"   {item['content']}")
            print()
    
    # 生成综合分析结论
    print("\n【综合原因分析】")
    reasons = []
    
    # 外围市场影响
    if us_market:
        negative_us = sum(1 for data in us_market.values() if data['涨跌幅'] < -0.5)
        if negative_us > 0:
            reasons.append(f"外围市场普跌，美股主要指数下跌，影响A股投资者情绪")
    
    # 技术面因素
    reasons.append("技术面调整需求，前期上涨后的正常回调")
    
    # 板块轮动
    if sector_analysis and sector_analysis['下跌板块数'] > sector_analysis['上涨板块数'] * 1.5:
        reasons.append("板块普跌，市场缺乏明显热点，资金观望情绪浓厚")
    
    # 情绪因素
    if sentiment and sentiment['恐慌因素']:
        reasons.append("市场恐慌情绪升温，投资者风险偏好下降")
    
    print("主要下跌原因：")
    for i, reason in enumerate(reasons, 1):
        print(f"{i}. {reason}")
    
    # 生成完整报告
    report = {
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "外围市场": us_market,
        "港股表现": hk_market,
        "板块分析": sector_analysis,
        "市场情绪": sentiment,
        "资金流向": fund_flow,
        "相关新闻": news,
        "下跌原因": reasons
    }
    
    return report

if __name__ == "__main__":
    try:
        report = generate_reason_analysis()
        
        # 保存报告
        report_file = f"report/market_reason_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n分析报告已保存至: {report_file}")
        
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()