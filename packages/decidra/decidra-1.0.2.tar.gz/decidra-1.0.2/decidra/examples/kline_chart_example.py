#!/usr/bin/env python3
"""
K线图表组件示例
演示如何使用 textual_plotext 创建K线图和成交量图
"""

import sys
import os
import random
from datetime import datetime, timedelta
from typing import List

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Static
from textual.binding import Binding

from monitor.widgets.kline_chart import KLineChartWidget, SimpleKLineWidget, ChartConfig
from base.futu_class import KLineData


def generate_sample_kline_data(days: int = 100, start_price: float = 100.0) -> List[KLineData]:
    """生成示例K线数据"""
    data = []
    current_price = start_price
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # 随机生成OHLC数据
        change = random.uniform(-0.05, 0.05)  # 日变动±5%
        open_price = current_price
        close_price = current_price * (1 + change)
        
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.03))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.03))
        
        volume = random.randint(10000, 1000000)
        turnover = volume * (high_price + low_price) / 2
        
        kline = KLineData(
            code="000001",
            time_key=date_str,
            open=round(open_price, 2),
            close=round(close_price, 2),
            high=round(high_price, 2),
            low=round(low_price, 2),
            volume=volume,
            turnover=round(turnover, 2)
        )
        
        data.append(kline)
        current_price = close_price
    
    return data


class KLineExampleApp(App):
    """K线图示例应用"""
    
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
    
    .charts-container {
        height: 1fr;
        layout: horizontal;
    }
    
    .left-panel {
        width: 2fr;
        margin-right: 1;
    }
    
    .right-panel {
        width: 1fr;
    }
    
    .controls {
        height: 8;
        background: $surface;
        border: solid $accent;
        padding: 1;
        layout: vertical;
    }
    
    .button-row {
        height: 3;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    Button {
        margin-right: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("r", "refresh_data", "刷新数据"),
        Binding("1", "switch_daily", "日线"),
        Binding("2", "switch_weekly", "周线"),
        Binding("3", "switch_monthly", "月线"),
    ]
    
    def __init__(self):
        super().__init__()
        self.sample_data = generate_sample_kline_data()
        self.current_period = "日线"
    
    def compose(self) -> ComposeResult:
        """组合应用界面"""
        
        # 头部信息
        with Container(classes="header"):
            yield Static(
                "[bold blue]K线图表组件示例[/bold blue]\n"
                "左侧：完整K线图表 | 右侧：简单K线图\n"
                "[dim]快捷键: Q=退出 R=刷新数据 1=日线 2=周线 3=月线[/dim]",
                id="header_info"
            )
        
        # 图表容器
        with Container(classes="charts-container"):
            # 左侧面板 - 完整K线图
            with Container(classes="left-panel"):
                yield KLineChartWidget(
                    stock_code="000001",
                    time_period="D",
                    config=ChartConfig(
                        show_volume=True,
                        chart_height=20,
                        volume_height=8,
                        theme="dark"
                    ),
                    id="main_chart"
                )
            
            # 右侧面板 - 控制区域和简单图表
            with Container(classes="right-panel"):
                # 控制按钮
                with Container(classes="controls"):
                    yield Static("[bold]图表控制[/bold]", id="control_title")
                    
                    with Container(classes="button-row"):
                        yield Button("刷新数据", variant="success", id="btn_refresh")
                        yield Button("日线", variant="primary", id="btn_daily")
                    
                    with Container(classes="button-row"):
                        yield Button("周线", variant="primary", id="btn_weekly")
                        yield Button("月线", variant="primary", id="btn_monthly")
                    
                    yield Static(
                        f"当前周期: {self.current_period}\n"
                        f"数据量: {len(self.sample_data)}根K线\n"
                        f"价格区间: {min(k.low for k in self.sample_data):.2f} - {max(k.high for k in self.sample_data):.2f}",
                        id="data_info"
                    )
                
                # 简单K线图
                yield SimpleKLineWidget(stock_code="000001", id="simple_chart")
    
    def on_mount(self) -> None:
        """应用启动时加载数据"""
        self.load_sample_data()
    
    def load_sample_data(self) -> None:
        """加载示例数据到图表"""
        # 更新主图表
        main_chart = self.query_one("#main_chart", KLineChartWidget)
        main_chart.update_data(self.sample_data)
        
        # 更新简单图表
        simple_chart = self.query_one("#simple_chart", SimpleKLineWidget)
        simple_chart.update_kline_data(self.sample_data)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """按钮点击事件"""
        button_id = event.button.id
        
        if button_id == "btn_refresh":
            self.action_refresh_data()
        elif button_id == "btn_daily":
            self.action_switch_daily()
        elif button_id == "btn_weekly":
            self.action_switch_weekly()
        elif button_id == "btn_monthly":
            self.action_switch_monthly()
    
    def action_refresh_data(self) -> None:
        """刷新示例数据"""
        self.sample_data = generate_sample_kline_data()
        self.load_sample_data()
        
        # 更新数据信息
        data_info = self.query_one("#data_info", Static)
        data_info.update(
            f"当前周期: {self.current_period}\n"
            f"数据量: {len(self.sample_data)}根K线\n"
            f"价格区间: {min(k.low for k in self.sample_data):.2f} - {max(k.high for k in self.sample_data):.2f}"
        )
    
    def action_switch_daily(self) -> None:
        """切换到日线"""
        self.current_period = "日线"
        main_chart = self.query_one("#main_chart", KLineChartWidget)
        main_chart.set_stock("000001", "D")
        self._update_period_info()
    
    def action_switch_weekly(self) -> None:
        """切换到周线"""
        self.current_period = "周线"
        main_chart = self.query_one("#main_chart", KLineChartWidget)
        main_chart.set_stock("000001", "W")
        self._update_period_info()
    
    def action_switch_monthly(self) -> None:
        """切换到月线"""
        self.current_period = "月线"
        main_chart = self.query_one("#main_chart", KLineChartWidget)
        main_chart.set_stock("000001", "M")
        self._update_period_info()
    
    def _update_period_info(self) -> None:
        """更新周期信息显示"""
        data_info = self.query_one("#data_info", Static)
        data_info.update(
            f"当前周期: {self.current_period}\n"
            f"数据量: {len(self.sample_data)}根K线\n"
            f"价格区间: {min(k.low for k in self.sample_data):.2f} - {max(k.high for k in self.sample_data):.2f}"
        )


def main():
    """运行示例应用"""
    app = KLineExampleApp()
    app.run()


if __name__ == "__main__":
    main()