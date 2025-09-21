#!/usr/bin/env python3
"""
股票真实价值走势分析系统
基于多维度估值模型，提供完整的价值投资分析框架
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValuationResult:
    """估值结果数据类"""
    method: str
    value: float
    confidence: float
    assumptions: Dict
    timestamp: datetime

@dataclass
class ValueTrend:
    """价值趋势数据类"""
    current_price: float
    fair_value_range: Tuple[float, float]
    deviation: float
    trend_direction: str
    strength: str
    confidence: float

class BaseValuationModel(ABC):
    """估值模型基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.confidence = 0.8
    
    @abstractmethod
    def calculate(self, data: Dict) -> ValuationResult:
        """计算估值"""
        pass
    
    @abstractmethod
    def validate_inputs(self, data: Dict) -> bool:
        """验证输入数据"""
        pass

class DCFValuationModel(BaseValuationModel):
    """DCF现金流折现模型"""
    
    def __init__(self):
        super().__init__("DCF")
        self.confidence = 0.85
    
    def calculate(self, data: Dict) -> ValuationResult:
        """DCF估值计算"""
        try:
            # 获取基础数据
            current_fcf = data.get('free_cash_flow', 0)
            shares = data.get('shares_outstanding', 1)
            wacc = data.get('wacc', 0.10)
            terminal_growth = data.get('terminal_growth', 0.03)
            years = data.get('forecast_years', 10)
            
            if current_fcf <= 0 or shares <= 0:
                return ValuationResult("DCF", 0, 0.1, {"error": "Invalid cash flow or shares"}, datetime.now())
            
            # 获取增长率假设
            growth_rates = data.get('growth_rates', self._estimate_growth_rates(data))
            
            # 计算未来现金流
            future_cfs = []
            for i, gr in enumerate(growth_rates[:years]):
                cf = current_fcf * (1 + gr) ** (i + 1)
                pv_cf = cf / (1 + wacc) ** (i + 1)
                future_cfs.append({
                    'year': i + 1,
                    'cash_flow': cf,
                    'present_value': pv_cf,
                    'growth_rate': gr
                })
            
            # 计算终值
            terminal_cf = future_cfs[-1]['cash_flow'] * (1 + terminal_growth)
            terminal_value = terminal_cf / (wacc - terminal_growth)
            pv_terminal = terminal_value / (1 + wacc) ** years
            
            # 企业价值和每股价值
            enterprise_value = sum(cf['present_value'] for cf in future_cfs) + pv_terminal
            net_debt = data.get('net_debt', 0)
            equity_value = enterprise_value - net_debt
            value_per_share = equity_value / shares
            
            assumptions = {
                'wacc': wacc,
                'terminal_growth': terminal_growth,
                'current_fcf': current_fcf,
                'growth_rates': growth_rates,
                'enterprise_value': enterprise_value,
                'equity_value': equity_value
            }
            
            return ValuationResult("DCF", value_per_share, self.confidence, assumptions, datetime.now())
            
        except Exception as e:
            logger.error(f"DCF calculation error: {e}")
            return ValuationResult("DCF", 0, 0.1, {"error": str(e)}, datetime.now())
    
    def _estimate_growth_rates(self, data: Dict) -> List[float]:
        """估算增长率"""
        # 基于历史数据和行业特征
        historical_growth = data.get('historical_growth', 0.10)
        industry_growth = data.get('industry_growth', 0.08)
        
        # 递减增长率模型
        base_rate = min(historical_growth, industry_growth, 0.15)
        return [max(base_rate * (0.9 ** i), 0.03) for i in range(15)]
    
    def validate_inputs(self, data: Dict) -> bool:
        """验证输入数据"""
        required_fields = ['free_cash_flow', 'shares_outstanding']
        return all(field in data for field in required_fields)

