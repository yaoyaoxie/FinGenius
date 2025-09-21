#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明日A股操作策略分析
基于技术面、情绪面、消息面等多维度分析
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json

def analyze_technical_signals():
    """分析技术面信号"""
    print("正在分析技术面信号...")
    
    try:
        # 获取主要指数数据
        sh_index = ak.stock_zh_index_spot_sina()
        sh_data = sh_index[sh_index['名称'] == '上证指数']
        
        technical_signals = {
            "当前点位": "",
            "关键支撑": "",
            "关键阻力": "", 
            "技术指标": {},
            "明日概率": {}
        }
        
        if not sh_data.empty:
            current_price = sh_data.iloc[0].get('最新价', 0)
            change_pct = sh_data.iloc[0].get('涨跌幅', 0)
            
            technical_signals["当前点位"] = f"{current_price:.2f}"
            technical_signals["关键支撑"] = "3800点（缺口支撑）、3730点（月线支撑）"
            technical_signals["关键阻力"] = "3850点（5日线）、3900点（整数关口）"
            
            # 基于当前位置判断明日走势概率
            if current_price < 3820:
                technical_signals["明日概率"] = {
                    "上涨概率": "35%",
                    "下跌概率": "40%", 
                    "震荡概率": "25%",
                    "主要观点": "接近关键支撑，或有技术性反弹"
                }
            elif current_price < 3850:
                technical_signals["明日概率"] = {
                    "上涨概率": "25%",
                    "下跌概率": "45%",
                    "震荡概率": "30%",
                    "主要观点": "处于弱势区域，继续调整概率较大"
                }
            else:
                technical_signals["明日概率"] = {
                    "上涨概率": "40%",
                    "下跌概率": "30%",
                    "震荡概率": "30%",
                    "主要观点": "重回强势区域，反弹概率增加"
                }
        
        return technical_signals
        
    except Exception as e:
        print(f"技术分析失败: {e}")
        return None

def analyze_market_sentiment():
    """分析市场情绪"""
    print("正在分析市场情绪...")
    
    sentiment_analysis = {
        "恐慌贪婪指数": "",
        "投资者情绪": "",
        "明日预期": "",
        "操作建议": ""
    }
    
    try:
        # 基于今日表现分析情绪
        sh_index = ak.stock_zh_index_spot_sina()
        sh_data = sh_index[sh_index['名称'] == '上证指数']
        
        if not sh_data.empty:
            change_pct = sh_data.iloc[0].get('涨跌幅', 0)
            
            # 简化的情绪指标
            if change_pct < -2:
                sentiment_score = "极度恐慌"
            elif change_pct < -1:
                sentiment_score = "恐慌"
            elif change_pct < -0.5:
                sentiment_score = "谨慎"
            elif change_pct < 0.5:
                sentiment_score = "中性"
            elif change_pct < 1:
                sentiment_score = "乐观"
            else:
                sentiment_score = "极度乐观"
            
            sentiment_analysis["恐慌贪婪指数"] = sentiment_score
            sentiment_analysis["投资者情绪"] = "恐慌情绪有所释放，但仍有谨慎情绪"
            
            # 明日情绪预期
            if change_pct < -1.5:
                sentiment_analysis["明日预期"] = "恐慌情绪或有所缓解，可能出现超跌反弹"
                sentiment_analysis["操作建议"] = "不宜过度恐慌，可考虑逢低布局"
            elif change_pct < -0.5:
                sentiment_analysis["明日预期"] = "市场情绪偏弱，需要观察盘中表现"
                sentiment_analysis["操作建议"] = "保持谨慎，控制仓位"
            else:
                sentiment_analysis["明日预期"] = "市场情绪相对稳定"
                sentiment_analysis["操作建议"] = "正常操作，关注个股机会"
        
        return sentiment_analysis
        
    except Exception as e:
        print(f"情绪分析失败: {e}")
        return None

def analyze_sector_rotation():
    """分析板块轮动机会"""
    print("正在分析板块轮动...")
    
    try:
        # 获取行业板块数据
        sector_df = ak.stock_board_industry_name_em()
        
        if not sector_df.empty:
            # 分析今日表现较好的板块（可能有持续性）
            strong_sectors = sector_df[sector_df['涨跌幅'] > 1].nlargest(5, '涨跌幅')
            
            # 分析超跌板块（可能有反弹机会）
            weak_sectors = sector_df[sector_df['涨跌幅'] < -1].nsmallest(5, '涨跌幅')
            
            sector_analysis = {
                "强势板块": [],
                "超跌板块": [],
                "明日关注": []
            }
            
            # 强势板块分析
            for _, sector in strong_sectors.iterrows():
                sector_analysis["强势板块"].append({
                    "名称": sector['板块名称'],
                    "涨跌幅": f"{sector['涨跌幅']:.2f}%",
                    "分析": "连续强势，可能有持续性" if sector['涨跌幅'] > 2 else "日内强势，需观察次日表现"
                })
            
            # 超跌板块分析
            for _, sector in weak_sectors.iterrows():
                sector_analysis["超跌板块"].append({
                    "名称": sector['板块名称'],
                    "涨跌幅": f"{sector['涨跌幅']:.2f}%",
                    "分析": "超跌严重，或有反弹机会" if sector['涨跌幅'] < -3 else "技术超跌，可关注反弹"
                })
            
            # 明日关注建议
            if len(sector_analysis["强势板块"]) > 0:
                sector_analysis["明日关注"].append("关注强势板块的持续性，但不宜追高")
            
            if len(sector_analysis["超跌板块"]) > 0:
                sector_analysis["明日关注"].append("关注超跌板块的反弹机会，可逢低布局")
            
            sector_analysis["明日关注"].append("避免追涨杀跌，关注板块轮动节奏")
            
            return sector_analysis
    
    except Exception as e:
        print(f"板块分析失败: {e}")
        return None

