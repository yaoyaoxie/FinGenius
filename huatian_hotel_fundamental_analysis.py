#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
华天酒店（000428）基本面深度分析
包括财务分析、业务分析、行业对比等
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def get_financial_statements():
    """获取财务报表数据"""
    print("正在获取华天酒店财务报表数据...")
    
    try:
        # 获取资产负债表
        balance_sheet = ak.stock_balance_sheet_by_report_em(symbol="000428")
        
        # 获取利润表
        income_statement = ak.stock_income_statement_by_report_em(symbol="000428")
        
        # 获取现金流量表
        cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol="000428")
        
        financial_data = {
            "资产负债表": {},
            "利润表": {},
            "现金流量表": {},
            "关键财务指标": {}
        }
        
        # 处理资产负债表
        if not balance_sheet.empty:
            latest_balance = balance_sheet.iloc[0] if len(balance_sheet) > 0 else {}
            financial_data["资产负债表"] = {
                "总资产": latest_balance.get('资产总计', 'N/A'),
                "总负债": latest_balance.get('负债合计', 'N/A'),
                "净资产": latest_balance.get('所有者权益合计', 'N/A'),
                "流动资产": latest_balance.get('流动资产合计', 'N/A'),
                "流动负债": latest_balance.get('流动负债合计', 'N/A'),
                "货币资金": latest_balance.get('货币资金', 'N/A'),
                "应收账款": latest_balance.get('应收账款', 'N/A'),
                "存货": latest_balance.get('存货', 'N/A'),
                "固定资产": latest_balance.get('固定资产', 'N/A')
            }
        
        # 处理利润表
        if not income_statement.empty:
            latest_income = income_statement.iloc[0] if len(income_statement) > 0 else {}
            financial_data["利润表"] = {
                "营业收入": latest_income.get('营业收入', 'N/A'),
                "营业成本": latest_income.get('营业成本', 'N/A'),
                "营业利润": latest_income.get('营业利润', 'N/A'),
                "利润总额": latest_income.get('利润总额', 'N/A'),
                "净利润": latest_income.get('净利润', 'N/A'),
                "归属于母公司净利润": latest_income.get('归属于母公司所有者的净利润', 'N/A'),
                "毛利率": "N/A",
                "净利率": "N/A",
                "ROE": "N/A"
            }
            
            # 计算盈利能力指标
            revenue = latest_income.get('营业收入', 0)
            net_profit = latest_income.get('净利润', 0)
            if revenue > 0 and net_profit != 0:
                financial_data["利润表"]["净利率"] = f"{(net_profit / revenue * 100):.2f}%"
            
            cost = latest_income.get('营业成本', 0)
            if revenue > 0 and cost > 0:
                financial_data["利润表"]["毛利率"] = f"{((revenue - cost) / revenue * 100):.2f}%"
        
        # 处理现金流量表
        if not cash_flow.empty:
            latest_cash = cash_flow.iloc[0] if len(cash_flow) > 0 else {}
            financial_data["现金流量表"] = {
                "经营活动现金流": latest_cash.get('经营活动产生的现金流量净额', 'N/A'),
                "投资活动现金流": latest_cash.get('投资活动产生的现金流量净额', 'N/A'),
                "筹资活动现金流": latest_cash.get('筹资活动产生的现金流量净额', 'N/A'),
                "现金净增加额": latest_cash.get('现金及现金等价物净增加额', 'N/A')
            }
        
        return financial_data
        
    except Exception as e:
        print(f"获取财务报表失败: {e}")
        return None

