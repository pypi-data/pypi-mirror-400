"""
标签页组件使用示例
演示 TabbedContent、TabPane、ContentTab 的使用方法
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textual.app import App, ComposeResult
from textual.widgets import Button, Static, Label, ListView, ListItem
from textual.containers import Vertical, Horizontal
from textual import on

from monitor.widgets.tab import TabbedContent, TabPane


class StockDataWidget(Static):
    """股票数据显示组件"""
    
    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        super().__init__()
        self.update_stock_data()
    
    def update_stock_data(self) -> None:
        """更新股票数据显示"""
        # 模拟股票数据
        mock_data = {
            "HK.00700": {"name": "腾讯控股", "price": 350.50, "change": "+2.5%"},
            "US.AAPL": {"name": "苹果公司", "price": 150.25, "change": "-1.2%"},
            "SH.600519": {"name": "贵州茅台", "price": 1680.00, "change": "+0.8%"},
        }
        
        data = mock_data.get(self.stock_code, {"name": "未知股票", "price": 0.00, "change": "0.0%"})
        
        content = f"""
📈 股票代码: {self.stock_code}
📊 股票名称: {data['name']}
💰 当前价格: ${data['price']:.2f}
📈 涨跌幅: {data['change']}
⏰ 更新时间: 实时数据
        """
        self.update(content.strip())


class NewsWidget(Vertical):
    """新闻列表组件"""
    
    def compose(self) -> ComposeResult:
        """组合新闻内容"""
        yield Static("📰 市场新闻", classes="news-title")
        
        news_items = [
            "📰 股市今日收盘：主要指数小幅上涨",
            "📈 科技股表现强劲，腾讯涨幅超过3%",
            "💼 央行宣布维持利率不变", 
            "🏭 制造业PMI指数持续回升",
            "💱 人民币汇率保持稳定",
            "🌏 亚太股市普遍上涨",
        ]
        
        for news in news_items:
            yield Static(news, classes="news-item")


class SettingsWidget(Vertical):
    """设置组件"""
    
    def compose(self) -> ComposeResult:
        yield Static("⚙️ 系统设置", classes="setting-title")
        yield Static("")
        yield Button("🔔 通知设置", id="notification-btn")
        yield Button("🎨 主题设置", id="theme-btn") 
        yield Button("📊 数据源配置", id="data-btn")
        yield Button("🔐 账户管理", id="account-btn")
        yield Static("")
        yield Static("💡 提示: 点击按钮进行相应设置")


class TabExample(App):
    """标签页组件示例应用"""
    
    CSS = """
    Screen {
        background: $background;
    }
    
    .main-container {
        width: 90%;
        height: 90%;
        margin: 2;
        background: $surface;
        border: solid $primary;
    }
    
    .header {
        dock: top;
        height: 3;
        background: $primary;
        color: $text;
        text-align: center;
        content-align: center middle;
        text-style: bold;
    }
    
    .control-panel {
        dock: bottom;
        height: 7;
        background: $panel;
        border-top: solid $secondary;
        padding: 1;
    }
    
    .setting-title {
        text-align: center;
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }
    
    TabbedContent {
        margin: 1;
    }
    
    Button {
        margin: 0 1;
        min-width: 15;
    }
    
    StockDataWidget {
        background: $panel;
        border: solid $secondary;
        padding: 1;
        margin: 1;
    }
    
    NewsWidget {
        background: $panel;
        border: solid $secondary;
        margin: 1;
    }
    
    .news-title {
        text-align: center;
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .news-item {
        padding: 0 1;
        margin-bottom: 1;
        background: $surface;
        border-left: thick $accent;
    }
    
    .status {
        color: $success;
        text-style: italic;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.tabbed_content = None
        self.status_widget = None
        self.dynamic_tab_counter = 0
        
    def compose(self) -> ComposeResult:
        with Vertical(classes="main-container"):
            yield Static("📊 股票监控系统 - 标签页演示", classes="header")
            
            # 创建标签页内容
            with TabbedContent("股票监控", "市场新闻", "系统设置", initial="tab-1", id="main-tabs"):
                # 第一个标签页：股票监控
                with TabPane("📈 股票监控", id="tab-1"):
                    yield StockDataWidget("HK.00700")
                    with Horizontal():
                        yield Button("切换到苹果", id="switch-aapl", variant="primary")
                        yield Button("切换到茅台", id="switch-moutai", variant="success")
                        yield Button("添加新股票", id="add-stock", variant="default")
                
                # 第二个标签页：市场新闻
                with TabPane("📰 市场新闻", id="tab-2"):
                    yield NewsWidget()
                
                # 第三个标签页：系统设置
                with TabPane("⚙️ 系统设置", id="tab-3"):
                    yield SettingsWidget()
            
            # 控制面板
            with Horizontal(classes="control-panel"):
                with Vertical():
                    yield Static("动态管理操作:")
                    with Horizontal():
                        yield Button("添加股票页", id="add-stock-tab", variant="success")
                        yield Button("添加分析页", id="add-analysis-tab", variant="primary")
                        yield Button("添加监控页", id="add-monitor-tab", variant="default")
                    with Horizontal():
                        yield Button("删除最后页", id="remove-last-tab", variant="error")
                        yield Button("清空所有页", id="clear-all-tabs", variant="warning")
                        yield Button("重置页面", id="reset-tabs", variant="default")
                
                with Vertical():
                    yield Static("页面控制:")
                    with Horizontal():
                        yield Button("禁用设置页", id="disable-settings")
                        yield Button("启用设置页", id="enable-settings")
                        yield Button("隐藏新闻页", id="hide-news")
                        yield Button("显示新闻页", id="show-news")
                
                with Vertical():
                    yield Static("状态信息:", classes="status", id="status")
    
    def on_mount(self) -> None:
        """组件挂载时获取引用"""
        self.tabbed_content = self.query_one("#main-tabs", TabbedContent)
        self.status_widget = self.query_one("#status", Static)
        self.update_status("系统已启动，当前显示股票监控页面")
    
    def update_status(self, message: str) -> None:
        """更新状态信息"""
        if self.status_widget:
            self.status_widget.update(f"状态: {message}")
    
    @on(Button.Pressed, "#switch-aapl")
    def on_switch_aapl(self, event: Button.Pressed) -> None:
        """切换到苹果股票"""
        event.stop()
        stock_widget = self.query_one(StockDataWidget)
        stock_widget.stock_code = "US.AAPL"
        stock_widget.update_stock_data()
        self.update_status("已切换到苹果公司 (US.AAPL)")
    
    @on(Button.Pressed, "#switch-moutai")
    def on_switch_moutai(self, event: Button.Pressed) -> None:
        """切换到茅台股票"""
        event.stop()
        stock_widget = self.query_one(StockDataWidget)
        stock_widget.stock_code = "SH.600519"
        stock_widget.update_stock_data()
        self.update_status("已切换到贵州茅台 (SH.600519)")
    
    @on(Button.Pressed, "#add-stock")
    async def on_add_stock(self, event: Button.Pressed) -> None:
        """添加新的股票标签页"""
        event.stop()
        
        # 创建新的股票监控标签页
        new_pane = TabPane(
            "📊 新股票",
            StockDataWidget("HK.00388"),
            id=f"stock-{self.tabbed_content.tab_count + 1}"
        )
        
        # 异步添加标签页
        await self.tabbed_content.add_pane(new_pane)
        self.update_status("已添加新的股票监控标签页")
    
    @on(Button.Pressed, "#add-stock-tab")
    async def on_add_stock_tab(self, event: Button.Pressed) -> None:
        """动态添加股票标签页"""
        event.stop()
        
        self.dynamic_tab_counter += 1
        stock_codes = ["HK.00700", "US.AAPL", "SH.600519", "HK.00388", "US.TSLA", "SZ.000001"]
        selected_stock = stock_codes[self.dynamic_tab_counter % len(stock_codes)]
        
        new_pane = TabPane(
            f"📈 股票-{self.dynamic_tab_counter}",
            StockDataWidget(selected_stock),
            id=f"dynamic-stock-{self.dynamic_tab_counter}"
        )
        
        await self.tabbed_content.add_pane(new_pane)
        self.update_status(f"已添加股票标签页: {selected_stock}")
    
    @on(Button.Pressed, "#add-analysis-tab")
    async def on_add_analysis_tab(self, event: Button.Pressed) -> None:
        """动态添加分析标签页"""
        event.stop()
        
        self.dynamic_tab_counter += 1
        
        # 创建分析内容
        analysis_content = Static(f"""
📊 技术分析报告 #{self.dynamic_tab_counter}

🔍 K线分析：当前处于上升趋势
📈 移动平均线：MA5 > MA10 > MA20
💹 成交量：放量上涨信号明显
⚡ RSI指标：处于超买区域，注意回调风险
🎯 支撑位：$340.00
🚀 阻力位：$380.00

⏰ 分析时间：实时更新
        """)
        
        new_pane = TabPane(
            f"📊 分析-{self.dynamic_tab_counter}",
            analysis_content,
            id=f"dynamic-analysis-{self.dynamic_tab_counter}"
        )
        
        await self.tabbed_content.add_pane(new_pane)
        self.update_status(f"已添加技术分析标签页")
    
    @on(Button.Pressed, "#add-monitor-tab")
    async def on_add_monitor_tab(self, event: Button.Pressed) -> None:
        """动态添加监控标签页"""
        event.stop()
        
        self.dynamic_tab_counter += 1
        
        # 创建监控内容
        monitor_content = Vertical()
        monitor_content.compose_add_child(Static(f"🖥️ 系统监控 #{self.dynamic_tab_counter}", classes="news-title"))
        monitor_content.compose_add_child(Static(""))
        monitor_content.compose_add_child(Static("📊 CPU使用率: 45%"))
        monitor_content.compose_add_child(Static("💾 内存使用率: 68%"))
        monitor_content.compose_add_child(Static("🌐 网络延迟: 15ms"))
        monitor_content.compose_add_child(Static("💽 磁盘使用率: 72%"))
        monitor_content.compose_add_child(Static("⚡ 数据更新频率: 5秒/次"))
        monitor_content.compose_add_child(Static(""))
        monitor_content.compose_add_child(Static("✅ 所有服务运行正常"))
        
        new_pane = TabPane(
            f"🖥️ 监控-{self.dynamic_tab_counter}",
            monitor_content,
            id=f"dynamic-monitor-{self.dynamic_tab_counter}"
        )
        
        await self.tabbed_content.add_pane(new_pane)
        self.update_status(f"已添加系统监控标签页")
    
    @on(Button.Pressed, "#remove-last-tab")
    async def on_remove_last_tab(self, event: Button.Pressed) -> None:
        """删除最后一个动态添加的标签页"""
        event.stop()
        
        # 查找最后一个动态添加的tab
        all_tabs = self.tabbed_content.query(TabPane)
        dynamic_tabs = [tab for tab in all_tabs if tab.id and tab.id.startswith("dynamic-")]
        
        if dynamic_tabs:
            last_tab = dynamic_tabs[-1]
            tab_id = last_tab.id
            await self.tabbed_content.remove_pane(tab_id)
            self.update_status(f"已删除标签页: {tab_id}")
        else:
            self.update_status("没有可删除的动态标签页")
    
    @on(Button.Pressed, "#clear-all-tabs")
    async def on_clear_all_tabs(self, event: Button.Pressed) -> None:
        """清空所有标签页"""
        event.stop()
        
        try:
            await self.tabbed_content.clear_panes()
            self.update_status("已清空所有标签页")
        except Exception as e:
            self.update_status(f"清空标签页失败: {str(e)}")
    
    @on(Button.Pressed, "#reset-tabs")
    async def on_reset_tabs(self, event: Button.Pressed) -> None:
        """重置为初始标签页"""
        event.stop()
        
        try:
            # 先清空所有标签页
            await self.tabbed_content.clear_panes()
            
            # 重新添加初始标签页
            stock_pane = TabPane("📈 股票监控", StockDataWidget("HK.00700"), id="tab-1")
            news_pane = TabPane("📰 市场新闻", NewsWidget(), id="tab-2")
            settings_pane = TabPane("⚙️ 系统设置", SettingsWidget(), id="tab-3")
            
            await self.tabbed_content.add_pane(stock_pane)
            await self.tabbed_content.add_pane(news_pane)
            await self.tabbed_content.add_pane(settings_pane)
            
            # 重置计数器
            self.dynamic_tab_counter = 0
            
            # 激活第一个标签页
            self.tabbed_content.active = "tab-1"
            
            self.update_status("已重置为初始标签页")
            
        except Exception as e:
            self.update_status(f"重置标签页失败: {str(e)}")
    
    @on(Button.Pressed, "#disable-settings")
    def on_disable_settings(self, event: Button.Pressed) -> None:
        """禁用设置页"""
        event.stop()
        self.tabbed_content.disable_tab("tab-3")
        self.update_status("设置页已禁用")
    
    @on(Button.Pressed, "#enable-settings")
    def on_enable_settings(self, event: Button.Pressed) -> None:
        """启用设置页"""
        event.stop()
        self.tabbed_content.enable_tab("tab-3")
        self.update_status("设置页已启用")
    
    @on(Button.Pressed, "#hide-news")
    def on_hide_news(self, event: Button.Pressed) -> None:
        """隐藏新闻页"""
        event.stop()
        self.tabbed_content.hide_tab("tab-2")
        self.update_status("新闻页已隐藏")
    
    @on(Button.Pressed, "#show-news")
    def on_show_news(self, event: Button.Pressed) -> None:
        """显示新闻页"""
        event.stop()
        self.tabbed_content.show_tab("tab-2")
        self.update_status("新闻页已显示")
    
    # 设置页面按钮事件处理
    @on(Button.Pressed, "#notification-btn")
    def on_notification_pressed(self, event: Button.Pressed) -> None:
        """通知设置按钮"""
        event.stop()
        self.update_status("通知设置功能待开发")
    
    @on(Button.Pressed, "#theme-btn")
    def on_theme_pressed(self, event: Button.Pressed) -> None:
        """主题设置按钮"""
        event.stop()
        self.update_status("主题设置功能待开发")
    
    @on(Button.Pressed, "#data-btn")
    def on_data_pressed(self, event: Button.Pressed) -> None:
        """数据源配置按钮"""
        event.stop()
        self.update_status("数据源配置功能待开发")
    
    @on(Button.Pressed, "#account-btn")
    def on_account_pressed(self, event: Button.Pressed) -> None:
        """账户管理按钮"""
        event.stop()
        self.update_status("账户管理功能待开发")
    
    @on(TabbedContent.TabActivated)
    def on_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """标签页激活事件"""
        tab_names = {
            "tab-1": "股票监控",
            "tab-2": "市场新闻", 
            "tab-3": "系统设置"
        }
        
        tab_name = tab_names.get(event.tab.id, "未知页面")
        self.update_status(f"当前激活页面: {tab_name}")


if __name__ == "__main__":
    app = TabExample()
    app.run()