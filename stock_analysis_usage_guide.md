# 股票核心指标分析程序使用指南

## 🚀 程序概述

`stock_analysis_core_indicators.py` 是一个基于 **AKShare** 的完整股票分析系统，能够自动获取股票数据并进行多维度分析，为投资决策提供科学依据。

## 📋 功能特性

### ✅ **自动数据获取**
- 股票历史价格数据（日K线）
- 基本面财务数据
- 资金流向数据
- 行业和板块数据
- 龙虎榜数据

### ✅ **技术指标计算**
- 移动平均线系统（MA5/10/20/30/60）
- MACD指标（金叉死叉判断）
- RSI相对强弱指标
- KDJ随机指标
- 布林带（BOLL）
- 成交量分析

### ✅ **综合评分系统**
- 技术面评分（40%权重）
- 基本面评分（30%权重）
- 资金面评分（30%权重）
- 自动生成投资建议

## 🛠️ 安装和配置

### **1. 环境要求**
```bash
# Python 3.8+
python --version

# 安装依赖包
pip install akshare pandas numpy
```

### **2. 程序结构**
```
StockCoreIndicators类
├── get_price_data()           # 获取价格数据
├── calculate_technical_indicators()  # 计算技术指标
├── get_fundamental_data()     # 获取基本面数据
├── get_capital_flow()         # 获取资金流向
├── get_sector_analysis()      # 行业板块分析
├── comprehensive_analysis()   # 综合分析
└── _calculate_score()         # 评分计算
```

## 📊 使用方法详解

### **1. 基础使用**

```python
# 导入分析器
from stock_analysis_core_indicators import StockCoreIndicators

# 创建分析实例
analyzer = StockCoreIndicators("000001")  # 平安银行

# 执行完整分析
result = analyzer.comprehensive_analysis()

# 查看分析结果
print(f"股票代码: {result['STOCK_CODE']}")
print(f"综合评分: {result['COMPREHENSIVE_SCORE']['TOTAL_SCORE']}分")
print(f"投资建议: {result['INVESTMENT_RECOMMENDATION']}")
```

### **2. 获取特定数据**

```python
# 只获取价格数据
price_data = analyzer.get_price_data("6m")  # 6个月数据

# 只计算技术指标
tech_indicators = analyzer.calculate_technical_indicators(price_data)

# 只获取基本面数据
fundamental_data = analyzer.get_fundamental_data()

# 只获取资金流向
capital_flow = analyzer.get_capital_flow()
```

### **3. 分析结果解读**

#### **📈 技术指标解读**
```python
result['TECHNICAL_INDICATORS']
# 包含：
# - MA: 移动平均线数据
# - MACD: MACD指标和趋势判断
# - RSI: RSI数值和超买超卖信号
# - KDJ: KDJ指标和金叉死叉信号
# - BOLL: 布林带位置和突破信号
# - VOLUME: 成交量分析和放量缩量判断
```

#### **📊 基本面数据解读**
```python
result['FUNDAMENTAL_DATA']
# 包含：
# - BASIC_INFO: 基本信息（名称、行业、估值）
# - FINANCIAL_INDICATORS: 财务指标（ROE、ROA、毛利率等）
# - KEY_INDICATORS: 关键指标（每股收益、增长率等）
```

#### **💰 资金流向解读**
```python
result['CAPITAL_FLOW']
# 包含：
# - INDIVIDUAL_FLOW: 个股资金流向（主力、超大单、大单等）
# - LONGBANG: 龙虎榜数据（如有）
```

## 🎯 实战应用示例

### **示例1：批量分析股票池**

```python
# 创建股票池
stock_pool = ['000001', '000002', '600519', '000858', '002415']

# 批量分析
results = []
for code in stock_pool:
    try:
        analyzer = StockCoreIndicators(code)
        result = analyzer.comprehensive_analysis()
        results.append({
            'code': code,
            'score': result['COMPREHENSIVE_SCORE']['TOTAL_SCORE'],
            'recommendation': result['INVESTMENT_RECOMMENDATION']
        })
    except Exception as e:
        print(f"{code} 分析失败: {e}")

# 按评分排序
top_stocks = sorted(results, key=lambda x: x['score'], reverse=True)
print("评分排名:")
for stock in top_stocks:
    print(f"{stock['code']}: {stock['score']}分 - {stock['recommendation']}")
```