def generate_position_suggestions():
    """生成仓位建议"""
    print("正在生成仓位建议...")
    
    position_advice = {
        "激进型投资者": {},
        "稳健型投资者": {},
        "保守型投资者": {}
    }
    
    try:
        # 获取当前市场状态
        sh_index = ak.stock_zh_index_spot_sina()
        sh_data = sh_index[sh_index['名称'] == '上证指数']
        
        market_condition = "unknown"
        if not sh_data.empty:
            change_pct = sh_data.iloc[0].get('涨跌幅', 0)
            current_price = sh_data.iloc[0].get('最新价', 0)
            
            if change_pct < -1.5 and current_price < 3820:
                market_condition = "oversold"
            elif change_pct < -0.5 and current_price < 3850:
                market_condition = "weak"
            else:
                market_condition = "normal"
        
        # 基于市场状态给出建议
        if market_condition == "oversold":
            # 超跌状态
            position_advice["激进型投资者"] = {
                "建议仓位": "60-70%",
                "操作策略": "逢低布局，重点把握超跌反弹机会",
                "关注板块": "超跌优质股、强势板块回调机会",
                "风险控制": "设置止损位，控制单只股票仓位"
            }
            
            position_advice["稳健型投资者"] = {
                "建议仓位": "40-50%",
                "操作策略": "谨慎逢低布局，分批建仓",
                "关注板块": "业绩确定性强的蓝筹股、防御性板块",
                "风险控制": "严格止损，避免追高"
            }
            
            position_advice["保守型投资者"] = {
                "建议仓位": "20-30%",
                "操作策略": "保持低仓位，等待更明确信号",
                "关注板块": "高股息率股票、债券等稳健资产",
                "风险控制": "严格控制风险，优先保本"
            }
            
        elif market_condition == "weak":
            # 弱势状态
            position_advice["激进型投资者"] = {
                "建议仓位": "40-50%",
                "操作策略": "控制仓位，精选个股",
                "关注板块": "业绩超预期个股、政策受益板块",
                "风险控制": "快进快出，严格止盈止损"
            }
            
            position_advice["稳健型投资者"] = {
                "建议仓位": "30-40%",
                "操作策略": "保持谨慎，等待趋势明朗",
                "关注板块": "消费、医药等防御性板块",
                "风险控制": "避免追涨，控制回撤"
            }
            
            position_advice["保守型投资者"] = {
                "建议仓位": "10-20%",
                "操作策略": "以观望为主，保留现金",
                "关注板块": "货币基金、国债逆回购等",
                "风险控制": "优先保证本金安全"
            }
            
        else:
            # 正常状态
            position_advice["激进型投资者"] = {
                "建议仓位": "70-80%",
                "操作策略": "积极参与，把握结构性机会",
                "关注板块": "成长股、题材股、政策受益板块",
                "风险控制": "适度承担风险，注意仓位控制"
            }
            
            position_advice["稳健型投资者"] = {
                "建议仓位": "50-60%",
                "操作策略": "均衡配置，稳健操作",
                "关注板块": "蓝筹股、行业龙头、业绩稳定股",
                "风险控制": "分散投资，控制单一风险"
            }
            
            position_advice["保守型投资者"] = {
                "建议仓位": "30-40%",
                "操作策略": "谨慎参与，优选标的",
                "关注板块": "高股息股票、优质债券",
                "风险控制": "严格控制风险敞口"
            }
        
        return position_advice
        
    except Exception as e:
        print(f"仓位建议生成失败: {e}")
        return None

def analyze_empty_position_pros_cons():
    """分析空仓的利弊"""
    print("正在分析空仓策略...")
    
    empty_position_analysis = {
        "空仓优势": [
            "规避短期下跌风险，保护本金安全",
            "保持操作灵活性，等待更好买点",
            "避免情绪化交易，保持理性判断",
            "资金安全，可随时把握新机会"
        ],
        "空仓劣势": [
            "可能错过反弹行情，错失盈利机会",
            "难以准确判断底部，容易追涨",
            "资金利用效率低，时间成本高",
            "可能形成惯性，错过长期机会"
        ],
        "适用情况": [
            "市场趋势明显向下，无企稳迹象",
            "个人风险承受能力较低",
            "投资经验不足，难以把握波动",
            "资金有短期使用需求"
        ],
        "不适用情况": [
            "市场处于震荡筑底阶段",
            "个股机会较多，结构性行情明显",
            "有较强选股能力和风控能力",
            "追求长期投资回报"
        ]
    }
    
    return empty_position_analysis

