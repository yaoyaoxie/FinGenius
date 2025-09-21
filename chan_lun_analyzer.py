#!/usr/bin/env python3
"""
缠论技术分析工具
用于分析股票走势的笔、线段、中枢、背驰等缠论概念
"""

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import deque
import warnings
warnings.filterwarnings('ignore')

class ChanLunAnalyzer:
    """缠论分析器"""
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = None
        self.bi_list = []  # 笔列表
        self.xianduan_list = []  # 线段列表
        self.zhongshu_list = []  # 中枢列表
        
    def get_data(self, period="1y"):
        """获取股票数据"""
        try:
            stock_data = ak.stock_zh_a_hist(symbol=self.symbol, period="daily")
            stock_data['日期'] = pd.to_datetime(stock_data['日期'])
            stock_data = stock_data.sort_values('日期')
            
            if period == "1y":
                start_date = datetime.now() - timedelta(days=365)
            elif period == "6m":
                start_date = datetime.now() - timedelta(days=180)
            else:
                start_date = datetime.now() - timedelta(days=90)
                
            stock_data = stock_data[stock_data['日期'] >= start_date]
            
            # 转换数据类型
            stock_data['收盘'] = pd.to_numeric(stock_data['收盘'])
            stock_data['最高'] = pd.to_numeric(stock_data['最高'])
            stock_data['最低'] = pd.to_numeric(stock_data['最低'])
            stock_data['成交量'] = pd.to_numeric(stock_data['成交量'])
            
            self.data = stock_data.reset_index(drop=True)
            return self.data
            
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def find_fenxing(self, data):
        """识别分型"""
        fenxing_list = []
        
        for i in range(1, len(data) - 1):
            current_high = data.iloc[i]['最高']
            current_low = data.iloc[i]['最低']
            prev_high = data.iloc[i-1]['最高']
            prev_low = data.iloc[i-1]['最低']
            next_high = data.iloc[i+1]['最高']
            next_low = data.iloc[i+1]['最低']
            
            # 顶分型
            if current_high > prev_high and current_high > next_high:
                fenxing_list.append({
                    'type': '顶分型',
                    'index': i,
                    'date': data.iloc[i]['日期'],
                    'price': current_high,
                    'low': current_low
                })
            
            # 底分型
            if current_low < prev_low and current_low < next_low:
                fenxing_list.append({
                    'type': '底分型',
                    'index': i,
                    'date': data.iloc[i]['日期'],
                    'price': current_low,
                    'high': current_high
                })
        
        return fenxing_list
    
    def find_bi(self, data, fenxing_list):
        """识别笔"""
        bi_list = []
        
        if len(fenxing_list) < 2:
            return bi_list
        
        # 确保分型交替出现
        valid_fenxing = []
        last_type = None
        
        for fx in fenxing_list:
            if last_type is None or fx['type'] != last_type:
                valid_fenxing.append(fx)
                last_type = fx['type']
        
        # 识别笔
        for i in range(len(valid_fenxing) - 1):
            current_fx = valid_fenxing[i]
            next_fx = valid_fenxing[i + 1]
            
            # 笔的定义：相邻的顶分型和底分型
            if current_fx['type'] != next_fx['type']:
                # 检查是否有重叠
                if (current_fx['type'] == '顶分型' and 
                    current_fx['price'] > next_fx['price']):
                    bi_list.append({
                        'type': '下降笔',
                        'start_index': current_fx['index'],
                        'end_index': next_fx['index'],
                        'start_date': current_fx['date'],
                        'end_date': next_fx['date'],
                        'start_price': current_fx['price'],
                        'end_price': next_fx['price'],
                        'height': current_fx['price'] - next_fx['price']
                    })
                elif (current_fx['type'] == '底分型' and 
                      current_fx['price'] < next_fx['price']):
                    bi_list.append({
                        'type': '上升笔',
                        'start_index': current_fx['index'],
                        'end_index': next_fx['index'],
                        'start_date': current_fx['date'],
                        'end_date': next_fx['date'],
                        'start_price': current_fx['price'],
                        'end_price': next_fx['price'],
                        'height': next_fx['price'] - current_fx['price']
                    })
        
        return bi_list
    
    def find_xianduan(self, data, bi_list):
        """识别线段 - 修正版本"""
        xianduan_list = []
        
        if len(bi_list) < 3:
            return xianduan_list
        
        # 更简单的线段定义：连续3笔以上同方向的走势构成线段
        i = 0
        while i < len(bi_list) - 2:
            # 查找连续同方向的笔
            first_bi = bi_list[i]
            current_type = first_bi['type']
            
            # 收集连续的同方向笔
            consecutive_bi = [first_bi]
            j = i + 1
            
            while j < len(bi_list) and bi_list[j]['type'] == current_type:
                consecutive_bi.append(bi_list[j])
                j += 1
            
            # 如果连续3笔以上同方向，构成线段
            if len(consecutive_bi) >= 3:
                xianduan_list.append({
                    'type': current_type,
                    'bi_list': consecutive_bi.copy(),
                    'start_index': consecutive_bi[0]['start_index'],
                    'end_index': consecutive_bi[-1]['end_index'],
                    'start_date': consecutive_bi[0]['start_date'],
                    'end_date': consecutive_bi[-1]['end_date'],
                    'start_price': consecutive_bi[0]['start_price'],
                    'end_price': consecutive_bi[-1]['end_price'],
                    'height': abs(consecutive_bi[-1]['end_price'] - consecutive_bi[0]['start_price']),
                    'bi_count': len(consecutive_bi)
                })
                
                # 跳过已经处理的笔
                i = j
            else:
                i += 1
        
        return xianduan_list
    
    def find_zhongshu(self, data, xianduan_list):
        """识别中枢 - 修正版本"""
        zhongshu_list = []
        
        if len(xianduan_list) < 3:
            return zhongshu_list
        
        # 中枢定义：连续三个线段的价格重叠区域
        for i in range(len(xianduan_list) - 2):
            xd1 = xianduan_list[i]
            xd2 = xianduan_list[i + 1] 
            xd3 = xianduan_list[i + 2]
            
            # 获取每个线段的价格区间
            xd1_high = max(xd1['start_price'], xd1['end_price'])
            xd1_low = min(xd1['start_price'], xd1['end_price'])
            
            xd2_high = max(xd2['start_price'], xd2['end_price'])
            xd2_low = min(xd2['start_price'], xd2['end_price'])
            
            xd3_high = max(xd3['start_price'], xd3['end_price'])
            xd3_low = min(xd3['start_price'], xd3['end_price'])
            
            # 计算重叠区域
            overlap_low = max(xd1_low, xd2_low, xd3_low)
            overlap_high = min(xd1_high, xd2_high, xd3_high)
            
            if overlap_low < overlap_high:  # 有重叠区域
                zhongshu_list.append({
                    'start_index': min(xd1['start_index'], xd2['start_index'], xd3['start_index']),
                    'end_index': max(xd1['end_index'], xd2['end_index'], xd3['end_index']),
                    'upper': overlap_high,
                    'lower': overlap_low,
                    'center': (overlap_high + overlap_low) / 2,
                    'height': overlap_high - overlap_low,
                    'xianduan_count': 3,
                    'xd1': xd1, 'xd2': xd2, 'xd3': xd3
                })
        
        return zhongshu_list
    
    def find_beichi(self, data, bi_list, xianduan_list):
        """识别背驰"""
        beichi_list = []
        
        # 笔背驰
        if len(bi_list) >= 2:
            for i in range(len(bi_list) - 1):
                current_bi = bi_list[i + 1]
                prev_bi = bi_list[i]
                
                if current_bi['type'] == prev_bi['type']:  # 同方向
                    # 比较高度和成交量
                    current_volume = data.iloc[current_bi['start_index']:current_bi['end_index']]['成交量'].sum()
                    prev_volume = data.iloc[prev_bi['start_index']:prev_bi['end_index']]['成交量'].sum()
                    
                    # 背驰条件：价格创新高/新低，但成交量减少
                    if (current_bi['type'] == '上升笔' and 
                        current_bi['height'] > prev_bi['height'] and 
                        current_volume < prev_volume):
                        beichi_list.append({
                            'type': '笔背驰（上升）',
                            'index': current_bi['end_index'],
                            'date': current_bi['end_date'],
                            'price': current_bi['end_price']
                        })
                    elif (current_bi['type'] == '下降笔' and 
                          current_bi['height'] > prev_bi['height'] and 
                          current_volume < prev_volume):
                        beichi_list.append({
                            'type': '笔背驰（下降）',
                            'index': current_bi['end_index'],
                            'date': current_bi['end_date'],
                            'price': current_bi['end_price']
                        })
        
        return beichi_list
    
    def find_buy_sell_points(self, data, zhongshu_list, beichi_list):
        """识别买卖点"""
        buy_points = []
        sell_points = []
        
        # 基于中枢的买卖点
        for zhongshu in zhongshu_list:
            current_price = data.iloc[-1]['收盘']
            
            # 第三类买点：突破中枢后回踩不破
            if current_price > zhongshu['upper'] * 1.02:  # 突破2%
                buy_points.append({
                    'type': '第三类买点',
                    'price': zhongshu['upper'],
                    'condition': '突破中枢后回踩不破'
                })
            
            # 第三类卖点：跌破中枢后反弹不过
            if current_price < zhongshu['lower'] * 0.98:  # 跌破2%
                sell_points.append({
                    'type': '第三类卖点',
                    'price': zhongshu['lower'],
                    'condition': '跌破中枢后反弹不过'
                })
        
        # 基于背驰的买卖点
        for beichi in beichi_list:
            if '上升背驰' in beichi['type']:
                sell_points.append({
                    'type': '背驰卖点',
                    'price': beichi['price'],
                    'condition': '上升背驰'
                })
            elif '下降背驰' in beichi['type']:
                buy_points.append({
                    'type': '背驰买点',
                    'price': beichi['price'],
                    'condition': '下降背驰'
                })
        
        return buy_points, sell_points
    
    def analyze_zoushi_type(self, xianduan_list):
        """分析走势类型 - 修正版本"""
        if len(xianduan_list) < 2:
            return "无法判断"
        
        # 计算最近几个线段的整体方向
        recent_xd = xianduan_list[-min(5, len(xianduan_list)):]
        
        # 统计上升和下降线段的数量
        up_count = sum(1 for xd in recent_xd if xd['type'] == '上升笔')
        down_count = sum(1 for xd in recent_xd if xd['type'] == '下降笔')
        
        # 计算价格变化趋势
        start_price = recent_xd[0]['start_price']
        end_price = recent_xd[-1]['end_price']
        
        if up_count > down_count and end_price > start_price:
            return "上涨趋势"
        elif down_count > up_count and end_price < start_price:
            return "下跌趋势"
        else:
            return "盘整走势"
    
    def comprehensive_chan_analysis(self, data):
        """完整的缠论分析"""
        print("开始缠论技术分析...")
        
        # 1. 识别分型
        fenxing_list = self.find_fenxing(data)
        print(f"识别到 {len(fenxing_list)} 个分型")
        
        # 2. 识别笔
        bi_list = self.find_bi(data, fenxing_list)
        print(f"识别到 {len(bi_list)} 笔")
        
        # 3. 识别线段
        xianduan_list = self.find_xianduan(data, bi_list)
        print(f"识别到 {len(xianduan_list)} 个线段")
        
        # 4. 识别中枢
        zhongshu_list = self.find_zhongshu(data, xianduan_list)
        print(f"识别到 {len(zhongshu_list)} 个中枢")
        
        # 5. 识别背驰
        beichi_list = self.find_beichi(data, bi_list, xianduan_list)
        print(f"识别到 {len(beichi_list)} 个背驰")
        
        # 6. 识别买卖点
        buy_points, sell_points = self.find_buy_sell_points(data, zhongshu_list, beichi_list)
        print(f"识别到 {len(buy_points)} 个买点, {len(sell_points)} 个卖点")
        
        # 7. 分析走势类型
        zoushi_type = self.analyze_zoushi_type(xianduan_list)
        print(f"当前走势类型: {zoushi_type}")
        
        return {
            'fenxing_list': fenxing_list,
            'bi_list': bi_list,
            'xianduan_list': xianduan_list,
            'zhongshu_list': zhongshu_list,
            'beichi_list': beichi_list,
            'buy_points': buy_points,
            'sell_points': sell_points,
            'zoushi_type': zoushi_type,
            'data': data
        }
    
    def generate_chan_report(self, chan_result):
        """生成缠论分析报告"""
        data = chan_result['data']
        current_price = data.iloc[-1]['收盘']
        current_date = data.iloc[-1]['日期']
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    缠论技术分析报告                           ║
╠══════════════════════════════════════════════════════════════╣
║ 股票代码: {self.symbol}                                        ║
║ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}	  ║
║ 当前价格: ¥{current_price:.2f}				  ║
║ 走势类型: {chan_result['zoushi_type']}					  ║
╠══════════════════════════════════════════════════════════════╣

