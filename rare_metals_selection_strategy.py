#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
稀有金属行业选股策略分析
包括行业分析、标的筛选、选股框架等
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def get_rare_metals_industry_overview():
    """获取稀有金属行业整体情况"""
    print("正在分析稀有金属行业整体情况...")
    
    try:
        # 获取稀有金属相关板块表现
        industry_data = ak.stock_board_industry_name_em()
        
        # 筛选稀有金属相关板块
        rare_metals_sectors = industry_data[
            industry_data['板块名称'].str.contains('有色|金属|稀土|锂|钴|镍|钨|钼|锗|铟|镓|铂|钯', na=False)
        ]
        
        industry_overview = {
            "行业分类": {},
            "整体表现": {},
            "价格趋势": {},
            "政策环境": []
        }
        
        # 主要细分领域分类
        industry_overview["行业分类"] = {
            "锂盐相关": ["天齐锂业", "赣锋锂业", "雅化集团", "盛新锂能", "融捷股份"],
            "稀土永磁": ["北方稀土", "盛和资源", "广晟有色", "五矿稀土", "中科三环"],
            "钴镍材料": ["华友钴业", "寒锐钴业", "格林美", "洛阳钼业"],
            "钨钼金属": ["厦门钨业", "中钨高新", "章源钨业", "金钼股份"],
            "小金属": ["云南锗业", "驰宏锌锗", "罗平锌电", "株冶集团"],
            "贵金属": ["山东黄金", "中金黄金", "银泰黄金", "湖南黄金"]
        }
        
        # 板块整体表现分析
        if not rare_metals_sectors.empty:
            avg_performance = rare_metals_sectors['涨跌幅'].mean()
            up_count = len(rare_metals_sectors[rare_metals_sectors['涨跌幅'] > 0])
            down_count = len(rare_metals_sectors[rare_metals_sectors['涨跌幅'] < 0])
            
            industry_overview["整体表现"] = {
                "平均涨跌幅": f"{avg_performance:.2f}%",
                "上涨板块数": up_count,
                "下跌板块数": down_count,
                "活跃板块": rare_metals_sectors.nlargest(3, '涨跌幅')[['板块名称', '涨跌幅']].to_dict('records')
            }
        
        # 政策环境分析
        industry_overview["政策环境"] = [
            "国家战略性矿产资源保护政策",
            "新能源产业扶持政策",
            "稀土行业整合和规范发展",
            "环保政策趋严影响供给",
            "国际贸易摩擦影响进出口"
        ]
        
        return industry_overview
        
    except Exception as e:
        print(f"行业整体分析失败: {e}")
        return None

