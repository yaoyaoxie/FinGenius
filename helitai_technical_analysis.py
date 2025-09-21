#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
和而泰(002402)技术面深度分析
"""

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_stock_data(code, days=240):
    """获取股票数据"""
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    df = ak.stock_zh_a_hist(symbol=code, period='daily', start_date=start_date, end_date=end_date)
    if df.empty:
        return None
    
    # 数据预处理
    df.columns = ['date', 'code', 'open', 'close', 'high', 'low', 'vol', 'turnover', 'amp', 'change_pct', 'change', 'turnover_rate']
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    return df

def calculate_ma(df, periods=[5, 10, 20, 30, 60, 120]):
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

def calculate_bollinger_bands(df, period=20, std_dev=2):
    """计算布林带"""
    df['BB_Middle'] = df['close'].rolling(window=period).mean()
    bb_std = df['close'].rolling(window=period).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * std_dev)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * std_dev)
    return df

def analyze_candlestick_pattern(df):
    """分析K线形态"""
    patterns = []
    
    # 获取最近3日数据
    recent = df.tail(3)
    
    # 判断阳线阴线
    latest = recent.iloc[-1]
    if latest['close'] > latest['open']:
        patterns.append("阳线")
    else:
        patterns.append("阴线")
    
    # 判断实体大小
    body_size = abs(latest['close'] - latest['open'])
    total_range = latest['high'] - latest['low']
    if total_range > 0:
        body_ratio = body_size / total_range
        if body_ratio > 0.7:
            patterns.append("大实体")
        elif body_ratio > 0.4:
            patterns.append("中实体")
        else:
            patterns.append("小实体")
    
    # 判断是否有长上影线
    if latest['high'] > max(latest['open'], latest['close']):
        upper_shadow = latest['high'] - max(latest['open'], latest['close'])
        if upper_shadow > body_size * 0.5:
            patterns.append("长上影线")
    
    # 判断是否有长下影线
    if latest['low'] < min(latest['open'], latest['close']):
        lower_shadow = min(latest['open'], latest['close']) - latest['low']
        if lower_shadow > body_size * 0.5:
            patterns.append("长下影线")
    
    return patterns

def find_support_resistance_levels(df, window=20):
    """寻找支撑压力位"""
    # 获取近期数据
    recent_data = df.tail(window)
    
    # 短期压力和支撑
    resistance = recent_data['high'].max()
    support = recent_data['low'].min()
    
    # 计算斐波那契回调位
    recent_high = df['high'].tail(30).max()
    recent_low = df['low'].tail(30).min()
    
    fib_levels = {
        'fib_236': recent_high - (recent_high - recent_low) * 0.236,
        'fib_382': recent_high - (recent_high - recent_low) * 0.382,
        'fib_500': recent_high - (recent_high - recent_low) * 0.500,
        'fib_618': recent_high - (recent_high - recent_low) * 0.618,
        'fib_786': recent_high - (recent_high - recent_low) * 0.786
    }
    
    return {
        'resistance': resistance,
        'support': support,
        'recent_high': recent_high,
        'recent_low': recent_low,
        **fib_levels
    }

def volume_analysis(df):
    """成交量分析"""
    recent_5d = df.tail(5)
    recent_10d = df.tail(10)
    recent_20d = df.tail(20)
    
    vol_5d_avg = recent_5d['vol'].mean()
    vol_10d_avg = recent_10d['vol'].mean()
    vol_20d_avg = recent_20d['vol'].mean()
    
    latest_vol = df.iloc[-1]['vol']
    latest_price_change = df.iloc[-1]['change_pct']
    
    # 量价关系分析
    vol_trend = ""
    if latest_vol > vol_5d_avg * 1.2:
        vol_trend = "放量"
        if latest_price_change > 0:
            vol_trend += "上涨"
        else:
            vol_trend += "下跌"
    elif latest_vol < vol_5d_avg * 0.8:
        vol_trend = "缩量"
        if latest_price_change > 0:
            vol_trend += "上涨"
        else:
            vol_trend += "下跌"
    else:
        vol_trend = "正常成交"
    
    return {
        'vol_5d_avg': vol_5d_avg,
        'vol_10d_avg': vol_10d_avg,
        'vol_20d_avg': vol_20d_avg,
        'latest_vol': latest_vol,
        'vol_trend': vol_trend,
        'vol_ratio_5d': latest_vol / vol_5d_avg if vol_5d_avg > 0 else 1
    }

def comprehensive_analysis():
    """综合分析"""
    print("="*60)
    print("           和而泰(002402)技术面深度分析报告")
    print("="*60)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 获取数据
    df = get_stock_data('002402', 240)
    if df is None:
        print("获取数据失败")
        return
    
    # 计算技术指标
    df = calculate_ma(df)
    df = calculate_macd(df)
    df = calculate_kdj(df)
    df = calculate_rsi(df)
    df = calculate_bollinger_bands(df)
    
    # 获取最新数据
    latest = df.iloc[-1]
    current_price = latest['close']
    
    print(f"\n📊 一、当前价格信息")
    print(f"   收盘价: {current_price:.2f}元")
    print(f"   涨跌幅: {latest['change_pct']:+.2f}%")
    print(f"   成交量: {latest['vol']/10000:.1f}万股")
    print(f"   振幅: {latest['amp']:.2f}%")
    print(f"   换手率: {latest['turnover_rate']:.2f}%")
    
    # 获取近期高点低点
    sr_levels = find_support_resistance_levels(df)
    
    print(f"\n📈 二、价格位置分析")
    print(f"   当前价格相对近期高点: {(current_price/sr_levels['recent_high']-1)*100:+.1f}%")
    print(f"   当前价格相对近期低点: {(current_price/sr_levels['recent_low']-1)*100:+.1f}%")
    
    # 均线分析
    print(f"\n📊 三、均线排列分析")
    ma_periods = [5, 10, 20, 30, 60, 120]
    ma_values = {}
    
    for period in ma_periods:
        ma_val = latest[f'MA{period}']
        ma_values[period] = ma_val
        price_vs_ma = (current_price - ma_val) / ma_val * 100
        print(f"   MA{period:3d}: {ma_val:6.2f}元  ({price_vs_ma:+5.1f}%)")
    
    # 判断均线排列
    ma_sorted = [ma_values[p] for p in [5, 10, 20, 60]]
    if ma_sorted == sorted(ma_sorted, reverse=True):
        ma_trend = "多头排列(强势)"
    elif ma_sorted == sorted(ma_sorted):
        ma_trend = "空头排列(弱势)"
    else:
        ma_trend = "纠缠排列(震荡)"
    
    print(f"   均线状态: {ma_trend}")
    
    print(f"\n🔍 四、K线形态分析")
    # 最近5日K线
    recent_5d = df.tail(5)
    for i, row in recent_5d.iterrows():
        candle_info = f"   {row['date'].strftime('%m-%d')}: {row['close']:6.2f} ({row['change_pct']:+5.1f}%) vol:{row['vol']/10000:5.1f}万"
        print(candle_info)
    
    # K线形态识别
    patterns = analyze_candlestick_pattern(df)
    print(f"   最新K线形态: {' '.join(patterns)}")
    
    print(f"\n📈 五、技术指标分析")
    
    # MACD分析
    dif, dea, macd = latest['DIF'], latest['DEA'], latest['MACD']
    print(f"   MACD: DIF={dif:6.3f}  DEA={dea:6.3f}  MACD={macd:6.3f}")
    
    if macd > 0:
        macd_signal = "多头市场" + ("金叉" if dif > dea else "粘合")
    else:
        macd_signal = "空头市场" + ("死叉" if dif < dea else "粘合")
    print(f"   MACD状态: {macd_signal}")
    
    # KDJ分析
    k, d, j = latest['K'], latest['D'], latest['J']
    print(f"   KDJ: K={k:5.1f}  D={d:5.1f}  J={j:5.1f}")
    
    if j > 100:
        kdj_status = "严重超买"
    elif j > 80:
        kdj_status = "超买区域"
    elif j < 0:
        kdj_status = "严重超卖"
    elif j < 20:
        kdj_status = "超卖区域"
    else:
        kdj_status = "正常区域"
    
    kdj_signal = "金叉" if k > d else "死叉"
    print(f"   KDJ状态: {kdj_status} ({kdj_signal})")
    
    # RSI分析
    rsi6, rsi12, rsi24 = latest['RSI6'], latest['RSI12'], latest['RSI24']
    print(f"   RSI: RSI6={rsi6:5.1f}  RSI12={rsi12:5.1f}  RSI24={rsi24:5.1f}")
    
    if rsi6 > 80:
        rsi_status = "严重超买"
    elif rsi6 > 70:
        rsi_status = "超买区域"
    elif rsi6 < 20:
        rsi_status = "严重超卖"
    elif rsi6 < 30:
        rsi_status = "超卖区域"
    else:
        rsi_status = "正常区域"
    print(f"   RSI状态: {rsi_status}")
    
    # 布林带分析
    bb_upper, bb_middle, bb_lower = latest['BB_Upper'], latest['BB_Middle'], latest['BB_Lower']
    bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) * 100
    print(f"   布林带: 上轨={bb_upper:6.2f}  中轨={bb_middle:6.2f}  下轨={bb_lower:6.2f}")
    print(f"   布林带位置: {bb_position:4.1f}% ({'上轨附近' if bb_position > 80 else '下轨附近' if bb_position < 20 else '中轨附近'})")
    
    print(f"\n📊 六、成交量分析")
    vol_info = volume_analysis(df)
    print(f"   近5日平均成交量: {vol_info['vol_5d_avg']/10000:5.1f}万股")
    print(f"   近10日平均成交量: {vol_info['vol_10d_avg']/10000:5.1f}万股")
    print(f"   近20日平均成交量: {vol_info['vol_20d_avg']/10000:5.1f}万股")
    print(f"   最新成交量: {vol_info['latest_vol']/10000:5.1f}万股")
    print(f"   成交量比率: {vol_info['vol_ratio_5d']:4.2f}")
    print(f"   量价关系: {vol_info['vol_trend']}")
    
    print(f"\n🎯 七、支撑压力位分析")
    print(f"   短期压力位: {sr_levels['resistance']:6.2f}元")
    print(f"   短期支撑位: {sr_levels['support']:6.2f}元")
    print(f"   近期最高点: {sr_levels['recent_high']:6.2f}元")
    print(f"   近期最低点: {sr_levels['recent_low']:6.2f}元")
    print(f"   斐波那契位:")
    print(f"     23.6%: {sr_levels['fib_236']:6.2f}元")
    print(f"     38.2%: {sr_levels['fib_382']:6.2f}元")
    print(f"     50.0%: {sr_levels['fib_500']:6.2f}元")
    print(f"     61.8%: {sr_levels['fib_618']:6.2f}元")
    
    print(f"\n🔮 八、下周走势预测")
    
    # 综合评分
    score = 0
    reasons = []
    
    # 均线得分
    if current_price > ma_values[5] > ma_values[10] > ma_values[20]:
        score += 2
        reasons.append("多头排列")
    elif current_price < ma_values[5] < ma_values[10] < ma_values[20]:
        score -= 2
        reasons.append("空头排列")
    
    # MACD得分
    if macd > 0 and dif > dea:
        score += 1
        reasons.append("MACD金叉")
    elif macd < 0 and dif < dea:
        score -= 1
        reasons.append("MACD死叉")
    
    # KDJ得分
    if k > d and j < 90:
        score += 1
        reasons.append("KDJ金叉")
    elif k < d and j > 10:
        score -= 1
        reasons.append("KDJ死叉")
    
    # RSI得分
    if 30 < rsi6 < 70:
        if rsi6 > 50:
            score += 0.5
        else:
            score -= 0.5
    
    # 成交量得分
    if vol_info['vol_ratio_5d'] > 1.2:
        score += 0.5
        reasons.append("放量")
    elif vol_info['vol_ratio_5d'] < 0.8:
        score -= 0.5
        reasons.append("缩量")
    
    # 位置得分
    if bb_position > 80:
        score -= 1
        reasons.append("布林带上轨")
    elif bb_position < 20:
        score += 1
        reasons.append("布林带下轨")
    
    print(f"   综合评分: {score:+.1f}分")
    print(f"   主要理由: {'; '.join(reasons)}")
    
    # 预测价格区间
    if score >= 2:
        trend = "强势上涨"
        target_high = sr_levels['resistance'] * 1.05
        target_low = current_price * 0.98
    elif score >= 1:
        trend = "震荡上涨"
        target_high = sr_levels['resistance'] * 1.02
        target_low = sr_levels['fib_382']
    elif score <= -2:
        trend = "强势下跌"
        target_high = current_price * 1.02
        target_low = sr_levels['support'] * 0.95
    elif score <= -1:
        trend = "震荡下跌"
        target_high = sr_levels['fib_382']
        target_low = sr_levels['support']
    else:
        trend = "区间震荡"
        target_high = sr_levels['fib_236']
        target_low = sr_levels['fib_500']
    
    print(f"   技术趋势: {trend}")
    print(f"   预测区间: {target_low:.2f}元 - {target_high:.2f}元")
    
    print(f"\n💡 九、操作建议")
    print(f"   买入策略:")
    print(f"     - 短线: 回调至{sr_levels['fib_618']:.2f}元附近低吸")
    print(f"     - 中线: 突破{sr_levels['recent_high']:.2f}元后回踩确认")
    print(f"   卖出策略:")
    print(f"     - 短线: 反弹至{sr_levels['fib_236']:.2f}元附近减仓")
    print(f"     - 中线: 有效跌破{ma_values[20]:.2f}元止损")
    print(f"   关键位置:")
    print(f"     - 支撑位: {sr_levels['support']:.2f}元")
    print(f"     - 压力位: {sr_levels['resistance']:.2f}元")
    print(f"     - 止损位: {sr_levels['fib_618']:.2f}元")
    print(f"     - 目标位: {sr_levels['recent_high'] * 1.05:.2f}元")
    
    print(f"\n⚠️  风险提示")
    print("   1. 当前技术指标显示超买，短期有回调风险")
    print("   2. 需关注成交量是否能持续放大")
    print("   3. 大盘环境影响个股走势")
    print("   4. 建议控制仓位，设置止损")
    
    print("\n" + "="*60)
    print("📊 本分析基于技术分析，仅供参考，投资有风险，入市需谨慎")
    print("="*60)

if __name__ == "__main__":
    comprehensive_analysis()