class ResourceValuationModel(BaseValuationModel):
    """资源价值评估模型（适用于矿业、石油等资源型公司）"""
    
    def __init__(self):
        super().__init__("Resource")
        self.confidence = 0.80
    
    def calculate(self, data: Dict) -> ValuationResult:
        """资源价值计算"""
        try:
            resources = data.get('resources', {})
            shares = data.get('shares_outstanding', 1)
            
            if not resources or shares <= 0:
                return ValuationResult("Resource", 0, 0.1, {"error": "No resources or invalid shares"}, datetime.now())
            
            total_resource_value = 0
            resource_details = {}
            
            for resource_name, resource_data in resources.items():
                reserves = resource_data.get('reserves', 0)
                price_per_unit = resource_data.get('price_per_unit', 0)
                cost_per_unit = resource_data.get('cost_per_unit', 0)
                recovery_rate = resource_data.get('recovery_rate', 0.7)
                
                if reserves <= 0 or price_per_unit <= 0:
                    continue
                
                # 计算资源价值
                gross_value = reserves * price_per_unit
                total_cost = reserves * cost_per_unit
                net_value = gross_value - total_cost
                
                # 考虑开采率和时间价值
                discount_factor = resource_data.get('discount_factor', 0.5)
                adjusted_value = net_value * recovery_rate * discount_factor
                
                resource_details[resource_name] = {
                    'reserves': reserves,
                    'gross_value': gross_value,
                    'total_cost': total_cost,
                    'net_value': net_value,
                    'adjusted_value': adjusted_value,
                    'recovery_rate': recovery_rate,
                    'discount_factor': discount_factor
                }
                
                total_resource_value += adjusted_value
            
            # 每股资源价值
            value_per_share = total_resource_value / shares
            
            assumptions = {
                'total_resource_value': total_resource_value,
                'resources': resource_details,
                'recovery_rate': 0.7,
                'discount_factor': 0.5
            }
            
            return ValuationResult("Resource", value_per_share, self.confidence, assumptions, datetime.now())
            
        except Exception as e:
            logger.error(f"Resource valuation error: {e}")
            return ValuationResult("Resource", 0, 0.1, {"error": str(e)}, datetime.now())
    
    def validate_inputs(self, data: Dict) -> bool:
        """验证输入数据"""
        return 'resources' in data and 'shares_outstanding' in data

class PBROEValuationModel(BaseValuationModel):
    """PB-ROE估值模型"""
    
    def __init__(self):
        super().__init__("PB-ROE")
        self.confidence = 0.75
    
    def calculate(self, data: Dict) -> ValuationResult:
        """PB-ROE估值计算"""
        try:
            roe = data.get('roe', 0.10)
            bvps = data.get('book_value_per_share', 10.0)
            required_return = data.get('required_return', 0.12)
            industry_avg_pb = data.get('industry_avg_pb', 1.5)
            
            if roe <= 0 or bvps <= 0:
                return ValuationResult("PB-ROE", bvps, 0.3, {"error": "Invalid ROE or BVPS"}, datetime.now())
            
            # 基于ROE计算合理PB
            fair_pb = roe / required_return
            
            # 考虑行业溢价/折价
            if roe > 0.15:  # ROE优秀
                premium = min((roe - 0.15) * 5, 0.5)
                adjusted_pb = fair_pb * (1 + premium)
            elif roe < 0.08:  # ROE较低
                discount = min((0.08 - roe) * 3, 0.3)
                adjusted_pb = fair_pb * (1 - discount)
            else:
                adjusted_pb = fair_pb
            
            # 限制PB在合理范围
            adjusted_pb = max(0.5, min(adjusted_pb, 3.0))
            
            value_per_share = adjusted_pb * bvps
            
            assumptions = {
                'roe': roe,
                'bvps': bvps,
                'fair_pb': fair_pb,
                'adjusted_pb': adjusted_pb,
                'required_return': required_return,
                'industry_avg_pb': industry_avg_pb
            }
            
            return ValuationResult("PB-ROE", value_per_share, self.confidence, assumptions, datetime.now())
            
        except Exception as e:
            logger.error(f"PB-ROE calculation error: {e}")
            return ValuationResult("PB-ROE", 0, 0.1, {"error": str(e)}, datetime.now())
    
    def validate_inputs(self, data: Dict) -> bool:
        """验证输入数据"""
        return 'roe' in data and 'book_value_per_share' in data