def get_rare_metals_stock_pool():
    """获取稀有金属主要标的股票池"""
    print("正在梳理稀有金属主要标的...")
    
    # 定义稀有金属核心标的
    stock_pool = {
        "锂盐龙头": {
            "天齐锂业": {"代码": "002466", "主营业务": "锂矿开采和锂盐生产", "地位": "全球最大锂矿商"},
            "赣锋锂业": {"代码": "002460", "主营业务": "锂盐产品和锂电池", "地位": "全球领先锂生态企业"},
            "雅化集团": {"代码": "002497", "主营业务": "锂盐和民爆产品", "地位": "锂盐新贵"},
            "盛新锂能": {"代码": "002240", "主营业务": "锂盐和新能源材料", "地位": "锂盐产能快速扩张"},
            "融捷股份": {"代码": "002192", "主营业务": "锂矿采选和锂盐", "地位": "锂矿资源储备丰富"}
        },
        "稀土永磁": {
            "北方稀土": {"代码": "600111", "主营业务": "稀土原料和功能材料", "地位": "中国稀土龙头"},
            "盛和资源": {"代码": "600392", "主营业务": "稀土冶炼和深加工", "地位": "稀土全产业链"},
            "广晟有色": {"代码": "600259", "主营业务": "稀土开采和加工", "地位": "南方稀土整合平台"},
            "五矿稀土": {"代码": "000831", "主营业务": "稀土氧化物和金属", "地位": "五矿集团旗下稀土平台"},
            "中科三环": {"代码": "000970", "主营业务": "稀土永磁材料", "地位": "全球领先磁材企业"}
        },
        "钴镍材料": {
            "华友钴业": {"代码": "603799", "主营业务": "钴产品和新能源材料", "地位": "全球钴业龙头"},
            "寒锐钴业": {"代码": "300618", "主营业务": "钴粉制造和销售", "地位": "钴粉细分龙头"},
            "格林美": {"代码": "002340", "主营业务": "钴镍回收和新能源材料", "地位": "循环经济龙头"},
            "洛阳钼业": {"代码": "603993", "主营业务": "铜钴矿开采", "地位": "国际矿业巨头"}
        },
        "钨钼金属": {
            "厦门钨业": {"代码": "600549", "主营业务": "钨钼稀土新能源材料", "地位": "钨业龙头"},
            "中钨高新": {"代码": "000657", "主营业务": "硬质合金和钨制品", "地位": "中国五矿钨产业平台"},
            "章源钨业": {"代码": "002378", "主营业务": "钨矿开采和冶炼", "地位": "钨矿资源企业"},
            "金钼股份": {"代码": "601958", "主营业务": "钼矿开采和冶炼", "地位": "钼业龙头"}
        },
        "小金属": {
            "云南锗业": {"代码": "002428", "主营业务": "锗矿开采和加工", "地位": "国内锗业龙头"},
            "驰宏锌锗": {"代码": "600497", "主营业务": "铅锌锗冶炼", "地位": "铅锌锗一体化"},
            "株冶集团": {"代码": "600961", "主营业务": "锌冶炼和稀贵综合回收", "地位": "锌冶炼龙头"}
        },
        "贵金属": {
            "山东黄金": {"代码": "600547", "主营业务": "黄金开采和冶炼", "地位": "黄金行业龙头"},
            "中金黄金": {"代码": "600489", "主营业务": "黄金和铜开采", "地位": "央企黄金平台"},
            "银泰黄金": {"代码": "000975", "主营业务": "黄金开采", "地位": "民营黄金企业"},
            "湖南黄金": {"代码": "002155", "主营业务": "黄金和锑钨开采", "地位": "黄金锑钨综合"}
        }
    }
    
    return stock_pool

def analyze_stock_fundamentals(code, name):
    """分析个股基本面"""
    try:
        # 获取当前股价数据
        current_data = ak.stock_zh_a_spot_em()
        stock_data = current_data[current_data['代码'] == code]
        
        # 获取历史表现
        hist_data = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=(datetime.now() - timedelta(days=250)).strftime("%Y%m%d"), end_date=datetime.now().strftime("%Y%m%d"))
        
        analysis = {
            "当前价格": "N/A",
            "涨跌幅": "N/A",
            "市值": "N/A",
            "近1年涨跌幅": "N/A",
            "近6月涨跌幅": "N/A",
            "近3月涨跌幅": "N/A",
            "波动率": "N/A",
            "相对位置": "N/A",
            "技术评分": 0
        }
        
        if not stock_data.empty:
            analysis["当前价格"] = f"{stock_data.iloc[0].get('最新价', 0):.2f}"
            analysis["涨跌幅"] = f"{stock_data.iloc[0].get('涨跌幅', 0):.2f}%"
            analysis["市值"] = stock_data.iloc[0].get('总市值', 'N/A')
        
        if not hist_data.empty and len(hist_data) > 0:
            current_price = hist_data['收盘'].iloc[-1]
            
            # 计算不同时间段涨跌幅
            if len(hist_data) >= 125:  # 近6月
                half_year_ago = hist_data['收盘'].iloc[-125]
                analysis["近6月涨跌幅"] = f"{((current_price - half_year_ago) / half_year_ago * 100):.2f}%"
            
            if len(hist_data) >= 60:  # 近3月
                quarter_ago = hist_data['收盘'].iloc[-60]
                analysis["近3月涨跌幅"] = f"{((current_price - quarter_ago) / quarter_ago * 100):.2f}%"
            
            if len(hist_data) >= 250:  # 近1年
                year_ago = hist_data['收盘'].iloc[-250]
                analysis["近1年涨跌幅"] = f"{((current_price - year_ago) / year_ago * 100):.2f}%"
            
            # 计算波动率
            if len(hist_data) >= 60:
                recent_data = hist_data.tail(60)
                daily_returns = recent_data['收盘'].pct_change().dropna()
                volatility = daily_returns.std() * np.sqrt(252) * 100
                analysis["波动率"] = f"{volatility:.2f}%"
            
            # 相对位置
            price_range = hist_data['最高'].max() - hist_data['最低'].min()
            current_position = (current_price - hist_data['最低'].min()) / price_range * 100
            analysis["相对位置"] = f"{current_position:.1f}%"
            
            # 技术评分（简化版）
            score = 0
            if len(hist_data) >= 20:
                recent_data = hist_data.tail(20)
                ma5 = recent_data['收盘'].tail(5).mean()
                ma10 = recent_data['收盘'].tail(10).mean()
                ma20 = recent_data['收盘'].mean()
                
                if current_price > ma5 > ma10:
                    score += 2
                elif current_price > ma5:
                    score += 1
                
                if current_position < 80:  # 不在绝对高位
                    score += 1
                
                if volatility < 50:  # 波动适中
                    score += 1
            
            analysis["技术评分"] = min(score, 5)  # 满分5分
        
        return analysis
        
    except Exception as e:
        print(f"分析{code}基本面失败: {e}")
        return None

