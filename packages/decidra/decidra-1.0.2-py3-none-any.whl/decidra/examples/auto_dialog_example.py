"""
自动补全输入对话框使用示例
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textual.app import App, ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical, Horizontal
from textual import on

from textual_autocomplete._autocomplete import DropdownItem, TargetState

from monitor.widgets.auto_dialog import WindowInputDialog


class AutoCompleteDialogExample(App):
    """自动补全对话框示例应用"""
    
    CSS = """
    Screen {
        align: center middle;
        background: $background;
    }
    
    .container {
        width: 60;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }
    
    .title {
        text-align: center;
        margin-bottom: 2;
        color: $primary;
        text-style: bold;
    }
    
    .result {
        margin-top: 2;
        padding: 1;
        background: $panel;
        border: solid $secondary;
        height: auto;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.result_widget = None
        
    def compose(self) -> ComposeResult:
        with Vertical(classes="container"):
            yield Static("自动补全输入对话框示例", classes="title")
            
            with Horizontal():
                yield Button("股票代码输入", id="stock-btn", variant="primary")
                yield Button("水果名称输入", id="fruit-btn", variant="success")
                yield Button("普通输入", id="normal-btn", variant="default")
            
            yield Static("结果将显示在这里...", classes="result", id="result")
    
    def on_mount(self) -> None:
        """组件挂载时获取结果显示组件"""
        self.result_widget = self.query_one("#result", Static)
    
    @on(Button.Pressed, "#stock-btn")
    def on_stock_button_pressed(self, event: Button.Pressed) -> None:
        """打开股票代码输入对话框"""
        event.stop()
        
        def stock_candidates_callback(state: TargetState) -> list[DropdownItem]:
            stock_codes = [
                "HK.00700",  # 腾讯控股
                "HK.00175",  # 吉利汽车
                "HK.00388",  # 香港交易所
                "HK.00939",  # 建设银行
                "HK.01398",  # 工商银行
                "US.AAPL",   # 苹果
                "US.TSLA",   # 特斯拉
                "US.GOOGL",  # 谷歌
                "US.MSFT",   # 微软
                "US.AMZN",   # 亚马逊
                "SH.600000", # 浦发银行
                "SH.600519", # 贵州茅台
                "SH.600036", # 招商银行
                "SZ.000001", # 平安银行
                "SZ.000002", # 万科A
            ]
            
            # 根据输入过滤股票代码
            filtered = [code for code in stock_codes if code.upper().startswith(state.text.upper())]
            return [
                DropdownItem(code, prefix="📈 ")
                for code in filtered
            ]
        
        dialog = WindowInputDialog(
            message="请输入股票代码:",
            title="股票选择",
            placeholder="例如: HK.00700",
            enable_autocomplete=True,
            candidates_callback=stock_candidates_callback,
            submit_callback=self.on_stock_submit
        )
        
        self.push_screen(dialog)
    
    @on(Button.Pressed, "#fruit-btn")
    def on_fruit_button_pressed(self, event: Button.Pressed) -> None:
        """打开水果名称输入对话框"""
        event.stop()
        
        def fruit_candidates_callback(state: TargetState) -> list[DropdownItem]:
            fruits = [
                "Apple", "Banana", "Cherry", "Orange", "Pineapple", 
                "Strawberry", "Watermelon", "Grape", "Mango", "Peach"
            ]
            
            # 根据输入过滤水果名称
            filtered = [fruit for fruit in fruits if fruit.lower().startswith(state.text.lower())]
            return [
                DropdownItem(fruit, prefix="🍎 ")
                for fruit in filtered
            ]
        
        dialog = WindowInputDialog(
            message="请输入水果名称:",
            title="水果选择",
            placeholder="例如: Apple",
            enable_autocomplete=True,
            candidates_callback=fruit_candidates_callback,
            submit_callback=self.on_fruit_submit
        )
        
        self.push_screen(dialog)
    
    @on(Button.Pressed, "#normal-btn")
    def on_normal_button_pressed(self, event: Button.Pressed) -> None:
        """打开普通输入对话框"""
        event.stop()
        
        dialog = WindowInputDialog(
            message="请输入任意文本:",
            title="普通输入",
            placeholder="输入任意内容...",
            enable_autocomplete=False,
            submit_callback=self.on_normal_submit
        )
        
        self.push_screen(dialog)
    
    def on_stock_submit(self, value: str) -> None:
        """处理股票代码提交"""
        if self.result_widget:
            self.result_widget.update(f"已选择股票代码: {value}")
    
    def on_fruit_submit(self, value: str) -> None:
        """处理水果名称提交"""
        if self.result_widget:
            self.result_widget.update(f"已选择水果: {value}")
    
    def on_normal_submit(self, value: str) -> None:
        """处理普通输入提交"""
        if self.result_widget:
            self.result_widget.update(f"输入的文本: {value}")
    
    @on(WindowInputDialog.InputResult)
    def on_input_result(self, event: WindowInputDialog.InputResult) -> None:
        """处理输入结果消息"""
        if event.submitted:
            self.log(f"用户提交了: {event.value}")
        else:
            self.log("用户取消了输入")
            if self.result_widget:
                self.result_widget.update("用户取消了输入")


if __name__ == "__main__":
    app = AutoCompleteDialogExample()
    app.run()