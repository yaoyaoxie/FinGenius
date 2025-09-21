#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雅化集团（002497）综合分析
包括基本面、技术面、行业分析等
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def get_basic_info():
    """获取雅化集团基本信息"""
    print("正在获取雅化集团基本信息...")
    
    try:
        # 获取股票基本信息
        stock_info = ak.stock_individual_info_em(symbol="002497")
        
        # 获取实时股价数据
        current_data = ak.stock_zh_a_spot_em()
        yh_data = current_data[current_data['代码'] == '002497']
        
        basic_info = {
            "股票代码": "002497",
            "股票名称": "雅化集团",
            "当前价格": "",
            "涨跌幅": "",
            "成交量": "",
            "市值": "",
            "基本信息": {}
        }
        
        if not yh_data.empty:
            basic_info["当前价格"] = f"{yh_data.iloc[0].get('最新价', 'N/A'):.2f}" if pd.notna(yh_data.iloc[0].get('最新价')) else "N/A"
            basic_info["涨跌幅"] = f"{yh_data.iloc[0].get('涨跌幅', 0):.2f}%" if pd.notna(yh_data.iloc[0].get('涨跌幅')) else "0.00%"
            basic_info["成交量"] = yh_data.iloc[0].get('成交量', 'N/A')
            basic_info["市值"] = yh_data.iloc[0].get('总市值', 'N/A')
        
        if not stock_info.empty:
            # 提取关键信息
            info_dict = {}
            for _, row in stock_info.iterrows():
                info_dict[row.get('item', '')] = row.get('value', '')
            
            basic_info["基本信息"] = {
                "公司全称": info_dict.get('股票简称', '雅化集团'),
                "所属行业": info_dict.get('所属行业', '化工行业'),
                "成立日期": info_dict.get('成立日期', ''),
                "上市日期": info_dict.get('上市日期', ''),
                "法人代表": info_dict.get('法人代表', ''),
                "总经理": info_dict.get('总经理', ''),
                "董秘": info_dict.get('董秘', ''),
                "联系电话": info_dict.get('联系电话', ''),
                "传真": info_dict.get('传真', ''),
                "公司网址": info_dict.get('公司网址', ''),
                "电子邮箱": info_dict.get('电子邮箱', ''),
                "注册地址": info_dict.get('注册地址', ''),
                "办公地址": info_dict.get('办公地址', ''),
                "主营业务": info_dict.get('主营业务', '锂盐产品及民爆产品')
            }
        
        return basic_info
        
    except Exception as e:
        print(f"获取基本信息失败: {e}")
        return None

def get_financial_data():
    """获取财务数据"""
    print("正在获取财务数据...")
    
    try:
        # 获取主要财务指标
        financial_indicators = ak.stock_financial_abstract(symbol="002497")
        
        # 获取资产负债表
        balance_sheet = ak.stock_balance_sheet_by_report_em(symbol="002497")
        
        # 获取利润表
        income_statement = ak.stock_income_statement_by_report_em(symbol="002497")
        
        # 获取现金流量表
        cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol="002497")
        
        financial_data = {
            "主要指标": {},
            "盈利能力": {},
            "偿债能力": {},
            "运营能力": {},
            "成长能力": {},
            "现金流": {}
        }
        
        # 处理主要财务指标
        if not financial_indicators.empty:
            latest_data = financial_indicators.iloc[0] if len(financial_indicators) > 0 else {}
            financial_data["主要指标"] = {
                "营业收入": latest_data.get('营业收入', 'N/A'),
                "净利润": latest_data.get('净利润', 'N/A'),
                "总资产": latest_data.get('总资产', 'N/A'),
                "净资产": latest_data.get('净资产', 'N/A'),
                "每股收益": latest_data.get('每股收益', 'N/A'),
                "每股净资产": latest_data.get('每股净资产', 'N/A'),
                "毛利率": latest_data.get('毛利率', 'N/A'),
                "净利率": latest_data.get('净利率', 'N/A'),
                "ROE": latest_data.get('净资产收益率', 'N/A'),
                "资产负债率": latest_data.get('资产负债率', 'N/A')
            }
        
        return financial_data
        
    except Exception as e:
        print(f"获取财务数据失败: {e}")
        return None

