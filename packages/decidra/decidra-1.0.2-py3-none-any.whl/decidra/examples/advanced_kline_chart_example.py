#!/usr/bin/env python3
"""
高级K线图表分析示例
演示集成analysis模块的完整股票分析功能，包括技术指标、AI分析、实时数据等
"""

import sys
import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Static, Input, Select, Switch, TabbedContent, TabPane, DataTable
from textual.binding import Binding
from textual import events

from monitor.widgets.kline_chart import KLineChartWidget, SimpleKLineWidget, ChartConfig
from monitor.analysis.analysis_data_manager import AnalysisDataManager, AnalysisDataSet
from monitor.analysis.chart_manager import ChartManager
from monitor.analysis.ai_analysis_manager import AIAnalysisManager
from base.futu_class import KLineData, OrderBookData


class RealTimeDataSimulator:
    """实时数据模拟器"""
    
    def __init__(self):
        self.is_running = False
        self.callbacks = []
        self.base_price = 100.0
        self.current_price = self.base_price
        
    def add_callback(self, callback):
        """添加数据更新回调"""
        self.callbacks.append(callback)
    
    async def start_simulation(self):
        """开始模拟实时数据"""
        self.is_running = True
        while self.is_running:
            # 模拟价格变动
            change = random.uniform(-0.02, 0.02)  # ±2%变动
            self.current_price *= (1 + change)
            
            # 模拟实时数据
            realtime_data = {
                'last_price': round(self.current_price, 2),
                'change': round(self.current_price - self.base_price, 2),
                'change_rate': round((self.current_price - self.base_price) / self.base_price * 100, 2),
                'volume': random.randint(1000, 10000),
                'turnover': random.randint(100000, 1000000),
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            # 通知所有回调
            for callback in self.callbacks:
                await callback(realtime_data)
            
            await asyncio.sleep(1)  # 1秒更新一次
    
    def stop_simulation(self):
        """停止模拟"""
        self.is_running = False


class TechnicalIndicatorsPanel(Container):
    """技术指标面板"""
    
    DEFAULT_CSS = """
    TechnicalIndicatorsPanel {
        height: 1fr;
        border: solid $accent;
        border-title-color: $text;
        padding: 1;
        layout: vertical;
    }
    
    .indicator-row {
        height: 3;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    .indicator-label {
        width: 8;
        content-align: right middle;
        margin-right: 1;
    }
    
    .indicator-value {
        width: 12;
        content-align: left middle;
        background: $surface;
        border: solid $accent;
        padding: 0 1;
    }
    
    .indicator-signal {
        width: 8;
        content-align: center middle;
        margin-left: 1;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "技术指标"
        
    def compose(self) -> ComposeResult:
        """组合技术指标显示"""
        # MA均线
        with Container(classes="indicator-row"):
            yield Static("MA5:", classes="indicator-label")
            yield Static("--", id="ma5_value", classes="indicator-value")
            yield Static("--", id="ma5_signal", classes="indicator-signal")
        
        with Container(classes="indicator-row"):
            yield Static("MA20:", classes="indicator-label")
            yield Static("--", id="ma20_value", classes="indicator-value")
            yield Static("--", id="ma20_signal", classes="indicator-signal")
        
        # RSI指标
        with Container(classes="indicator-row"):
            yield Static("RSI:", classes="indicator-label")
            yield Static("--", id="rsi_value", classes="indicator-value")
            yield Static("--", id="rsi_signal", classes="indicator-signal")
        
        # MACD指标
        with Container(classes="indicator-row"):
            yield Static("MACD:", classes="indicator-label")
            yield Static("--", id="macd_value", classes="indicator-value")
            yield Static("--", id="macd_signal", classes="indicator-signal")
        
        # 布林带
        with Container(classes="indicator-row"):
            yield Static("BOLL:", classes="indicator-label")
            yield Static("--", id="boll_value", classes="indicator-value")
            yield Static("--", id="boll_signal", classes="indicator-signal")
    
    def update_indicators(self, indicators: Dict[str, Any]):
        """更新技术指标显示"""
        if 'ma' in indicators:
            ma_data = indicators['ma']
            if len(ma_data['ma5']) > 0:
                self.query_one("#ma5_value", Static).update(f"{ma_data['ma5'][-1]:.2f}")
                # 简单的信号判断
                current_price = ma_data.get('current_price', 0)
                signal = "看涨" if current_price > ma_data['ma5'][-1] else "看跌"
                self.query_one("#ma5_signal", Static).update(f"[green]{signal}[/green]" if signal == "看涨" else f"[red]{signal}[/red]")
            
            if len(ma_data['ma20']) > 0:
                self.query_one("#ma20_value", Static).update(f"{ma_data['ma20'][-1]:.2f}")
        
        if 'rsi' in indicators:
            rsi_value = indicators['rsi'][-1] if indicators['rsi'] else 0
            self.query_one("#rsi_value", Static).update(f"{rsi_value:.2f}")
            if rsi_value > 70:
                signal = "[red]超买[/red]"
            elif rsi_value < 30:
                signal = "[green]超卖[/green]"
            else:
                signal = "中性"
            self.query_one("#rsi_signal", Static).update(signal)


class MarketDataPanel(Container):
    """市场数据面板"""
    
    DEFAULT_CSS = """
    MarketDataPanel {
        height: 1fr;
        border: solid $accent;
        border-title-color: $text;
        padding: 1;
        layout: vertical;
    }
    
    .realtime-info {
        height: 8;
        background: $surface;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }
    
    .orderbook-container {
        height: 1fr;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "实时数据"
        
    def compose(self) -> ComposeResult:
        """组合市场数据显示"""
        # 实时行情信息
        with Container(classes="realtime-info"):
            yield Static(
                "[bold blue]实时行情[/bold blue]\n"
                "价格: -- 涨跌: -- 涨幅: --%\n"
                "成交量: -- 成交额: --\n"
                "更新时间: --",
                id="realtime_info"
            )
        
        # 五档买卖盘
        with Container(classes="orderbook-container"):
            yield DataTable(id="orderbook_table", show_header=True, zebra_stripes=True)
    
    async def update_realtime_data(self, data: Dict[str, Any]):
        """更新实时数据显示"""
        info_text = (
            f"[bold blue]实时行情[/bold blue]\n"
            f"价格: [bold]{data['last_price']}[/bold] "
            f"涨跌: {'[green]+' if data['change'] >= 0 else '[red]'}{data['change']:.2f}[/] "
            f"涨幅: {'[green]+' if data['change_rate'] >= 0 else '[red]'}{data['change_rate']:.2f}%[/]\n"
            f"成交量: {data['volume']:,} 成交额: {data['turnover']:,}\n"
            f"更新时间: {data['timestamp']}"
        )
        self.query_one("#realtime_info", Static).update(info_text)
    
    def setup_orderbook_table(self):
        """设置五档表格"""
        table = self.query_one("#orderbook_table", DataTable)
        table.add_columns("买盘", "价格", "卖盘")
        
        # 模拟五档数据
        for i in range(5):
            buy_vol = random.randint(100, 1000) * 100
            sell_vol = random.randint(100, 1000) * 100
            price = 100.0 + random.uniform(-2, 2)
            table.add_row(f"{buy_vol:,}", f"{price:.2f}", f"{sell_vol:,}")


class AIAnalysisPanel(ScrollableContainer):
    """AI分析面板"""
    
    DEFAULT_CSS = """
    AIAnalysisPanel {
        height: 1fr;
        border: solid $accent;
        border-title-color: $text;
        padding: 1;
    }
    
    .analysis-content {
        background: $surface;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }
    
    .analysis-buttons {
        height: 5;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    .analysis-buttons Button {
        margin-right: 1;
        width: 12;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "AI智能分析"
        
    def compose(self) -> ComposeResult:
        """组合AI分析显示"""
        # 分析按钮
        with Container(classes="analysis-buttons"):
            yield Button("技术分析", variant="primary", id="btn_technical")
            yield Button("基本面", variant="primary", id="btn_fundamental")
            yield Button("风险评估", variant="warning", id="btn_risk")
        
        # 分析结果显示
        yield Static(
            "[dim]点击上方按钮获取AI分析建议...[/dim]",
            id="analysis_content",
            classes="analysis-content"
        )
    
    def update_analysis(self, analysis_type: str, content: str):
        """更新分析内容"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        analysis_text = (
            f"[bold blue]{analysis_type} 分析报告[/bold blue] [dim]({timestamp})[/dim]\n\n"
            f"{content}\n\n"
            "[dim]以上分析仅供参考，投资有风险，决策需谨慎。[/dim]"
        )
        self.query_one("#analysis_content", Static).update(analysis_text)


class ConfigPanel(Container):
    """配置面板"""
    
    DEFAULT_CSS = """
    ConfigPanel {
        height: 1fr;
        border: solid $accent;
        border-title-color: $text;
        padding: 1;
        layout: vertical;
    }
    
    .config-row {
        height: 3;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    .config-label {
        width: 12;
        content-align: right middle;
        margin-right: 1;
    }
    
    .config-input {
        width: 1fr;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "图表配置"
        
    def compose(self) -> ComposeResult:
        """组合配置面板"""
        # 股票代码输入
        with Container(classes="config-row"):
            yield Static("股票代码:", classes="config-label")
            yield Input(placeholder="如: HK.00700", value="HK.00700", id="stock_input", classes="config-input")
        
        # 时间周期选择
        with Container(classes="config-row"):
            yield Static("时间周期:", classes="config-label")
            yield Select([
                ("日线", "D"),
                ("周线", "W"),
                ("月线", "M")
            ], value="D", id="period_select", classes="config-input")
        
        # 显示选项
        with Container(classes="config-row"):
            yield Static("显示成交量:", classes="config-label")
            yield Switch(value=True, id="volume_switch", classes="config-input")
        
        with Container(classes="config-row"):
            yield Static("显示MA线:", classes="config-label")
            yield Switch(value=True, id="ma_switch", classes="config-input")
        
        with Container(classes="config-row"):
            yield Static("实时模拟:", classes="config-label")
            yield Switch(value=False, id="realtime_switch", classes="config-input")


def generate_advanced_kline_data(days: int = 200, start_price: float = 100.0) -> List[KLineData]:
    """生成高级示例K线数据，包含更真实的市场行为"""
    data = []
    current_price = start_price
    base_date = datetime.now() - timedelta(days=days)
    
    # 模拟不同的市场阶段
    trend_phases = [
        ('bull', 60, 0.02),    # 牛市阶段：60天，平均日涨2%
        ('correction', 20, -0.03),  # 调整阶段：20天，平均日跌3%
        ('consolidation', 40, 0.005),  # 盘整阶段：40天，小幅波动
        ('bear', 30, -0.015),  # 熊市阶段：30天，平均日跌1.5%
        ('recovery', 50, 0.01)  # 恢复阶段：50天，平均日涨1%
    ]
    
    day_count = 0
    for phase_type, phase_days, avg_change in trend_phases:
        for i in range(phase_days):
            if day_count >= days:
                break
                
            date = base_date + timedelta(days=day_count)
            date_str = date.strftime("%Y-%m-%d 00:00:00")
            
            # 根据市场阶段调整变动幅度
            if phase_type == 'bull':
                change = random.uniform(avg_change - 0.01, avg_change + 0.03)
            elif phase_type == 'bear':
                change = random.uniform(avg_change - 0.02, avg_change + 0.01)
            elif phase_type == 'correction':
                change = random.uniform(avg_change - 0.02, avg_change + 0.02)
            else:  # consolidation or recovery
                change = random.uniform(avg_change - 0.015, avg_change + 0.015)
            
            # 添加一些随机的大幅波动
            if random.random() < 0.05:  # 5%概率出现大幅波动
                change *= random.uniform(2, 4)
                if random.random() < 0.5:
                    change = -abs(change)
            
            open_price = current_price
            close_price = current_price * (1 + change)
            
            # 生成更真实的高低价
            if change > 0:  # 上涨日
                high_price = max(open_price, close_price) * (1 + random.uniform(0.005, 0.02))
                low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
            else:  # 下跌日
                high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
                low_price = min(open_price, close_price) * (1 - random.uniform(0.005, 0.02))
            
            # 成交量与价格变动相关
            base_volume = 500000
            volume_multiplier = 1 + abs(change) * 3  # 变动越大，成交量越大
            volume = int(base_volume * volume_multiplier * random.uniform(0.5, 1.5))
            
            turnover = volume * (high_price + low_price) / 2
            
            kline = KLineData(
                code="HK.00700",
                time_key=date_str,
                open=round(open_price, 2),
                close=round(close_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                volume=volume,
                turnover=round(turnover, 2),
                pe_ratio=round(random.uniform(15, 35), 3),
                turnover_rate=round(random.uniform(0.001, 0.01), 5)
            )
            
            data.append(kline)
            current_price = close_price
            day_count += 1
    
    return data


def calculate_technical_indicators(kline_data: List[KLineData]) -> Dict[str, Any]:
    """计算技术指标"""
    if not kline_data:
        return {}
    
    closes = [k.close for k in kline_data]
    
    # 计算MA均线
    def calculate_ma(prices, period):
        if len(prices) < period:
            return []
        ma = []
        for i in range(len(prices)):
            if i < period - 1:
                ma.append(None)
            else:
                ma.append(sum(prices[i-period+1:i+1]) / period)
        return ma
    
    # 计算RSI
    def calculate_rsi(prices, period=14):
        if len(prices) < period + 1:
            return []
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        rsi = []
        for i in range(len(gains)):
            if i < period - 1:
                rsi.append(None)
            else:
                avg_gain = sum(gains[i-period+1:i+1]) / period
                avg_loss = sum(losses[i-period+1:i+1]) / period
                
                if avg_loss == 0:
                    rsi.append(100)
                else:
                    rs = avg_gain / avg_loss
                    rsi.append(100 - (100 / (1 + rs)))
        
        return rsi
    
    indicators = {
        'ma': {
            'ma5': calculate_ma(closes, 5),
            'ma10': calculate_ma(closes, 10),
            'ma20': calculate_ma(closes, 20),
            'ma60': calculate_ma(closes, 60),
            'current_price': closes[-1] if closes else 0
        },
        'rsi': calculate_rsi(closes, 14)
    }
    
    return indicators


class AdvancedKLineExampleApp(App):
    """高级K线图示例应用"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    .header {
        height: 5;
        background: $surface;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
    }
    
    .main-container {
        height: 1fr;
        layout: horizontal;
    }
    
    .left-panel {
        width: 2fr;
        layout: vertical;
    }
    
    .chart-area {
        height: 20;
        margin-right: 1;
        margin-bottom: 1;
    }
    
    .indicators-area {
        height: 1fr;
        margin-right: 1;
    }
    
    .right-panel {
        width: 1fr;
        layout: vertical;
    }
    
    TabbedContent {
        height: 1fr;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("r", "refresh_data", "刷新数据"),
        Binding("ctrl+t", "toggle_realtime", "切换实时模拟"),
        Binding("ctrl+s", "take_screenshot", "截图"),
        Binding("h", "show_help", "帮助"),
    ]
    
    def __init__(self):
        super().__init__()
        self.sample_data = generate_advanced_kline_data()
        self.technical_indicators = calculate_technical_indicators(self.sample_data)
        self.realtime_simulator = RealTimeDataSimulator()
        self.current_stock = "HK.00700"
        self.current_period = "D"
        
    def compose(self) -> ComposeResult:
        """组合应用界面"""
        
        # 头部信息
        with Container(classes="header"):
            yield Static(
                "[bold blue]高级K线图表分析系统[/bold blue]\n"
                "集成技术指标计算、实时数据模拟、AI分析等功能\n"
                "[dim]快捷键: Q=退出 R=刷新 Ctrl+T=实时模拟 Ctrl+S=截图 H=帮助[/dim]",
                id="header_info"
            )
        
        # 主容器
        with Container(classes="main-container"):
            # 左侧面板 - 图表区域
            with Container(classes="left-panel"):
                # K线图表
                with Container(classes="chart-area"):
                    yield KLineChartWidget(
                        stock_code=self.current_stock,
                        time_period=self.current_period,
                        config=ChartConfig(
                            show_volume=True,
                            chart_height=25,
                            volume_height=10,
                            theme="dark"
                        ),
                        id="main_chart"
                    )
                
                # 技术指标面板
                #with Container(classes="indicators-area"):
                #    yield TechnicalIndicatorsPanel(id="indicators_panel")
            
            # 右侧面板 - 数据和分析
            #with Container(classes="right-panel"):
            #    with TabbedContent():
            #        with TabPane("实时数据", id="realtime_tab"):
            #            yield MarketDataPanel(id="market_panel")
            #        
            #        with TabPane("AI分析", id="analysis_tab"):
            #            yield AIAnalysisPanel(id="ai_panel")
            #        
            #        with TabPane("配置", id="config_tab"):
            #            yield ConfigPanel(id="config_panel")
    
    def on_mount(self) -> None:
        """应用启动时的初始化"""
        self.load_initial_data()
        self.setup_realtime_simulator()
        
    def load_initial_data(self) -> None:
        """加载初始数据"""
        # 更新主图表
        main_chart = self.query_one("#main_chart", KLineChartWidget)
        main_chart.update_data(self.sample_data)
        
        # 更新技术指标
        #indicators_panel = self.query_one("#indicators_panel", TechnicalIndicatorsPanel)
        #indicators_panel.update_indicators(self.technical_indicators)
        
        # 设置五档表格
        #market_panel = self.query_one("#market_panel", MarketDataPanel)
        #market_panel.setup_orderbook_table()
    
    def setup_realtime_simulator(self) -> None:
        """设置实时数据模拟器"""
        async def on_realtime_update(data):
            market_panel = self.query_one("#market_panel", MarketDataPanel)
            await market_panel.update_realtime_data(data)
        
        self.realtime_simulator.add_callback(on_realtime_update)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """按钮点击事件处理"""
        button_id = event.button.id
        
        if button_id == "btn_technical":
            self.generate_ai_analysis("技术分析")
        elif button_id == "btn_fundamental":
            self.generate_ai_analysis("基本面分析")
        elif button_id == "btn_risk":
            self.generate_ai_analysis("风险评估")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """输入框提交事件"""
        if event.input.id == "stock_input":
            new_stock = event.input.value.upper()
            if new_stock:
                self.current_stock = new_stock
                self.action_refresh_data()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """选择框改变事件"""
        if event.select.id == "period_select":
            self.current_period = event.value
            main_chart = self.query_one("#main_chart", KLineChartWidget)
            main_chart.set_stock(self.current_stock, self.current_period)
    
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """开关改变事件"""
        if event.switch.id == "realtime_switch":
            if event.value:
                asyncio.create_task(self.realtime_simulator.start_simulation())
            else:
                self.realtime_simulator.stop_simulation()
    
    def generate_ai_analysis(self, analysis_type: str) -> None:
        """生成AI分析内容"""
        ai_panel = self.query_one("#ai_panel", AIAnalysisPanel)
        
        # 模拟AI分析生成
        if analysis_type == "技术分析":
            content = self.generate_technical_analysis()
        elif analysis_type == "基本面分析":
            content = self.generate_fundamental_analysis()
        else:  # 风险评估
            content = self.generate_risk_assessment()
        
        ai_panel.update_analysis(analysis_type, content)
    
    def generate_technical_analysis(self) -> str:
        """生成技术分析内容"""
        current_price = self.sample_data[-1].close if self.sample_data else 100
        ma20 = self.technical_indicators['ma']['ma20'][-1] if self.technical_indicators['ma']['ma20'] else None
        rsi = self.technical_indicators['rsi'][-1] if self.technical_indicators['rsi'] else None
        
        analysis = f"当前价格: {current_price:.2f}\n\n"
        
        if ma20:
            if current_price > ma20:
                analysis += f"• 价格位于20日均线({ma20:.2f})上方，显示上升趋势\n"
            else:
                analysis += f"• 价格位于20日均线({ma20:.2f})下方，趋势偏弱\n"
        
        if rsi:
            if rsi > 70:
                analysis += f"• RSI指标为{rsi:.1f}，处于超买状态，注意回调风险\n"
            elif rsi < 30:
                analysis += f"• RSI指标为{rsi:.1f}，处于超卖状态，可能迎来反弹\n"
            else:
                analysis += f"• RSI指标为{rsi:.1f}，处于正常范围\n"
        
        # 成交量分析
        recent_volumes = [k.volume for k in self.sample_data[-5:]]
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        current_volume = recent_volumes[-1]
        
        if current_volume > avg_volume * 1.5:
            analysis += "• 成交量显著放大，市场活跃度较高\n"
        elif current_volume < avg_volume * 0.5:
            analysis += "• 成交量萎缩，市场观望情绪较浓\n"
        
        analysis += "\n[bold]建议:[/bold] 基于技术面分析，建议关注关键支撑位和阻力位的突破情况。"
        
        return analysis
    
    def generate_fundamental_analysis(self) -> str:
        """生成基本面分析内容"""
        return """
[bold]行业地位:[/bold] 该股票所属行业为优质赛道，具有较好的发展前景。

[bold]财务状况:[/bold]
• 营收增长稳定，盈利能力较强
• 资产负债率控制在合理范围内
• 现金流状况良好，具备持续经营能力

[bold]估值水平:[/bold]
• 当前PE估值处于历史中位数水平
• 与同行业相比，估值具有一定吸引力
• PB估值合理，安全边际较高

[bold]风险因素:[/bold]
• 宏观经济环境变化的影响
• 行业政策调整的不确定性
• 市场竞争加剧的风险

[bold]投资建议:[/bold] 从基本面角度看，公司基本面稳健，建议中长期持有。
"""
    
    def generate_risk_assessment(self) -> str:
        """生成风险评估内容"""
        # 计算价格波动率
        prices = [k.close for k in self.sample_data[-20:]]  # 最近20天
        if len(prices) > 1:
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 * (252**0.5) * 100
        else:
            volatility = 20.0
        
        if volatility > 40:
            risk_level = "[red]高风险[/red]"
            risk_desc = "价格波动较大，适合风险承受能力较强的投资者"
        elif volatility > 25:
            risk_level = "[yellow]中等风险[/yellow]"
            risk_desc = "价格波动适中，需要控制好仓位"
        else:
            risk_level = "[green]低风险[/green]"
            risk_desc = "价格波动相对较小，但仍需注意市场变化"
        
        return f"""
[bold]风险等级:[/bold] {risk_level}

[bold]波动率分析:[/bold]
• 近20日年化波动率: {volatility:.1f}%
• {risk_desc}

[bold]主要风险点:[/bold]
• 市场系统性风险
• 流动性风险
• 政策变化风险
• 行业周期性风险

[bold]风险控制建议:[/bold]
• 合理分配资金，避免重仓单股
• 设置止损位，控制最大损失
• 关注市场情绪变化，灵活调整策略
• 定期回顾投资组合，及时优化配置

[bold]风险提示:[/bold] 股市有风险，投资需谨慎。以上分析仅供参考。
"""
    
    def action_refresh_data(self) -> None:
        """刷新数据"""
        self.sample_data = generate_advanced_kline_data(days=300)
        self.technical_indicators = calculate_technical_indicators(self.sample_data)
        self.load_initial_data()
        
        # 更新头部信息
        header_info = self.query_one("#header_info", Static)
        header_info.update(
            f"[bold blue]高级K线图表分析系统[/bold blue] - 数据已更新 {datetime.now().strftime('%H:%M:%S')}\n"
            f"股票代码: {self.current_stock} | 周期: {self.current_period} | 数据量: {len(self.sample_data)}根K线\n"
            "[dim]快捷键: Q=退出 R=刷新 Ctrl+T=实时模拟 Ctrl+S=截图 H=帮助[/dim]"
        )
    
    def action_toggle_realtime(self) -> None:
        """切换实时模拟"""
        realtime_switch = self.query_one("#realtime_switch", Switch)
        realtime_switch.value = not realtime_switch.value
    
    def action_take_screenshot(self) -> None:
        """截图功能"""
        # 这里可以实现截图功能
        self.notify("截图功能暂未实现")
    
    def action_show_help(self) -> None:
        """显示帮助信息"""
        help_text = """
[bold blue]高级K线图表分析系统 - 使用指南[/bold blue]

[bold]基本功能:[/bold]
• 多周期K线图显示(日/周/月线)
• 技术指标计算(MA、RSI、MACD等)
• 实时数据模拟
• AI智能分析

[bold]快捷键:[/bold]
• Q: 退出应用
• R: 刷新数据
• Ctrl+T: 开启/关闭实时模拟
• H: 显示此帮助

[bold]图表操作:[/bold]
• ←→: 左右滚动图表
• ↑↓: 缩放图表
• Home/End: 跳转到开始/结束
• V: 切换成交量显示

[bold]面板说明:[/bold]
• 实时数据: 显示模拟实时行情和五档数据
• AI分析: 提供技术面、基本面和风险评估
• 配置: 调整图表显示参数

[bold]注意事项:[/bold]
• 所有数据均为模拟数据，仅供学习使用
• AI分析内容为示例，不构成投资建议
• 投资有风险，决策需谨慎
"""
        self.push_screen("help", help_text)
        self.notify("帮助信息已显示")


def main():
    """运行高级K线图示例应用"""
    app = AdvancedKLineExampleApp()
    app.run()


if __name__ == "__main__":
    main()