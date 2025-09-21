#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国稀土(000831)阶梯分析Agent
调用指令：【阶梯分析启动】
功能：提供中国稀土的阶梯定投策略、技术分析和投资建议
"""

import json
from datetime import datetime

class ChinaRareEarthAgent:
    """中国稀土阶梯分析Agent"""
    
    def __init__(self):
        # 基础数据配置
        self.base_data = {
            "stock_code": "000831",
            "stock_name": "中国稀土",
            "current_price": 56.47,  # 2025年9月12日收盘价
            "market_cap": 600,  # 亿元
            "pe_ratio": 134.0,  # 2025E PE
            "roe": 3.42,  # 2025H1
            "gross_margin": 13.37,  # 2025H1
        }
        
        # 阶梯定投档位配置
        self.tier_system = {
            "tier_1": {"price_range": [15.0, 18.0], "allocation": 35, "status": "未触发", "logic": "极端熊市/系统性风险"},
            "tier_2": {"price_range": [18.0, 21.0], "allocation": 25, "status": "未触发", "logic": "深度价值区间"},
            "tier_3": {"price_range": [21.0, 24.0], "allocation": 20, "status": "未触发", "logic": "合理偏低估值"},
            "tier_4": {"price_range": [24.0, 30.0], "allocation": 15, "status": "当前区域", "logic": "谨慎建仓区间"},
            "tier_5": {"price_range": [30.0, 36.0], "allocation": 5, "status": "未触发", "logic": "趋势确认加仓"},
            "tier_6": {"price_range": [36.0, 42.0], "allocation": 0, "status": "目标位", "logic": "分批止盈"},
            "tier_7": {"price_range": [42.0, 50.0], "allocation": -20, "status": "减仓区", "logic": "每涨5%减仓20%"},
        }
        
        # 核心投资逻辑
        self.investment_logic = {
            "确定性评级": "★★★★★",
            "战略地位": "中重稀土唯一上市平台，政策护城河最深",
            "核心优势": ["控制全国70%+中重稀土配额", "稀土出口管制+配额制双保险", "军工航天不可替代"],
            "成长驱动": ["新能源车需求爆发", "人形机器人量产元年", "风电永磁电机渗透率提升"],
            "政策红利": ["2025年配额制供给刚性", "七类中重稀土出口管制", "央企主导资源整合"],
        }
        
        # 风险控制系统
        self.risk_control = {
            "仓位限制": {"current_max": 15, "target_max": 30, "extreme_max": 50},
            "止损位": 36.0,  # 技术支撑位
            "目标位": [48.0, 53.0],  # 机构一致目标价区间
            "关键风险": [
                "估值泡沫：当前PE 134倍，已透支2026年业绩",
                "价格风险：稀土现货指数245万/吨，低于公司套保价280万/吨",
                "技术高位：56.47元处于历史高位，技术回调压力大",
                "需求证伪：新能源车库存63天，磁材订单环比下滑",
            ],
        }
        
        # 操作建议
        self.operation_advice = {
            "当前策略": "等待更好买点，绝不追高",
            "建议仓位": "0-15%（仅限第4档）",
            "买入区间": "36-42元（可重仓布局）",
            "卖出区间": "48-53元（分批止盈）",
            "执行原则": "耐心等待比匆忙买入更重要",
        }

    def get_current_status(self):
        """获取当前状态"""
        current_tier = None
        for tier_name, tier_data in self.tier_system.items():
            if tier_data["status"] == "当前区域":
                current_tier = tier_name
                break
        
        return {
            "当前价格": self.base_data["current_price"],
            "所处档位": current_tier,
            "建议仓位": self.tier_system[current_tier]["allocation"] if current_tier else 0,
            "当前策略": self.operation_advice["当前策略"],
            "确定性评级": self.investment_logic["确定性评级"],
        }

    def get_tier_analysis(self, price=None):
        """获取阶梯分析"""
        if price is None:
            price = self.base_data["current_price"]
        
        current_tier = None
        for tier_name, tier_data in self.tier_system.items():
            if tier_data["price_range"][0] <= price <= tier_data["price_range"][1]:
                current_tier = tier_name
                break
        
        if current_tier:
            tier_info = self.tier_system[current_tier]
            return {
                "档位": current_tier,
                "价格区间": f"{tier_info['price_range'][0]}-{tier_info['price_range'][1]}元",
                "仓位分配": f"{tier_info['allocation']}%",
                "操作逻辑": tier_info["logic"],
                "状态": tier_info["status"],
            }
        else:
            return {"错误": "价格超出分析范围"}

    def get_investment_logic(self):
        """获取投资逻辑"""
        return {
            "战略地位": self.investment_logic["战略地位"],
            "核心优势": self.investment_logic["核心优势"],
            "成长驱动": self.investment_logic["成长驱动"],
            "政策红利": self.investment_logic["政策红利"],
        }

    def get_risk_analysis(self):
        """获取风险分析"""
        return {
            "仓位限制": self.risk_control["仓位限制"],
            "止损位": self.risk_control["止损位"],
            "目标位": self.risk_control["目标位"],
            "关键风险": self.risk_control["关键风险"],
        }

    def get_operation_advice(self):
        """获取操作建议"""
        return self.operation_advice

    def generate_investment_report(self):
        """生成完整投资报告"""
        current_status = self.get_current_status()
        tier_analysis = self.get_tier_analysis()
        investment_logic = self.get_investment_logic()
        risk_analysis = self.get_risk_analysis()
        operation_advice = self.get_operation_advice()
        
        report = f"""
