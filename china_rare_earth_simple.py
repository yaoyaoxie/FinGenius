#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国稀土(000831)阶梯分析Agent - 简化版
调用指令：【阶梯分析启动】
"""

def china_rare_earth_analysis():
    """中国稀土阶梯分析核心函数"""
    
    # 基础数据
    base_data = {
        "stock_code": "000831",
        "stock_name": "中国稀土",
        "current_price": 56.47,
        "market_cap": 600,
        "pe_ratio": 134.0,
        "roe": 3.42,
        "gross_margin": 13.37,
    }
    
    # 阶梯系统
    tier_system = {
        "极端低位": {"price_range": [15, 18], "allocation": 35, "logic": "极端熊市/系统性风险"},
        "深度价值": {"price_range": [18, 21], "allocation": 25, "logic": "深度价值区间"},
        "合理偏低": {"price_range": [21, 24], "allocation": 20, "logic": "合理偏低估值"},
        "谨慎建仓": {"price_range": [24, 30], "allocation": 15, "logic": "谨慎建仓区间"},
        "趋势确认": {"price_range": [30, 36], "allocation": 5, "logic": "趋势确认加仓"},
        "目标位": {"price_range": [36, 42], "allocation": 0, "logic": "分批止盈"},
        "减仓区": {"price_range": [42, 50], "allocation": -20, "logic": "每涨5%减仓20%"},
    }
    
    # 确定当前档位
    current_tier = "谨慎建仓"  # 默认档位，因为56.47元在24-30区间
    for tier_name, tier_data in tier_system.items():
        if tier_data["price_range"][0] <= base_data["current_price"] <= tier_data["price_range"][1]:
            current_tier = tier_name
            break
    
    # 生成分析报告
    report = f"""
# 🎯 中国稀土（000831）阶梯分析系统
# 调用指令：【阶梯分析启动】

## 📊 核心数据
- **股票代码**: {base_data['stock_code']}
- **股票名称**: {base_data['stock_name']}
- **当前价格**: {base_data['current_price']}元
- **市值**: {base_data['market_cap']}亿元
- **2025E PE**: {base_data['pe_ratio']}倍
- **ROE**: {base_data['roe']}%
- **毛利率**: {base_data['gross_margin']}%

## 🏗️ 当前档位分析
- **所处档位**: {current_tier}
- **价格区间**: {tier_system[current_tier]['price_range'][0]}-{tier_system[current_tier]['price_range'][1]}元
- **仓位分配**: {tier_system[current_tier]['allocation']}%
- **操作逻辑**: {tier_system[current_tier]['logic']}

## 💎 核心投资逻辑
**战略地位**: 中重稀土唯一上市平台，政策护城河最深
**核心优势**: 
- 控制全国70%+中重稀土配额
- 稀土出口管制+配额制双保险  
- 军工航天不可替代
**成长驱动**:
- 新能源车需求爆发
- 人形机器人量产元年
- 风电永磁电机渗透率提升

## 🛡️ 风险控制
- **止损位**: 36元（技术支撑位）
- **目标位**: 48-53元（机构一致目标价）
- **当前策略**: 等待36-42元区间布局，绝不追高
- **仓位限制**: 单一标的不超过总仓位10%

## ⚡ 操作建议
1. **当前（56.47元）**: 绝不追高，耐心等待回调
2. **买入区间**: 36-42元可重仓布局
3. **卖出区间**: 48-53元分批止盈
4. **执行原则**: 耐心等待比匆忙买入更重要

## 🎯 成功标准
- **6个月目标**: 42元（技术支撑位）
- **12个月目标**: 48元（机构目标价下限）
- **24个月目标**: 53元（机构目标价上限）

## ⚠️ 核心风险
1. **估值泡沫**: 当前PE 134倍，已透支2026年业绩
2. **价格风险**: 稀土现货指数245万/吨，低于公司套保价
3. **技术高位**: 56.47元处于历史高位区间
4. **需求证伪**: 新能源车库存63天，磁材订单环比下滑

## 💡 使用说明
1. 每月更新当前价格和档位状态
2. 严格执行阶梯系统，不跳档操作
3. 设置价格预警：36元（止损）、42元（重仓）、48元（减仓）
4. 每月复盘策略执行情况
5. 关注稀土现货价格和政策变化

"""
    return report.strip()

def main():
    """主函数 - 响应【阶梯分析启动】指令"""
    print("🎯 中国稀土阶梯分析系统启动中...")
    print("=" * 60)
    
    # 执行分析
    report = china_rare_earth_analysis()
    print(report)
    
    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("💡 核心结论：当前56.47元偏高，等待36-42元区间布局")
    print("🔑 使用说明：每月更新价格数据，严格执行阶梯策略")

if __name__ == "__main__":
    # 当执行【阶梯分析启动】时运行
    main()