class AssetBasedValuationModel(BaseValuationModel):
    """资产基础估值模型"""
    
    def __init__(self):
        super().__init__("Asset-Based")
        self.confidence = 0.70
    
    def calculate(self, data: Dict) -> ValuationResult:
        """资产基础估值"""
        try:
            total_assets = data.get('total_assets', 0)
            total_liabilities = data.get('total_liabilities', 0)
            shares = data.get('shares_outstanding', 1)
            liquidation_discount = data.get('liquidation_discount', 0.3)
            
            if total_assets <= 0 or shares <= 0:
                return ValuationResult("Asset-Based", 0, 0.1, {"error": "Invalid assets or shares"}, datetime.now())
            
            # 计算净资产
            net_assets = total_assets - total_liabilities
            
            # 考虑清算折价
            adjusted_assets = net_assets * (1 - liquidation_discount)
            
            # 每股价值
            value_per_share = max(adjusted_assets / shares, 0)
            
            assumptions = {
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'net_assets': net_assets,
                'liquidation_discount': liquidation_discount,
                'adjusted_assets': adjusted_assets
            }
            
            return ValuationResult("Asset-Based", value_per_share, self.confidence, assumptions, datetime.now())
            
        except Exception as e:
            logger.error(f"Asset-based valuation error: {e}")
            return ValuationResult("Asset-Based", 0, 0.1, {"error": str(e)}, datetime.now())
    
    def validate_inputs(self, data: Dict) -> bool:
        """验证输入数据"""
        return 'total_assets' in data and 'total_liabilities' in data and 'shares_outstanding' in data