【分型分析】
识别到 {len(chan_result['fenxing_list'])} 个分型
最近分型: {chan_result['fenxing_list'][-1]['type'] if chan_result['fenxing_list'] else '无'}
价格: ¥{chan_result['fenxing_list'][-1]['price']:.2f} if chan_result['fenxing_list'] else '无'

【笔分析】  
识别到 {len(chan_result['bi_list'])} 笔
最近一笔: {chan_result['bi_list'][-1]['type'] if chan_result['bi_list'] else '无'}
高度: ¥{chan_result['bi_list'][-1]['height']:.2f} if chan_result['bi_list'] else '无'

【线段分析】
识别到 {len(chan_result['xianduan_list'])} 个线段
最近线段: {chan_result['xianduan_list'][-1]['type'] if chan_result['xianduan_list'] else '无'}
"""

        # 中枢分析
        if chan_result['zhongshu_list']:
            latest_zhongshu = chan_result['zhongshu_list'][-1]
            report += f"""
【中枢分析】
识别到 {len(chan_result['zhongshu_list'])} 个中枢
最近中枢范围: ¥{latest_zhongshu['lower']:.2f} - ¥{latest_zhongshu['upper']:.2f}
中枢中心: ¥{latest_zhongshu['center']:.2f}
"""
        
        # 背驰分析
        if chan_result['beichi_list']:
            report += f"""