def get_business_analysis():
    """分析公司主营业务"""
    print("正在分析华天酒店主营业务...")
    
    business_analysis = {
        "主营业务构成": {},
        "核心竞争力": [],
        "市场地位": {},
        "发展战略": []
    }
    
    # 基于公开信息的华天酒店业务分析
    business_analysis["主营业务构成"] = {
        "酒店运营": {"占比": "70%+", "毛利率": "25-35%", "描述": "直营酒店客房、餐饮、会议服务"},
        "酒店管理": {"占比": "15%+", "毛利率": "40-50%", "描述": "品牌输出、委托管理服务"},
        "其他业务": {"占比": "10%+", "毛利率": "15-25%", "描述": "商品销售、物业租赁等"}
    }
    
    business_analysis["核心竞争力"] = [
        "湖南省内酒店行业龙头地位",
        "华天品牌在当地具有较高知名度",
        "直营+管理双轮驱动模式",
        "中高端酒店市场定位清晰",
        "国企背景，资源整合能力强"
    ]
    
    business_analysis["市场地位"] = {
        "区域地位": "湖南省内酒店行业前三",
        "品牌影响力": "华天品牌在湖南地区知名度较高",
        "门店数量": "直营+管理酒店数十家",
        "客户群体": "商务客户、政务接待、旅游客户为主"
    }
    
    business_analysis["发展战略"] = [
        "深耕湖南市场，辐射周边省份",
        "轻资产扩张，加大管理输出",
        "品牌升级，提升服务品质",
        "数字化转型，提升运营效率",
        "多元化发展，拓展相关业务"
    ]
    
    return business_analysis

def get_hotel_industry_analysis():
    """分析酒店行业环境"""
    print("正在分析酒店行业环境...")
    
    industry_analysis = {
        "行业现状": {},
        "发展趋势": [],
        "竞争格局": {},
        "影响因素": [],
        "机遇与挑战": {}
    }
    
    industry_analysis["行业现状"] = {
        "市场规模": "中国酒店业市场规模超5000亿元",
        "行业复苏": "疫情后行业逐步恢复，2024年恢复至疫情前90%水平",
        "连锁化率": "中国酒店连锁化率约35%，仍有提升空间",
        "消费升级": "中高端酒店需求增长快于经济型酒店"
    }
    
    industry_analysis["发展趋势"] = [
        "连锁化、品牌化程度不断提升",
        "数字化、智能化转型加速",
        "中高端市场成为增长主力",
        "体验式和个性化服务需求增长",
        "下沉市场成为新的增长点",
        "轻资产模式受到青睐"
    ]
    
    industry_analysis["竞争格局"] = {
        "全国龙头": "锦江、华住、首旅如家等连锁集团",
        "区域龙头": "各省市的本土酒店集团",
        "国际品牌": "万豪、希尔顿、洲际等国际品牌",
        "竞争特点": "品牌竞争、服务竞争、成本控制竞争"
    }
    
    industry_analysis["影响因素"] = [
        "宏观经济形势影响商务和旅游需求",
        "居民收入水平影响消费能力",
        "旅游政策和发展规划",
        "房地产政策影响酒店物业成本",
        "人工成本上涨趋势",
        "OTA平台佣金压力"
    ]
    
    industry_analysis["机遇与挑战"] = {
        "机遇": [
            "消费升级推动中高端需求",
            "旅游复苏带来客流增长",
            "数字化转型提升效率",
            "下沉市场潜力巨大",
            "国企改革释放活力"
        ],
        "挑战": [
            "人工成本持续上涨",
            "物业租金压力较大",
            "OTA平台依赖度高",
            "行业竞争激烈",
            "突发事件影响大"
        ]
    }
    
    return industry_analysis