# 🎯 中国稀土（000831）阶梯分析报告

## 📊 当前状态
- **当前价格**: {current_status['当前价格']}元
- **所处档位**: {current_status.get('所处档位', '分析中')}
- **建议仓位**: {current_status['建议仓位']}%
- **当前策略**: {current_status['当前策略']}
- **确定性评级**: {current_status['确定性评级']}

## 🏗️ 阶梯分析
- **档位**: {tier_analysis['档位']}
- **价格区间**: {tier_analysis['价格区间']}
- **仓位分配**: {tier_analysis['仓位分配']}
- **操作逻辑**: {tier_analysis['操作逻辑']}
- **状态**: {tier_analysis['状态']}

## 💎 投资逻辑
- **战略地位**: {investment_logic['战略地位']}
- **核心优势**: {', '.join(investment_logic['核心优势'])}
- **成长驱动**: {', '.join(investment_logic['成长驱动'])}
- **政策红利**: {', '.join(investment_logic['政策红利'])}

## 🛡️ 风险控制
- **仓位限制**: 当前最大{risk_analysis['仓位限制']['current_max']}%，目标最大{risk_analysis['仓位限制']['target_max']}%
- **止损位**: {risk_analysis['止损位']}元
- **目标位**: {risk_analysis['目标位'][0]}-{risk_analysis['目标位'][1]}元
- **关键风险**: {', '.join(risk_analysis['关键风险'][:2])}

## ⚡ 操作建议
- **当前策略**: {operation_advice['当前策略']}
- **建议仓位**: {operation_advice['建议仓位']}
- **买入区间**: {operation_advice['买入区间']}
- **卖出区间**: {operation_advice['卖出区间']}
- **执行原则**: {operation_advice['执行原则']}
        """
        return report.strip()

# 创建Agent实例
china_rare_earth_agent = ChinaRareEarthAgent()

def main():
    """主函数 - 阶梯分析启动"""
    print("【阶梯分析启动】中国稀土(000831)分析系统")
    print("=" * 60)
    
    # 获取完整分析报告
    report = china_rare_earth_agent.generate_investment_report()
    print(report)
    
    print("\n" + "=" * 60)
    print("💡 使用说明：")
    print("1. 当前价格56.47元处于高位，建议等待36-42元区间再布局")
    print("2. 严格按阶梯系统执行，绝不追高")
    print("3. 每月复盘策略执行情况")
    print("4. 设置价格预警：36元（止损）、42元（重仓）、48元（减仓）")

if __name__ == "__main__":
    # 当执行【阶梯分析启动】时运行
    main()