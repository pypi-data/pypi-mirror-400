#!/usr/bin/env python3
"""
简单的 AutoComplete 测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textual.app import App, ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical
from textual_autocomplete._autocomplete import DropdownItem, TargetState

from monitor.widgets.window_dialog import show_input_dialog


class SimpleAutoCompleteTest(App):
    """简单的 AutoComplete 测试应用"""
    
    def compose(self) -> ComposeResult:
        """构建界面"""
        with Vertical():
            yield Static("AutoComplete 测试", id="title")
            yield Button("测试水果选择", id="test-btn")
            yield Static("结果将显示在这里", id="result")
    
    def fruit_candidates(self, state: TargetState) -> list[DropdownItem]:
        """水果候选项"""
        fruits = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
        
        # 简单过滤
        filtered = [f for f in fruits if state.text.lower() in f.lower()]
        
        return [DropdownItem(fruit) for fruit in filtered[:5]]
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击"""
        if event.button.id == "test-btn":
            try:
                result = await show_input_dialog(
                    self,
                    message="请选择水果:",
                    title="水果选择",
                    placeholder="输入水果名称...",
                    candidates_callback=self.fruit_candidates
                )
                
                if result:
                    self.query_one("#result").update(f"选择的水果: {result}")
                else:
                    self.query_one("#result").update("已取消选择")
            except Exception as e:
                self.query_one("#result").update(f"错误: {str(e)}")


if __name__ == "__main__":
    app = SimpleAutoCompleteTest()
    app.run()