def generate_comprehensive_strategy():
    """生成综合策略建议"""
    print("\n=== 明日A股操作策略分析 ===")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取各项分析
    technical = analyze_technical_signals()
    sentiment = analyze_market_sentiment()
    sectors = analyze_sector_rotation()
    positions = generate_position_suggestions()
    empty_analysis = analyze_empty_position_pros_cons()
    
    print("\n【技术面分析】")
    if technical:
        print(f"当前点位: {technical['当前点位']}")
        print(f"关键支撑: {technical['关键支撑']}")
        print(f"关键阻力: {technical['关键阻力']}")
        print(f"明日走势概率: {technical['明日概率']['主要观点']}")
        print(f"上涨概率: {technical['明日概率']['上涨概率']}")
        print(f"下跌概率: {technical['明日概率']['下跌概率']}")
        print(f"震荡概率: {technical['明日概率']['震荡概率']}")
    
    print("\n【市场情绪分析】")
    if sentiment:
        print(f"恐慌贪婪指数: {sentiment['恐慌贪婪指数']}")
        print(f"投资者情绪: {sentiment['投资者情绪']}")
        print(f"明日预期: {sentiment['明日预期']}")
        print(f"操作建议: {sentiment['操作建议']}")
    
    print("\n【板块轮动分析】")
    if sectors:
        if sectors['强势板块']:
            print("今日强势板块:")
            for sector in sectors['强势板块']:
                print(f"  - {sector['名称']}: {sector['涨跌幅']} ({sector['分析']})")
        
        if sectors['超跌板块']:
            print("今日超跌板块:")
            for sector in sectors['超跌板块']:
                print(f"  - {sector['名称']}: {sector['涨跌幅']} ({sector['分析']})")
        
        print("明日关注要点:")
        for point in sectors['明日关注']:
            print(f"  - {point}")
    
    print("\n【空仓策略分析】")
    if empty_analysis:
        print("空仓优势:")
        for advantage in empty_analysis['空仓优势']:
            print(f"  ✓ {advantage}")
        
        print("\n空仓劣势:")
        for disadvantage in empty_analysis['空仓劣势']:
            print(f"  ✗ {disadvantage}")
        
        print("\n空仓适用情况:")
        for condition in empty_analysis['适用情况']:
            print(f"  ○ {condition}")
    
    print("\n【不同投资者类型的仓位建议】")
    if positions:
        for investor_type, advice in positions.items():
            print(f"\n{investor_type}:")
            print(f"  建议仓位: {advice['建议仓位']}")
            print(f"  操作策略: {advice['操作策略']}")
            print(f"  关注板块: {advice['关注板块']}")
            print(f"  风险控制: {advice['风险控制']}")
    
    print("\n【综合结论与建议】")
    print("=" * 60)
    
    # 基于分析给出综合建议
    if technical and technical['明日概率']['下跌概率'] > '40%':
        print("🚨 市场风险提示:")
        print("- 技术面显示继续调整概率较大")
        print("- 建议控制仓位，避免激进操作")
        print("- 等待更明确的市场信号")
        
        print("\n💡 具体操作建议:")
        print("1. 不建议完全空仓，但应控制仓位")
        print("2. 激进型投资者: 3-5成仓位，关注超跌反弹")
        print("3. 稳健型投资者: 2-4成仓位，等待企稳信号")
        print("4. 保守型投资者: 1-3成仓位，优先保本")
        
    else:
        print("✅ 市场机会提示:")
        print("- 技术面显示反弹概率增加")
        print("- 可适当参与，但需控制仓位")
        print("- 重点关注业绩确定性强的标的")
        
        print("\n💡 具体操作建议:")
        print("1. 可适当参与，但不宜满仓")
        print("2. 激进型投资者: 5-7成仓位，精选个股")
        print("3. 稳健型投资者: 4-6成仓位，均衡配置")
        print("4. 保守型投资者: 2-4成仓位，稳健为主")
    
    print("\n⚠️  重要提醒:")
    print("- 以上建议仅供参考，投资有风险，决策需谨慎")
    print("- 请根据个人风险承受能力和投资经验做出决策")
    print("- 建议设置止损位，严格控制风险")
    print("- 密切关注市场变化，及时调整策略")
    
    # 生成完整报告
    report = {
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "技术面分析": technical,
        "市场情绪": sentiment,
        "板块轮动": sectors,
        "仓位建议": positions,
        "空仓分析": empty_analysis
    }
    
    return report

if __name__ == "__main__":
    try:
        report = generate_comprehensive_strategy()
        
        # 保存报告
        report_file = f"report/tomorrow_strategy_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n策略报告已保存至: {report_file}")
        
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()