def get_historical_performance():
    """获取历史表现"""
    print("正在获取历史表现数据...")
    
    try:
        # 获取历史股价数据
        hist_data = ak.stock_zh_a_hist(symbol="002497", period="daily", start_date=(datetime.now() - timedelta(days=365)).strftime("%Y%m%d"), end_date=datetime.now().strftime("%Y%m%d"))
        
        performance_data = {
            "近1年涨跌幅": "N/A",
            "近6月涨跌幅": "N/A", 
            "近3月涨跌幅": "N/A",
            "近1月涨跌幅": "N/A",
            "今年涨跌幅": "N/A",
            "波动率": "N/A",
            "最高价": "N/A",
            "最低价": "N/A",
            "当前相对位置": "N/A"
        }
        
        if not hist_data.empty and len(hist_data) > 0:
            # 计算不同时间段的涨跌幅
            current_price = hist_data['收盘'].iloc[-1]
            
            # 近1年
            if len(hist_data) >= 250:
                year_ago_price = hist_data['收盘'].iloc[-250]
                performance_data["近1年涨跌幅"] = f"{((current_price - year_ago_price) / year_ago_price * 100):.2f}%"
            
            # 近6月
            if len(hist_data) >= 125:
                half_year_ago_price = hist_data['收盘'].iloc[-125]
                performance_data["近6月涨跌幅"] = f"{((current_price - half_year_ago_price) / half_year_ago_price * 100):.2f}%"
            
            # 近3月
            if len(hist_data) >= 60:
                quarter_ago_price = hist_data['收盘'].iloc[-60]
                performance_data["近3月涨跌幅"] = f"{((current_price - quarter_ago_price) / quarter_ago_price * 100):.2f}%"
            
            # 近1月
            if len(hist_data) >= 20:
                month_ago_price = hist_data['收盘'].iloc[-20]
                performance_data["近1月涨跌幅"] = f"{((current_price - month_ago_price) / month_ago_price * 100):.2f}%"
            
            # 计算波动率（近60日）
            if len(hist_data) >= 60:
                recent_data = hist_data.tail(60)
                daily_returns = recent_data['收盘'].pct_change().dropna()
                volatility = daily_returns.std() * np.sqrt(252) * 100  # 年化波动率
                performance_data["波动率"] = f"{volatility:.2f}%"
            
            # 最高价和最低价
            performance_data["最高价"] = f"{hist_data['最高'].max():.2f}"
            performance_data["最低价"] = f"{hist_data['最低'].min():.2f}"
            
            # 当前相对位置
            price_range = hist_data['最高'].max() - hist_data['最低'].min()
            current_position = (current_price - hist_data['最低'].min()) / price_range * 100
            performance_data["当前相对位置"] = f"{current_position:.1f}%"
        
        return performance_data
        
    except Exception as e:
        print(f"获取历史表现失败: {e}")
        return None

