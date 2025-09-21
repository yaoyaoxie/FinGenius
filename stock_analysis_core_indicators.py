#!/usr/bin/env python3
"""
股票分析核心指标体系梳理
基于AKShare获取最新数据进行分析
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockCoreIndicators:
    """股票核心指标分析器"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.stock_code = self._format_stock_code(symbol)
        
    def _format_stock_code(self, symbol: str) -> str:
        """格式化股票代码"""
        # 处理不同格式的股票代码
        symbol = symbol.replace('.', '').replace('sh', '').replace('sz', '')
        if len(symbol) == 6 and symbol.isdigit():
            return symbol
        else:
            raise ValueError(f"无效的股票代码: {symbol}")
    
    def get_price_data(self, period: str = "1y") -> pd.DataFrame:
        """获取股价数据"""
        try:
            # 获取股票历史数据
            stock_data = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily")
            stock_data['日期'] = pd.to_datetime(stock_data['日期'])
            stock_data = stock_data.sort_values('日期')
            
            # 设置时间范围
            if period == "1y":
                start_date = datetime.now() - timedelta(days=365)
            elif period == "6m":
                start_date = datetime.now() - timedelta(days=180)
            elif period == "3m":
                start_date = datetime.now() - timedelta(days=90)
            else:
                start_date = datetime.now() - timedelta(days=365)
                
            stock_data = stock_data[stock_data['日期'] >= start_date]
            return stock_data
            
        except Exception as e:
            print(f"获取股价数据失败: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> dict:
        """计算技术指标"""
        if data.empty:
            return {}
            
        df = data.copy()
        df['收盘'] = pd.to_numeric(df['收盘'])
        df['最高'] = pd.to_numeric(df['最高'])
        df['最低'] = pd.to_numeric(df['最低'])
        df['成交量'] = pd.to_numeric(df['成交量'])
        
        indicators = {}
        
        # 1. 移动平均线系统
        indicators['MA'] = {
            'MA5': df['收盘'].rolling(5).mean().iloc[-1],
            'MA10': df['收盘'].rolling(10).mean().iloc[-1],
            'MA20': df['收盘'].rolling(20).mean().iloc[-1],
            'MA30': df['收盘'].rolling(30).mean().iloc[-1],
            'MA60': df['收盘'].rolling(60).mean().iloc[-1]
        }
        
        # 2. MACD指标
        exp1 = df['收盘'].ewm(span=12).mean()
        exp2 = df['收盘'].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        indicators['MACD'] = {
            'MACD': macd.iloc[-1],
            'SIGNAL': signal.iloc[-1],
            'HISTOGRAM': histogram.iloc[-1],
            'MACD_TREND': '多头' if macd.iloc[-1] > signal.iloc[-1] else '空头'
        }
        
        # 3. RSI相对强弱指标
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        indicators['RSI'] = {
            'RSI14': rsi.iloc[-1],
            'RSI_SIGNAL': '超买' if rsi.iloc[-1] > 70 else '超卖' if rsi.iloc[-1] < 30 else '正常'
        }
        
        # 4. KDJ随机指标
        low_9 = df['最低'].rolling(window=9).min()
        high_9 = df['最高'].rolling(window=9).max()
        rsv = (df['收盘'] - low_9) / (high_9 - low_9) * 100
        k = rsv.ewm(alpha=1/3).mean()
        d = k.ewm(alpha=1/3).mean()
        j = 3 * k - 2 * d
        
        indicators['KDJ'] = {
            'K': k.iloc[-1],
            'D': d.iloc[-1],
            'J': j.iloc[-1],
            'KDJ_SIGNAL': '金叉' if k.iloc[-1] > d.iloc[-1] else '死叉'
        }
        
        # 5. 布林带
        bb_middle = df['收盘'].rolling(20).mean()
        bb_std = df['收盘'].rolling(20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        current_price = df['收盘'].iloc[-1]
        indicators['BOLL'] = {
            'UPPER': bb_upper.iloc[-1],
            'MIDDLE': bb_middle.iloc[-1],
            'LOWER': bb_lower.iloc[-1],
            'POSITION': '上轨' if current_price > bb_upper.iloc[-1] else '下轨' if current_price < bb_lower.iloc[-1] else '中轨'
        }
        
        # 6. 成交量分析
        volume_ma5 = df['成交量'].rolling(5).mean()
        volume_ma10 = df['成交量'].rolling(10).mean()
        
        indicators['VOLUME'] = {
            'CURRENT': df['成交量'].iloc[-1],
            'MA5': volume_ma5.iloc[-1],
            'MA10': volume_ma10.iloc[-1],
            'VOLUME_RATIO': df['成交量'].iloc[-1] / volume_ma10.iloc[-1],
            'VOLUME_SIGNAL': '放量' if df['成交量'].iloc[-1] > volume_ma10.iloc[-1] * 1.2 else '缩量'
        }
        
        return indicators
    
    def get_fundamental_data(self) -> dict:
        """获取基本面数据"""
        fundamentals = {}
        
        try:
            # 1. 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=self.stock_code)
            if not stock_info.empty:
                info_dict = dict(zip(stock_info['item'], stock_info['value']))
                fundamentals['BASIC_INFO'] = {
                    '名称': info_dict.get('股票简称', ''),
                    '行业': info_dict.get('所属行业', ''),
                    '市盈率': info_dict.get('市盈率', ''),
                    '市净率': info_dict.get('市净率', ''),
                    '总市值': info_dict.get('总市值', ''),
                    '流通市值': info_dict.get('流通市值', '')
                }
            
            # 2. 获取财务指标
            finance_indicator = ak.stock_financial_indicator(stock=self.stock_code)
            if not finance_indicator.empty:
                latest = finance_indicator.iloc[0]
                fundamentals['FINANCIAL_INDICATORS'] = {
                    'ROE': latest.get('净资产收益率', ''),
                    'ROA': latest.get('总资产收益率', ''),
                    '毛利率': latest.get('销售毛利率', ''),
                    '净利率': latest.get('销售净利率', ''),
                    '负债率': latest.get('资产负债率', '')
                }
            
            # 3. 获取主要指标
            key_indicator = ak.stock_key_indicator(stock=self.stock_code)
            if not key_indicator.empty:
                latest = key_indicator.iloc[0]
                fundamentals['KEY_INDICATORS'] = {
                    '每股收益': latest.get('基本每股收益', ''),
                    '每股净资产': latest.get('每股净资产', ''),
                    '每股现金流': latest.get('每股经营现金流', ''),
                    '营业收入增长率': latest.get('营业收入增长率', ''),
                    '净利润增长率': latest.get('净利润增长率', '')
                }
                
        except Exception as e:
            print(f"获取基本面数据失败: {e}")
            
        return fundamentals
    
    def get_capital_flow(self) -> dict:
        """获取资金流向数据"""
        capital_data = {}
        
        try:
            # 1. 获取个股资金流向
            capital_flow = ak.stock_individual_fund_flow(stock=self.stock_code)
            if not capital_flow.empty:
                latest = capital_flow.iloc[0]
                capital_data['INDIVIDUAL_FLOW'] = {
                    '主力净流入': latest.get('主力净流入', ''),
                    '超大单净流入': latest.get('超大单净流入', ''),
                    '大单净流入': latest.get('大单净流入', ''),
                    '中单净流入': latest.get('中单净流入', ''),
                    '小单净流入': latest.get('小单净流入', '')
                }
            
            # 2. 获取龙虎榜数据（如果有）
            try:
                longhu = ak.stock_lhb_detail_em(symbol=self.stock_code)
                if not longhu.empty:
                    latest_longhu = longhu.iloc[0]
                    capital_data['LONGBANG'] = {
                        '上榜日期': latest_longhu.get('上榜日期', ''),
                        '买入额': latest_longhu.get('买入额', ''),
                        '卖出额': latest_longhu.get('卖出额', ''),
                        '净额': latest_longhu.get('净额', '')
                    }
            except:
                pass  # 可能没有龙虎榜数据
                
        except Exception as e:
            print(f"获取资金流向数据失败: {e}")
            
        return capital_data
    
    def get_sector_analysis(self) -> dict:
        """获取行业和板块分析"""
        sector_data = {}
        
        try:
            # 1. 获取行业资金流向
            sector_flow = ak.stock_sector_fund_flow_rank()
            if not sector_flow.empty:
                # 找到该股票所属行业
                stock_info = ak.stock_individual_info_em(symbol=self.stock_code)
                if not stock_info.empty:
                    industry = stock_info[stock_info['item'] == '所属行业']['value'].iloc[0]
                    industry_flow = sector_flow[sector_flow['行业'] == industry]
                    
                    if not industry_flow.empty:
                        sector_data['INDUSTRY_FLOW'] = {
                            '行业名称': industry,
                            '行业涨跌幅': industry_flow.iloc[0]['行业涨跌幅'],
                            '主力净流入': industry_flow.iloc[0]['主力净流入'],
                            '主力净占比': industry_flow.iloc[0]['主力净占比']
                        }
            
            # 2. 获取概念板块表现
            concept_flow = ak.stock_concept_fund_flow_rank()
            if not concept_flow.empty:
                sector_data['CONCEPT_FLOW'] = concept_flow.head(10).to_dict('records')
                
        except Exception as e:
            print(f"获取行业板块数据失败: {e}")
            
        return sector_data
    
    def comprehensive_analysis(self) -> dict:
        """综合股票分析"""
        print(f"正在分析股票 {self.symbol} ...")
        
        # 获取数据
        price_data = self.get_price_data("6m")
        technical = self.calculate_technical_indicators(price_data)
        fundamental = self.get_fundamental_data()
        capital = self.get_capital_flow()
        sector = self.get_sector_analysis()
        
        # 综合评分
        score = self._calculate_score(technical, fundamental, capital)
        
        result = {
            'STOCK_CODE': self.symbol,
            'ANALYSIS_DATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'TECHNICAL_INDICATORS': technical,
            'FUNDAMENTAL_DATA': fundamental,
            'CAPITAL_FLOW': capital,
            'SECTOR_ANALYSIS': sector,
            'COMPREHENSIVE_SCORE': score,
            'INVESTMENT_RECOMMENDATION': self._generate_recommendation(score, technical, fundamental)
        }
        
        return result
    
    def _calculate_score(self, technical: dict, fundamental: dict, capital: dict) -> dict:
        """计算综合评分"""
        score = 0
        details = {}
        
        # 技术面评分 (40%)
        tech_score = 0
        if technical:
            # MACD评分
            if technical.get('MACD', {}).get('MACD_TREND') == '多头':
                tech_score += 15
            else:
                tech_score += 5
                
            # RSI评分
            rsi = technical.get('RSI', {}).get('RSI14', 50)
            if 30 <= rsi <= 70:
                tech_score += 15
            else:
                tech_score += 5
                
            # KDJ评分
            if technical.get('KDJ', {}).get('KDJ_SIGNAL') == '金叉':
                tech_score += 10
            else:
                tech_score += 3
                
        details['TECHNICAL_SCORE'] = tech_score
        
        # 基本面评分 (30%)
        fund_score = 0
        if fundamental:
            # ROE评分
            roe = fundamental.get('FINANCIAL_INDICATORS', {}).get('ROE', 0)
            if isinstance(roe, (int, float)) and roe > 10:
                fund_score += 15
            else:
                fund_score += 8
                
            # 负债率评分
            debt_ratio = fundamental.get('FINANCIAL_INDICATORS', {}).get('负债率', 50)
            if isinstance(debt_ratio, (int, float)) and debt_ratio < 60:
                fund_score += 15
            else:
                fund_score += 8
                
        details['FUNDAMENTAL_SCORE'] = fund_score
        
        # 资金面评分 (30%)
        capital_score = 0
        if capital:
            main_flow = capital.get('INDIVIDUAL_FLOW', {}).get('主力净流入', 0)
            if isinstance(main_flow, (int, float)) and main_flow > 0:
                capital_score += 20
            else:
                capital_score += 10
                
            # 龙虎榜加分
            if capital.get('LONGBANG'):
                capital_score += 10
                
        details['CAPITAL_SCORE'] = capital_score
        
        # 总分
        total_score = tech_score + fund_score + capital_score
        details['TOTAL_SCORE'] = total_score
        details['SCORE_LEVEL'] = self._get_score_level(total_score)
        
        return details
    
    def _get_score_level(self, score: int) -> str:
        """获取评分等级"""
        if score >= 80:
            return '优秀'
        elif score >= 60:
            return '良好'
        elif score >= 40:
            return '一般'
        else:
            return '较差'
    
    def _generate_recommendation(self, score: dict, technical: dict, fundamental: dict) -> str:
        """生成投资建议"""
        total_score = score.get('TOTAL_SCORE', 0)
        level = score.get('SCORE_LEVEL', '一般')
        
        if total_score >= 80:
            recommendation = "强烈推荐 - 技术面、基本面、资金面均表现优秀"
        elif total_score >= 60:
            recommendation = "推荐 - 整体表现良好，可适当关注"
        elif total_score >= 40:
            recommendation = "中性 - 表现一般，需谨慎观察"
        else:
            recommendation = "谨慎 - 表现较差，建议观望"
            
        # 添加具体建议
        if technical.get('MACD', {}).get('MACD_TREND') == '多头':
            recommendation += "，MACD呈多头排列"
        else:
            recommendation += "，MACD呈空头排列"
            
        if fundamental.get('FINANCIAL_INDICATORS', {}).get('ROE', 0) > 15:
            recommendation += "，ROE表现优秀"
            
        return recommendation

def main():
    """主函数"""
    print("=== 股票核心指标分析系统 ===")
    print("本系统基于AKShare数据，分析股票的核心指标和投资逻辑")
    print()
    
    # 示例分析
    stock_codes = ['000001', '000002', '600519']  # 平安银行、万科A、贵州茅台
    
    for code in stock_codes:
        try:
            analyzer = StockCoreIndicators(code)
            result = analyzer.comprehensive_analysis()
            
            print(f"\n{'='*50}")
            print(f"股票代码: {result['STOCK_CODE']}")
            print(f"分析时间: {result['ANALYSIS_DATE']}")
            print(f"综合评分: {result['COMPREHENSIVE_SCORE']['TOTAL_SCORE']}分")
            print(f"评分等级: {result['COMPREHENSIVE_SCORE']['SCORE_LEVEL']}")
            print(f"投资建议: {result['INVESTMENT_RECOMMENDATION']}")
            
            # 详细指标
            print(f"\n【技术面指标】")
            tech = result['TECHNICAL_INDICATORS']
            if tech:
                print(f"MACD趋势: {tech.get('MACD', {}).get('MACD_TREND', 'N/A')}")
                print(f"RSI(14): {tech.get('RSI', {}).get('RSI14', 'N/A'):.2f}")
                print(f"KDJ信号: {tech.get('KDJ', {}).get('KDJ_SIGNAL', 'N/A')}")
                print(f"成交量状态: {tech.get('VOLUME', {}).get('VOLUME_SIGNAL', 'N/A')}")
            
            print(f"\n【基本面数据】")
            fund = result['FUNDAMENTAL_DATA']
            if fund:
                basic = fund.get('BASIC_INFO', {})
                print(f"股票名称: {basic.get('名称', 'N/A')}")
                print(f"所属行业: {basic.get('行业', 'N/A')}")
                print(f"市盈率: {basic.get('市盈率', 'N/A')}")
                
                financial = fund.get('FINANCIAL_INDICATORS', {})
                print(f"ROE: {financial.get('ROE', 'N/A')}")
                print(f"毛利率: {financial.get('毛利率', 'N/A')}")
                
            print(f"\n【资金流向】")
            capital = result['CAPITAL_FLOW']
            if capital:
                flow = capital.get('INDIVIDUAL_FLOW', {})
                print(f"主力净流入: {flow.get('主力净流入', 'N/A')}")
                print(f"超大单净流入: {flow.get('超大单净流入', 'N/A')}")
                
        except Exception as e:
            print(f"分析股票 {code} 时出错: {e}")
            continue
    
    print(f"\n{'='*50}")
    print("\n=== 炒股核心指标体系总结 ===")
    print("""
【技术分析核心指标】
1. 趋势指标：MA均线系统、MACD、ADX
2. 动量指标：RSI、KDJ、CCI
3. 波动指标：布林带、ATR
4. 成交量指标：成交量、OBV、VR
5. 形态识别：支撑阻力位、头肩顶底

【基本面分析核心逻辑】
1. 财务指标：ROE、ROA、毛利率、净利率
2. 成长性：营收增长率、净利润增长率
3. 估值水平：PE、PB、PEG
4. 偿债能力：资产负债率、流动比率
5. 运营能力：存货周转率、应收账款周转率

【资金流向监控要点】
1. 主力资金：大单净流入、主力净流入
2. 散户资金：小单净流入
3. 机构动向：龙虎榜、机构席位
4. 北向资金：沪深港通资金流向
5. 融资融券：融资余额、融券余量

【市场情绪指标】
1. 涨停板数量、跌停板数量
2. 涨跌家数比
3. 成交量变化
4. 波动率指数（VIX）
5. 投资者信心指数

【风险控制要点】
1. 仓位管理：单只股票不超过总资金20%
2. 止损设置：技术面止损8-10%，基本面止损15%
3. 分散投资：不同行业、不同市值
4. 政策风险：关注监管政策变化
5. 系统性风险：大盘趋势判断
""")

if __name__ == "__main__":
    main()