【背驰分析】
识别到 {len(chan_result['beichi_list'])} 个背驰
最近背驰: {chan_result['beichi_list'][-1]['type']}
价格: ¥{chan_result['beichi_list'][-1]['price']:.2f}
"""
        
        # 买卖点分析
        if chan_result['buy_points']:
            report += f"""
【买点分析】
识别到 {len(chan_result['buy_points'])} 个买点
"""
            for bp in chan_result['buy_points']:
                report += f"{bp['type']}: ¥{bp['price']:.2f} ({bp['condition']})\n"
        
        if chan_result['sell_points']:
            report += f"""
【卖点分析】
识别到 {len(chan_result['sell_points'])} 个卖点
"""
            for sp in chan_result['sell_points']:
                report += f"{sp['type']}: ¥{sp['price']:.2f} ({sp['condition']})\n"
        
        # 操作建议
        report += """
【缠论操作建议】
"""
        if chan_result['buy_points'] and not chan_result['sell_points']:
            report += "🟢 建议关注买入机会\n"
        elif chan_result['sell_points'] and not chan_result['buy_points']:
            report += "🔴 建议关注卖出机会\n"
        elif chan_result['buy_points'] and chan_result['sell_points']:
            report += "🟡 多空交织，谨慎操作\n"
        else:
            report += "⚪ 等待明确信号\n"
        
        report += """
