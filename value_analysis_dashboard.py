#!/usr/bin/env python3
"""
股票真实价值分析系统可视化界面
提供交互式的价值分析仪表板
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta
import json
from stock_value_analysis_system import StockValueAnalysisSystem, ValueTrend, ValuationResult
import warnings
warnings.filterwarnings('ignore')

# 配置页面
st.set_page_config(
    page_title="股票真实价值分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}

.value-insight {
    background-color: #e8f4f8;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
}

.warning-card {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ffc107;
}

.danger-card {
    background-color: #f8d7da;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #dc3545;
}
</style>
""", unsafe_allow_html=True)

class ValueAnalysisDashboard:
    """价值分析仪表板类"""
    
    def __init__(self):
        self.system = StockValueAnalysisSystem()
        self.init_session_state()
    
    def init_session_state(self):
        """初始化会话状态"""
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = ['601899', '000001', '600519']
        if 'alerts_enabled' not in st.session_state:
            st.session_state.alerts_enabled = True
    
    def run_dashboard(self):
        """运行仪表板"""
        # 主标题
        st.markdown('<h1 class="main-header">📊 股票真实价值走势分析系统</h1>', unsafe_allow_html=True)
        
        # 侧边栏
        with st.sidebar:
            self.render_sidebar()
        
        # 主内容区域
        self.render_main_content()
    
    def render_sidebar(self):
        """渲染侧边栏"""
        st.header("⚙️ 系统配置")
        
        # 股票输入
        st.subheader("🔍 股票分析")
        symbol = st.text_input("股票代码", value="601899", placeholder="输入股票代码，如：601899")
        
        if st.button("🔍 分析股票", type="primary"):
            with st.spinner(f"正在分析 {symbol}..."):
                self.analyze_stock(symbol)
        
        # 快捷分析按钮
        st.subheader("📈 快捷分析")
        quick_symbols = ['601899', '000001', '600519', '000858', '002415']
        for sym in quick_symbols:
            if st.button(f"分析 {sym}"):
                self.analyze_stock(sym)
        
        # 监控列表
        st.subheader("⭐ 监控列表")
        for symbol in st.session_state.watchlist:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📊 {symbol}", key=f"watch_{symbol}"):
                    self.analyze_stock(symbol)
            with col2:
                if st.button("❌", key=f"remove_{symbol}"):
                    st.session_state.watchlist.remove(symbol)
                    st.rerun()
        
        # 添加股票到监控列表
        new_symbol = st.text_input("添加股票到监控列表", placeholder="输入股票代码")
        if st.button("➕ 添加") and new_symbol:
            if new_symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_symbol)
                st.rerun()
        
        # 预警设置
        st.subheader("🚨 预警设置")
        st.session_state.alerts_enabled = st.checkbox("启用价值偏离预警", value=True)
        
        if st.session_state.alerts_enabled:
            alert_threshold = st.slider("预警阈值", min_value=0.1, max_value=1.0, value=0.3, step=0.05,
                                      help="当价值偏离度超过此阈值时发出预警")
            st.session_state.alert_threshold = alert_threshold
        
        # 系统信息
        st.subheader("ℹ️ 系统信息")
        st.info(f"">
        **系统功能**：
        • 多维度估值分析\n
        • 价值趋势判断\n
        • 投资建议生成\n
        • 风险等级评估\n
        
        **估值方法**：\n
        • DCF现金流折现\n
        • 资源重置价值\n
        • PB-ROE模型\n
        • 资产基础估值
        """)
    
    def render_main_content(self):
        """渲染主内容区域"""
        # 如果没有分析结果，显示欢迎界面
        if not st.session_state.analysis_results:
            self.render_welcome_screen()
            return
        
        # 获取当前显示的股票（默认为最新分析的股票）
        current_symbol = list(st.session_state.analysis_results.keys())[-1]
        result = st.session_state.analysis_results[current_symbol]
        
        # 标签页布局
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 概览", "🔍 详细分析", "📊 历史趋势", "⚠️ 风险分析", "💡 投资建议"])
        
        with tab1:
            self.render_overview(result)
        
        with tab2:
            self.render_detailed_analysis(result)
        
        with tab3:
            self.render_historical_analysis(current_symbol)
        
        with tab4:
            self.render_risk_analysis(result)
        
        with tab5:
            self.render_investment_advice(result)
    
    def render_welcome_screen(self):
        """渲染欢迎界面"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ## 🎯 欢迎使用股票真实价值分析系统
            
            ### 系统特色
            🏔️ **多维度估值** - 融合DCF、资源价值、PB-ROE等多种估值方法\n
            📊 **趋势分析** - 智能判断价值走向和投资时机\n
            🚨 **预警系统** - 实时监控价值偏离度\n
            💡 **投资建议** - 基于价值分析的专业建议
            
            ### 快速开始
            1. **输入股票代码** - 在左侧输入您要分析的股票\n
            2. **运行分析** - 点击分析按钮开始价值评估\n
            3. **查看结果** - 在标签页中查看详细分析结果\n
            4. **设置监控** - 添加股票到监控列表，实时跟踪
            
            ### 核心功能
            - **真实价值计算**：基于多种估值模型的综合评估\n
            - **价值偏离分析**：识别价格与价值的偏离程度\n
            - **趋势走向判断**：预测价值走向和变化趋势\n
            - **投资时机建议**：提供基于价值的买卖建议
            """)
            
            # 示例分析按钮
            if st.button("🚀 开始分析紫金矿业", type="primary", use_container_width=True):
                self.analyze_stock("601899")
                st.rerun()
    
    def analyze_stock(self, symbol: str):
        """分析股票"""
        try:
            # 运行综合分析
            result = self.system.run_comprehensive_analysis(symbol)
            
            # 保存结果到会话状态
            st.session_state.analysis_results[symbol] = result
            
            # 检查是否需要预警
            if st.session_state.get('alerts_enabled', False):
                self.check_alerts(symbol, result)
                
        except Exception as e:
            st.error(f"分析股票 {symbol} 时出错：{e}")
    
    def check_alerts(self, symbol: str, result: Dict):
        """检查预警条件"""
        try:
            deviation = abs(result['value_trend']['deviation'])
            threshold = st.session_state.get('alert_threshold', 0.3)
            
            if deviation > threshold:
                trend_direction = result['value_trend']['trend_direction']
                
                if 'severely_undervalued' in trend_direction:
                    st.success(f"🚨 {symbol} 出现严重低估机会！偏离度：{deviation:.1%}")
                elif 'severely_overvalued' in trend_direction:
                    st.warning(f"⚠️ {symbol} 出现严重高估风险！偏离度：{deviation:.1%}")
                else:
                    st.info(f"📊 {symbol} 价值偏离度较高：{deviation:.1%}")
                    
        except Exception as e:
            logger.error(f"预警检查失败：{e}")
    
    def render_overview(self, result: Dict):
        """渲染概览页面"""
        st.header("📈 价值分析概览")
        
        # 核心指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = result['current_price']
            fair_value = result['weighted_average_value']
            deviation = result['value_trend']['deviation']
            
            st.metric(
                label="当前价格",
                value=f"¥{current_price:.2f}",
                delta=f"{deviation:.1%}"
            )
        
        with col2:
            fair_value_low, fair_value_high = result['value_trend']['fair_value_range']
            st.metric(
                label="合理价值区间",
                value=f"¥{fair_value_low:.2f} - ¥{fair_value_high:.2f}",
                delta=f"均值: ¥{(fair_value_low + fair_value_high)/2:.2f}"
            )
        
        with col3:
            trend_direction = result['value_trend']['trend_direction']
            strength = result['value_trend']['strength']
            
            # 根据趋势方向设置颜色
            if 'undervalued' in trend_direction:
                color = "🟢"
            elif 'overvalued' in trend_direction:
                color = "🔴"
            else:
                color = "🟡"
            
            st.metric(
                label=f"{color} 趋势判断",
                value=trend_direction.replace('_', ' ').title(),
                delta=f"强度: {strength}"
            )
        
        with col4:
            confidence = result['value_trend']['confidence']
            data_quality = result['data_quality']
            
            st.metric(
                label="分析置信度",
                value=f"{confidence:.1%}",
                delta=f"数据质量: {data_quality}"
            )
        
        # 价值偏离度可视化
        st.subheader("📊 价值偏离度分析")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 创建价值偏离度图表
            fig = self.create_deviation_chart(result)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 价值状态指示器
            self.render_value_status_indicator(result)
        
        # 估值方法对比
        st.subheader("🔍 多维度估值对比")
        self.render_valuation_comparison(result)
    
    def create_deviation_chart(self, result: Dict) -> go.Figure:
        """创建价值偏离度图表"""
        current_price = result['current_price']
        fair_value_low, fair_value_high = result['value_trend']['fair_value_range']
        fair_value_mid = (fair_value_low + fair_value_high) / 2
        deviation = result['value_trend']['deviation']
        
        fig = go.Figure()
        
        # 合理价值区间
        fig.add_shape(type="rect",
                     x0=0, y0=fair_value_low, x1=1, y1=fair_value_high,
                     fillcolor="lightblue", opacity=0.3,
                     line=dict(color="blue", width=2),
                     name="合理价值区间")
        
        # 当前价格
        fig.add_hline(y=current_price, line_color="red", line_width=3,
                     annotation_text=f"当前价格 ¥{current_price:.2f}",
                     annotation_position="right")
        
        # 均值线
        fig.add_hline(y=fair_value_mid, line_color="green", line_width=2, line_dash="dash",
                     annotation_text=f"合理价值 ¥{fair_value_mid:.2f}",
                     annotation_position="left")
        
        # 偏离度标注
        fig.add_annotation(x=0.5, y=current_price,
                          text=f"偏离度: {deviation:.1%}",
                          showarrow=True, arrowhead=2,
                          bgcolor="yellow", opacity=0.8)
        
        fig.update_layout(
            title="价值偏离度可视化",
            xaxis_title="",
            yaxis_title="价格 (元)",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def render_value_status_indicator(self, result: Dict):
        """渲染价值状态指示器"""
        trend_direction = result['value_trend']['trend_direction']
        deviation = result['value_trend']['deviation']
        
        # 根据趋势方向显示不同状态
        if 'severely_undervalued' in trend_direction:
            st.markdown('''
            <div class="value-insight">
            <h4>🟢 严重低估机会</h4>
            <p>当前价格严重低于内在价值，可能是难得的投资机会</p>
            </div>
            ''', unsafe_allow_html=True)
        elif 'undervalued' in trend_direction:
            st.markdown('''
            <div class="value-insight">
            <h4>🟡 轻度低估</h4>
            <p>当前价格低于内在价值，可以考虑逐步买入</p>
            </div>
            ''', unsafe_allow_html=True)
        elif 'overvalued' in trend_direction:
            st.markdown('''
            <div class="warning-card">
            <h4>🟠 轻度高估</h4>
            <p>当前价格高于内在价值，需要谨慎操作</p>
            </div>
            ''', unsafe_allow_html=True)
        elif 'severely_overvalued' in trend_direction:
            st.markdown('''
            <div class="danger-card">
            <h4>🔴 严重高估风险</h4>
            <p>当前价格严重高于内在价值，面临价值回归风险</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="metric-card">
            <h4>⚪ 合理估值</h4>
            <p>当前价格接近内在价值，估值合理</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # 关键指标
        st.metric("偏离程度", f"{abs(deviation):.1%}")
        st.metric("趋势强度", result['value_trend']['strength'].title())
    
    def render_valuation_comparison(self, result: Dict):
        """渲染估值方法对比"""
        valuation_summary = result['valuation_summary']
        
        if not valuation_summary:
            st.info("暂无估值数据")
            return
        
        # 创建对比图表
        methods = list(valuation_summary.keys())
        values = [data['value'] for data in valuation_summary.values()]
        confidences = [data['confidence'] for data in valuation_summary.values()]
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("估值对比", "置信度对比"),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 估值对比
        fig.add_trace(
            go.Bar(x=methods, y=values, name="估值", marker_color="lightblue"),
            row=1, col=1
        )
        
        # 添加当前价格线
        current_price = result['current_price']
        fig.add_hline(y=current_price, line_dash="dash", line_color="red",
                     annotation_text=f"当前价格: ¥{current_price:.2f}")
        
        # 置信度对比
        fig.add_trace(
            go.Bar(x=methods, y=confidences, name="置信度", marker_color="lightgreen"),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        fig.update_xaxes(title_text="估值方法", row=1, col=1)
        fig.update_yaxes(title_text="估值 (元)", row=1, col=1)
        fig.update_xaxes(title_text="估值方法", row=1, col=2)
        fig.update_yaxes(title_text="置信度", row=1, col=2)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 详细数据表格
        with st.expander("📋 查看详细估值数据"):
            df_data = []
            for method, data in valuation_summary.items():
                df_data.append({
                    "估值方法": method,
                    "估值结果": f"¥{data['value']:.2f}",
                    "置信度": f"{data['confidence']:.1%}",
                    "相对当前价格": f"{(data['value'] - result['current_price']) / result['current_price']:.1%}"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
    
    def render_detailed_analysis(self, result: Dict):
        """渲染详细分析页面"""
        st.header("🔍 详细价值分析")
        
        # 各估值方法详细分析
        valuation_summary = result['valuation_summary']
        
        if not valuation_summary:
            st.warning("暂无详细分析数据")
            return
        
        # 为每种估值方法创建标签页
        tabs = st.tabs(list(valuation_summary.keys()))
        
        for i, (method, data) in enumerate(valuation_summary.items()):
            with tabs[i]:
                self.render_method_analysis(method, data, result)
    
    def render_method_analysis(self, method: str, data: Dict, result: Dict):
        """渲染具体估值方法分析"""
        method_names = {
            'dcf': 'DCF现金流折现模型',
            'resource': '资源重置价值模型',
            'pb_roe': 'PB-ROE估值模型',
            'asset_based': '资产基础估值模型'
        }
        
        st.subheader(f"📊 {method_names.get(method, method)}分析")
        
        # 估值结果展示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("估值结果", f"¥{data['value']:.2f}")
        with col2:
            st.metric("置信度", f"{data['confidence']:.1%}")
        with col3:
            deviation = (data['value'] - result['current_price']) / result['current_price']
            st.metric("相对当前价格", f"{deviation:.1%}")
        
        # 关键假设参数
        if 'assumptions' in data and data['assumptions']:
            st.subheader("📋 关键假设参数")
            
            assumptions = data['assumptions']
            
            if method == 'dcf':
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("WACC折现率", f"{assumptions.get('wacc', 0):.1%}")
                    st.metric("永续增长率", f"{assumptions.get('terminal_growth', 0):.1%}")
                with col2:
                    st.metric("当前自由现金流", f"¥{assumptions.get('current_fcf', 0)/1e8:.1f}亿")
                    st.metric("企业价值", f"¥{assumptions.get('enterprise_value', 0)/1e8:.1f}亿")
            
            elif method == 'resource':
                if 'resources' in assumptions:
                    st.write("**资源储量情况：**")
                    for resource, info in assumptions['resources'].items():
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{resource.upper()}**")
                            st.write(f"储量: {info.get('reserves', 0):,}{info.get('unit', '')}")
                            st.write(f"总价值: ¥{info.get('gross_value', 0)/1e12:.2f}万亿")
                        with col2:
                            st.write(f"净价值: ¥{info.get('net_value', 0)/1e12:.2f}万亿")
                            st.write(f"调整后价值: ¥{info.get('adjusted_value', 0)/1e12:.2f}万亿")
            
            elif method == 'pb_roe':
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("当前ROE", f"{assumptions.get('roe', 0):.1%}")
                    st.metric("每股净资产", f"¥{assumptions.get('bvps', 0):.2f}")
                with col2:
                    st.metric("合理PB", f"{assumptions.get('fair_pb', 0):.2f}")
                    st.metric("调整后PB", f"{assumptions.get('adjusted_pb', 0):.2f}")
            
            elif method == 'asset_based':
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("总资产", f"¥{assumptions.get('total_assets', 0)/1e8:.1f}亿")
                    st.metric("净资产", f"¥{assumptions.get('net_assets', 0)/1e8:.1f}亿")
                with col2:
                    st.metric("清算折价率", f"{assumptions.get('liquidation_discount', 0):.1%}")
                    st.metric("调整后资产", f"¥{assumptions.get('adjusted_assets', 0)/1e8:.1f}亿")
        
        # 模型适用性分析
        st.subheader("🎯 模型适用性分析")
        
        applicability_texts = {
            'dcf': """
            **适用场景**：
            - 现金流稳定的公司\n
            - 盈利可预测的企业\n
            - 成熟期的公司\n            
            **不适用场景**：\n
            - 初创公司\n
            - 周期性强的企业\n
            - 重资产公司
            """,
            'resource': """
            **适用场景**：
            - 矿业、石油公司\n
            - 资源储量清晰的企业\n
            - 大宗商品相关公司\n            
            **不适用场景**：\n
            - 轻资产公司\n
            - 服务业企业\n
            - 科技公司
            """,
            'pb_roe': """
            **适用场景**：
            - 资产密集型公司\n
            - 盈利能力稳定的企业\n
            - 金融业公司\n            
            **不适用场景**：\n
            - 轻资产公司\n
            - 高成长企业\n
            - 亏损公司
            """,
            'asset_based': """
            **适用场景**：
            - 资产清算估值\n
            - 破产重组评估\n
            - 资产担保估值\n            
            **不适用场景**：\n
            - 持续经营企业\n
            - 轻资产公司\n
            - 高成长企业
            """
        }
        
        st.markdown(applicability_texts.get(method, ""))
    
    def render_historical_analysis(self, symbol: str):
        """渲染历史趋势分析"""
        st.header("📊 历史价值趋势分析")
        
        # 获取历史数据
        historical_data = self.system.get_historical_analysis(symbol, days=90)
        
        if not historical_data:
            st.info("暂无历史分析数据")
            return
        
        # 转换为DataFrame
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # 创建历史趋势图表
        fig = self.create_historical_trend_chart(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # 趋势统计
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_deviation = df['deviation'].mean()
            st.metric("平均偏离度", f"{avg_deviation:.1%}")
        
        with col2:
            max_deviation = df['deviation'].abs().max()
            st.metric("最大偏离度", f"{max_deviation:.1%}")
        
        with col3:
            trend_changes = self.count_trend_changes(df)
            st.metric("趋势变化次数", trend_changes)
        
        # 详细历史数据表格
        with st.expander("📋 查看详细历史数据"):
            df_display = df.copy()
            df_display['偏离度'] = df_display['deviation'].apply(lambda x: f"{x:.1%}")
            df_display['日期'] = df_display['date'].dt.strftime('%Y-%m-%d')
            
            display_df = df_display[['日期', 'current_price', 'fair_value_low', 'fair_value_high', '偏离度', 'trend_direction']]
            display_df.columns = ['日期', '当前价格', '合理价值下限', '合理价值上限', '偏离度', '趋势判断']
            
            st.dataframe(display_df, use_container_width=True)
    
    def create_historical_trend_chart(self, df: pd.DataFrame) -> go.Figure:
        """创建历史趋势图表"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=("价格与价值对比", "价值偏离度趋势")
        )
        
        # 价格与价值对比
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['current_price'], name="当前价格",
                      line=dict(color='red', width=2)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['fair_value_low'], name="合理价值下限",
                      line=dict(color='blue', width=1), fill=None),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['fair_value_high'], name="合理价值上限",
                      line=dict(color='blue', width=1), fill='tonexty'),
            row=1, col=1
        )
        
        # 偏离度趋势
        colors = ['green' if x < 0 else 'red' for x in df['deviation']]
        fig.add_trace(
            go.Bar(x=df['date'], y=df['deviation'], name="偏离度", marker_color=colors),
            row=2, col=1
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        
        fig.update_layout(height=600, showlegend=True)
        fig.update_xaxes(title_text="日期", row=2, col=1)
        fig.update_yaxes(title_text="价格 (元)", row=1, col=1)
        fig.update_yaxes(title_text="偏离度", row=2, col=1)
        
        return fig
    
    def count_trend_changes(self, df: pd.DataFrame) -> int:
        """计算趋势变化次数"""
        if len(df) < 2:
            return 0
        
        changes = 0
        for i in range(1, len(df)):
            if df.iloc[i]['trend_direction'] != df.iloc[i-1]['trend_direction']:
                changes += 1
        
        return changes
    
    def render_risk_analysis(self, result: Dict):
        """渲染风险分析页面"""
        st.header("⚠️ 风险分析")
        
        # 整体风险评估
        risk_level = result.get('risk_level', '未知')
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if risk_level == "高风险":
                st.error(f"🚨 风险等级: {risk_level}")
            elif risk_level == "中等风险":
                st.warning(f"⚠️ 风险等级: {risk_level}")
            else:
                st.success(f"✅ 风险等级: {risk_level}")
        
        with col2:
            self.render_risk_details(result)
        
        # 价值波动风险
        st.subheader("📈 价值波动风险")
        self.render_value_volatility_risk(result)
        
        # 模型风险
        st.subheader("🔧 模型风险")
        self.render_model_risk(result)
    
    def render_risk_details(self, result: Dict):
        """渲染风险详情"""
        value_trend = result['value_trend']
        deviation = abs(value_trend['deviation'])
        confidence = value_trend['confidence']
        
        st.write(f"**价值偏离风险**: {deviation:.1%}")
        st.write(f"**模型置信度**: {confidence:.1%}")
        st.write(f"**趋势强度**: {value_trend['strength'].title()}")
        
        # 风险描述
        if deviation > 0.5:
            st.error("当前价格严重偏离内在价值，面临较大的价值回归风险")
        elif deviation > 0.2:
            st.warning("当前价格偏离内在价值，需要关注价值回归时机")
        else:
            st.success("当前价格接近内在价值，估值风险较低")
    
    def render_value_volatility_risk(self, result: Dict):
        """渲染价值波动风险"""
        st.write("""
        **主要价值波动风险因素：**
        
        📊 **估值模型风险**
        - 模型假设参数变化\n
        - 未来现金流预测偏差\n
        - 折现率选择影响\n
        
        🏭 **基本面风险**  \n
        - 盈利能力变化\n
        - 资产质量恶化\n
        - 行业竞争加剧\n
        
        🌍 **宏观环境风险**
        - 利率环境变化\n
        - 经济周期影响\n
        - 政策监管变化
        """)
    
    def render_model_risk(self, result: Dict):
        """渲染模型风险"""
        st.write("""
        **模型特定风险：**
        
        🔢 **DCF模型风险**
        - 未来现金流预测准确性\n
        - 永续增长率假设合理性\n
        - 折现率参数敏感性

        
        ⛏️ **资源价值模型风险**  \n
        - 资源储量估算准确性\n
        - 大宗商品价格波动\n
        - 开采成本变化

        
        📈 **PB-ROE模型风险**
        - 净资产收益率稳定性\n
        - 行业比较基准选择\n
        - 资产质量评估
        """)
    
    def render_investment_advice(self, result: Dict):
        """渲染投资建议页面"""
        st.header("💡 投资建议")
        
        # 主要投资建议
        investment_rec = result.get('investment_recommendation', {})
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎯 核心投资建议")
            
            summary = investment_rec.get('summary', '暂无建议')
            st.markdown(f"**{summary}**")
            
            # 具体建议
            specific_recs = investment_rec.get('specific_recommendations', {})
            if specific_recs:
                st.subheader("📋 具体操作建议")
                
                for method, rec in specific_recs.items():
                    with st.expander(f"{method} 建议"):
                        st.write(f"**建议**: {rec['advice']}")
                        st.write("**关注因素**:")
                        for factor in rec['key_factors']:
                            st.write(f"• {factor}")
        
        with col2:
            st.subheader("⏰ 时机策略")
            timing_strategy = investment_rec.get('timing_strategy', '等待时机')
            st.info(timing_strategy)
            
            st.subheader("🛡️ 风险管理")
            risk_mgmt = investment_rec.get('risk_management', '正常风险管理')
            st.warning(risk_mgmt)
        
        # 投资逻辑阐述
        st.subheader("🧠 投资逻辑阐述")
        self.render_investment_logic(result)
        
        # 关键监控指标
        st.subheader("📊 关键监控指标")
        self.render_key_monitoring_metrics(result)
    
    def render_investment_logic(self, result: Dict):
        """渲染投资逻辑"""
        value_trend = result['value_trend']
        insights = result.get('insights', {})
        
        trend_direction = value_trend['trend_direction']
        deviation = value_trend['deviation']
        
        if 'undervalued' in trend_direction:
            st.success("""
            **价值投资逻辑：**
            
            🎯 **核心理念**: 以低于内在价值的价格买入优质资产
            
            📊 **数据支撑**: 当前价格相对内在价值存在明显折价
            
            ⏰ **时间优势**: 价值回归只是时间问题，耐心等待必有回报
            
            🛡️ **安全边际**: 折价买入提供了下跌保护空间
            
            💎 **长期价值**: 公司基本面稳固，长期价值增长确定
            """)
        elif 'overvalued' in trend_direction:
            st.warning("""
            **风险规避逻辑：**
            
            ⚠️ **风险警示**: 当前价格明显高于内在价值
            
            📉 **回归风险**: 面临价值回归导致的下跌风险
            
            ⏳ **时机选择**: 等待更好的买入时机，不急于追高
            
            💰 **资金保护**: 保护本金安全，避免高位接盘
            
            🔄 **逆向思维**: 别人贪婪时我恐惧，等待恐慌性抛售
            """)
        else:
            st.info("""
            **持有观望逻辑：**
            
            ⚖️ **估值合理**: 当前价格基本反映内在价值
            
            👀 **等待时机**: 等待更明确的价值信号
            
            📈 **趋势观察**: 关注基本面变化和价值走向
            
            🎯 **精选标的**: 在合理估值范围内精选优质标的
            
            ⏱️ **择时操作**: 等待更好的买入或卖出时机
            """)
    
    def render_key_monitoring_metrics(self, result: Dict):
        """渲染关键监控指标"""
        st.write("""
        **必须持续监控的核心指标：**
        
        📊 **估值指标**
        - 价值偏离度变化\n
        - 各估值模型结果更新\n
        - 模型置信度变化\n
        
        🏢 **基本面指标**  \n
        - 财务数据季度更新\n
        - 盈利能力变化趋势\n
        - 资产质量评估\n
        
        🌍 **市场环境指标**
        - 行业估值水平变化\n
        - 宏观经济环境影响\n
        - 政策监管变化
        """)
        
        # 自动监控建议
        st.info("💡 **建议设置自动监控预警，当价值偏离度超过设定阈值时及时提醒**")

# 主函数
def main():
    """主函数"""
    st.title("📊 股票真实价值走势分析系统")
    
    # 创建仪表板实例
    dashboard = ValueAnalysisDashboard()
    
    # 运行仪表板
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()