def build_selection_framework():
    """建立选股框架和评估标准"""
    print("正在建立选股框架...")
    
    selection_framework = {
        "评估维度": {
            "基本面权重": 0.4,
            "技术面权重": 0.3,
            "行业前景权重": 0.2,
            "估值水平权重": 0.1
        },
        "基本面指标": {
            "业绩成长性": {"权重": 0.3, "标准": "营收和利润增长率"},
            "盈利能力": {"权重": 0.25, "标准": "ROE、毛利率、净利率"},
            "财务健康": {"权重": 0.25, "标准": "资产负债率、现金流"},
            "行业地位": {"权重": 0.2, "标准": "市场份额、技术实力"}
        },
        "技术面指标": {
            "趋势强度": {"权重": 0.4, "标准": "均线排列、价格位置"},
            "成交量": {"权重": 0.3, "标准": "放量上涨、缩量调整"},
            "波动率": {"权重": 0.2, "标准": "波动适中，不过于剧烈"},
            "相对强弱": {"权重": 0.1, "标准": "相对大盘和板块表现"}
        },
        "行业前景指标": {
            "需求增长": {"权重": 0.4, "标准": "下游需求增长潜力"},
            "供给格局": {"权重": 0.3, "标准": "行业集中度、竞争格局"},
            "政策支持": {"权重": 0.2, "标准": "国家政策扶持力度"},
            "价格趋势": {"权重": 0.1, "标准": "产品价格走势"}
        },
        "估值指标": {
            "PE估值": {"权重": 0.4, "标准": "相对历史水平和同业比较"},
            "PB估值": {"权重": 0.3, "标准": "净资产溢价合理性"},
            "PEG估值": {"权重": 0.3, "标准": "成长性匹配度"}
        }
    }
    
    return selection_framework

def get_current_metal_prices():
    """获取当前金属价格趋势"""
    print("正在获取金属价格趋势...")
    
    # 模拟当前金属价格数据（实际需要接入专业价格数据库）
    metal_prices = {
        "锂盐价格": {
            "碳酸锂(万元/吨)": "7.5-8.0",
            "氢氧化锂(万元/吨)": "7.8-8.5",
            "趋势": "企稳回升",
            "分析": "成本支撑+需求回暖"
        },
        "稀土价格": {
            "氧化镨钕(万元/吨)": "40-45",
            "氧化铽(万元/吨)": "650-700",
            "氧化镝(万元/吨)": "200-220",
            "趋势": "震荡整理",
            "分析": "供需相对平衡"
        },
        "钴价": {
            "电解钴(万元/吨)": "22-25",
            "趋势": "偏弱震荡",
            "分析": "供给过剩压力"
        },
        "镍价": {
            "电解镍(万元/吨)": "12-14",
            "趋势": "震荡偏弱",
            "分析": "不锈钢需求疲软"
        },
        "钨价": {
            "APT(万元/吨)": "18-20",
            "趋势": "相对稳定",
            "分析": "成本支撑较强"
        },
        "黄金价格": {
            "现货黄金(元/克)": "450-480",
            "趋势": "震荡上行",
            "分析": "避险需求+美元走弱"
        }
    }
    
    return metal_prices

