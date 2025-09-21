#!/usr/bin/env python3
"""
缠论分析调试版本
详细检查每个步骤的结果
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque
import warnings
warnings.filterwarnings('ignore')

class ChanLunDebugger:
    """缠论调试器"""
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = None
        self.bi_list = []
        self.xianduan_list = []
        
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
        """识别笔 - 详细调试版本"""
        bi_list = []
        
        print(f"\n【调试】开始识别笔，分型数量: {len(fenxing_list)}")
        
        if len(fenxing_list) < 2:
            return bi_list
        
        # 确保分型交替出现
        valid_fenxing = []
        last_type = None
        
        print("【调试】分型详细信息:")
        for i, fx in enumerate(fenxing_list):
            print(f"  {i}: {fx['type']} - 价格: ¥{fx['price']:.2f} - 日期: {fx['date'].strftime('%Y-%m-%d')}")
        
        for fx in fenxing_list:
            if last_type is None or fx['type'] != last_type:
                valid_fenxing.append(fx)
                last_type = fx['type']
        
        print(f"【调试】有效分型数量: {len(valid_fenxing)}")
        
        # 识别笔
        for i in range(len(valid_fenxing) - 1):
            current_fx = valid_fenxing[i]
            next_fx = valid_fenxing[i + 1]
            
            print(f"【调试】处理分型对 {i}: {current_fx['type']} -> {next_fx['type']}")
            
            # 笔的定义：相邻的顶分型和底分型
            if current_fx['type'] != next_fx['type']:
                # 检查是否有重叠
                if (current_fx['type'] == '顶分型' and 
                    current_fx['price'] > next_fx['price']):
                    bi = {
                        'type': '下降笔',
                        'start_index': current_fx['index'],
                        'end_index': next_fx['index'],
                        'start_date': current_fx['date'],
                        'end_date': next_fx['date'],
                        'start_price': current_fx['price'],
                        'end_price': next_fx['price'],
                        'height': current_fx['price'] - next_fx['price']
                    }
                    bi_list.append(bi)
                    print(f"【调试】识别到下降笔: ¥{bi['start_price']:.2f} -> ¥{bi['end_price']:.2f}")
                    
                elif (current_fx['type'] == '底分型' and 
                      current_fx['price'] < next_fx['price']):
                    bi = {
                        'type': '上升笔',
                        'start_index': current_fx['index'],
                        'end_index': next_fx['index'],
                        'start_date': current_fx['date'],
                        'end_date': next_fx['date'],
                        'start_price': current_fx['price'],
                        'end_price': next_fx['price'],
                        'height': next_fx['price'] - current_fx['price']
                    }
                    bi_list.append(bi)
                    print(f"【调试】识别到上升笔: ¥{bi['start_price']:.2f} -> ¥{bi['end_price']:.2f}")
        
        print(f"【调试】最终识别到 {len(bi_list)} 笔")
        return bi_list
    
    def find_xianduan(self, data, bi_list):
        """识别线段 - 详细调试版本"""
        xianduan_list = []
        
        print(f"\n【调试】开始识别线段，笔数量: {len(bi_list)}")
        
        if len(bi_list) < 3:
            print("【调试】笔数量不足3个，无法构成线段")
            return xianduan_list
        
        print("【调试】笔的详细信息:")
        for i, bi in enumerate(bi_list):
            print(f"  {i}: {bi['type']} - 价格: ¥{bi['start_price']:.2f} -> ¥{bi['end_price']:.2f} - 日期: {bi['start_date'].strftime('%Y-%m-%d')} -> {bi['end_date'].strftime('%Y-%m-%d')}")
        
        # 更简单的线段定义：连续3笔以上同方向的走势构成线段
        i = 0
        while i < len(bi_list) - 2:
            print(f"【调试】从笔 {i} 开始检查线段")
            
            first_bi = bi_list[i]
            current_type = first_bi['type']
            
            # 收集连续的同方向笔
            consecutive_bi = [first_bi]
            j = i + 1
            
            while j < len(bi_list) and bi_list[j]['type'] == current_type:
                consecutive_bi.append(bi_list[j])
                j += 1
            
            print(f"【调试】找到 {len(consecutive_bi)} 个连续的 {current_type}")
            
            # 如果连续3笔以上同方向，构成线段
            if len(consecutive_bi) >= 3:
                xianduan = {
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
                }
                xianduan_list.append(xianduan)
                print(f"【调试】识别到线段: {current_type} - 包含 {len(consecutive_bi)} 笔")
                print(f"      价格范围: ¥{xianduan['start_price']:.2f} -> ¥{xianduan['end_price']:.2f}")
                
                # 跳过已经处理的笔
                i = j
            else:
                print(f"【调试】笔数量不足3个，不构成线段")
                i += 1
        
        print(f"【调试】最终识别到 {len(xianduan_list)} 个线段")
        return xianduan_list
    
    def debug_analysis(self):
        """完整的调试分析"""
        print("=" * 60)
        print("缠论分析调试 - 紫金矿业（601899）")
        print("=" * 60)
        print(f"调试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 获取数据
        print("正在获取紫金矿业历史数据...")
        data = self.get_data("1y")
        
        if data.empty:
            print("获取数据失败，无法进行调试")
            return
        
        print(f"获取到 {len(data)} 个交易日数据")
        print(f"时间范围: {data.iloc[0]['日期'].strftime('%Y-%m-%d')} 至 {data.iloc[-1]['日期'].strftime('%Y-%m-%d')}")
        print(f"价格区间: ¥{data['收盘'].min():.2f} - ¥{data['收盘'].max():.2f}")
        print(f"当前价格: ¥{data.iloc[-1]['收盘']:.2f}")
        print()
        
        # 1. 分型识别
        print("【步骤1】识别分型...")
        fenxing_list = self.find_fenxing(data)
        print(f"识别到 {len(fenxing_list)} 个分型")
        
        if len(fenxing_list) > 0:
            print("最近5个分型:")
            for i, fx in enumerate(fenxing_list[-5:], 1):
                print(f"  {i}: {fx['type']} - 价格: ¥{fx['price']:.2f} - 日期: {fx['date'].strftime('%Y-%m-%d')}")
        
        # 2. 笔识别
        print(f"\n【步骤2】识别笔...")
        bi_list = self.find_bi(data, fenxing_list)
        
        # 3. 线段识别
        print(f"\n【步骤3】识别线段...")
        xianduan_list = self.find_xianduan(data, bi_list)
        
        # 总结
        print(f"\n【调试总结】")
        print(f"分型数量: {len(fenxing_list)}")
        print(f"笔数量: {len(bi_list)}")
        print(f"线段数量: {len(xianduan_list)}")
        
        if len(xianduan_list) == 0:
            print("\n⚠️  线段识别为0，可能原因:")
            print("1. 笔的方向变化太频繁，没有连续3笔同方向")
            print("2. 市场震荡剧烈，趋势不明确")
            print("3. 数据时间周期较短，趋势不完整")
            
            # 分析笔的方向分布
            if bi_list:
                up_count = sum(1 for bi in bi_list if bi['type'] == '上升笔')
                down_count = sum(1 for bi in bi_list if bi['type'] == '下降笔')
                print(f"\n笔的方向分布:")
                print(f"上升笔: {up_count}")
                print(f"下降笔: {down_count}")
                print(f"交替频率: {len(bi_list)} 笔中有 {min(up_count, down_count)} 次方向变化")
        
        return {
            'data': data,
            'fenxing_list': fenxing_list,
            'bi_list': bi_list,
            'xianduan_list': xianduan_list
        }

def main():
    """主函数"""
    debugger = ChanLunDebugger("601899")
    result = debugger.debug_analysis()
    
    print("\n" + "=" * 60)
    print("缠论调试分析完成")
    print("=" * 60)

if __name__ == "__main__":
    main()