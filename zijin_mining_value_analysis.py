#!/usr/bin/env python3
"""
紫金矿业（601899）内在价值分析
从价值投资角度评估真实价值走向
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ValueInvestingAnalyzer:
    """价值投资分析器"""
    
    def __init__(self, symbol="601899"):
        self.symbol = symbol
        self.name = "紫金矿业"
        
    def get_financial_data(self):
        """获取财务数据"""
        financial_data = {}
        
        try:
            # 1. 获取主要财务指标
            print("正在获取财务数据...")
            
            # 财务摘要
            financial_abstract = ak.stock_financial_abstract(symbol=self.symbol)
            if not financial_abstract.empty:
                latest = financial_abstract.iloc[0]
                financial_data['financial_summary'] = {
                    '报告期': latest.get('报告期', ''),
                    '基本每股收益': latest.get('基本每股收益', 0),
                    '每股净资产': latest.get('每股净资产', 0),
                    '净资产收益率': latest.get('净资产收益率', 0),
                    '总资产收益率': latest.get('总资产收益率', 0),
                    '毛利率': latest.get('销售毛利率', 0),
                    '净利率': latest.get('销售净利率', 0),
                    '资产负债率': latest.get('资产负债率', 0),
                    '营业收入': latest.get('营业收入', 0),
                    '营业利润': latest.get('营业利润', 0),
                    '净利润': latest.get('净利润', 0)
                }
            
            # 2. 获取资产负债表
            balance_sheet = ak.stock_balance_sheet(stock=self.symbol)
            if not balance_sheet.empty:
                latest_bs = balance_sheet.iloc[0]
                financial_data['balance_sheet'] = {
                    '资产总计': latest_bs.get('资产总计', 0),
                    '负债合计': latest_bs.get('负债合计', 0),
                    '所有者权益': latest_bs.get('所有者权益', 0),
                    '流动资产': latest_bs.get('流动资产', 0),
                    '流动负债': latest_bs.get('流动负债', 0),
                    '货币资金': latest_bs.get('货币资金', 0),
                    '存货': latest_bs.get('存货', 0),
                    '固定资产': latest_bs.get('固定资产', 0)
                }
            
            # 3. 获取现金流量表
            cash_flow = ak.stock_cash_flow_sheet(stock=self.symbol)
            if not cash_flow.empty:
                latest_cf = cash_flow.iloc[0]
                financial_data['cash_flow'] = {
                    '经营活动现金流': latest_cf.get('经营活动产生的现金流量净额', 0),
                    '投资活动现金流': latest_cf.get('投资活动产生的现金流量净额', 0),
                    '筹资活动现金流': latest_cf.get('筹资活动产生的现金流量净额', 0),
                    '现金净增加额': latest_cf.get('现金及现金等价物净增加额', 0)
                }
            
            # 4. 获取历史财务数据（5年）
            financial_report = ak.stock_financial_report_sina(stock=self.symbol, symbol="业绩报表")
            if not financial_report.empty:
                financial_data['historical_performance'] = []
                for _, row in financial_report.head(5).iterrows():
                    financial_data['historical_performance'].append({
                        '报告期': row.get('报告期', ''),
                        '营业收入': row.get('营业收入', 0),
                        '营业利润': row.get('营业利润', 0),
                        '净利润': row.get('净利润', 0),
                        '营业收入同比增长': row.get('营业收入同比增长', 0),
                        '净利润同比增长': row.get('净利润同比增长', 0)
                    })
            
            # 5. 获取估值指标
            stock_info = ak.stock_individual_info_em(symbol=self.symbol)
            if not stock_info.empty:
                info_dict = dict(zip(stock_info['item'], stock_info['value']))
                financial_data['valuation'] = {
                    '市盈率': info_dict.get('市盈率', 0),
                    '市净率': info_dict.get('市净率', 0),
                    '总市值': info_dict.get('总市值', 0),
                    '流通市值': info_dict.get('流通市值', 0),
                    '每股收益': info_dict.get('每股收益', 0),
                    '每股净资产': info_dict.get('每股净资产', 0)
                }
            
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            
        return financial_data
    
    def calculate_dcf_value(self, financial_data, wacc=0.10, g=0.03):
        """DCF现金流折现估值"""
        print("\n正在进行DCF现金流折现估值...")
        
        dcf_result = {}
        
        try:
            # 获取最新财务数据
            if 'cash_flow' in financial_data:
                operating_cash_flow = financial_data['cash_flow'].get('经营活动现金流', 0)
            else:
                operating_cash_flow = 20000000000  # 默认值200亿
            
            if 'financial_summary' in financial_data:
                net_profit = financial_data['financial_summary'].get('净利润', operating_cash_flow * 0.6)
            else:
                net_profit = operating_cash_flow * 0.6
            
            # 获取股本信息
            shares = 26470000000  # 紫金矿业总股本约264.7亿股
            
            # DCF计算基础参数
            current_fcf = operating_cash_flow  # 自由现金流
            shares_outstanding = shares
            
            # 未来10年现金流预测（考虑矿业周期性）
            years = 10
            growth_rates = [0.15, 0.12, 0.10, 0.08, 0.06, 0.05, 0.04, 0.04, 0.03, 0.03]  # 递减增长率
            
            print(f"基础自由现金流: ¥{current_fcf/1e8:.1f}亿元")
            print(f"总股本: {shares_outstanding/1e8:.1f}亿股")
            print(f"WACC折现率: {wacc:.1%}")
            print(f"永续增长率: {g:.1%}")
            
            # 计算未来现金流
            future_cfs = []
            for i, gr in enumerate(growth_rates):
                cf = current_fcf * (1 + gr) ** (i + 1)
                pv_cf = cf / (1 + wacc) ** (i + 1)
                future_cfs.append({
                    'year': i + 1,
                    'cash_flow': cf,
                    'present_value': pv_cf,
                    'growth_rate': gr
                })
                print(f"第{i+1}年: 现金流¥{cf/1e8:.1f}亿, 现值¥{pv_cf/1e8:.1f}亿")
            
            # 计算终值
            terminal_cf = future_cfs[-1]['cash_flow'] * (1 + g)
            terminal_value = terminal_cf / (wacc - g)
            pv_terminal = terminal_value / (1 + wacc) ** years
            
            print(f"\n终值计算:")
            print(f"第11年现金流: ¥{terminal_cf/1e8:.1f}亿")
            print(f"终值: ¥{terminal_value/1e8:.1f}亿")
            print(f"终值现值: ¥{pv_terminal/1e8:.1f}亿")
            
            # 企业价值
            enterprise_value = sum(cf['present_value'] for cf in future_cfs) + pv_terminal
            
            # 股权价值（假设净负债为0，保守估计）
            net_debt = 0  # 可以调整
            equity_value = enterprise_value - net_debt
            
            # 每股价值
            value_per_share = equity_value / shares_outstanding
            
            # 当前市场价格
            current_data = ak.stock_zh_a_spot_em()
            current_price = current_data[current_data['代码'] == '601899']['最新价'].iloc[0] if not current_data.empty else 25.0
            
            dcf_result = {
                'enterprise_value': enterprise_value,
                'equity_value': equity_value,
                'value_per_share': value_per_share,
                'current_price': current_price,
                'upside_downside': (value_per_share - current_price) / current_price,
                'future_cash_flows': future_cfs,
                'terminal_value': terminal_value,
                'pv_terminal': pv_terminal,
                'assumptions': {
                    'wacc': wacc,
                    'terminal_growth': g,
                    'current_fcf': current_fcf
                }
            }
            
            print(f"\nDCF估值结果:")
            print(f"企业价值: ¥{enterprise_value/1e8:.1f}亿元")
            print(f"股权价值: ¥{equity_value/1e8:.1f}亿元") 
            print(f"每股内在价值: ¥{value_per_share:.2f}")
            print(f"当前股价: ¥{current_price:.2f}")
            print(f"估值偏差: {(value_per_share - current_price) / current_price:.1%}")
            
            # 敏感性分析
            print(f"\n敏感性分析（每股价值）:")
            print(f"WACC\\增长率 | 1.0%  | 2.0%  | 3.0%  | 4.0%  | 5.0%")
            print("-" * 50)
            for w in [0.08, 0.09, 0.10, 0.11, 0.12]:
                row = f"{w:.1%}      |"
                for g_test in [0.01, 0.02, 0.03, 0.04, 0.05]:
                    # 简化计算
                    if w > g_test:
                        tv_test = terminal_cf / (w - g_test)
                        pv_tv_test = tv_test / (1 + w) ** years
                        ev_test = sum(cf['present_value'] for cf in future_cfs) + pv_tv_test
                        value_test = (ev_test - net_debt) / shares_outstanding
                        row += f" {value_test:.2f} |"
                    else:
                        row += "  N/A  |"
                print(row)
            
        except Exception as e:
            print(f"DCF计算失败: {e}")
            dcf_result = {'error': str(e)}
            
        return dcf_result
    
    def calculate_resource_value(self):
        """资源价值评估（矿业特有）"""
        print("\n正在进行资源价值评估...")
        
        resource_result = {}
        
        try:
            # 紫金矿业主要资源储量（基于公开信息）
            resources = {
                'gold': {'reserves': 3000, 'unit': '吨', 'price_per_unit': 450000000, 'cost_per_unit': 250000000},  # 3000吨黄金
                'copper': {'reserves': 75000000, 'unit': '吨', 'price_per_unit': 70000, 'cost_per_unit': 40000},    # 7500万吨铜
                'zinc': {'reserves': 10000000, 'unit': '吨', 'price_per_unit': 25000, 'cost_per_unit': 15000},     # 1000万吨锌
                'silver': {'reserves': 10000, 'unit': '吨', 'price_per_unit': 5000000, 'cost_per_unit': 3000000}, # 1万吨白银
            }
            
            print("资源储量情况:")
            total_resource_value = 0
            
            for resource, data in resources.items():
                reserves = data['reserves']
                price = data['price_per_unit']
                cost = data['cost_per_unit']
                
                # 计算资源总价值（考虑开采成本）
                gross_value = reserves * price
                total_cost = reserves * cost
                net_value = gross_value - total_cost
                
                # 考虑开采率（70%）和时间价值（折现50%）
                recovery_rate = 0.7  # 开采回收率
                discount_factor = 0.5  # 时间价值折现
                adjusted_value = net_value * recovery_rate * discount_factor
                
                resource_result[resource] = {
                    'reserves': reserves,
                    'unit': data['unit'],
                    'gross_value': gross_value,
                    'total_cost': total_cost,
                    'net_value': net_value,
                    'adjusted_value': adjusted_value,
                    'current_price': price,
                    'extraction_cost': cost
                }
                
                total_resource_value += adjusted_value
                
                print(f"{resource.upper()}: {reserves:,}{data['unit']}")
                print(f"  总价值: ¥{gross_value/1e12:.2f}万亿元")
                print(f"  开采成本: ¥{total_cost/1e12:.2f}万亿元") 
                print(f"  净价值: ¥{net_value/1e12:.2f}万亿元")
                print(f"  调整后价值: ¥{adjusted_value/1e12:.2f}万亿元")
                print()
            
            # 每股资源价值
            shares = 26470000000  # 总股本
            resource_value_per_share = total_resource_value / shares
            
            resource_result['summary'] = {
                'total_resource_value': total_resource_value,
                'resource_value_per_share': resource_value_per_share,
                'shares_outstanding': shares
            }
            
            print(f"资源价值总计: ¥{total_resource_value/1e12:.2f}万亿元")
            print(f"每股资源价值: ¥{resource_value_per_share:.2f}")
            
        except Exception as e:
            print(f"资源价值评估失败: {e}")
            resource_result = {'error': str(e)}
            
        return resource_result
    
    def calculate_pb_roe_value(self, financial_data):
        """PB-ROE估值分析"""
        print("\n正在进行PB-ROE估值分析...")
        
        pb_roe_result = {}
        
        try:
            # 获取关键指标
            if 'financial_summary' in financial_data:
                roe = financial_data['financial_summary'].get('净资产收益率', 0.15)  # 默认值15%
                pb = financial_data['valuation'].get('市净率', 1.5)  # 默认值1.5
                eps = financial_data['financial_summary'].get('基本每股收益', 1.0)
                bvps = financial_data['financial_summary'].get('每股净资产', 10.0)
            else:
                roe = 0.15
                pb = 1.5
                eps = 1.0
                bvps = 10.0
            
            # 合理PB计算（基于ROE）
            # 公式: 合理PB = ROE / 要求回报率
            required_return = 0.12  # 12%要求回报率
            fair_pb = roe / required_return
            
            # 合理股价计算
            fair_price_pb_roe = fair_pb * bvps
            
            # 行业对比（有色金属行业平均）
            industry_avg_roe = 0.10  # 行业平均ROE 10%
            industry_avg_pb = 1.8    # 行业平均PB 1.8
            
            # PB-ROE回归分析
            # 如果ROE > 行业平均，应该享受PB溢价
            if roe > industry_avg_roe:
                premium = (roe - industry_avg_roe) * 10  # 每1%ROE溢价10%PB
                adjusted_pb = industry_avg_pb * (1 + premium)
            else:
                discount = (industry_avg_roe - roe) * 8   # 每1%ROE折价8%PB
                adjusted_pb = industry_avg_pb * (1 - discount)
            
            adjusted_price = adjusted_pb * bvps
            
            pb_roe_result = {
                'current_roe': roe,
                'current_pb': pb,
                'fair_pb': fair_pb,
                'current_bvps': bvps,
                'fair_price_pb_roe': fair_price_pb_roe,
                'industry_avg_roe': industry_avg_roe,
                'industry_avg_pb': industry_avg_pb,
                'adjusted_pb': adjusted_pb,
                'adjusted_price': adjusted_price
            }
            
            print(f"当前ROE: {roe:.1%}")
            print(f"当前PB: {pb:.2f}")
            print(f"每股净资产: ¥{bvps:.2f}")
            print(f"基于ROE的合理PB: {fair_pb:.2f}")
            print(f"PB-ROE合理股价: ¥{fair_price_pb_roe:.2f}")
            print(f"行业平均ROE: {industry_avg_roe:.1%}")
            print(f"行业平均PB: {industry_avg_pb:.2f}")
            print(f"调整后市盈率: {adjusted_pb:.2f}")
            print(f"调整后股价: ¥{adjusted_price:.2f}")
            
            # ROE持续性分析
            print(f"\nROE质量分析:")
            if roe > 0.15:
                print("🟢 ROE优秀 (>15%)，盈利能力强")
            elif roe > 0.10:
                print("🟡 ROE良好 (10%-15%)，盈利能力尚可")
            else:
                print("🔴 ROE偏低 (<10%)，盈利能力较弱")
            
        except Exception as e:
            print(f"PB-ROE分析失败: {e}")
            pb_roe_result = {'error': str(e)}
            
        return pb_roe_result
    
    def analyze_gold_price_impact(self):
        """分析黄金价格对价值的影响"""
        print("\n分析黄金价格影响...")
        
        gold_impact = {}
        
        try:
            # 获取黄金价格数据
            gold_price = ak.futures_global_commodity_hist(symbol="伦敦黄金")
            if not gold_price.empty:
                current_gold_price = gold_price.iloc[-1]['收盘']
                gold_52w_high = gold_price['最高'].max()
                gold_52w_low = gold_price['最低'].min()
                
                # 黄金价格相对位置
                gold_price_position = (current_gold_price - gold_52w_low) / (gold_52w_high - gold_52w_low)
                
                # 黄金价格对紫金矿业的影响系数（基于历史相关性）
                sensitivity = 0.7  # 70%的相关性
                
                # 计算黄金价格对盈利的影响
                if gold_price_position > 0.7:
                    earnings_impact = 0.15  # 高金价提升15%盈利
                elif gold_price_position > 0.3:
                    earnings_impact = 0.05  # 中等金价提升5%盈利
                else:
                    earnings_impact = -0.1  # 低金价降低10%盈利
                
                gold_impact = {
                    'current_gold_price': current_gold_price,
                    'gold_52w_high': gold_52w_high,
                    'gold_52w_low': gold_52w_low,
                    'gold_price_position': gold_price_position,
                    'sensitivity': sensitivity,
                    'earnings_impact': earnings_impact
                }
                
                print(f"当前黄金价格: ${current_gold_price:.2f}/盎司")
                print(f"52周最高价: ${gold_52w_high:.2f}/盎司")
                print(f"52周最低价: ${gold_52w_low:.2f}/盎司")
                print(f"价格位置: {gold_price_position:.1%}")
                print(f"对盈利影响: {earnings_impact:+.1%}")
                
                if gold_price_position > 0.7:
                    print("🟢 黄金价格处于高位，利好紫金矿业")
                elif gold_price_position > 0.3:
                    print("🟡 黄金价格处于中等位置，影响中性")
                else:
                    print("🔴 黄金价格处于低位，对紫金矿业不利")
                    
        except Exception as e:
            print(f"黄金价格影响分析失败: {e}")
            gold_impact = {'error': str(e)}
            
        return gold_impact
    
    def comprehensive_value_analysis(self):
        """综合价值分析"""
        print("=" * 60)
        print("紫金矿业内在价值综合分析")
        print("=" * 60)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 获取基础数据
        financial_data = self.get_financial_data()
        
        # 各种估值方法
        dcf_result = self.calculate_dcf_value(financial_data)
        resource_result = self.calculate_resource_value()
        pb_roe_result = self.calculate_pb_roe_value(financial_data)
        gold_impact = self.analyze_gold_price_impact()
        
        # 获取当前股价
        try:
            current_data = ak.stock_zh_a_spot_em()
            current_price = current_data[current_data['代码'] == '601899']['最新价'].iloc[0] if not current_data.empty else 25.02
        except:
            current_price = 25.02
        
        # 综合价值计算（加权平均）
        print("\n" + "=" * 40)
        print("综合价值评估")
        print("=" * 40)
        
        # 各方法估值结果
        values = []
        weights = []
        
        # DCF估值 (权重40%)
        if 'value_per_share' in dcf_result:
            dcf_value = dcf_result['value_per_share']
            values.append(dcf_value)
            weights.append(0.4)
            print(f"DCF估值: ¥{dcf_value:.2f} (权重40%)")
        
        # 资源价值 (权重30%)
        if 'resource_value_per_share' in resource_result:
            resource_value = resource_result['resource_value_per_share']
            values.append(resource_value)
            weights.append(0.3)
            print(f"资源价值: ¥{resource_value:.2f} (权重30%)")
        
        # PB-ROE估值 (权重20%)
        if 'adjusted_price' in pb_roe_result:
            pb_roe_value = pb_roe_result['adjusted_price']
            values.append(pb_roe_value)
            weights.append(0.2)
            print(f"PB-ROE估值: ¥{pb_roe_value:.2f} (权重20%)")
        
        # 当前净资产 (权重10%)
        if 'financial_summary' in financial_data:
            bvps = financial_data['financial_summary'].get('每股净资产', 10.0)
            values.append(bvps)
            weights.append(0.1)
            print(f"净资产价值: ¥{bvps:.2f} (权重10%)")
        
        # 计算加权平均内在价值
        if values and weights:
            fair_value = sum(v * w for v, w in zip(values, weights))
            total_weight = sum(weights)
            fair_value = fair_value / total_weight if total_weight > 0 else fair_value
        else:
            fair_value = current_price
        
        # 黄金价格调整
        if 'earnings_impact' in gold_impact:
            gold_adjustment = 1 + gold_impact['earnings_impact']
            fair_value_gold = fair_value * gold_adjustment
        else:
            fair_value_gold = fair_value
        
        print(f"\n综合内在价值: ¥{fair_value:.2f}")
        print(f"黄金价格调整后: ¥{fair_value_gold:.2f}")
        print(f"当前市场价格: ¥{current_price:.2f}")
        print(f"估值偏差: {(fair_value_gold - current_price) / current_price:.1%}")
        
        # 价值走向判断
        print(f"\n价值走向分析:")
        if fair_value_gold > current_price * 1.15:
            print("🟢 价值被严重低估 - 建议买入")
            value_trend = "严重低估"
        elif fair_value_gold > current_price * 1.05:
            print("🟡 价值被轻度低估 - 可以考虑买入")
            value_trend = "轻度低估"
        elif fair_value_gold < current_price * 0.95:
            print("🔴 价值被高估 - 建议谨慎")
            value_trend = "高估"
        else:
            print("⚪ 价值合理 - 持有观望")
            value_trend = "合理"
        
        # 风险因素分析
        print(f"\n主要风险因素:")
        print("1. 金属价格波动风险 - 黄金价格大幅波动")
        print("2. 汇率变动风险 - 海外业务汇率影响") 
        print("3. 开采成本上升 - 能源、人工成本增加")
        print("4. 环保政策风险 - 环保标准提高增加成本")
        print("5. 地缘政治风险 - 海外矿山政治稳定性")
        
        # 价值支撑因素
        print(f"\n价值支撑因素:")
        print("1. 资源储量丰富 - 黄金、铜、锌等金属储量充足")
        print("2. 行业龙头地位 - 成本控制和规模优势明显")
        print("3. 国际化布局 - 分散风险，获取优质资源")
        print("4. 技术进步 - 开采效率提升，成本下降")
        print("5. 通胀对冲 - 黄金资源对抗通胀")
        
        return {
            'financial_data': financial_data,
            'dcf_valuation': dcf_result,
            'resource_valuation': resource_result,
            'pb_roe_valuation': pb_roe_result,
            'gold_impact': gold_impact,
            'fair_value': fair_value,
            'fair_value_gold_adjusted': fair_value_gold,
            'current_price': current_price,
            'value_trend': value_trend,
            'valuation_gap': (fair_value_gold - current_price) / current_price
        }

def main():
    """主函数"""
    print("紫金矿业（601899）内在价值分析系统")
    print("=" * 60)
    
    # 创建分析器
    analyzer = ValueInvestingAnalyzer("601899")
    
    # 执行综合分析
    result = analyzer.comprehensive_value_analysis()
    
    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    main()