def select_top_stocks(stock_pool, framework, metal_prices):
    """根据选股框架筛选优质标的"""
    print("正在筛选优质标的...")
    
    stock_scores = {}
    
    for category, stocks in stock_pool.items():
        for name, info in stocks.items():
            code = info["代码"]
            
            # 获取基本面数据
            fundamental_data = analyze_stock_fundamentals(code, name)
            if not fundamental_data:
                continue
            
            # 计算综合评分
            total_score = 0
            
            # 技术面评分（满分5分）
            technical_score = fundamental_data.get("技术评分", 0)
            
            # 基本面评分（基于涨跌幅和相对位置）
            try:
                performance_score = 0
                if fundamental_data["近6月涨跌幅"] != "N/A":
                    perf_6m = float(fundamental_data["近6月涨跌幅"].replace("%", ""))
                    if perf_6m > 20: performance_score += 2
                    elif perf_6m > 0: performance_score += 1
                
                if fundamental_data["近3月涨跌幅"] != "N/A":
                    perf_3m = float(fundamental_data["近3月涨跌幅"].replace("%", ""))
                    if perf_3m > 15: performance_score += 2
                    elif perf_3m > 0: performance_score += 1
                
                if fundamental_data["相对位置"] != "N/A":
                    position = float(fundamental_data["相对位置"].replace("%", ""))
                    if position < 70: performance_score += 1
                
                fundamental_score = min(performance_score, 5)
                
            except:
                fundamental_score = 3  # 默认值
            
            # 行业前景评分（基于金属价格趋势）
            industry_score = 0
            if category == "锂盐龙头" and "回升" in metal_prices["锂盐价格"]["趋势"]:
                industry_score = 4
            elif category == "稀土永磁" and "整理" in metal_prices["稀土价格"]["趋势"]:
                industry_score = 3
            elif category == "贵金属" and "上行" in metal_prices["黄金价格"]["趋势"]:
                industry_score = 4
            else:
                industry_score = 2
            
            # 综合评分（加权平均）
            weights = {
                "技术面": 0.3,
                "基本面": 0.4,
                "行业前景": 0.2,
                "估值": 0.1  # 简化处理
            }
            
            total_score = (
                technical_score * weights["技术面"] +
                fundamental_score * weights["基本面"] +
                industry_score * weights["行业前景"]
            )
            
            stock_scores[name] = {
                "代码": code,
                "类别": category,
                "综合评分": round(total_score, 2),
                "技术评分": technical_score,
                "基本面评分": fundamental_score,
                "行业评分": industry_score,
                "当前价格": fundamental_data["当前价格"],
                "涨跌幅": fundamental_data["涨跌幅"],
                "市值": fundamental_data["市值"],
                "近6月涨幅": fundamental_data["近6月涨跌幅"],
                "近3月涨幅": fundamental_data["近3月涨跌幅"],
                "相对位置": fundamental_data["相对位置"]
            }
    
    # 按评分排序
    sorted_stocks = sorted(stock_scores.items(), key=lambda x: x[1]["综合评分"], reverse=True)
    
    return sorted_stocks

