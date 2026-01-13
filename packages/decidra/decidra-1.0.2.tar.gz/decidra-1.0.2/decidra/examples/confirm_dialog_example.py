#!/usr/bin/env python3
"""
确认对话框使用示例
演示如何在Textual应用中使用ConfirmDialog组件
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static, Header, Footer
from textual.binding import Binding
from textual_window import Window, WindowBar, WindowSwitcher


from monitor.widgets.dialog import ConfirmDialog


class ConfirmDialogDemo(App):
    """确认对话框演示应用"""
    
    CSS = """
    .demo-container {
        padding: 2;
        height: 1fr;
        align: center middle;
    }
    
    .demo-buttons {
        layout: horizontal;
        height: auto;
        width: auto;
        align: center middle;
    }
    
    .demo-buttons Button {
        margin: 0 1;
        min-width: 20;
    }
    
    .status-text {
        text-align: center;
        margin: 2 0;
        height: auto;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "退出"),
    ]
    
    def __init__(self):
        super().__init__()
        self.confirm_dialog = None
        self.status_text = None
    
    def compose(self) -> ComposeResult:
        """构建演示界面"""
        yield Header()
        
        with Vertical(classes="demo-container"):
            yield Static(
                "[bold cyan]确认对话框演示[/bold cyan]\n\n"
                "点击下面的按钮测试不同类型的确认对话框",
                classes="status-text"
            )
            
            with Horizontal(classes="demo-buttons"):
                yield Button("删除确认", variant="error", id="delete-btn")
                yield Button("保存确认", variant="success", id="save-btn")
                yield Button("退出确认", variant="warning", id="exit-btn")
                yield Button("自定义确认", variant="primary", id="custom-btn")
            
            self.status_text = Static(
                "[dim]等待用户操作...[/dim]",
                classes="status-text"
            )
            yield self.status_text
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id
        
        if button_id == "delete-btn":
            self.show_delete_confirm()
        elif button_id == "save-btn":
            self.show_save_confirm()
        elif button_id == "exit-btn":
            self.show_exit_confirm()
        elif button_id == "custom-btn":
            self.show_custom_confirm()
    
    def show_delete_confirm(self) -> None:
        """显示删除确认对话框"""
        if self.confirm_dialog:
            self.confirm_dialog.remove()
        
        self.confirm_dialog = ConfirmDialog(
            message="确定要删除这个项目吗？\n\n[red]警告：此操作不可撤销！[/red]",
            title="删除确认",
            confirm_text="删除",
            cancel_text="取消"
        )
        
        self.mount(self.confirm_dialog)
        self.confirm_dialog.show()
        self.status_text.update("[yellow]等待删除确认...[/yellow]")
    
    def show_save_confirm(self) -> None:
        """显示保存确认对话框"""
        if self.confirm_dialog:
            self.confirm_dialog.remove()
        
        self.confirm_dialog = ConfirmDialog(
            message="确定要保存当前更改吗？\n\n所有修改将被永久保存。",
            title="保存确认",
            confirm_text="保存",
            cancel_text="取消"
        )
        
        self.mount(self.confirm_dialog)
        self.confirm_dialog.show()
        self.status_text.update("[blue]等待保存确认...[/blue]")
    
    def show_exit_confirm(self) -> None:
        """显示退出确认对话框"""
        if self.confirm_dialog:
            self.confirm_dialog.remove()
        
        self.confirm_dialog = ConfirmDialog(
            message="确定要退出应用程序吗？\n\n未保存的更改将丢失。",
            title="退出确认",
            confirm_text="退出",
            cancel_text="继续使用"
        )
        
        self.mount(self.confirm_dialog)
        self.confirm_dialog.show()
        self.status_text.update("[red]等待退出确认...[/red]")
    
    def show_custom_confirm(self) -> None:
        """显示自定义确认对话框"""
        if self.confirm_dialog:
            self.confirm_dialog.remove()
        
        self.confirm_dialog = ConfirmDialog(
            message="这是一个自定义的确认对话框示例。\n\n"
                   "您可以自定义消息内容、标题和按钮文本。\n"
                   "支持Rich格式化文本和多行显示。",
            title="自定义确认",
            confirm_text="同意",
            cancel_text="拒绝"
        )
        
        self.mount(self.confirm_dialog)
        self.confirm_dialog.show()
        self.status_text.update("[cyan]等待自定义确认...[/cyan]")
    
    def on_confirm_dialog_confirm(self, message: ConfirmDialog.Confirm) -> None:
        """处理确认消息"""
        self.status_text.update("[bold green]✓ 用户确认了操作[/bold green]")
        
        if self.confirm_dialog:
            self.confirm_dialog.hide()
    
    def on_confirm_dialog_cancel(self, message: ConfirmDialog.Cancel) -> None:
        """处理取消消息"""
        self.status_text.update("[bold red]✗ 用户取消了操作[/bold red]")
        
        if self.confirm_dialog:
            self.confirm_dialog.hide()


def main():
    """运行演示应用"""
    app = ConfirmDialogDemo()
    app.title = "确认对话框演示"
    app.sub_title = "演示各种确认对话框的使用方法"
    app.run()


if __name__ == "__main__":
    main() 