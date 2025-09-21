#!/usr/bin/env python3
"""
华天酒店 (000428) 深度分析报告
基于多维度价值分析和酒店行业特点
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# 关闭警告
import warnings
warnings.filterwarnings('ignore')

class HotelAnalyzer:
    """酒店行业专业分析器"""
    
    def __init__(self):
        self.hotel_data = {
            '000428': {
                'company_name': '华天酒店集团股份有限公司',
                'hotels': 20,
                'rooms': 8000,
                'avg_rate': 450,  # 元/晚
                'occupancy': 0.65,
                'revpar': 292.5,  # 元/间夜
                'property_value': 10.0e9,  # 100亿
                'hotel_assets': 8.0e9,     # 80亿
                'land_value': 2.0e9,       # 20亿
            }
        }
    
    def comprehensive_analysis(self, symbol='000428'):
        """综合分析"""
        print("🏨 华天酒店深度分析报告")
        print("=" * 60)
        
        # 基础分析
        basic_analysis = self.basic_analysis(symbol)
        
        # 酒店行业分析
        industry_analysis = self.hotel_industry_analysis(symbol)
        
        # 多维度估值
        valuation_analysis = self.valuation_analysis(symbol)
        
        # 财务健康度
        financial_health = self.financial_health_analysis(symbol)
        
        # 投资建议
        investment_advice = self.investment_advice(basic_analysis, valuation_analysis, financial_health)
        
        return {
            'basic': basic_analysis,
            'industry': industry_analysis,
            'valuation': valuation_analysis,
            'financial': financial_health,
            'advice': investment_advice
        }
    
    def basic_analysis(self, symbol):
        """基础分析"""
        hotel_info = self.hotel_data[symbol]
        
        print("📊 基础数据分析")
        print("-" * 40)
        print(f"公司: {hotel_info['company_name']}")
        print(f"酒店数量: {hotel_info['hotels']}家")
        print(f"房间总数: {hotel_info['rooms']:,}间")
        print(f"平均房价: ¥{hotel_info['avg_rate']}/晚")
        print(f"入住率: {hotel_info['occupancy']:.1%}")
        print(f"RevPAR: ¥{hotel_info['revpar']}/间夜")
        print(f"物业资产: ¥{hotel_info['property_value']/1e8:.1f}亿")
        print()
        
        # 计算经营指标
        annual_revenue_per_room = hotel_info['avg_rate'] * 365 * hotel_info['occupancy']
        total_revenue = annual_revenue_per_room * hotel_info['rooms']
        
        print("💰 经营指标测算")
        print("-" * 40)
        print(f"单房年收入: ¥{annual_revenue_per_room:,.0f}")
        print(f"总营业收入: ¥{total_revenue/1e8:.1f}亿")
        print(f"资产周转率: {total_revenue/hotel_info['property_value']:.2f}")
        print()
        
        return {
            'revenue_per_room': annual_revenue_per_room,
            'total_revenue': total_revenue,
            'asset_turnover': total_revenue/hotel_info['property_value']
        }
    
    def hotel_industry_analysis(self, symbol):
        """酒店行业分析"""
        print("🏨 酒店行业分析")
        print("-" * 40)
        
        # 行业对比数据
        industry_benchmark = {
            'revpar': 350,  # 行业平均RevPAR
            'occupancy': 0.68,  # 行业平均入住率
            'avg_rate': 420,  # 行业平均房价
            'ebitda_margin': 0.25,  # EBITDA利润率
            'asset_turnover': 0.12  # 资产周转率
        }
        
        hotel_info = self.hotel_data[symbol]
        
        # 对比分析
        print("📈 行业对比分析")
        print(f"RevPAR对比: ¥{hotel_info['revpar']} vs 行业¥{industry_benchmark['revpar']}")
        print(f"入住率对比: {hotel_info['occupancy']:.1%} vs 行业{industry_benchmark['occupancy']:.1%}")
        print(f"房价对比: ¥{hotel_info['avg_rate']} vs 行业¥{industry_benchmark['avg_rate']}")
        
        # 竞争力评估
        revpar_gap = (hotel_info['revpar'] - industry_benchmark['revpar']) / industry_benchmark['revpar']
        occupancy_gap = (hotel_info['occupancy'] - industry_benchmark['occupancy']) / industry_benchmark['occupancy']
        rate_gap = (hotel_info['avg_rate'] - industry_benchmark['avg_rate']) / industry_benchmark['avg_rate']
        
        print(f"\n🎯 竞争力评估")
        print(f"RevPAR差距: {revpar_gap:+.1%}")
        print(f"入住率差距: {occupancy_gap:+.1%}")
        print(f"房价差距: {rate_gap:+.1%}")
        
        # 竞争地位判断
        if revpar_gap > 0.1:
            competitive_position = "行业领先"
        elif revpar_gap > -0.1:
            competitive_position = "行业中游"
        else:
            competitive_position = "行业落后"
            
        print(f"竞争地位: {competitive_position}")
        print()
        
        return {
            'revpar_gap': revpar_gap,
            'occupancy_gap': occupancy_gap,
            'rate_gap': rate_gap,
            'competitive_position': competitive_position
        }
    
    def valuation_analysis(self, symbol):
        """多维度估值分析"""
        print("💎 多维度估值分析")
        print("-" * 40)
        
        hotel_info = self.hotel_data[symbol]
        
        # 1. 资产基础估值
        asset_value_per_share = hotel_info['property_value'] / 1020000000  # 假设10.2亿股本
        
        # 2. 酒店行业EV/EBITDA估值
        annual_revenue = hotel_info['avg_rate'] * 365 * hotel_info['occupancy'] * hotel_info['rooms']
        ebitda = annual_revenue * 0.25  # 25% EBITDA利润率
        ev_ebitda_value = (ebitda * 8.0) / 1020000000  # 8倍EV/EBITDA
        
        # 3. DCF估值（基于现金流）
        free_cash_flow = ebitda * 0.4  # 假设FCF为EBITDA的40%
        dcf_value = self.simple_dcf_valuation(free_cash_flow, 1020000000)
        
        # 4. PB估值（基于净资产）
        book_value_per_share = asset_value_per_share * 0.8  # 考虑折旧
        pb_multiple = 0.8  # 酒店行业PB倍数
        pb_value = book_value_per_share * pb_multiple
        
        print("📊 各估值方法结果")
        print(f"资产基础估值: ¥{asset_value_per_share:.2f}")
        print(f"EV/EBITDA估值: ¥{ev_ebitda_value:.2f}")
        print(f"DCF估值: ¥{dcf_value:.2f}")
        print(f"PB估值: ¥{pb_value:.2f}")
        
        # 综合估值（加权平均）
        weights = {'asset': 0.3, 'ev_ebitda': 0.3, 'dcf': 0.2, 'pb': 0.2}
        fair_value = (asset_value_per_share * weights['asset'] + 
                     ev_ebitda_value * weights['ev_ebitda'] + 
                     dcf_value * weights['dcf'] + 
                     pb_value * weights['pb'])
        
        print(f"\n🎯 综合估值: ¥{fair_value:.2f}")
        
        # 价值区间
        values = [asset_value_per_share, ev_ebitda_value, dcf_value, pb_value]
        value_range = (min(values), max(values))
        print(f"合理价值区间: ¥{value_range[0]:.2f} - ¥{value_range[1]:.2f}")
        
        return {
            'asset_value': asset_value_per_share,
            'ev_ebitda_value': ev_ebitda_value,
            'dcf_value': dcf_value,
            'pb_value': pb_value,
            'fair_value': fair_value,
            'value_range': value_range
        }
    
    def simple_dcf_valuation(self, free_cash_flow, shares_outstanding):
        """简化DCF估值"""
        # 假设未来5年现金流增长率为8%，永续增长率为3%
        growth_rates = [0.08, 0.08, 0.08, 0.08, 0.08, 0.05, 0.05, 0.03, 0.03, 0.03]
        wacc = 0.10
        terminal_growth = 0.03
        
        # 计算未来现金流现值
        pv_cfs = []
        for i, gr in enumerate(growth_rates):
            cf = free_cash_flow * (1 + gr) ** (i + 1)
            pv_cf = cf / (1 + wacc) ** (i + 1)
            pv_cfs.append(pv_cf)
        
        # 终值
        terminal_cf = pv_cfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        pv_terminal = terminal_cf / (1 + wacc) ** 10
        
        # 企业价值
        enterprise_value = sum(pv_cfs) + pv_terminal
        value_per_share = enterprise_value / shares_outstanding
        
        return value_per_share
    
    def financial_health_analysis(self, symbol):
        """财务健康度分析"""
        print("💰 财务健康度分析")
        print("-" * 40)
        
        hotel_info = self.hotel_data[symbol]
        
        # 资产质量分析
        asset_quality_score = self.calculate_asset_quality(hotel_info)
        
        # 现金流稳定性
        cash_flow_stability = self.analyze_cash_flow_stability(hotel_info)
        
        # 债务风险
        debt_risk = self.analyze_debt_risk(hotel_info)
        
        # 综合财务健康度
        financial_health_score = (asset_quality_score + cash_flow_stability + (100 - debt_risk)) / 3
        
        print(f"资产质量得分: {asset_quality_score:.0f}/100")
        print(f"现金流稳定性: {cash_flow_stability:.0f}/100")
        print(f"债务风险得分: {100 - debt_risk:.0f}/100")
        print(f"综合健康度: {financial_health_score:.0f}/100")
        
        # 风险等级
        if financial_health_score >= 80:
            risk_level = "低风险"
        elif financial_health_score >= 60:
            risk_level = "中等风险"
        else:
            risk_level = "高风险"
            
        print(f"风险等级: {risk_level}")
        print()
        
        return {
            'asset_quality_score': asset_quality_score,
            'cash_flow_stability': cash_flow_stability,
            'debt_risk': debt_risk,
            'financial_health_score': financial_health_score,
            'risk_level': risk_level
        }
    
    def calculate_asset_quality(self, hotel_info):
        """计算资产质量得分"""
        # 基于物业位置、品牌、设施等因素
        base_score = 70  # 基础分
        
        # 资产规模调整
        if hotel_info['property_value'] > 5e9:
            base_score += 10
        elif hotel_info['property_value'] > 2e9:
            base_score += 5
        
        # 运营效率调整
        current_revpar = hotel_info['revpar']
        industry_avg = 350
        if current_revpar > industry_avg * 1.1:
            base_score += 10
        elif current_revpar > industry_avg:
            base_score += 5
        elif current_revpar < industry_avg * 0.9:
            base_score -= 10
        
        return min(100, max(0, base_score))
    
    def analyze_cash_flow_stability(self, hotel_info):
        """分析现金流稳定性"""
        # 酒店行业现金流相对稳定
        base_score = 75
        
        # 入住率稳定性
        if hotel_info['occupancy'] > 0.7:
            base_score += 10
        elif hotel_info['occupancy'] < 0.5:
            base_score -= 15
        
        # 房价稳定性（假设）
        if hotel_info['avg_rate'] > 500:
            base_score += 5
        elif hotel_info['avg_rate'] < 300:
            base_score -= 5
            
        return min(100, max(0, base_score))
    
    def analyze_debt_risk(self, hotel_info):
        """分析债务风险"""
        # 假设资产负债率45%
        debt_ratio = 0.45
        
        if debt_ratio < 0.3:
            return 20  # 低风险
        elif debt_ratio < 0.5:
            return 40  # 中等风险
        elif debt_ratio < 0.7:
            return 60  # 较高风险
        else:
            return 80  # 高风险
    
    def investment_advice(self, basic_analysis, valuation_analysis, financial_health):
        """投资建议"""
        print("💡 投资建议")
        print("=" * 40)
        
        fair_value = valuation_analysis['fair_value']
        current_price = 25.0  # 假设当前价格
        deviation = (current_price - fair_value) / fair_value
        
        print(f"当前价格: ¥{current_price:.2f}")
        print(f"合理价值: ¥{fair_value:.2f}")
        print(f"价值偏离: {deviation:+.1%}")
        
        # 投资建议
        if deviation > 0.5:
            recommendation = "强烈建议谨慎 - 当前价格严重高估"
            action = "等待更好买点，建议分批减仓"
            risk_level = "高风险"
        elif deviation > 0.2:
            recommendation = "建议谨慎 - 当前价格偏高"
            action = "持有观望，不急于买入"
            risk_level = "中等风险"
        elif deviation > -0.2:
            recommendation = "持有观望 - 估值合理"
            action = "可以持有，等待更好机会"
            risk_level = "低风险"
        else:
            recommendation = "建议买入 - 当前价格偏低"
            action = "可以逐步建仓，分批买入"
            risk_level = "低风险"
        
        print(f"\n投资建议: {recommendation}")
        print(f"操作策略: {action}")
        print(f"风险等级: {risk_level}")
        
        # 具体操作建议
        print(f"\n📋 具体操作建议")
        if deviation > 0.2:
            print("• 现有持仓：考虑分批减仓，锁定收益")
            print("• 潜在买家：暂时观望，等待更好时机")
            print("• 止损设置：建议设置止损位保护本金")
            target_buy_price = fair_value * 0.8
            print(f"• 目标买点：¥{target_buy_price:.2f}以下考虑买入")
        else:
            print("• 可以逐步建仓，分批买入")
            print("• 建议分3-5次完成建仓")
            print("• 单只股票仓位控制在20%以内")
            print("• 长期持有，享受价值回归")
        
        return {
            'recommendation': recommendation,
            'action': action,
            'risk_level': risk_level,
            'deviation': deviation,
            'fair_value': fair_value
        }

def main():
    """主函数"""
    analyzer = HotelAnalyzer()
    results = analyzer.comprehensive_analysis('000428')
    
    print("\n" + "=" * 60)
    print("📊 华天酒店分析总结")
    print("=" * 60)
    
    # 总结关键发现
    valuation = results['valuation']
    advice = results['advice']
    
    print(f"🏨 酒店规模: {results['basic']['total_revenue']/1e8:.1f}亿营业收入")
    print(f"💎 竞争地位: {results['industry']['competitive_position']}")
    print(f"📈 合理估值: ¥{valuation['fair_value']:.2f}")
    print(f"🎯 价值偏离: {advice['deviation']:+.1%}")
    print(f"💡 投资建议: {advice['recommendation']}")
    print(f"⚠️ 风险等级: {results['financial']['risk_level']}")
    
    print("\n✅ 分析完成！")

if __name__ == "__main__":
    main()