### **示例2：技术面筛选**

```python
def technical_screening(code):
    """技术面选股筛选"""
    analyzer = StockCoreIndicators(code)
    price_data = analyzer.get_price_data("3m")
    tech = analyzer.calculate_technical_indicators(price_data)
    
    # 筛选条件
    conditions = []
    
    # MACD多头
    if tech.get('MACD', {}).get('MACD_TREND') == '多头':
        conditions.append("MACD多头")
    
    # RSI适中
    rsi = tech.get('RSI', {}).get('RSI14', 50)
    if 40 <= rsi <= 60:
        conditions.append("RSI适中")
    
    # 成交量放大
    if tech.get('VOLUME', {}).get('VOLUME_SIGNAL') == '放量':
        conditions.append("成交量放大")
    
    # 布林带中轨上方
    if tech.get('BOLL', {}).get('POSITION') != '下轨':
        conditions.append("布林带中轨上方")
    
    return len(conditions), conditions

# 筛选技术面好的股票
candidates = ['000001', '000002', '600519']
for code in candidates:
    score, signals = technical_screening(code)
    if score >= 3:
        print(f"{code}: 技术面评分{score}/4 - {signals}")
```

### **示例3：资金流向监控**

```python
def monitor_capital_flow(codes, days=5):
    """监控资金流向"""
    for code in codes:
        analyzer = StockCoreIndicators(code)
        capital = analyzer.get_capital_flow()
        
        if capital.get('INDIVIDUAL_FLOW'):
            main_flow = capital['INDIVIDUAL_FLOW'].get('主力净流入', 0)
            
            # 判断资金流向
            if main_flow > 1000000:  # 100万以上
                print(f"🟢 {code}: 主力大幅流入 {main_flow:,.0f}元")
            elif main_flow < -1000000:
                print(f"🔴 {code}: 主力大幅流出 {main_flow:,.0f}元")
            else:
                print(f"⚪ {code}: 主力小幅变动 {main_flow:,.0f}元")

# 监控股票池资金流向
stock_list = ['000001', '000002', '600519', '000858']
monitor_capital_flow(stock_list)
```

### **示例4：估值分析**

```python
def valuation_analysis(code):
    """估值分析"""
    analyzer = StockCoreIndicators(code)
    fundamental = analyzer.get_fundamental_data()
    
    if fundamental.get('BASIC_INFO'):
        pe = fundamental['BASIC_INFO'].get('市盈率', 'N/A')
        pb = fundamental['BASIC_INFO'].get('市净率', 'N/A')
        
        # 估值判断
        valuation_status = "正常"
        if pe != 'N/A' and pe != '':
            pe_val = float(pe)
            if pe_val < 10:
                valuation_status = "低估"
            elif pe_val > 30:
                valuation_status = "高估"
        
        return {
            'code': code,
            'PE': pe,
            'PB': pb,
            'valuation': valuation_status
        }

# 分析估值水平
for code in ['000001', '600519']:
    result = valuation_analysis(code)
    print(f"{result['code']}: PE={result['PE']}, PB={result['PB']}, 估值{result['valuation']}")
```

## 📈 分析结果可视化

### **创建分析报告**