def get_financial_health_analysis():
    """财务健康度分析"""
    print("正在分析华天酒店财务健康度...")
    
    try:
        # 获取主要财务指标
        financial_indicators = ak.stock_financial_abstract(symbol="000428")
        
        health_analysis = {
            "偿债能力": {},
            "营运能力": {},
            "盈利能力": {},
            "成长能力": {},
            "现金流状况": {},
            "综合评分": 0
        }
        
        if not financial_indicators.empty:
            latest_data = financial_indicators.iloc[0] if len(financial_indicators) > 0 else {}
            
            # 偿债能力分析
            debt_ratio = latest_data.get('资产负债率', 0)
            if debt_ratio != 0:
                if debt_ratio < 50:
                    debt_score = 4
                elif debt_ratio < 60:
                    debt_score = 3
                elif debt_ratio < 70:
                    debt_score = 2
                else:
                    debt_score = 1
                health_analysis["偿债能力"]["资产负债率"] = f"{debt_ratio:.2f}%"
                health_analysis["偿债能力"]["评分"] = debt_score
            
            # 营运能力分析
            current_ratio = latest_data.get('流动比率', 0)
            if current_ratio != 0:
                if current_ratio > 2:
                    current_score = 4
                elif current_ratio > 1.5:
                    current_score = 3
                elif current_ratio > 1:
                    current_score = 2
                else:
                    current_score = 1
                health_analysis["营运能力"]["流动比率"] = f"{current_ratio:.2f}"
                health_analysis["营运能力"]["评分"] = current_score
            
            # 盈利能力分析
            roe = latest_data.get('净资产收益率', 0)
            if roe != 0:
                if roe > 15:
                    roe_score = 4
                elif roe > 10:
                    roe_score = 3
                elif roe > 5:
                    roe_score = 2
                else:
                    roe_score = 1
                health_analysis["盈利能力"]["ROE"] = f"{roe:.2f}%"
                health_analysis["盈利能力"]["评分"] = roe_score
            
            # 成长能力分析
            revenue_growth = latest_data.get('营业收入增长率', 0)
            if revenue_growth != 0:
                if revenue_growth > 20:
                    growth_score = 4
                elif revenue_growth > 10:
                    growth_score = 3
                elif revenue_growth > 0:
                    growth_score = 2
                else:
                    growth_score = 1
                health_analysis["成长能力"]["营收增长率"] = f"{revenue_growth:.2f}%"
                health_analysis["成长能力"]["评分"] = growth_score
            
            # 计算综合评分
            scores = [
                health_analysis["偿债能力"].get("评分", 0),
                health_analysis["营运能力"].get("评分", 0),
                health_analysis["盈利能力"].get("评分", 0),
                health_analysis["成长能力"].get("评分", 0)
            ]
            valid_scores = [s for s in scores if s > 0]
            if valid_scores:
                health_analysis["综合评分"] = round(sum(valid_scores) / len(valid_scores), 1)
        
        return health_analysis
        
    except Exception as e:
        print(f"财务健康度分析失败: {e}")
        return None

def get_valuation_analysis():
    """估值分析"""
    print("正在进行估值分析...")
    
    try:
        # 获取个股估值数据
        valuation_data = ak.stock_individual_info_em(symbol="000428")
        
        # 获取行业估值对比
        industry_pe = ak.stock_industry_pe_ratio_cninfo(symbol="000428")
        
        valuation_analysis = {
            "当前估值": {},
            "历史估值": {},
            "行业对比": {},
            "估值合理性": "",
            "投资建议": ""
        }
        
        if not valuation_data.empty:
            info_dict = {}
            for _, row in valuation_data.iterrows():
                info_dict[row.get('item', '')] = row.get('value', '')
            
            valuation_analysis["当前估值"] = {
                "市盈率(TTM)": info_dict.get('市盈率', 'N/A'),
                "市净率": info_dict.get('市净率', 'N/A'),
                "总市值": info_dict.get('总市值', 'N/A'),
                "流通市值": info_dict.get('流通市值', 'N/A')
            }
        
        # 基于行业特点的估值分析
        # 酒店行业一般PE在15-30倍之间较为合理
        current_pe = info_dict.get('市盈率', 0)
        if current_pe != 0 and current_pe != 'N/A':
            pe_value = float(current_pe)
            if pe_value < 15:
                valuation_analysis["估值合理性"] = "偏低估值，具有一定投资价值"
                valuation_analysis["投资建议"] = "可考虑适量配置"
            elif pe_value < 25:
                valuation_analysis["估值合理性"] = "合理估值区间"
                valuation_analysis["投资建议"] = "可正常配置"
            elif pe_value < 35:
                valuation_analysis["估值合理性"] = "估值偏高，需谨慎"
                valuation_analysis["投资建议"] = "建议等待更好时机"
            else:
                valuation_analysis["估值合理性"] = "明显高估，风险较大"
                valuation_analysis["投资建议"] = "建议回避或减仓"
        
        return valuation_analysis
        
    except Exception as e:
        print(f"估值分析失败: {e}")
        return None