def get_technical_analysis():
    """技术分析"""
    print("正在进行技术分析...")
    
    try:
        # 获取近期数据
        recent_data = ak.stock_zh_a_hist(symbol="002497", period="daily", start_date=(datetime.now() - timedelta(days=60)).strftime("%Y%m%d"), end_date=datetime.now().strftime("%Y%m%d"))
        
        technical_data = {
            "当前趋势": "",
            "关键支撑位": [],
            "关键阻力位": [],
            "技术指标": {},
            "短期展望": "",
            "操作建议": ""
        }
        
        if not recent_data.empty and len(recent_data) >= 20:
            # 获取最新数据
            latest_data = recent_data.iloc[-1]
            current_price = latest_data['收盘']
            
            # 计算移动平均线
            recent_data['MA5'] = recent_data['收盘'].rolling(window=5).mean()
            recent_data['MA10'] = recent_data['收盘'].rolling(window=10).mean()
            recent_data['MA20'] = recent_data['收盘'].rolling(window=20).mean()
            
            # 判断趋势
            ma5 = recent_data['MA5'].iloc[-1]
            ma10 = recent_data['MA10'].iloc[-1]
            ma20 = recent_data['MA20'].iloc[-1]
            
            if current_price > ma5 > ma10 > ma20:
                technical_data["当前趋势"] = "强势上升趋势"
            elif current_price > ma5 > ma10:
                technical_data["当前趋势"] = "温和上升趋势"
            elif current_price < ma5 < ma10 < ma20:
                technical_data["当前趋势"] = "明显下降趋势"
            elif current_price < ma5 < ma10:
                technical_data["当前趋势"] = "弱势下降趋势"
            else:
                technical_data["当前趋势"] = "震荡整理趋势"
            
            # 计算关键支撑位和阻力位
            recent_high = recent_data['最高'].tail(10).max()
            recent_low = recent_data['最低'].tail(10).min()
            
            technical_data["关键阻力位"] = [
                f"近期高点: {recent_high:.2f}",
                f"5日均线: {ma5:.2f}",
                f"10日均线: {ma10:.2f}"
            ]
            
            technical_data["关键支撑位"] = [
                f"近期低点: {recent_low:.2f}",
                f"20日均线: {ma20:.2f}",
                f"前期重要低点"
            ]
            
            # 技术指标
            technical_data["技术指标"] = {
                "5日均线": f"{ma5:.2f}",
                "10日均线": f"{ma10:.2f}",
                "20日均线": f"{ma20:.2f}",
                "当前价格相对5日均线": f"{((current_price - ma5) / ma5 * 100):.2f}%"
            }
            
            # 短期展望和操作建议
            if current_price > ma5:
                technical_data["短期展望"] = "短期偏乐观，关注能否突破近期高点"
                technical_data["操作建议"] = "可考虑适量参与，但需设置止损"
            else:
                technical_data["短期展望"] = "短期偏谨慎，关注支撑位有效性"
                technical_data["操作建议"] = "建议观望，等待更明确信号"
        
        return technical_data
        
    except Exception as e:
        print(f"技术分析失败: {e}")
        return None

def get_industry_analysis():
    """锂盐化工行业分析"""
    print("正在进行锂盐化工行业分析...")
    
    try:
        # 获取化工行业数据
        chemical_industry = ak.stock_board_industry_name_em()
        chemical_sector = chemical_industry[chemical_industry['板块名称'].str.contains('化工|化学', na=False)]
        
        # 获取锂电池相关概念板块
        concept_boards = ak.stock_board_concept_name_em()
        lithium_concepts = concept_boards[concept_boards['板块名称'].str.contains('锂|电池|新能源', na=False)]
        
        industry_data = {
            "行业概况": {},
            "板块表现": {},
            "锂盐市场": {},
            "行业趋势": [],
            "投资机会": [],
            "风险提示": []
        }
        
        # 获取相关板块表现
        if not chemical_industry.empty:
            chemical_related = chemical_industry[chemical_industry['板块名称'].str.contains('化学制品|化工原料', na=False)]
            if not chemical_related.empty:
                best_performing = chemical_related.loc[chemical_related['涨跌幅'].idxmax()]
                industry_data["板块表现"] = {
                    "表现最好板块": best_performing['板块名称'],
                    "涨跌幅": f"{best_performing['涨跌幅']:.2f}%",
                    "总市值": best_performing.get('总市值', 'N/A'),
                    "换手率": f"{best_performing.get('换手率', 0):.2f}%"
                }
        
        industry_data["行业概况"] = {
            "行业分类": "锂盐化工行业",
            "主要产品": "氢氧化锂、碳酸锂等锂盐产品",
            "应用领域": "锂电池、新能源汽车、储能",
            "行业特点": "强周期性，价格弹性大"
        }
        
        industry_data["锂盐市场"] = {
            "价格趋势": "锂盐价格经历大幅波动后趋于稳定",
            "供需状况": "供给逐步释放，需求持续增长",
            "主要企业": "天齐锂业、赣锋锂业、雅化集团等",
            "成本支撑": "锂矿成本提供价格底部支撑"
        }
        
        industry_data["行业趋势"] = [
            "新能源汽车渗透率持续提升，锂盐需求增长",
            "储能市场快速发展，为锂盐需求提供新增长点",
            "锂盐价格趋于理性，行业盈利能力改善",
            "技术进步推动成本下降和效率提升",
            "产业链整合加速，一体化优势凸显"
        ]
        
        industry_data["投资机会"] = [
            "锂盐价格企稳回升，企业盈利改善",
            "新能源汽车销量增长带动需求",
            "储能市场爆发提供新增需求",
            "行业估值处于相对低位",
            "政策支持新能源产业发展"
        ]
        
        industry_data["风险提示"] = [
            "锂盐价格波动风险较大",
            "供给释放过快可能导致供需失衡",
            "新能源汽车补贴政策变化",
            "技术路线变化风险",
            "环保政策趋严增加成本压力"
        ]
        
        return industry_data
        
    except Exception as e:
        print(f"行业分析失败: {e}")
        return None