```python
def generate_report(code):
    """生成分析报告"""
    analyzer = StockCoreIndicators(code)
    result = analyzer.comprehensive_analysis()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    股票分析报告                              ║
╠══════════════════════════════════════════════════════════════╣
║ 股票代码: {result['STOCK_CODE']}                                        ║
║ 分析时间: {result['ANALYSIS_DATE']}                          ║
║ 综合评分: {result['COMPREHENSIVE_SCORE']['TOTAL_SCORE']}分 ({result['COMPREHENSIVE_SCORE']['SCORE_LEVEL']})        ║
║ 投资建议: {result['INVESTMENT_RECOMMENDATION']}              ║
╠══════════════════════════════════════════════════════════════╣
║ 【技术指标】                                                  ║
"""
    
    # 技术指标
    tech = result['TECHNICAL_INDICATORS']
    if tech:
        report += f"""║ MACD趋势: {tech.get('MACD', {}).get('MACD_TREND', 'N/A')}                                      ║
║ RSI(14): {tech.get('RSI', {}).get('RSI14', 'N/A'):.2f} ({tech.get('RSI', {}).get('RSI_SIGNAL', 'N/A')})          ║
║ KDJ信号: {tech.get('KDJ', {}).get('KDJ_SIGNAL', 'N/A')}                                      ║
║ 成交量: {tech.get('VOLUME', {}).get('VOLUME_SIGNAL', 'N/A')}                                    ║
"""
    
    # 基本面
    fund = result['FUNDAMENTAL_DATA']
    if fund and fund.get('BASIC_INFO'):
        report += f"""╠══════════════════════════════════════════════════════════════╣
║ 【基本面】                                                    ║
║ 股票名称: {fund['BASIC_INFO'].get('名称', 'N/A')}                                        ║
║ 所属行业: {fund['BASIC_INFO'].get('行业', 'N/A')}                                        ║
║ 市盈率: {fund['BASIC_INFO'].get('市盈率', 'N/A')}                                          ║
"""
    
    report += "╚══════════════════════════════════════════════════════════════╝"
    
    return report

# 生成报告
print(generate_report("000001"))
```

## ⚠️ 注意事项和限制

### **1. 数据限制**
- 部分财务数据接口可能需要更新
- 实时性：免费数据有15分钟延迟
- 完整性：新股或停牌股票数据可能不全

### **2. 使用建议**
- 结合多个指标综合判断
- 定期更新数据重新分析
- 不要完全依赖自动分析结果
- 需要人工验证和判断

### **3. 错误处理**
```python
try:
    analyzer = StockCoreIndicators("000001")
    result = analyzer.comprehensive_analysis()
except ValueError as e:
    print(f"股票代码错误: {e}")
except Exception as e:
    print(f"分析失败: {e}")
```

## 🔧 **扩展和优化**

### **1. 添加新指标**
```python
def add_custom_indicator(self, data):
    """添加自定义指标"""
    # 例如添加威廉指标
    high_14 = data['最高'].rolling(14).max()
    low_14 = data['最低'].rolling(14).min()
    williams_r = (high_14 - data['收盘']) / (high_14 - low_14) * 100
    
    return {
        'WILLIAMS_R': williams_r.iloc[-1],
        'SIGNAL': '超买' if williams_r.iloc[-1] > 80 else '超卖' if williams_r.iloc[-1] < 20 else '正常'
    }
```

### **2. 策略回测**
```python
def backtest_strategy(self, data, strategy_rules):
    """简单策略回测"""
    signals = []
    positions = []
    
    for i, row in data.iterrows():
        # 根据策略规则生成信号
        signal = self.generate_signal(row, strategy_rules)
        signals.append(signal)
        
        # 计算收益
        if signal == '买入':
            positions.append(row['收盘'])
        elif signal == '卖出' and positions:
            buy_price = positions.pop(0)
            return_pct = (row['收盘'] - buy_price) / buy_price * 100
            print(f"交易收益: {return_pct:.2f}%")
```

## 📚 **总结**

这个分析程序提供了：

1. **完整的数据获取**：价格、基本面、资金流向
2. **丰富的技术指标**：覆盖趋势、动量、波动、成交量
3. **智能评分系统**：多维度综合评估
4. **灵活的使用方式**：支持批量分析、自定义筛选
5. **实用的输出格式**：易于理解和决策

通过合理使用这个工具，投资者可以：
- 快速筛选优质股票
- 识别买卖时机
- 监控资金流向
- 控制投资风险
- 提高决策效率

记住：**工具是辅助，最终决策还需要结合个人经验和市场判断**。