【缠论风险提示】
1. 缠论分析基于历史数据，不能保证未来走势
2. 需要结合其他技术指标和基本面分析
3. 严格设置止损，控制仓位风险
4. 中枢突破可能失败，需要确认

缠论核心思想：走势终完美
任何走势都会完成，关键是找到转折点
"""
        
        report += "╚══════════════════════════════════════════════════════════════╝"
        
        return report
    
    def plot_chan_analysis(self, chan_result, days=60):
        """绘制缠论分析图表"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime
            
            # 获取最近days天的数据
            data = chan_result['data'].tail(days).copy()
            dates = pd.to_datetime(data['日期'])
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
            
            # 绘制K线
            ax1.plot(dates, data['收盘'], 'b-', linewidth=1, label='收盘价')
            ax1.fill_between(dates, data['最低'], data['最高'], alpha=0.3, color='gray', label='高低价区间')
            
            # 标记分型
            for fx in chan_result['fenxing_list']:
                fx_date = pd.to_datetime(fx['date'])
                if fx_date in dates.values:
                    if fx['type'] == '顶分型':
                        ax1.plot(fx_date, fx['price'], 'rv', markersize=8, label='顶分型' if fx == chan_result['fenxing_list'][0] else "")
                    else:
                        ax1.plot(fx_date, fx['price'], 'g^', markersize=8, label='底分型' if fx == chan_result['fenxing_list'][0] else "")
            
            # 标记笔
            for bi in chan_result['bi_list']:
                start_date = pd.to_datetime(bi['start_date'])
                end_date = pd.to_datetime(bi['end_date'])
                if start_date in dates.values and end_date in dates.values:
                    color = 'red' if bi['type'] == '下降笔' else 'green'
                    ax1.plot([start_date, end_date], [bi['start_price'], bi['end_price']], 
                            color=color, linewidth=2, alpha=0.7)
            
            # 标记中枢
            for zs in chan_result['zhongshu_list']:
                start_idx = max(0, zs['start_index'] - len(data) + days)
                end_idx = min(days - 1, zs['end_index'] - len(data) + days)
                
                if start_idx < end_idx:
                    start_date = dates.iloc[start_idx]
                    end_date = dates.iloc[end_idx]
                    
                    # 绘制中枢矩形
                    ax1.axhspan(zs['lower'], zs['upper'], xmin=start_idx/days, xmax=end_idx/days, 
                               alpha=0.3, color='yellow', label='中枢' if zs == chan_result['zhongshu_list'][0] else "")
            
            ax1.set_title(f'{self.symbol} 缠论技术分析', fontsize=16)
            ax1.set_ylabel('价格 (元)')
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='upper left')
            
            # 绘制成交量
            ax2.bar(dates, data['成交量'], alpha=0.6, color='blue')
            ax2.set_ylabel('成交量')
            ax2.grid(True, alpha=0.3)
            
            # 设置x轴格式
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//10)))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("matplotlib 未安装，无法绘制图表")
        except Exception as e:
            print(f"绘制图表失败: {e}")