def generate_selection_strategy():
    """生成稀有金属选股策略报告"""
    print("\n=== 稀有金属行业选股策略分析 ===")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 获取各项分析数据
    industry_overview = get_rare_metals_industry_overview()
    stock_pool = get_rare_metals_stock_pool()
    framework = build_selection_framework()
    metal_prices = get_current_metal_prices()
    top_stocks = select_top_stocks(stock_pool, framework, metal_prices)
    
    print("\n【稀有金属行业概况】")
    if industry_overview:
        if industry_overview["整体表现"]:
            print(f"板块平均涨跌幅: {industry_overview['整体表现']['平均涨跌幅']}")
            print(f"上涨板块数: {industry_overview['整体表现']['上涨板块数']}")
            print(f"下跌板块数: {industry_overview['整体表现']['下跌板块数']}")
            
            if industry_overview["整体表现"]["活跃板块"]:
                print("最活跃板块:")
                for board in industry_overview["整体表现"]["活跃板块"]:
                    print(f"  - {board['板块名称']}: {board['涨跌幅']:.2f}%")
    
    print("\n【金属价格趋势】")
    if metal_prices:
        for metal, data in metal_prices.items():
            if isinstance(data, dict):
                print(f"\n{metal}:")
                for key, value in data.items():
                    if key != "趋势" and key != "分析":
                        print(f"  {key}: {value}")
                print(f"  趋势: {data.get('趋势', 'N/A')}")
                print(f"  分析: {data.get('分析', 'N/A')}")
    
    print("\n【选股框架】")
    if framework:
        print("评估维度权重:")
        for dimension, weight in framework["评估维度"].items():
            print(f"  - {dimension}: {weight*100:.0f}%")
        
        print("\n核心评估指标:")
        for category, indicators in framework.items():
            if category != "评估维度":
                print(f"\n{category}:")
                for indicator, details in indicators.items():
                    print(f"  - {indicator}: 权重{details['权重']*100:.0f}%, 标准: {details['标准']}")
    
    print("\n【优质标的推荐】")
    if top_stocks:
        print("综合评分前10名:")
        for i, (name, data) in enumerate(top_stocks[:10], 1):
            print(f"\n{i}. {name} ({data['代码']})")
            print(f"   综合评分: {data['综合评分']}/5.0")
            print(f"   所属类别: {data['类别']}")
            print(f"   当前价格: {data['当前价格']}")
            print(f"   今日涨跌: {data['涨跌幅']}")
            print(f"   近6月涨幅: {data['近6月涨幅']}")
            print(f"   近3月涨幅: {data['近3月涨幅']}")
            print(f"   相对位置: {data['相对位置']}")
            print(f"   技术评分: {data['技术评分']}/5")
            print(f"   基本面评分: {data['基本面评分']}/5")
            print(f"   行业评分: {data['行业评分']}/5")
    
    print("\n【分类别推荐】")
    if top_stocks:
        categories = {}
        for name, data in top_stocks:
            category = data['类别']
            if category not in categories:
                categories[category] = []
            categories[category].append((name, data))
        
        for category, stocks in categories.items():
            if stocks:
                print(f"\n{category}推荐:")
                for name, data in stocks[:3]:  # 每类推荐前3名
                    print(f"  - {name}: 评分{data['综合评分']}, 现价{data['当前价格']}, 6月{data['近6月涨幅']}")
    
    print("\n【投资策略建议】")
    print("=" * 70)
    
    strategy_advice = {
        "总体策略": "",
        "配置建议": [],
        "风险控制": [],
        "具体操作": []
    }
    
    # 基于分析给出策略建议
    if top_stocks and metal_prices:
        # 判断整体市场环境
        bull_market_count = len([s for s in top_stocks if float(s[1]['近6月涨幅'].replace('%', '')) > 20])
        
        if bull_market_count >= 5:
            strategy_advice["总体策略"] = "市场处于相对强势，可积极参与，但需控制仓位"
        elif bull_market_count >= 3:
            strategy_advice["总体策略"] = "市场分化明显，精选个股参与"
        else:
            strategy_advice["总体策略"] = "市场整体偏弱，谨慎参与，等待更好时机"
        
        strategy_advice["配置建议"] = [
            "分散投资: 不同金属品种均衡配置，降低单一风险",
            "龙头优先: 优先选择行业龙头和细分冠军",
            "分批建仓: 采用分批买入策略，避免集中建仓",
            "周期配置: 根据金属价格周期调整配置比例"
        ]
        
        strategy_advice["风险控制"] = [
            "设置止损: 单只股票止损位建议10-15%",
            "仓位控制: 总仓位不超过总资产的30-50%",
            "价格监控: 密切关注金属期货价格变化",
            "政策跟踪: 关注行业政策和贸易政策变化"
        ]
        
        strategy_advice["具体操作"] = [
            "选择3-5只不同细分领域的优质标的构建组合",
            "根据技术评分和基本面评分综合决定权重",
            "定期调仓，优胜劣汰，保持组合活力",
            "结合金属价格趋势调整仓位大小"
        ]
    
    print(f"总体策略: {strategy_advice['总体策略']}")
    
    print("\n配置建议:")
    for advice in strategy_advice["配置建议"]:
        print(f"  • {advice}")
    
    print("\n风险控制:")
    for risk in strategy_advice["风险控制"]:
        print(f"  ⚠ {risk}")
    
    print("\n具体操作:")
    for operation in strategy_advice["具体操作"]:
        print(f"  → {operation}")
    
    print("\n【重要提醒】")
    print("=" * 70)
    print("⚠ 稀有金属价格波动较大，投资需谨慎")
    print("⚠ 以上分析仅供参考，不构成投资建议")
    print("⚠ 请根据个人风险承受能力做出投资决策")
    print("⚠ 建议咨询专业投资顾问并进行充分研究")
    print("⚠ 定期关注行业动态和公司基本面变化")
    
    # 生成完整报告
    report = {
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "行业概况": industry_overview,
        "股票池": stock_pool,
        "选股框架": framework,
        "金属价格": metal_prices,
        "优质标的": dict(top_stocks[:15]),  # 前15名
        "策略建议": strategy_advice
    }
    
    return report

if __name__ == "__main__":
    try:
        report = generate_selection_strategy()
        
        # 保存报告
        report_file = f"report/rare_metals_strategy_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n策略报告已保存至: {report_file}")
        
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()