def get_lithium_price_trend():
    """获取锂盐价格趋势"""
    print("正在获取锂盐价格趋势...")
    
    try:
        # 获取锂相关产品价格数据
        # 这里使用一个简化的分析，实际应用中需要获取专业的锂盐价格数据
        
        lithium_data = {
            "电池级碳酸锂": {
                "当前价格": "约7-8万元/吨",
                "价格趋势": "近期企稳回升",
                "历史高点": "约60万元/吨",
                "历史低点": "约4万元/吨"
            },
            "氢氧化锂": {
                "当前价格": "约7-9万元/吨", 
                "价格趋势": "跟随碳酸锂走势",
                "特点": "高镍电池主要原料"
            },
            "市场分析": [
                "锂盐价格经历2022年高点后大幅回调",
                "2024年以来价格逐步企稳",
                "成本支撑作用下，价格下行空间有限",
                "需求回暖有望推动价格温和上涨"
            ]
        }
        
        return lithium_data
        
    except Exception as e:
        print(f"锂盐价格分析失败: {e}")
        return None

def generate_comprehensive_analysis():
    """生成综合分析报告"""
    print("\n=== 雅化集团（002497）综合分析报告 ===")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取各项分析数据
    basic_info = get_basic_info()
    financial_data = get_financial_data()
    performance = get_historical_performance()
    technical = get_technical_analysis()
    industry = get_industry_analysis()
    lithium_price = get_lithium_price_trend()
    
    print("\n【公司基本信息】")
    if basic_info:
        print(f"股票代码: {basic_info['股票代码']}")
        print(f"股票名称: {basic_info['股票名称']}")
        print(f"当前价格: {basic_info['当前价格']}")
        print(f"涨跌幅: {basic_info['涨跌幅']}")
        print(f"市值: {basic_info['市值']}")
        print(f"成交量: {basic_info['成交量']}")
        
        if basic_info['基本信息']:
            print(f"主营业务: {basic_info['基本信息'].get('主营业务', '锂盐产品及民爆产品')}")
            print(f"所属行业: {basic_info['基本信息'].get('所属行业', '化工行业')}")
    
    print("\n【历史表现分析】")
    if performance:
        for key, value in performance.items():
            print(f"{key}: {value}")
    
    print("\n【锂盐价格分析】")
    if lithium_price:
        for product, data in lithium_price.items():
            if isinstance(data, dict):
                print(f"{product}:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"{product}: {data}")
    
    print("\n【技术分析】")
    if technical:
        print(f"当前趋势: {technical['当前趋势']}")
        print(f"短期展望: {technical['短期展望']}")
        print(f"操作建议: {technical['操作建议']}")
        
        if technical['技术指标']:
            print("技术指标:")
            for key, value in technical['技术指标'].items():
                print(f"  {key}: {value}")
        
        if technical['关键支撑位']:
            print("关键支撑位:")
            for support in technical['关键支撑位']:
                print(f"  - {support}")
        
        if technical['关键阻力位']:
            print("关键阻力位:")
            for resistance in technical['关键阻力位']:
                print(f"  - {resistance}")
    
    print("\n【行业分析】")
    if industry:
        if industry['板块表现']:
            print("板块表现:")
            for key, value in industry['板块表现'].items():
                print(f"  {key}: {value}")
        
        if industry['行业概况']:
            print("行业概况:")
            for key, value in industry['行业概况'].items():
                print(f"  {key}: {value}")
        
        if industry['锂盐市场']:
            print("锂盐市场:")
            for key, value in industry['锂盐市场'].items():
                print(f"  {key}: {value}")
        
        if industry['行业趋势']:
            print("行业趋势:")
            for trend in industry['行业趋势']:
                print(f"  • {trend}")
        
        if industry['投资机会']:
            print("投资机会:")
            for opportunity in industry['投资机会']:
                print(f"  ✓ {opportunity}")
        
        if industry['风险提示']:
            print("风险提示:")
            for risk in industry['风险提示']:
                print(f"  ⚠ {risk}")
    
    print("\n【财务数据】")
    if financial_data and financial_data['主要指标']:
        print("主要财务指标:")
        for key, value in financial_data['主要指标'].items():
            print(f"  {key}: {value}")
    
    print("\n【综合投资建议】")
    print("=" * 60)
    
    # 基于分析给出投资建议
    investment_advice = {
        "短期评级": "",
        "中期评级": "",
        "目标价位": "",
        "止损位": "",
        "投资建议": "",
        "关注要点": []
    }
    
    # 综合分析给出建议
    if technical and industry:
        trend = technical['当前趋势']
        
        if '上升' in trend:
            investment_advice["短期评级"] = "买入"
            investment_advice["投资建议"] = "技术面向好，锂盐价格企稳，可考虑适量参与"
        elif '下降' in trend:
            investment_advice["短期评级"] = "观望"
            investment_advice["投资建议"] = "技术面偏弱，建议等待更好时机"
        else:
            investment_advice["短期评级"] = "中性"
            investment_advice["投资建议"] = "震荡整理，关注锂盐价格变化和公司业绩"
        
        investment_advice["中期评级"] = "中性偏乐观"
        investment_advice["目标价位"] = "根据技术面阻力位设定"
        investment_advice["止损位"] = "跌破关键支撑位止损"
        
        investment_advice["关注要点"] = [
            "关注锂盐价格走势和供需变化",
            "观察公司锂盐业务盈利能力",
            "注意新能源汽车销量数据",
            "跟踪行业产能释放情况",
            "监控资金流向和市场情绪变化"
        ]
    
    print(f"短期评级: {investment_advice['短期评级']}")
    print(f"中期评级: {investment_advice['中期评级']}")
    print(f"投资建议: {investment_advice['投资建议']}")
    print(f"目标价位: {investment_advice['目标价位']}")
    print(f"止损位: {investment_advice['止损位']}")
    
    if investment_advice['关注要点']:
        print("关注要点:")
        for point in investment_advice['关注要点']:
            print(f"  • {point}")
    
    # 生成完整报告
    report = {
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "公司信息": basic_info,
        "历史表现": performance,
        "锂盐价格": lithium_price,
        "技术分析": technical,
        "行业分析": industry,
        "财务数据": financial_data,
        "投资建议": investment_advice
    }
    
    return report

if __name__ == "__main__":
    try:
        report = generate_comprehensive_analysis()
        
        # 保存报告
        report_file = f"report/yahua_group_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n分析报告已保存至: {report_file}")
        
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()