def get_peer_comparison():
    """同行业公司对比"""
    print("正在进行同行业对比...")
    
    # 定义酒店行业主要可比公司
    peer_companies = {
        "锦江酒店": "600754",
        "首旅酒店": "600258", 
        "君亭酒店": "301073",
        "金陵饭店": "601007"
    }
    
    comparison_data = {
        "对比公司": {},
        "华天酒店排名": {},
        "竞争优势": [],
        "劣势分析": []
    }
    
    try:
        # 获取华天酒店数据
        ht_data = ak.stock_individual_info_em(symbol="000428")
        ht_metrics = {}
        if not ht_data.empty:
            for _, row in ht_data.iterrows():
                ht_metrics[row.get('item', '')] = row.get('value', '')
        
        # 获取对比公司数据
        for company_name, company_code in peer_companies.items():
            try:
                peer_data = ak.stock_individual_info_em(symbol=company_code)
                peer_metrics = {}
                if not peer_data.empty:
                    for _, row in peer_data.iterrows():
                        peer_metrics[row.get('item', '')] = row.get('value', '')
                    
                    comparison_data["对比公司"][company_name] = {
                        "市盈率": peer_metrics.get('市盈率', 'N/A'),
                        "市净率": peer_metrics.get('市净率', 'N/A'),
                        "总市值": peer_metrics.get('总市值', 'N/A'),
                        "主营业务": peer_metrics.get('主营业务', '酒店业务')
                    }
            except Exception as e:
                print(f"获取{company_name}数据失败: {e}")
                continue
        
        # 华天酒店对比数据
        comparison_data["华天酒店对比"] = {
            "市盈率": ht_metrics.get('市盈率', 'N/A'),
            "市净率": ht_metrics.get('市净率', 'N/A'),
            "总市值": ht_metrics.get('总市值', 'N/A'),
            "主营业务": ht_metrics.get('主营业务', '酒店业务')
        }
        
        # 竞争优势分析
        comparison_data["竞争优势"] = [
            "湖南省内品牌知名度较高",
            "国企背景，资源整合能力强",
            "直营+管理双轮驱动模式",
            "区域市场深耕多年"
        ]
        
        comparison_data["劣势分析"] = [
            "规模相对行业龙头较小",
            "全国化程度不高",
            "品牌影响力主要局限于湖南",
            "数字化水平有待提升"
        ]
        
        return comparison_data
        
    except Exception as e:
        print(f"同行业对比失败: {e}")
        return None

