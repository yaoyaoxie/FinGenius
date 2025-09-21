#!/usr/bin/env python3
"""
紫金矿业（601899）专项分析报告
基于AKShare获取最新数据进行深度分析
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ZijinMiningAnalyzer:
    """紫金矿业专项分析器"""
    
    def __init__(self):
        self.symbol = "601899"
        self.name = "紫金矿业"
        
    def get_current_price(self):
        """获取实时价格数据"""
        try:
            # 获取实时行情
            current_data = ak.stock_zh_a_spot_em()
            zijin_data = current_data[current_data['代码'] == self.symbol]
            
            if not zijin_data.empty:
                return {
                    'current_price': zijin_data.iloc[0]['最新价'],
                    'change_pct': zijin_data.iloc[0]['涨跌幅'],
                    'volume': zijin_data.iloc[0]['成交量'],
                    'amount': zijin_data.iloc[0]['成交额'],
                    'high': zijin_data.iloc[0]['最高'],
                    'low': zijin_data.iloc[0]['最低'],
                    'open': zijin_data.iloc[0]['今开'],
                    'previous_close': zijin_data.iloc[0]['昨收']
                }
        except Exception as e:
            print(f"获取实时价格失败: {e}")
            return None
    
    def get_price_data(self, period="1y"):
        """获取历史价格数据"""
        try:
            # 获取历史数据
            stock_data = ak.stock_zh_a_hist(symbol=self.symbol, period="daily")
            stock_data['日期'] = pd.to_datetime(stock_data['日期'])
            stock_data = stock_data.sort_values('日期')
            
            # 设置时间范围
            if period == "1y":
                start_date = datetime.now() - timedelta(days=365)
            elif period == "6m":
                start_date = datetime.now() - timedelta(days=180)
            else:
                start_date = datetime.now() - timedelta(days=90)
                
            stock_data = stock_data[stock_data['日期'] >= start_date]
            return stock_data
            
        except Exception as e:
            print(f"获取历史价格失败: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, data):
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
        
        indicators['MACD'] = {
            'MACD': macd.iloc[-1],
            'SIGNAL': signal.iloc[-1],
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
    
    def get_fundamental_data(self):
        """获取基本面数据"""
        fundamentals = {}
        
        try:
            # 1. 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=self.symbol)
            if not stock_info.empty:
                info_dict = dict(zip(stock_info['item'], stock_info['value']))
                fundamentals['BASIC_INFO'] = {
                    '名称': info_dict.get('股票简称', ''),
                    '行业': info_dict.get('所属行业', ''),
                    '市盈率': info_dict.get('市盈率', ''),
                    '市净率': info_dict.get('市净率', ''),
                    '总市值': info_dict.get('总市值', ''),
                    '流通市值': info_dict.get('流通市值', ''),
                    '每股收益': info_dict.get('每股收益', ''),
                    '每股净资产': info_dict.get('每股净资产', '')
                }
            
            # 2. 获取财务数据
            try:
                # 获取主要财务指标
                finance_report = ak.stock_financial_abstract(symbol=self.symbol)
                if not finance_report.empty:
                    latest = finance_report.iloc[0]
                    fundamentals['FINANCIAL_INDICATORS'] = {
                        'ROE': latest.get('净资产收益率', ''),
                        'ROA': latest.get('总资产收益率', ''),
                        '毛利率': latest.get('销售毛利率', ''),
                        '净利率': latest.get('销售净利率', ''),
                        '负债率': latest.get('资产负债率', '')
                    }
            except:
                pass
            
            # 3. 获取最新业绩
            try:
                performance = ak.stock_financial_report_sina(stock=self.symbol, symbol="业绩报表")
                if not performance.empty:
                    latest_perf = performance.iloc[0]
                    fundamentals['PERFORMANCE'] = {
                        '营业收入': latest_perf.get('营业收入', ''),
                        '净利润': latest_perf.get('净利润', ''),
                        '营收同比增长': latest_perf.get('营业收入同比增长', ''),
                        '净利同比增长': latest_perf.get('净利润同比增长', '')
                    }
            except:
                pass
                
        except Exception as e:
            print(f"获取基本面数据失败: {e}")
            
        return fundamentals
    
    def get_capital_flow(self):
        """获取资金流向数据"""
        capital_data = {}
        
        try:
            # 1. 获取个股资金流向
            capital_flow = ak.stock_individual_fund_flow(stock=self.symbol)
            if not capital_flow.empty:
                latest = capital_flow.iloc[0]
                capital_data['INDIVIDUAL_FLOW'] = {
                    '主力净流入': latest.get('主力净流入', ''),
                    '超大单净流入': latest.get('超大单净流入', ''),
                    '大单净流入': latest.get('大单净流入', ''),
                    '中单净流入': latest.get('中单净流入', ''),
                    '小单净流入': latest.get('小单净流入', '')
                }
            
            # 2. 获取北向资金数据
            try:
                north_flow = ak.stock_hsgt_hold_stock_em(market="沪股通")
                zijin_north = north_flow[north_flow['股票代码'] == self.symbol]
                if not zijin_north.empty:
                    capital_data['NORTH_FLOW'] = {
                        '持股数量': zijin_north.iloc[0]['持股数量'],
                        '持股市值': zijin_north.iloc[0]['持股市值'],
                        '持股占比': zijin_north.iloc[0]['持股占比']
                    }
            except:
                pass
                
        except Exception as e:
            print(f"获取资金流向数据失败: {e}")
            
        return capital_data
    
    def get_mining_industry_data(self):
        """获取矿业行业数据"""
        industry_data = {}
        
        try:
            # 获取行业资金流向
            sector_flow = ak.stock_sector_fund_flow_rank()
            if not sector_flow.empty:
                # 查找有色金属行业
                mining_sector = sector_flow[sector_flow['行业'].str.contains('有色')]
                if not mining_sector.empty:
                    industry_data['MINING_SECTOR'] = {
                        '行业名称': mining_sector.iloc[0]['行业'],
                        '行业涨跌幅': mining_sector.iloc[0]['行业涨跌幅'],
                        '主力净流入': mining_sector.iloc[0]['主力净流入'],
                        '主力净占比': mining_sector.iloc[0]['主力净占比']
                    }
            
            # 获取黄金价格走势（影响紫金矿业的重要因素）
            try:
                gold_price = ak.futures_global_commodity_hist(symbol="伦敦黄金")
                if not gold_price.empty:
                    latest_gold = gold_price.iloc[-1]
                    industry_data['GOLD_PRICE'] = {
                        '当前价格': latest_gold['收盘'],
                        '涨跌幅': latest_gold['涨跌幅'],
                        '趋势': '上涨' if latest_gold['涨跌幅'] > 0 else '下跌'
                    }
            except:
                pass
                
        except Exception as e:
            print(f"获取行业数据失败: {e}")
            
        return industry_data
    
    def get_news_sentiment(self):
        """获取新闻情绪分析"""
        news_data = {}
        
        try:
            # 获取个股新闻
            news = ak.stock_news_em(symbol=self.symbol)
            if not news.empty:
                # 获取最近5条新闻
                recent_news = news.head(5)
                news_data['RECENT_NEWS'] = []
                for _, row in recent_news.iterrows():
                    news_data['RECENT_NEWS'].append({
                        '标题': row['新闻标题'],
                        '发布时间': row['发布时间'],
                        '内容摘要': row['新闻内容'][:100] + '...'
                    })
        except Exception as e:
            print(f"获取新闻数据失败: {e}")
            
        return news_data
    
    def comprehensive_analysis(self):
        """紫金矿业综合分析"""
        print(f"正在深度分析 {self.name}（{self.symbol}）...")
        
        # 获取各类数据
        current_data = self.get_current_price()
        price_data = self.get_price_data("6m")
        technical = self.calculate_technical_indicators(price_data)
        fundamental = self.get_fundamental_data()
        capital = self.get_capital_flow()
        industry = self.get_mining_industry_data()
        news = self.get_news_sentiment()
        
        # 生成投资建议
        recommendation = self.generate_recommendation(
            technical, fundamental, capital, industry
        )
        
        result = {
            'STOCK_CODE': self.symbol,
            'STOCK_NAME': self.name,
            'ANALYSIS_DATE': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'CURRENT_DATA': current_data,
            'TECHNICAL_INDICATORS': technical,
            'FUNDAMENTAL_DATA': fundamental,
            'CAPITAL_FLOW': capital,
            'INDUSTRY_DATA': industry,
            'NEWS_DATA': news,
            'INVESTMENT_RECOMMENDATION': recommendation
        }
        
        return result
    
    def generate_recommendation(self, technical, fundamental, capital, industry):
        """生成投资建议"""
        signals = []
        
        # 技术面分析
        if technical:
            # MACD趋势
            if technical.get('MACD', {}).get('MACD_TREND') == '多头':
                signals.append("技术面MACD多头")
            else:
                signals.append("技术面MACD空头")
            
            # RSI状态
            rsi = technical.get('RSI', {}).get('RSI14', 50)
            if rsi < 30:
                signals.append("RSI超卖反弹机会")
            elif rsi > 70:
                signals.append("RSI超买需谨慎")
            
            # 成交量
            if technical.get('VOLUME', {}).get('VOLUME_SIGNAL') == '放量':
                signals.append("成交量放大关注")
        
        # 基本面分析
        if fundamental and fundamental.get('BASIC_INFO'):
            pe = fundamental['BASIC_INFO'].get('市盈率', '')
            if pe and pe != '':
                pe_val = float(pe)
                if pe_val < 15:
                    signals.append("估值较低有优势")
                elif pe_val > 30:
                    signals.append("估值偏高需谨慎")
        
        # 资金流向分析
        if capital and capital.get('INDIVIDUAL_FLOW'):
            main_flow = capital['INDIVIDUAL_FLOW'].get('主力净流入', 0)
            # 处理字符串类型的数字
            if isinstance(main_flow, str) and main_flow != '':
                try:
                    main_flow = float(main_flow.replace(',', ''))
                except:
                    main_flow = 0
            elif main_flow == '' or main_flow is None:
                main_flow = 0
                
            if main_flow > 10000000:  # 1000万以上
                signals.append("主力资金大幅流入")
            elif main_flow < -10000000:
                signals.append("主力资金大幅流出")
        
        # 行业分析
        if industry and industry.get('MINING_SECTOR'):
            sector_change = industry['MINING_SECTOR'].get('行业涨跌幅', 0)
            if sector_change > 2:
                signals.append("行业整体上涨利好")
            elif sector_change < -2:
                signals.append("行业整体下跌压力")
        
        # 综合判断
        positive_signals = [s for s in signals if any(keyword in s for keyword in ['多头', '流入', '上涨', '较低', '反弹', '放大', '利好'])]
        negative_signals = [s for s in signals if any(keyword in s for keyword in ['空头', '流出', '下跌', '偏高', '超买', '压力'])]
        
        if len(positive_signals) > len(negative_signals):
            return f"推荐 - {len(positive_signals)}个积极信号: {', '.join(positive_signals[:3])}"
        elif len(negative_signals) > len(positive_signals):
            return f"谨慎 - {len(negative_signals)}个风险信号: {', '.join(negative_signals[:3])}"
        else:
            return f"中性 - 信号平衡，建议观望: {', '.join(signals[:2])}"

def main():
    """主函数：紫金矿业专项分析"""
    print("=" * 60)
    print("紫金矿业（601899）深度投资分析报告")
    print("=" * 60)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建分析器
    analyzer = ZijinMiningAnalyzer()
    
    # 执行综合分析
    result = analyzer.comprehensive_analysis()
    
    # 1. 当前价格分析
    print("【当前价格分析】")
    if result['CURRENT_DATA']:
        current = result['CURRENT_DATA']
        print(f"当前价格: ¥{current['current_price']:.2f}")
        print(f"涨跌幅: {current['change_pct']:.2f}%")
        print(f"成交量: {current['volume']:,}股")
        print(f"成交额: ¥{current['amount']:,.0f}万")
        print(f"最高/最低: ¥{current['high']:.2f}/{current['low']:.2f}")
    print()
    
    # 2. 技术面分析
    print("【技术面分析】")
    tech = result['TECHNICAL_INDICATORS']
    if tech:
        print(f"MACD趋势: {tech['MACD']['MACD_TREND']}")
        print(f"RSI(14): {tech['RSI']['RSI14']:.2f} ({tech['RSI']['RSI_SIGNAL']})")
        print(f"KDJ信号: {tech['KDJ']['KDJ_SIGNAL']}")
        print(f"布林带位置: {tech['BOLL']['POSITION']}")
        print(f"成交量状态: {tech['VOLUME']['VOLUME_SIGNAL']}")
        print(f"量比: {tech['VOLUME']['VOLUME_RATIO']:.2f}")
        
        # 均线分析
        ma_data = tech['MA']
        print(f"\n均线系统:")
        print(f"MA5: ¥{ma_data['MA5']:.2f}")
        print(f"MA10: ¥{ma_data['MA10']:.2f}")
        print(f"MA20: ¥{ma_data['MA20']:.2f}")
        print(f"MA60: ¥{ma_data['MA60']:.2f}")
        
        # 判断多头排列
        if ma_data['MA5'] > ma_data['MA10'] > ma_data['MA20']:
            print("✅ 短期多头排列")
        if ma_data['MA20'] > ma_data['MA60']:
            print("✅ 长期趋势向上")
    print()
    
    # 3. 基本面分析
    print("【基本面分析】")
    fund = result['FUNDAMENTAL_DATA']
    if fund and fund.get('BASIC_INFO'):
        basic = fund['BASIC_INFO']
        print(f"公司名称: {basic['名称']}")
        print(f"所属行业: {basic['行业']}")
        print(f"总市值: {basic['总市值']}")
        print(f"流通市值: {basic['流通市值']}")
        print(f"市盈率: {basic['市盈率']}")
        print(f"市净率: {basic['市净率']}")
        print(f"每股收益: {basic['每股收益']}")
        print(f"每股净资产: {basic['每股净资产']}")
    
    if fund and fund.get('FINANCIAL_INDICATORS'):
        financial = fund['FINANCIAL_INDICATORS']
        print(f"\n财务指标:")
        print(f"ROE: {financial['ROE']}")
        print(f"ROA: {financial['ROA']}")
        print(f"毛利率: {financial['毛利率']}")
        print(f"净利率: {financial['净利率']}")
        print(f"资产负债率: {financial['负债率']}")
    
    if fund and fund.get('PERFORMANCE'):
        perf = fund['PERFORMANCE']
        print(f"\n最新业绩:")
        print(f"营业收入: {perf['营业收入']}")
        print(f"净利润: {perf['净利润']}")
        print(f"营收同比增长: {perf['营收同比增长']}")
        print(f"净利同比增长: {perf['净利同比增长']}")
    print()
    
    # 4. 资金流向分析
    print("【资金流向分析】")
    capital = result['CAPITAL_FLOW']
    if capital and capital.get('INDIVIDUAL_FLOW'):
        flow = capital['INDIVIDUAL_FLOW']
        # 处理资金流向数据格式
        def format_flow_value(value):
            if isinstance(value, str) and value != '':
                try:
                    return float(value.replace(',', ''))
                except:
                    return 0
            elif isinstance(value, (int, float)):
                return value
            else:
                return 0
        
        main_flow = format_flow_value(flow['主力净流入'])
        big_flow = format_flow_value(flow['超大单净流入'])
        large_flow = format_flow_value(flow['大单净流入'])
        medium_flow = format_flow_value(flow['中单净流入'])
        small_flow = format_flow_value(flow['小单净流入'])
        
        print(f"主力净流入: ¥{main_flow:,.0f}")
        print(f"超大单净流入: ¥{big_flow:,.0f}")
        print(f"大单净流入: ¥{large_flow:,.0f}")
        print(f"中单净流入: ¥{medium_flow:,.0f}")
        print(f"小单净流入: ¥{small_flow:,.0f}")
    
    if capital and capital.get('NORTH_FLOW'):
        north = capital['NORTH_FLOW']
        print(f"\n北向资金:")
        print(f"持股数量: {north['持股数量']}")
        print(f"持股市值: {north['持股市值']}")
        print(f"持股占比: {north['持股占比']}")
    print()
    
    # 5. 行业分析
    print("【行业分析】")
    industry = result['INDUSTRY_DATA']
    if industry and industry.get('MINING_SECTOR'):
        sector = industry['MINING_SECTOR']
        print(f"行业名称: {sector['行业名称']}")
        print(f"行业涨跌幅: {sector['行业涨跌幅']}%")
        print(f"主力净流入: ¥{sector['主力净流入']:,.0f}")
        print(f"主力净占比: {sector['主力净占比']}")
    
    if industry and industry.get('GOLD_PRICE'):
        gold = industry['GOLD_PRICE']
        print(f"\n黄金价格:")
        print(f"当前价格: ${gold['当前价格']}")
        print(f"涨跌幅: {gold['涨跌幅']}%")
        print(f"趋势: {gold['趋势']}")
    print()
    
    # 6. 新闻分析
    print("【最新资讯】")
    news = result['NEWS_DATA']
    if news and news.get('RECENT_NEWS'):
        for i, news_item in enumerate(news['RECENT_NEWS'][:3], 1):
            print(f"{i}. {news_item['标题']}")
            print(f"   发布时间: {news_item['发布时间']}")
            print(f"   {news_item['内容摘要']}")
            print()
    
    # 7. 投资建议
    print("【投资建议】")
    print(result['INVESTMENT_RECOMMENDATION'])
    print()
    
    # 8. 风险提示
    print("【风险提示】")
    print("1. 金属价格波动风险")
    print("2. 汇率变动风险") 
    print("3. 环保政策风险")
    print("4. 海外经营风险")
    print("5. 市场系统性风险")
    print()
    
    print("=" * 60)
    print("免责声明：本分析仅供参考，不构成投资建议")
    print("投资有风险，入市需谨慎")
    print("=" * 60)

if __name__ == "__main__":
    main()