def analyze_zijin_mining_chan_lun():
    """紫金矿业缠论分析专项函数"""
    print("=" * 60)
    print("紫金矿业（601899）缠论技术分析")
    print("=" * 60)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建缠论分析器
    analyzer = ChanLunAnalyzer("601899")
    
    # 获取数据
    print("正在获取紫金矿业历史数据...")
    data = analyzer.get_data("1y")
    
    if data.empty:
        print("获取数据失败，无法进行分析")
        return
    
    print(f"获取到 {len(data)} 个交易日数据")
    print(f"时间范围: {data.iloc[0]['日期'].strftime('%Y-%m-%d')} 至 {data.iloc[-1]['日期'].strftime('%Y-%m-%d')}")
    print(f"价格区间: ¥{data['收盘'].min():.2f} - ¥{data['收盘'].max():.2f}")
    print()
    
    # 执行缠论分析
    print("开始执行缠论分析...")
    chan_result = analyzer.comprehensive_chan_analysis(data)
    
    # 生成分析报告
    print("\n生成缠论分析报告...")
    report = analyzer.generate_chan_report(chan_result)
    print(report)
    
    # 绘制分析图表
    print("\n绘制缠论分析图表...")
    analyzer.plot_chan_analysis(chan_result, days=120)
    
    # 专项分析
    print("\n【紫金矿业专项缠论分析】")
    
    # 1. 走势类型分析
    zoushi_type = chan_result['zoushi_type']
    print(f"当前走势类型: {zoushi_type}")
    
    # 2. 中枢分析
    if chan_result['zhongshu_list']:
        latest_zhongshu = chan_result['zhongshu_list'][-1]
        current_price = data.iloc[-1]['收盘']
        
        print(f"\n最新中枢分析:")
        print(f"中枢范围: ¥{latest_zhongshu['lower']:.2f} - ¥{latest_zhongshu['upper']:.2f}")
        print(f"当前价格: ¥{current_price:.2f}")
        
        if current_price > latest_zhongshu['upper']:
            print("🟢 当前价格在中枢上方，关注第三类买点")
        elif current_price < latest_zhongshu['lower']:
            print("🔴 当前价格在中枢下方，关注第三类卖点")
        else:
            print("🟡 当前价格在中枢内部，震荡整理")
    
    # 3. 买卖点分析
    if chan_result['buy_points']:
        print(f"\n买入信号: {len(chan_result['buy_points'])}个")
        for bp in chan_result['buy_points']:
            print(f"  - {bp['type']}: ¥{bp['price']:.2f}")
    
    if chan_result['sell_points']:
        print(f"\n卖出信号: {len(chan_result['sell_points'])}个")
        for sp in chan_result['sell_points']:
            print(f"  - {sp['type']}: ¥{sp['price']:.2f}")
    
    # 4. 背驰分析
    if chan_result['beichi_list']:
        print(f"\n背驰警告: {len(chan_result['beichi_list'])}个")
        for bc in chan_result['beichi_list']:
            print(f"  - {bc['type']}: ¥{bc['price']:.2f}")
    
    # 5. 操作建议
    print(f"\n【缠论操作建议】")
    if zoushi_type == "上涨趋势":
        print("🟢 整体上涨趋势，逢低关注买入机会")
        print("📈 关注回调不创新低的买入点")
    elif zoushi_type == "下跌趋势":
        print("🔴 整体下跌趋势，谨慎操作")
        print("📉 等待明确的底部信号")
    else:
        print("🟡 盘整走势，高抛低吸")
        print("📊 关注中枢突破方向")
    
    print(f"\n【风险控制】")
    print("⚠️  严格设置止损，控制单只股票仓位")
    print("⚠️  缠论分析需结合基本面和市场环境")
    print("⚠️  中枢突破可能失败，需要确认")
    
    print("=" * 60)
    print("缠论分析完成，仅供参考")
    print("=" * 60)

if __name__ == "__main__":
    analyze_zijin_mining_chan_lun()