#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
和而泰(002402)技术面分析
"""

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_ma(df, periods=[5, 10, 20, 60]):
    """计算移动平均线"""
    for period in periods:
        df[f'MA{period}'] = df['close'].rolling(window=period).mean()
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    ema_fast = df['close'].ewm(span=fast).mean()
    ema_slow = df['close'].ewm(span=slow).mean()
    df['DIF'] = ema_fast - ema_slow
    df['DEA'] = df['DIF'].ewm(span=signal).mean()
    df['MACD'] = 2 * (df['DIF'] - df['DEA'])
    return df

def calculate_kdj(df, n=9, m1=3, m2=3):
    """计算KDJ指标"""
    low_n = df['low'].rolling(window=n).min()
    high_n = df['high'].rolling(window=n).max()
    rsv = (df['close'] - low_n) / (high_n - low_n) * 100
    df['K'] = rsv.ewm(alpha=1/m1).mean()
    df['D'] = df['K'].ewm(alpha=1/m2).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df

def calculate_rsi(df, periods=[6, 12, 24]):
    """计算RSI指标"""
    for period in periods:
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        rs = gain / loss
        df[f'RSI{period}'] = 100 - (100 / (1 + rs))
    return df

def find_support_resistance(df, window=20):
    """寻找支撑压力位"""
    # 近期最高价作为压力位
    resistance = df['high'].tail(window).max()
    # 近期最低价作为支撑位
    support = df['low'].tail(window).min()
    
    # 斐波那契回调位
    high = df['high'].tail(30).max()
    low = df['low'].tail(30).min()
    fib_382 = high - (high - low) * 0.382
    fib_500 = high - (high - low) * 0.5
    fib_618 = high - (high - low) * 0.618
    
    return {
        'resistance': resistance,
        'support': support,
        'fib_382': fib_382,
        'fib_500': fib_500,
        'fib_618': fib_618
    }

def analyze_volume(df):
    """成交量分析"""
    recent_vol = df['vol'].tail(10).mean()
    avg_vol = df['vol'].tail(30).mean()
    vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
    
    # 量价关系
    price_change = df['close'].pct_change().tail(10).mean()
    vol_change = df['vol'].pct_change().tail(10).mean()
    
    return {
        'recent_avg_vol': recent_vol,
        '30d_avg_vol': avg_vol,
        'vol_ratio': vol_ratio,
        'price_change_10d': price_change,
        'vol_change_10d': vol_change
    }

def main():
    # 获取数据
    stock_code = '002402'
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=120)).strftime('%Y%m%d')
    
    print(f"=== 和而泰({stock_code})技术面分析报告 ===")
    print(f"分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # 获取日线数据
    df = ak.stock_zh_a_hist(symbol=stock_code, period='daily', start_date=start_date, end_date=end_date)
    
    if df.empty:
        print("未获取到数据，分析终止")
        return
    
    # 数据预处理
    df.columns = ['date', 'code', 'open', 'close', 'high', 'low', 'vol', 'turnover', 'amp', 'change_pct', 'change', 'turnover_rate']
    df = df.sort_values('date').reset_index(drop=True)
    
    # 计算技术指标
    df = calculate_ma(df)
    df = calculate_macd(df)
    df = calculate_kdj(df)
    df = calculate_rsi(df)
    
    # 获取最新数据
    latest = df.iloc[-1]
    
    print(f"\n一、当前价格信息")
    print(f"收盘价: {latest['close']:.2f}元")
    print(f"涨跌幅: {latest['change_pct']:.2f}%")
    print(f"成交量: {latest['vol']/10000:.1f}万股")
    print(f"振幅: {latest['amp']:.2f}%")
    
    print(f"\n二、K线形态分析")
    # 最近5日K线分析
    recent_5d = df.tail(5)
    print("近5日走势:")
    for i, row in recent_5d.iterrows():
        print(f"  {row['date']}: {row['close']:.2f} ({row['change_pct']:+.2f}%) 成交量:{row['vol']/10000:.1f}万")
    
    # 趋势判断
    current_price = latest['close']
    ma5 = latest['MA5']
    ma10 = latest['MA10']
    ma20 = latest['MA20']
    ma60 = latest['MA60']
    
    print(f"\n三、均线排列分析")
    print(f"MA5:  {ma5:.2f}元")
    print(f"MA10: {ma10:.2f}元") 
    print(f"MA20: {ma20:.2f}元")
    print(f"MA60: {ma60:.2f}元")
    
    # 均线排列判断
    if ma5 > ma10 > ma20 > ma60:
        trend = "多头排列"
        trend_desc = "强势上涨"
    elif ma5 < ma10 < ma20 < ma60:
        trend = "空头排列"
        trend_desc = "弱势下跌"
    else:
        trend = "纠缠排列"
        trend_desc = "震荡整理"
    
    print(f"均线状态: {trend} - {trend_desc}")
    
    # 价格相对均线位置
    if current_price > ma5:
        print(f"股价位于MA5之上，短期强势")
    else:
        print(f"股价位于MA5之下，短期弱势")
        
    print(f"\n四、技术指标状态")
    
    # MACD分析
    dif = latest['DIF']
    dea = latest['DEA']
    macd = latest['MACD']
    print(f"MACD: DIF={dif:.3f}, DEA={dea:.3f}, MACD={macd:.3f}")
    
    if macd > 0:
        if dif > dea:
            macd_signal = "金叉看涨"
        else:
            macd_signal = "多头减弱"
    else:
        if dif < dea:
            macd_signal = "死叉看跌"
        else:
            macd_signal = "空头减弱"
    print(f"MACD状态: {macd_signal}")
    
    # KDJ分析
    k = latest['K']
    d = latest['D']
    j = latest['J']
    print(f"KDJ: K={k:.1f}, D={d:.1f}, J={j:.1f}")
    
    if k > d:
        kdj_signal = "金叉看涨"
    else:
        kdj_signal = "死叉看跌"
    
    if j > 80:
        kdj_overbought = "严重超买"
    elif j > 50:
        kdj_overbought = "相对强势"
    elif j > 20:
        kdj_overbought = "相对弱势"
    else:
        kdj_overbought = "严重超卖"
    
    print(f"KDJ状态: {kdj_signal}, {kdj_overbought}")
    
    # RSI分析
    rsi6 = latest['RSI6']
    rsi12 = latest['RSI12']
    rsi24 = latest['RSI24']
    print(f"RSI: RSI6={rsi6:.1f}, RSI12={rsi12:.1f}, RSI24={rsi24:.1f}")
    
    if rsi6 > 70:
        rsi_signal = "超买"
    elif rsi6 < 30:
        rsi_signal = "超卖"
    else:
        rsi_signal = "正常"
    print(f"RSI状态: {rsi_signal}")
    
    print(f"\n五、成交量分析")
    vol_analysis = analyze_volume(df)
    print(f"近10日平均成交量: {vol_analysis['recent_avg_vol']/10000:.1f}万股")
    print(f"近30日平均成交量: {vol_analysis['30d_avg_vol']/10000:.1f}万股")
    print(f"成交量比率: {vol_analysis['vol_ratio']:.2f}")
    print(f"近10日价格变化: {vol_analysis['price_change_10d']*100:.2f}%")
    print(f"近10日成交量变化: {vol_analysis['vol_change_10d']*100:.2f}%")
    
    if vol_analysis['vol_ratio'] > 1.2:
        vol_comment = "放量"
    elif vol_analysis['vol_ratio'] < 0.8:
        vol_comment = "缩量"
    else:
        vol_comment = "正常"
    print(f"成交量状态: {vol_comment}")
    
    print(f"\n六、支撑压力位分析")
    sr = find_support_resistance(df)
    print(f"短期压力位: {sr['resistance']:.2f}元")
    print(f"短期支撑位: {sr['support']:.2f}元")
    print(f"斐波那契38.2%: {sr['fib_382']:.2f}元")
    print(f"斐波那契50.0%: {sr['fib_500']:.2f}元")
    print(f"斐波那契61.8%: {sr['fib_618']:.2f}元")
    
    print(f"\n七、下周走势预判")
    
    # 综合技术分析
    bullish_signals = 0
    bearish_signals = 0
    
    # 均线分析
    if current_price > ma5 > ma10 > ma20:
        bullish_signals += 2
    elif current_price < ma5 < ma10 < ma20:
        bearish_signals += 2
    
    # MACD分析
    if macd > 0 and dif > dea:
        bullish_signals += 1
    elif macd < 0 and dif < dea:
        bearish_signals += 1
    
    # KDJ分析
    if k > d and j < 80:
        bullish_signals += 1
    elif k < d and j > 20:
        bearish_signals += 1
    
    # RSI分析
    if rsi6 > 50 and rsi6 < 70:
        bullish_signals += 1
    elif rsi6 < 50 and rsi6 > 30:
        bearish_signals += 1
    
    # 成交量分析
    if vol_analysis['vol_ratio'] > 1.1 and vol_analysis['price_change_10d'] > 0:
        bullish_signals += 1
    elif vol_analysis['vol_ratio'] < 0.9 and vol_analysis['price_change_10d'] < 0:
        bearish_signals += 1
    
    print(f"综合信号: 看涨({bullish_signals}) vs 看跌({bearish_signals})")
    
    # 价格预测
    if bullish_signals > bearish_signals:
        trend_forecast = "震荡上涨"
        # 预测价格区间
        target_high = sr['resistance'] * 1.02
        target_low = current_price * 0.98
        if target_low < sr['support']:
            target_low = sr['support'] * 1.01
    elif bearish_signals > bullish_signals:
        trend_forecast = "震荡下跌"
        target_low = sr['support'] * 0.98
        target_high = current_price * 1.02
        if target_high > sr['resistance']:
            target_high = sr['resistance'] * 0.99
    else:
        trend_forecast = "区间震荡"
        target_high = sr['resistance'] * 0.98
        target_low = sr['support'] * 1.02
    
    print(f"技术趋势: {trend_forecast}")
    print(f"预测价格区间: {target_low:.2f}元 - {target_high:.2f}元")
    
    # 关键操作建议
    print(f"\n八、操作建议")
    print(f"买入参考: 回调至{sr['fib_618']:.2f}元附近或突破{sr['resistance']:.2f}元")
    print(f"卖出参考: 反弹至{sr['fib_382']:.2f}元附近或跌破{sr['support']:.2f}元")
    print(f"止损位: {sr['support'] * 0.97:.2f}元")
    print(f"目标位: {sr['resistance'] * 1.05:.2f}元")
    
    print("\n" + "="*50)
    print("⚠️  风险提示: 以上分析仅供参考，投资有风险，入市需谨慎")

if __name__ == "__main__":
    main()