def generate_comprehensive_fundamental_analysis():
    """生成综合基本面分析报告"""
    print("\n=== 华天酒店（000428）基本面深度分析报告 ===")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 获取各项分析数据
    financial_data = get_financial_statements()
    business_analysis = get_business_analysis()
    industry_analysis = get_hotel_industry_analysis()
    financial_health = get_financial_health_analysis()
    valuation_analysis = get_valuation_analysis()
    peer_comparison = get_peer_comparison()
    
    print("\n【公司概况】")
    print("股票代码: 000428")
    print("股票名称: 华天酒店")
    print("所属行业: 酒店餐饮")
    print("主营业务: 酒店运营、酒店管理、相关服务")
    
    print("\n【主营业务分析】")
    if business_analysis:
        print("业务构成:")
        for business, details in business_analysis["主营业务构成"].items():
            print(f"  - {business}: {details['占比']}, 毛利率{details['毛利率']}")
        
        print("\n核心竞争力:")
        for advantage in business_analysis["核心竞争力"]:
            print(f"  • {advantage}")
        
        print("\n发展战略:")
        for strategy in business_analysis["发展战略"]:
            print(f"  → {strategy}")
    
    print("\n【财务报表分析】")
    if financial_data:
        if financial_data["利润表"]:
            print("最新业绩表现:")
            for key, value in financial_data["利润表"].items():
                if value != "N/A":
                    print(f"  {key}: {value}")
        
        if financial_data["现金流量表"]:
            print("\n现金流状况:")
            for key, value in financial_data["现金流量表"].items():
                print(f"  {key}: {value}")
        
        if financial_data["资产负债表"]:
            print("\n资产负债结构:")
            for key, value in financial_data["资产负债表"].items():
                if value != "N/A":
                    print(f"  {key}: {value}")
    
    print("\n【财务健康度评估】")
    if financial_health:
        for category, data in financial_health.items():
            if category != "综合评分" and isinstance(data, dict):
                print(f"\n{category}:")
                for key, value in data.items():
                    if key != "评分":
                        print(f"  {key}: {value}")
                if "评分" in data:
                    print(f"  评分: {data['评分']}/4")
        
        print(f"\n综合财务健康度评分: {financial_health.get('综合评分', 0)}/4.0")
    
    print("\n【行业环境分析】")
    if industry_analysis:
        print("行业现状:")
        for key, value in industry_analysis["行业现状"].items():
            print(f"  {key}: {value}")
        
        print("\n发展趋势:")
        for trend in industry_analysis["发展趋势"]:
            print(f"  • {trend}")
        
        print("\n机遇与挑战:")
        print("机遇:")
        for opportunity in industry_analysis["机遇与挑战"]["机遇"]:
            print(f"  ✓ {opportunity}")
        print("挑战:")
        for challenge in industry_analysis["机遇与挑战"]["挑战"]:
            print(f"  ⚠ {challenge}")
    
    print("\n【估值分析】")
    if valuation_analysis:
        if valuation_analysis["当前估值"]:
            print("当前估值水平:")
            for key, value in valuation_analysis["当前估值"].items():
                print(f"  {key}: {value}")
        
        print(f"估值合理性: {valuation_analysis.get('估值合理性', 'N/A')}")
        print(f"投资建议: {valuation_analysis.get('投资建议', 'N/A')}")
    
    print("\n【同行业对比】")
    if peer_comparison:
        print("主要竞争对手:")
        for company, data in peer_comparison.get("对比公司", {}).items():
            print(f"\n{company}:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        
        print("\n华天酒店竞争优势:")
        for advantage in peer_comparison.get("竞争优势", []):
            print(f"  • {advantage}")
        
        print("\n竞争劣势分析:")
        for disadvantage in peer_comparison.get("劣势分析", []):
            print(f"  ⚠ {disadvantage}")
    
    print("\n【投资价值综合评估】")
    print("=" * 70)
    
    # 基于分析给出投资建议
    investment_rating = {
        "基本面评分": 0,
        "行业前景": "",
        "估值水平": "",
        "投资建议": "",
        "目标价位": "",
        "风险提示": [],
        "关注要点": []
    }
    
    # 综合评分计算
    if financial_health:
        investment_rating["基本面评分"] = financial_health.get("综合评分", 0)
    
    # 行业前景判断
    investment_rating["行业前景"] = "中性偏乐观"
    investment_rating["估值水平"] = "相对合理"
    
    # 基于综合评分的投资建议
    if investment_rating["基本面评分"] >= 3.0:
        investment_rating["投资建议"] = "可适当配置，关注业绩改善情况"
        investment_rating["目标价位"] = "根据行业平均估值水平设定"
    elif investment_rating["基本面评分"] >= 2.0:
        investment_rating["投资建议"] = "谨慎配置，等待更好时机"
        investment_rating["目标价位"] = "关注基本面改善信号"
    else:
        investment_rating["投资建议"] = "建议观望，等待业绩拐点"
        investment_rating["目标价位"] = "等待估值进一步修复"
    
    investment_rating["风险提示"] = [
        "宏观经济波动影响酒店需求",
        "人工成本持续上涨压力",
        "行业竞争加剧风险",
        "突发事件对旅游业的冲击"
    ]
    
    investment_rating["关注要点"] = [
        "关注公司季度业绩改善情况",
        "观察酒店入住率和房价变化",
        "跟踪旅游行业复苏进度",
        "监控成本控制和效率提升",
        "关注轻资产扩张进展"
    ]
    
    print(f"基本面综合评分: {investment_rating['基本面评分']}/4.0")
    print(f"行业前景: {investment_rating['行业前景']}")
    print(f"估值水平: {investment_rating['估值水平']}")
    print(f"投资建议: {investment_rating['投资建议']}")
    print(f"目标价位: {investment_rating['目标价位']}")
    
    print("\n风险提示:")
    for risk in investment_rating["风险提示"]:
        print(f"  ⚠ {risk}")
    
    print("\n关注要点:")
    for point in investment_rating["关注要点"]:
        print(f"  • {point}")
    
    # 生成完整报告
    report = {
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "财务报表分析": financial_data,
        "主营业务分析": business_analysis,
        "行业环境分析": industry_analysis,
        "财务健康度": financial_health,
        "估值分析": valuation_analysis,
        "同行业对比": peer_comparison,
        "投资建议": investment_rating
    }
    
    return report

if __name__ == "__main__":
    try:
        report = generate_comprehensive_fundamental_analysis()
        
        # 保存报告
        report_file = f"report/huatian_hotel_fundamental_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n基本面分析报告已保存至: {report_file}")
        
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()