class ValueTrendAnalyzer:
    """价值趋势分析器"""
    
    def __init__(self):
        self.deviation_thresholds = {
            'severely_overvalued': 0.50,   # 50%以上高估
            'overvalued': 0.20,            # 20-50%高估
            'fair_value': 0.20,            # ±20%合理
            'undervalued': -0.20,          # -20%到-50%低估
            'severely_undervalued': -0.50  # -50%以下严重低估
        }
    
    def analyze_value_trend(self, current_price: float, valuation_results: List[ValuationResult]) -> ValueTrend:
        """分析价值趋势"""
        try:
            # 计算加权平均价值
            total_confidence = sum(result.confidence for result in valuation_results)
            if total_confidence == 0:
                return ValueTrend(current_price, (0, 0), 0, "unknown", "weak", 0)
            
            weighted_value = sum(result.value * result.confidence for result in valuation_results) / total_confidence
            
            # 计算价值区间（置信区间）
            values = [result.value for result in valuation_results]
            fair_value_low = np.percentile(values, 25)
            fair_value_high = np.percentile(values, 75)
            
            # 计算偏离度
            deviation = (current_price - weighted_value) / weighted_value
            
            # 判断趋势方向和强度
            if deviation > self.deviation_thresholds['severely_overvalued']:
                trend_direction = "severely_overvalued"
                strength = "strong"
            elif deviation > self.deviation_thresholds['overvalued']:
                trend_direction = "overvalued"
                strength = "moderate"
            elif abs(deviation) <= self.deviation_thresholds['fair_value']:
                trend_direction = "fair_value"
                strength = "weak"
            elif deviation > self.deviation_thresholds['undervalued']:
                trend_direction = "undervalued"
                strength = "moderate"
            else:
                trend_direction = "severely_undervalued"
                strength = "strong"
            
            # 计算整体置信度
            confidence = min(total_confidence / len(valuation_results), 1.0)
            
            return ValueTrend(
                current_price=current_price,
                fair_value_range=(fair_value_low, fair_value_high),
                deviation=deviation,
                trend_direction=trend_direction,
                strength=strength,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Value trend analysis error: {e}")
            return ValueTrend(current_price, (0, 0), 0, "error", "weak", 0)
    
    def generate_value_insights(self, value_trend: ValueTrend, valuation_results: List[ValuationResult]) -> Dict:
        """生成价值洞察"""
        insights = {
            'summary': self._generate_summary(value_trend),
            'risk_assessment': self._assess_risk(value_trend),
            'investment_recommendation': self._generate_recommendation(value_trend),
            'timing_suggestion': self._generate_timing_suggestion(value_trend),
            'key_factors': self._identify_key_factors(valuation_results)
        }
        return insights
    
    def _generate_summary(self, value_trend: ValueTrend) -> str:
        """生成总结"""
        direction_map = {
            "severely_overvalued": "严重高估",
            "overvalued": "高估",
            "fair_value": "合理估值",
            "undervalued": "低估",
            "severely_undervalued": "严重低估",
            "unknown": "未知",
            "error": "分析错误"
        }
        
        fair_value_mid = (value_trend.fair_value_range[0] + value_trend.fair_value_range[1]) / 2
        deviation_pct = value_trend.deviation * 100
        
        return f"当前价格相对于合理价值({fair_value_mid:.2f}){direction_map.get(value_trend.trend_direction, '未知')},偏离度为{deviation_pct:.1f}%"
    
    def _assess_risk(self, value_trend: ValueTrend) -> str:
        """风险评估"""
        if value_trend.trend_direction in ["severely_overvalued", "severely_undervalued"]:
            return "高风险 - 价格严重偏离内在价值，面临价值回归风险"
        elif value_trend.trend_direction in ["overvalued", "undervalued"]:
            return "中等风险 - 价格偏离内在价值，需要关注价值回归时机"
        else:
            return "低风险 - 价格接近内在价值，估值合理"
    
    def _generate_recommendation(self, value_trend: ValueTrend) -> str:
        """生成投资建议"""
        recommendations = {
            "severely_overvalued": "建议卖出或避免买入，等待价值回归",
            "overvalued": "建议减仓或等待更好买入时机",
            "fair_value": "建议持有观望，等待明确信号",
            "undervalued": "建议考虑买入，但需分批建仓",
            "severely_undervalued": "强烈建议买入，这是难得的价值投资机会"
        }
        return recommendations.get(value_trend.trend_direction, "建议进一步分析")
    
    def _generate_timing_suggestion(self, value_trend: ValueTrend) -> str:
        """生成时机建议"""
        if value_trend.trend_direction == "severely_undervalued":
            return "立即行动 - 分批建仓，越跌越买"
        elif value_trend.trend_direction == "undervalued":
            return "逐步行动 - 分3-6个月建仓"
        elif value_trend.trend_direction == "fair_value":
            return "等待时机 - 关注价值变化"
        else:
            return "观望等待 - 等待价值回归"
    
    def _identify_key_factors(self, valuation_results: List[ValuationResult]) -> List[str]:
        """识别关键因素"""
        key_factors = []
        
        for result in valuation_results:
            if result.method == "DCF":
                key_factors.append("未来现金流增长能力")
            elif result.method == "Resource":
                key_factors.append("资源储量和价格")
            elif result.method == "PB-ROE":
                key_factors.append("净资产收益率")
            elif result.method == "Asset-Based":
                key_factors.append("资产质量和负债情况")
        
        return list(set(key_factors))

class StockValueAnalysisSystem:
    """股票真实价值分析系统主类"""
    
    def __init__(self, db_path: str = "stock_value_analysis.db"):
        self.db_path = db_path
        self.valuation_models = {
            'dcf': DCFValuationModel(),
            'resource': ResourceValuationModel(),
            'pb_roe': PBROEValuationModel(),
            'asset_based': AssetBasedValuationModel()
        }
        self.trend_analyzer = ValueTrendAnalyzer()
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建估值结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS valuation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                method TEXT NOT NULL,
                value REAL NOT NULL,
                confidence REAL NOT NULL,
                assumptions TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建价值趋势表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS value_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                current_price REAL NOT NULL,
                fair_value_low REAL NOT NULL,
                fair_value_high REAL NOT NULL,
                deviation REAL NOT NULL,
                trend_direction TEXT NOT NULL,
                strength TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_stock_data(self, symbol: str) -> Dict:
        """获取股票基础数据"""
        try:
            logger.info(f"Getting stock data for {symbol}")
            
            # 获取基本信息
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            info_dict = {}
            if not stock_info.empty:
                info_dict = dict(zip(stock_info['item'], stock_info['value']))
            
            # 获取财务数据
            financial_data = {}
            try:
                financial_abstract = ak.stock_financial_abstract(symbol=symbol)
                if not financial_abstract.empty:
                    latest = financial_abstract.iloc[0]
                    financial_data = {
                        'net_profit': latest.get('净利润', 0),
                        'roe': latest.get('净资产收益率', 0.10),
                        'eps': latest.get('基本每股收益', 1.0),
                        'bvps': latest.get('每股净资产', 10.0),
                        'revenue': latest.get('营业收入', 0),
                        'free_cash_flow': latest.get('净利润', 0) * 0.8  # 粗略估算
                    }
            except:
                financial_data = {
                    'net_profit': 0,
                    'roe': 0.10,
                    'eps': 1.0,
                    'bvps': 10.0,
                    'revenue': 0,
                    'free_cash_flow': 1000000000  # 默认值10亿
                }
            
            # 获取当前股价
            current_data = ak.stock_zh_a_spot_em()
            current_price = 25.0  # 默认值
            if not current_data.empty:
                stock_data = current_data[current_data['代码'] == symbol]
                if not stock_data.empty:
                    current_price = stock_data.iloc[0]['最新价']
            
            # 获取股本信息
            shares = 1000000000  # 默认值10亿股
            try:
                # 这里需要根据具体股票调整
                if symbol == '601899':  # 紫金矿业
                    shares = 26470000000
                elif symbol == '000001':  # 平安银行
                    shares = 19400000000
                else:
                    # 估算股本
                    market_cap = float(info_dict.get('总市值', 100000000000))
                    shares = int(market_cap / current_price)
            except:
                shares = 1000000000
            
            # 获取资产负债表数据
            balance_data = {}
            try:
                # 简化的资产负债表数据
                total_assets = float(info_dict.get('总资产', 100000000000))
                total_liabilities = float(info_dict.get('总负债', 50000000000))
                balance_data = {
                    'total_assets': total_assets,
                    'total_liabilities': total_liabilities,
                    'net_assets': total_assets - total_liabilities
                }
            except:
                balance_data = {
                    'total_assets': 100000000000,
                    'total_liabilities': 50000000000,
                    'net_assets': 50000000000
                }
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'shares_outstanding': shares,
                'financial_data': financial_data,
                'balance_data': balance_data,
                'stock_info': info_dict,
                'timestamp': datetime.now()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting stock data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'current_price': 25.0,
                'shares_outstanding': 1000000000,
                'financial_data': {'free_cash_flow': 1000000000, 'roe': 0.10, 'bvps': 10.0},
                'balance_data': {'total_assets': 100000000000, 'total_liabilities': 50000000000},
                'stock_info': {},
                'timestamp': datetime.now()
            }
    
    def run_comprehensive_analysis(self, symbol: str, industry_data: Optional[Dict] = None) -> Dict:
        """运行综合分析"""
        logger.info(f"Running comprehensive analysis for {symbol}")
        
        # 获取基础数据
        stock_data = self.get_stock_data(symbol)
        current_price = stock_data['current_price']
        
        # 准备估值输入数据
        valuation_inputs = {
            'dcf': {
                'free_cash_flow': stock_data['financial_data'].get('free_cash_flow', 1000000000),
                'shares_outstanding': stock_data['shares_outstanding'],
                'wacc': 0.10,
                'terminal_growth': 0.03,
                'historical_growth': 0.10,
                'industry_growth': 0.08
            },
            'resource': self._get_resource_data(symbol, stock_data),
            'pb_roe': {
                'roe': stock_data['financial_data'].get('roe', 0.10),
                'book_value_per_share': stock_data['financial_data'].get('bvps', 10.0),
                'required_return': 0.12,
                'industry_avg_pb': 1.5
            },
            'asset_based': {
                'total_assets': stock_data['balance_data'].get('total_assets', 100000000000),
                'total_liabilities': stock_data['balance_data'].get('total_liabilities', 50000000000),
                'shares_outstanding': stock_data['shares_outstanding'],
                'liquidation_discount': 0.3
            }
        }
        
        # 运行各估值模型
        valuation_results = []
        for method, model in self.valuation_models.items():
            if model.validate_inputs(valuation_inputs[method]):
                result = model.calculate(valuation_inputs[method])
                valuation_results.append(result)
                
                # 保存到数据库
                self._save_valuation_result(symbol, result)
        
        # 分析价值趋势
        if valuation_results:
            value_trend = self.trend_analyzer.analyze_value_trend(current_price, valuation_results)
            insights = self.trend_analyzer.generate_value_insights(value_trend, valuation_results)
            
            # 保存趋势分析结果
            self._save_value_trend(symbol, value_trend)
        else:
            value_trend = ValueTrend(current_price, (0, 0), 0, "error", "weak", 0)
            insights = {}
        
        # 生成综合报告
        comprehensive_report = self._generate_comprehensive_report(symbol, stock_data, valuation_results, value_trend, insights)
        
        return comprehensive_report
    
    def _get_resource_data(self, symbol: str, stock_data: Dict) -> Dict:
        """获取资源数据（针对资源型公司）"""
        # 这里可以根据不同公司配置不同的资源数据
        # 以紫金矿业为例
        if symbol == '601899':
            return {
                'shares_outstanding': stock_data['shares_outstanding'],
                'resources': {
                    'gold': {
                        'reserves': 3000,  # 吨
                        'unit': '吨',
                        'price_per_unit': 450000000,  # 元/吨
                        'cost_per_unit': 250000000,   # 元/吨
                        'recovery_rate': 0.7,
                        'discount_factor': 0.5
                    },
                    'copper': {
                        'reserves': 75000000,  # 吨
                        'unit': '吨',
                        'price_per_unit': 70000,    # 元/吨
                        'cost_per_unit': 40000,     # 元/吨
                        'recovery_rate': 0.7,
                        'discount_factor': 0.5
                    },
                    'zinc': {
                        'reserves': 10000000,  # 吨
                        'unit': '吨',
                        'price_per_unit': 25000,    # 元/吨
                        'cost_per_unit': 15000,     # 元/吨
                        'recovery_rate': 0.7,
                        'discount_factor': 0.5
                    }
                }
            }
        else:
            # 默认资源数据（可根据需要扩展）
            return {
                'shares_outstanding': stock_data['shares_outstanding'],
                'resources': {}
            }
    
    def _save_valuation_result(self, symbol: str, result: ValuationResult):
        """保存估值结果到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO valuation_results (symbol, method, value, confidence, assumptions, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                result.method,
                result.value,
                result.confidence,
                json.dumps(result.assumptions),
                result.timestamp
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving valuation result: {e}")
    
    def _save_value_trend(self, symbol: str, value_trend: ValueTrend):
        """保存价值趋势到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO value_trends (symbol, current_price, fair_value_low, fair_value_high, 
                                        deviation, trend_direction, strength, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                value_trend.current_price,
                value_trend.fair_value_range[0],
                value_trend.fair_value_range[1],
                value_trend.deviation,
                value_trend.trend_direction,
                value_trend.strength,
                value_trend.confidence,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving value trend: {e}")
    
    def _generate_comprehensive_report(self, symbol: str, stock_data: Dict, 
                                     valuation_results: List[ValuationResult], 
                                     value_trend: ValueTrend, insights: Dict) -> Dict:
        """生成综合分析报告"""
        
        # 估值结果汇总
        valuation_summary = {}
        for result in valuation_results:
            valuation_summary[result.method] = {
                'value': result.value,
                'confidence': result.confidence,
                'assumptions': result.assumptions
            }
        
        # 计算加权平均价值
        total_confidence = sum(result.confidence for result in valuation_results)
        weighted_avg_value = sum(result.value * result.confidence for result in valuation_results) / total_confidence if total_confidence > 0 else 0
        
        # 生成投资建议
        investment_recommendation = self._generate_detailed_recommendation(value_trend, valuation_results)
        
        report = {
            'symbol': symbol,
            'company_name': stock_data['stock_info'].get('股票简称', symbol),
            'analysis_date': datetime.now().isoformat(),
            'current_price': stock_data['current_price'],
            'valuation_summary': valuation_summary,
            'weighted_average_value': weighted_avg_value,
            'value_trend': {
                'deviation': value_trend.deviation,
                'trend_direction': value_trend.trend_direction,
                'strength': value_trend.strength,
                'confidence': value_trend.confidence,
                'fair_value_range': value_trend.fair_value_range
            },
            'insights': insights,
            'investment_recommendation': investment_recommendation,
            'data_quality': self._assess_data_quality(stock_data),
            'risk_level': self._assess_overall_risk(value_trend, valuation_results)
        }
        
        return report
    
    def _generate_detailed_recommendation(self, value_trend: ValueTrend, valuation_results: List[ValuationResult]) -> Dict:
        """生成详细的投资建议"""
        
        base_recommendation = self.trend_analyzer._generate_recommendation(value_trend)
        
        # 基于不同估值方法的具体建议
        specific_recommendations = {}
        for result in valuation_results:
            if result.method == "DCF":
                dcf_value = result.value
                specific_recommendations['DCF'] = {
                    'value': dcf_value,
                    'advice': "关注公司盈利能力和现金流增长",
                    'key_factors': ["未来业绩增长", "现金流稳定性", "资本回报率"]
                }
            elif result.method == "Resource":
                resource_value = result.value
                specific_recommendations['Resource'] = {
                    'value': resource_value,
                    'advice': "关注资源价格走势和储量变化",
                    'key_factors': ["大宗商品价格", "资源储量", "开采成本"]
                }
            elif result.method == "PB-ROE":
                pb_roe_value = result.value
                specific_recommendations['PB-ROE'] = {
                    'value': pb_roe_value,
                    'advice': "关注净资产收益率和资产质量",
                    'key_factors': ["ROE水平", "资产质量", "行业对比"]
                }
        
        return {
            'summary': base_recommendation,
            'specific_recommendations': specific_recommendations,
            'risk_management': self._generate_risk_management_advice(value_trend),
            'timing_strategy': self._generate_timing_strategy(value_trend)
        }
    
    def _generate_risk_management_advice(self, value_trend: ValueTrend) -> str:
        """生成风险管理建议"""
        if value_trend.trend_direction in ["severely_overvalued", "severely_undervalued"]:
            return "严格控制仓位，分批建仓/减仓，设置止损点"
        elif value_trend.trend_direction in ["overvalued", "undervalued"]:
            return "适度控制仓位，关注价值变化，灵活调整"
        else:
            return "正常仓位管理，关注基本面变化"
    
    def _generate_timing_strategy(self, value_trend: ValueTrend) -> str:
        """生成时机策略建议"""
        if value_trend.trend_direction == "severely_undervalued":
            return "分6-12个月逐步建仓，越跌越买"
        elif value_trend.trend_direction == "undervalued":
            return "分3-6个月建仓，关注价值底"
        elif value_trend.trend_direction == "fair_value":
            return "持有观望，等待明确信号"
        else:
            return "等待更好时机，不急于行动"
    
    def _assess_data_quality(self, stock_data: Dict) -> str:
        """评估数据质量"""
        # 简化的数据质量评估
        has_financial = len(stock_data.get('financial_data', {})) > 0
        has_balance = len(stock_data.get('balance_data', {})) > 0
        has_info = len(stock_data.get('stock_info', {})) > 0
        
        if has_financial and has_balance and has_info:
            return "高质量 - 完整财务数据"
        elif has_financial and has_balance:
            return "中等质量 - 基本财务数据完整"
        else:
            return "低质量 - 使用估算值"
    
    def _assess_overall_risk(self, value_trend: ValueTrend, valuation_results: List[ValuationResult]) -> str:
        """评估整体风险"""
        # 基于价值偏离度和估值离散度
        deviation = abs(value_trend.deviation)
        confidence = value_trend.confidence
        
        if deviation > 0.5:
            return "高风险"
        elif deviation > 0.2:
            return "中等风险"
        else:
            return "低风险"
    
    def get_historical_analysis(self, symbol: str, days: int = 30) -> List[Dict]:
        """获取历史分析数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取历史价值趋势数据
            cursor.execute('''
                SELECT * FROM value_trends 
                WHERE symbol = ? 
                AND timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
            ''', (symbol, days))
            
            rows = cursor.fetchall()
            conn.close()
            
            historical_data = []
            for row in rows:
                historical_data.append({
                    'date': row[9],  # timestamp
                    'current_price': row[2],
                    'fair_value_low': row[3],
                    'fair_value_high': row[4],
                    'deviation': row[5],
                    'trend_direction': row[6],
                    'strength': row[7],
                    'confidence': row[8]
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical analysis: {e}")
            return []
    
    def set_alert_thresholds(self, symbol: str, thresholds: Dict):
        """设置预警阈值"""
        # 实现预警功能
        pass

def main():
    """主函数 - 演示系统功能"""
    print("=" * 60)
    print("股票真实价值走势分析系统")
    print("=" * 60)
    
    # 创建系统实例
    system = StockValueAnalysisSystem()
    
    # 测试股票列表
    test_stocks = ['601899', '000001', '600519']  # 紫金矿业、平安银行、贵州茅台
    
    for symbol in test_stocks:
        print(f"\n分析股票: {symbol}")
        print("-" * 40)
        
        try:
            # 运行综合分析
            result = system.run_comprehensive_analysis(symbol)
            
            # 输出核心结果
            print(f"股票名称: {result['company_name']}")
            print(f"当前价格: ¥{result['current_price']:.2f}")
            print(f"加权平均价值: ¥{result['weighted_average_value']:.2f}")
            print(f"价值偏离度: {result['value_trend']['deviation']:.1%}")
            print(f"趋势判断: {result['value_trend']['trend_direction']}")
            print(f"投资建议: {result['insights']['summary']}")
            print(f"数据质量: {result['data_quality']}")
            print(f"风险等级: {result['risk_level']}")
            
            # 输出各估值方法结果
            print(f"\n详细估值结果:")
            for method, data in result['valuation_summary'].items():
                print(f"  {method}: ¥{data['value']:.2f} (置信度: {data['confidence']:.1%})")
            
        except Exception as e:
            print(f"分析失败: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("系统功能演示完成")
    print("=" * 60)

if __name__ == "__main__":
    main()