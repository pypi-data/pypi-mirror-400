#!/usr/bin/env python3
"""
窗口化对话框使用示例
演示如何在Textual应用中使用WindowConfirmDialog和WindowInputDialog组件
基于textual-window设计模式的现代化对话框
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Grid
from textual.widgets import Button, Static, Header, Footer, Label
from textual.binding import Binding
from textual.validation import Function, ValidationResult
from datetime import datetime

from monitor.widgets.window_dialog import (
    WindowConfirmDialog, 
    WindowInputDialog,
    WindowDialogWithInput,
    show_confirm_dialog,
    show_input_dialog,
    show_embedded_input_dialog,
    CommonDialogs
)


class WindowDialogDemo(App):
    """窗口化对话框演示应用"""
    
    CSS = """
    .demo-container {
        padding: 2;
        height: 1fr;
        layout: vertical;
    }
    
    .demo-section {
        margin-bottom: 2;
        border: solid $primary;
        padding: 1;
        height: auto;
    }
    
    .section-title {
        text-align: center;
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
    }
    
    .demo-grid {
        layout: grid;
        grid-size: 3 2;
        grid-gutter: 1 2;
        height: auto;
        margin: 1 0;
    }
    
    .demo-grid Button {
        height: 4;
        min-width: 20;
    }
    
    .status-panel {
        height: 10;
        border: solid $primary;
        padding: 1;
        margin-top: 2;
        background: $surface;
    }
    
    .status-text {
        height: 1fr;
        text-align: left;
        color: $text;
    }
    
    .success { color: $success; }
    .error { color: $error; }
    .warning { color: $warning; }
    .info { color: $primary; }
    """
    
    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("c", "clear_log", "清空日志"),
        Binding("h", "show_help", "帮助"),
    ]
    
    def __init__(self):
        super().__init__()
        self.log_messages = []
        self.status_text = None
        self.user_data = {}  # 存储用户输入的数据
    
    def compose(self) -> ComposeResult:
        """构建演示界面"""
        yield Header()
        
        with Vertical(classes="demo-container"):
            yield Static(
                "[bold cyan]窗口化对话框演示[/bold cyan]\n"
                "基于ModalScreen的现代化对话框体验 - 确认 & 输入 & 内嵌表单",
                id="title"
            )
            
            # 确认对话框部分
            with Vertical(classes="demo-section"):
                yield Label("[bold]确认对话框演示[/bold]", classes="section-title")
                with Grid(classes="demo-grid"):
                    yield Button("删除文件", variant="error", id="delete-btn")
                    yield Button("保存更改", variant="success", id="save-btn")
                    yield Button("退出应用", variant="warning", id="exit-btn")
                    yield Button("自定义确认", variant="primary", id="custom-confirm-btn")
                    yield Button("回调演示", variant="default", id="callback-btn")
                    yield Button("异步流程", variant="default", id="async-btn")
            
            # 输入对话框部分
            with Vertical(classes="demo-section"):
                yield Label("[bold]输入对话框演示[/bold]", classes="section-title")
                with Grid(classes="demo-grid"):
                    yield Button("文本输入", variant="primary", id="text-input-btn")
                    yield Button("数字输入", variant="success", id="number-input-btn")
                    yield Button("密码输入", variant="warning", id="password-input-btn")
                    yield Button("文件名输入", variant="error", id="filename-input-btn")
                    yield Button("自定义验证", variant="default", id="custom-input-btn")
                    yield Button("用户信息", variant="default", id="user-info-btn")
            
            # 内嵌输入对话框部分
            with Vertical(classes="demo-section"):
                yield Label("[bold]内嵌输入对话框演示[/bold]", classes="section-title")
                with Grid(classes="demo-grid"):
                    yield Button("用户表单", variant="primary", id="embedded-user-btn")
                    yield Button("登录表单", variant="success", id="embedded-login-btn")
                    yield Button("自定义表单", variant="warning", id="embedded-custom-btn")
                    yield Button("订单表单", variant="error", id="embedded-order-btn")
                    yield Button("设置表单", variant="default", id="embedded-settings-btn")
                    yield Button("反馈表单", variant="default", id="embedded-feedback-btn")
            
            # WindowDialogWithInput直接使用演示部分
            with Vertical(classes="demo-section"):
                yield Label("[bold]WindowDialogWithInput 直接使用演示[/bold]", classes="section-title")
                with Grid(classes="demo-grid"):
                    yield Button("基础API调用", variant="primary", id="direct-basic-btn")
                    yield Button("高级验证", variant="success", id="direct-validation-btn")
                    yield Button("动态字段", variant="warning", id="direct-dynamic-btn")
                    yield Button("回调演示", variant="error", id="direct-callback-btn")
                    yield Button("配置向导", variant="default", id="direct-wizard-btn")
                    yield Button("批量操作", variant="default", id="direct-batch-btn")
            
            # 状态面板
            with Vertical(classes="status-panel"):
                yield Label("[bold]操作日志与用户数据[/bold]")
                self.status_text = Static(
                    "准备就绪，点击上方按钮测试对话框功能...",
                    classes="status-text"
                )
                yield self.status_text
        
        yield Footer()
    
    def log_message(self, message: str, level: str = "info"):
        """记录消息到状态面板"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "info": "info",
            "success": "success", 
            "error": "error",
            "warning": "warning"
        }
        color = color_map.get(level, "info")
        
        formatted_msg = f"[{color}]{timestamp}[/{color}] {message}"
        self.log_messages.append(formatted_msg)
        
        # 保持最近12条消息
        if len(self.log_messages) > 12:
            self.log_messages.pop(0)
        
        self.update_status_display()
    
    def update_status_display(self):
        """更新状态显示"""
        if self.status_text:
            content = "\n".join(self.log_messages)
            
            # 添加用户数据显示
            if self.user_data:
                data_lines = ["\n[bold yellow]用户数据:[/bold yellow]"]
                for key, value in self.user_data.items():
                    # 密码字段特殊处理
                    display_value = "*" * len(str(value)) if "密码" in key else str(value)
                    data_lines.append(f"  {key}: {display_value}")
                content += "\n" + "\n".join(data_lines)
            
            self.status_text.update(content or "日志已清空...")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id
        
        # 确认对话框演示
        if button_id == "delete-btn":
            self.run_worker(self.show_delete_confirm(), exclusive=True)
        elif button_id == "save-btn":
            self.run_worker(self.show_save_confirm(), exclusive=True)
        elif button_id == "exit-btn":
            self.run_worker(self.show_exit_confirm(), exclusive=True)
        elif button_id == "custom-confirm-btn":
            self.run_worker(self.show_custom_confirm(), exclusive=True)
        elif button_id == "callback-btn":
            self.run_worker(self.show_callback_demo(), exclusive=True)
        elif button_id == "async-btn":
            self.run_worker(self.show_async_demo(), exclusive=True)
        
        # 输入对话框演示
        elif button_id == "text-input-btn":
            self.run_worker(self.show_text_input(), exclusive=True)
        elif button_id == "number-input-btn":
            self.run_worker(self.show_number_input(), exclusive=True)
        elif button_id == "password-input-btn":
            self.run_worker(self.show_password_input(), exclusive=True)
        elif button_id == "filename-input-btn":
            self.run_worker(self.show_filename_input(), exclusive=True)
        elif button_id == "custom-input-btn":
            self.run_worker(self.show_custom_input(), exclusive=True)
        elif button_id == "user-info-btn":
            self.run_worker(self.show_user_info_demo(), exclusive=True)
        
        # 内嵌输入对话框演示
        elif button_id == "embedded-user-btn":
            self.run_worker(self.show_embedded_user_form(), exclusive=True)
        elif button_id == "embedded-login-btn":
            self.run_worker(self.show_embedded_login_form(), exclusive=True)
        elif button_id == "embedded-custom-btn":
            self.run_worker(self.show_embedded_custom_form(), exclusive=True)
        elif button_id == "embedded-order-btn":
            self.run_worker(self.show_embedded_order_form(), exclusive=True)
        elif button_id == "embedded-settings-btn":
            self.run_worker(self.show_embedded_settings_form(), exclusive=True)
        elif button_id == "embedded-feedback-btn":
            self.run_worker(self.show_embedded_feedback_form(), exclusive=True)
        
        # WindowDialogWithInput直接使用演示部分
        elif button_id == "direct-basic-btn":
            self.run_worker(self.show_direct_basic_demo(), exclusive=True)
        elif button_id == "direct-validation-btn":
            self.run_worker(self.show_direct_validation_demo(), exclusive=True)
        elif button_id == "direct-dynamic-btn":
            self.run_worker(self.show_direct_dynamic_demo(), exclusive=True)
        elif button_id == "direct-callback-btn":
            self.run_worker(self.show_direct_callback_demo(), exclusive=True)
        elif button_id == "direct-wizard-btn":
            self.run_worker(self.show_direct_wizard_demo(), exclusive=True)
        elif button_id == "direct-batch-btn":
            self.run_worker(self.show_direct_batch_demo(), exclusive=True)
    
    # ==================== 确认对话框演示方法 ====================
    
    async def show_delete_confirm(self) -> None:
        """显示删除确认对话框"""
        try:
            self.log_message("显示删除确认对话框", "info")
            
            result = await CommonDialogs.confirm_delete(self, "重要文件 config.ini")
            
            if result:
                self.log_message("✓ 用户确认删除操作", "success")
            else:
                self.log_message("✗ 用户取消删除操作", "warning")
        except Exception as e:
            self.log_message(f"删除确认操作失败: {e}", "error")
    
    async def show_save_confirm(self) -> None:
        """显示保存确认对话框"""
        try:
            self.log_message("显示保存确认对话框", "info")
            
            result = await CommonDialogs.confirm_save(self, "配置文件更改")
            
            if result:
                self.log_message("✓ 文件已保存", "success")
            else:
                self.log_message("✗ 保存已取消", "warning")
        except Exception as e:
            self.log_message(f"保存确认操作失败: {e}", "error")
    
    async def show_exit_confirm(self) -> None:
        """显示退出确认对话框"""
        try:
            self.log_message("显示退出确认对话框", "info")
            
            result = await CommonDialogs.confirm_exit(self)
            
            if result:
                self.log_message("✓ 用户确认退出", "success")
                self.log_message("(演示模式: 实际应用中会退出)", "info")
            else:
                self.log_message("✗ 取消退出操作", "warning")
        except Exception as e:
            self.log_message(f"退出确认操作失败: {e}", "error")
    
    async def show_custom_confirm(self) -> None:
        """显示自定义确认对话框"""
        try:
            self.log_message("显示自定义确认对话框", "info")
            
            result = await show_confirm_dialog(
                self,
                message="这是一个完全自定义的确认对话框。\n\n"
                       "您可以自定义：\n"
                       "• 消息内容和格式\n"
                       "• 窗口标题\n"
                       "• 按钮文本\n"
                       "• 回调函数\n"
                       "• 对话框ID\n\n"
                       "[yellow]是否继续演示？[/yellow]",
                title="自定义确认演示",
                confirm_text="继续",
                cancel_text="返回",
                dialog_id="custom-confirm-demo"
            )
            
            if result:
                self.log_message("✓ 用户选择继续演示", "success")
            else:
                self.log_message("✗ 用户选择返回", "warning")
        except Exception as e:
            self.log_message(f"自定义确认对话框操作失败: {e}", "error")
    
    async def show_callback_demo(self) -> None:
        """显示回调函数演示"""
        try:
            self.log_message("显示回调函数演示", "info")
            
            def confirm_callback():
                self.log_message("🔄 确认回调函数已执行", "success")
            
            def cancel_callback():
                self.log_message("🔄 取消回调函数已执行", "warning")
            
            result = await show_confirm_dialog(
                self,
                message="这个对话框演示回调函数功能。\n\n"
                       "无论您选择确认还是取消，\n"
                       "相应的回调函数都会被执行。\n\n"
                       "查看下方日志可以看到回调执行情况。",
                title="回调演示",
                confirm_text="确认",
                cancel_text="取消",
                confirm_callback=confirm_callback,
                cancel_callback=cancel_callback,
                dialog_id="callback-demo"
            )
            
            if result:
                self.log_message("✓ 对话框返回: 确认", "success")
            else:
                self.log_message("✗ 对话框返回: 取消", "warning")
        except Exception as e:
            self.log_message(f"回调演示操作失败: {e}", "error")
    
    async def show_async_demo(self) -> None:
        """显示异步等待演示"""
        try:
            self.log_message("开始异步操作演示...", "info")
            
            # 第一个对话框
            result1 = await show_confirm_dialog(
                self,
                message="这是异步操作演示的第一步。\n\n"
                       "点击确认继续下一步操作。",
                title="异步演示 - 步骤 1/3",
                confirm_text="下一步",
                cancel_text="取消"
            )
            
            if not result1:
                self.log_message("✗ 用户在第一步取消操作", "warning")
                return
            
            self.log_message("✓ 第一步完成，继续第二步...", "info")
            
            # 第二个对话框
            result2 = await show_confirm_dialog(
                self,
                message="这是第二步操作。\n\n"
                       "您已经完成了第一步，\n"
                       "确认继续最后一步吗？",
                title="异步演示 - 步骤 2/3",
                confirm_text="完成",
                cancel_text="返回"
            )
            
            if not result2:
                self.log_message("✗ 用户在第二步取消操作", "warning")
                return
            
            self.log_message("✓ 第二步完成，执行最终确认...", "info")
            
            # 最终确认
            result3 = await show_confirm_dialog(
                self,
                message="恭喜！您已完成所有步骤。\n\n"
                       "[green]✓ 步骤 1: 已完成[/green]\n"
                       "[green]✓ 步骤 2: 已完成[/green]\n"
                       "[yellow]◆ 步骤 3: 等待确认[/yellow]\n\n"
                       "确认提交所有更改？",
                title="异步演示 - 最终确认",
                confirm_text="提交",
                cancel_text="放弃"
            )
            
            if result3:
                self.log_message("🎉 异步操作演示完成！所有步骤已提交", "success")
            else:
                self.log_message("⚠️ 用户放弃最终提交", "warning")
        except Exception as e:
            self.log_message(f"异步操作演示失败: {e}", "error")
    
    # ==================== 输入对话框演示方法 ====================
    
    async def show_text_input(self) -> None:
        """显示文本输入对话框"""
        try:
            self.log_message("显示文本输入对话框", "info")
            
            result = await CommonDialogs.input_text(
                self, 
                "请输入您的姓名:",
                title="文本输入演示",
                placeholder="例如: 张三",
                default_value=self.user_data.get("姓名", "")
            )
            
            if result:
                self.user_data["姓名"] = result
                self.log_message(f"✓ 用户输入姓名: {result}", "success")
            else:
                self.log_message("✗ 用户取消文本输入", "warning")
        except Exception as e:
            self.log_message(f"文本输入操作失败: {e}", "error")
    
    async def show_number_input(self) -> None:
        """显示数字输入对话框"""
        try:
            self.log_message("显示数字输入对话框", "info")
            
            result = await CommonDialogs.input_number(
                self,
                "请输入您的年龄:",
                title="数字输入演示",
                placeholder="例如: 25",
                default_value=self.user_data.get("年龄", "")
            )
            
            if result:
                self.user_data["年龄"] = result
                self.log_message(f"✓ 用户输入年龄: {result}", "success")
            else:
                self.log_message("✗ 用户取消数字输入", "warning")
        except Exception as e:
            self.log_message(f"数字输入操作失败: {e}", "error")
    
    async def show_password_input(self) -> None:
        """显示密码输入对话框"""
        try:
            self.log_message("显示密码输入对话框", "info")
            
            result = await CommonDialogs.input_password(
                self,
                "请输入密码:\n\n[dim]注意: 输入的内容将被隐藏[/dim]",
                title="密码输入演示"
            )
            
            if result:
                self.user_data["密码"] = result
                self.log_message(f"✓ 用户输入密码: {'*' * len(result)}", "success")
            else:
                self.log_message("✗ 用户取消密码输入", "warning")
        except Exception as e:
            self.log_message(f"密码输入操作失败: {e}", "error")
    
    async def show_filename_input(self) -> None:
        """显示文件名输入对话框"""
        try:
            self.log_message("显示文件名输入对话框", "info")
            
            result = await CommonDialogs.input_filename(
                self,
                "请输入文件名:\n\n[dim]文件名不能包含特殊字符: < > : \" / \\ | ? *[/dim]",
                title="文件名输入演示",
                placeholder="例如: document.txt",
                default_value=self.user_data.get("文件名", "")
            )
            
            if result:
                self.user_data["文件名"] = result
                self.log_message(f"✓ 用户输入文件名: {result}", "success")
            else:
                self.log_message("✗ 用户取消文件名输入", "warning")
        except Exception as e:
            self.log_message(f"文件名输入操作失败: {e}", "error")
    
    async def show_custom_input(self) -> None:
        """显示自定义验证输入对话框"""
        try:
            self.log_message("显示自定义验证输入对话框", "info")
            
            # 自定义邮箱验证器
            def validate_email(value: str):
                if "@" not in value or "." not in value:
                    raise ValueError("请输入有效的邮箱地址")
                if len(value) < 5:
                    raise ValueError("邮箱地址太短")
                return True
            
            result = await show_input_dialog(
                self,
                message="请输入您的邮箱地址:\n\n"
                       "[dim]验证规则:[/dim]\n"
                       "[dim]• 必须包含 @ 符号[/dim]\n"
                       "[dim]• 必须包含 . 符号[/dim]\n"
                       "[dim]• 长度至少5个字符[/dim]",
                title="邮箱输入 - 自定义验证",
                placeholder="例如: user@example.com",
                validator=Function(validate_email),
                default_value=self.user_data.get("邮箱", "")
            )
            
            if result:
                self.user_data["邮箱"] = result
                self.log_message(f"✓ 用户输入邮箱: {result}", "success")
            else:
                self.log_message("✗ 用户取消邮箱输入", "warning")
        except Exception as e:
            self.log_message(f"自定义验证输入操作失败: {e}", "error")
    
    async def show_user_info_demo(self) -> None:
        """显示用户信息收集演示"""
        try:
            self.log_message("开始用户信息收集演示...", "info")
            
            # 确认开始收集
            start_confirm = await show_confirm_dialog(
                self,
                message="即将开始收集用户信息。\n\n"
                       "这将演示如何使用多个输入对话框\n"
                       "依次收集不同类型的用户数据。\n\n"
                       "是否开始收集？",
                title="用户信息收集",
                confirm_text="开始",
                cancel_text="取消"
            )
            
            if not start_confirm:
                self.log_message("✗ 用户取消信息收集", "warning")
                return
            
            # 收集姓名
            name = await show_input_dialog(
                self,
                "第1步: 请输入您的姓名",
                title="信息收集 1/4 - 姓名",
                placeholder="姓名",
                required=True
            )
            
            if not name:
                self.log_message("✗ 用户在姓名输入步骤取消", "warning")
                return
            
            # 收集年龄
            age = await CommonDialogs.input_number(
                self,
                "第2步: 请输入您的年龄",
                title="信息收集 2/4 - 年龄"
            )
            
            if not age:
                self.log_message("✗ 用户在年龄输入步骤取消", "warning")
                return
            
            # 收集邮箱
            def validate_email(value: str):
                if "@" not in value:
                    raise ValueError("邮箱必须包含@符号")
                return True
            
            email = await show_input_dialog(
                self,
                "第3步: 请输入您的邮箱",
                title="信息收集 3/4 - 邮箱",
                validator=Function(validate_email),
                placeholder="user@example.com"
            )
            
            if not email:
                self.log_message("✗ 用户在邮箱输入步骤取消", "warning")
                return
            
            # 收集备注
            note = await show_input_dialog(
                self,
                "第4步: 请输入备注信息 (可选)",
                title="信息收集 4/4 - 备注",
                required=False,
                placeholder="其他信息..."
            )
            
            # 最终确认
            summary = f"姓名: {name}\n年龄: {age}\n邮箱: {email}\n备注: {note or '无'}"
            
            final_confirm = await show_confirm_dialog(
                self,
                f"请确认您的信息:\n\n{summary}\n\n确认保存这些信息吗？",
                title="确认用户信息",
                confirm_text="保存",
                cancel_text="重新输入"
            )
            
            if final_confirm:
                # 保存所有信息
                self.user_data.update({
                    "姓名": name,
                    "年龄": age,
                    "邮箱": email,
                    "备注": note or "无"
                })
                self.log_message("🎉 用户信息收集完成并已保存！", "success")
            else:
                self.log_message("✗ 用户选择重新输入信息", "warning")
        except Exception as e:
            self.log_message(f"用户信息收集失败: {e}", "error")
    
    # ==================== 内嵌输入对话框演示方法 ====================
    
    async def show_embedded_user_form(self) -> None:
        """显示内嵌用户信息表单"""
        try:
            self.log_message("显示内嵌用户信息表单", "info")
            
            result = await CommonDialogs.embedded_user_form(self, "用户信息收集")
            
            if result:
                # 保存到用户数据
                self.user_data.update(result)
                self.log_message("✓ 用户信息表单提交成功", "success")
                for key, value in result.items():
                    self.log_message(f"  {key}: {value}", "info")
            else:
                self.log_message("✗ 用户取消信息表单", "warning")
        except Exception as e:
            self.log_message(f"用户信息表单操作失败: {e}", "error")
    
    async def show_embedded_login_form(self) -> None:
        """显示内嵌登录表单"""
        try:
            self.log_message("显示内嵌登录表单", "info")
            
            result = await CommonDialogs.embedded_login_form(self)
            
            if result:
                # 保存登录信息（密码除外）
                login_data = {k: v for k, v in result.items() if k != 'password'}
                login_data['password'] = '*' * len(result.get('password', ''))
                self.user_data.update(login_data)
                self.log_message("✓ 登录信息提交成功", "success")
                self.log_message(f"  用户名: {result.get('username', '')}", "info")
                self.log_message(f"  记住我: {result.get('remember', 'no')}", "info")
            else:
                self.log_message("✗ 用户取消登录", "warning")
        except Exception as e:
            self.log_message(f"登录表单操作失败: {e}", "error")
    
    async def show_embedded_custom_form(self) -> None:
        """显示自定义内嵌表单"""
        try:
            self.log_message("显示自定义内嵌表单", "info")
            
            def validate_url(value: str):
                if not value.startswith(('http://', 'https://')):
                    raise ValueError("URL必须以http://或https://开头")
                return True
            
            def validate_positive_number(value: str):
                try:
                    num = float(value)
                    if num <= 0:
                        raise ValueError("必须是正数")
                    return True
                except ValueError:
                    raise ValueError("请输入有效的正数")
            
            input_fields = [
                {
                    'name': 'project_name',
                    'label': '项目名称',
                    'placeholder': '请输入项目名称',
                    'required': True
                },
                {
                    'name': 'website_url',
                    'label': '网站URL',
                    'placeholder': 'https://example.com',
                    'required': True,
                    'validator': Function(validate_url)
                },
                {
                    'name': 'budget',
                    'label': '预算金额',
                    'placeholder': '请输入预算（元）',
                    'required': True,
                    'validator': Function(validate_positive_number)
                },
                {
                    'name': 'description',
                    'label': '项目描述',
                    'placeholder': '请描述项目详情',
                    'required': False
                }
            ]
            
            result = await show_embedded_input_dialog(
                self,
                message="请填写自定义项目信息：",
                input_fields=input_fields,
                title="自定义项目表单",
                show_preview=True
            )
            
            if result:
                self.user_data.update({f"项目_{k}": v for k, v in result.items()})
                self.log_message("✓ 自定义表单提交成功", "success")
            else:
                self.log_message("✗ 用户取消自定义表单", "warning")
        except Exception as e:
            self.log_message(f"自定义表单操作失败: {e}", "error")
    
    async def show_embedded_order_form(self) -> None:
        """显示订单表单"""
        try:
            self.log_message("显示订单表单", "info")
            
            def validate_quantity(value: str):
                try:
                    qty = int(value)
                    if qty <= 0:
                        raise ValueError("数量必须大于0")
                    if qty > 999:
                        raise ValueError("数量不能超过999")
                    return True
                except ValueError:
                    raise ValueError("请输入有效的数量（1-999）")
            
            input_fields = [
                {
                    'name': 'product',
                    'label': '产品名称',
                    'placeholder': '请选择或输入产品名称',
                    'required': True,
                    'default_value': '智能手机'
                },
                {
                    'name': 'quantity',
                    'label': '购买数量',
                    'placeholder': '请输入购买数量',
                    'required': True,
                    'validator': Function(validate_quantity),
                    'default_value': '1'
                },
                {
                    'name': 'shipping_address',
                    'label': '收货地址',
                    'placeholder': '请输入详细的收货地址',
                    'required': True
                },
                {
                    'name': 'notes',
                    'label': '备注信息',
                    'placeholder': '特殊要求或备注',
                    'required': False
                }
            ]
            
            result = await show_embedded_input_dialog(
                self,
                message="请填写订单信息：",
                input_fields=input_fields,
                title="订单信息表单",
                show_preview=True,
                submit_text="下单",
                cancel_text="取消"
            )
            
            if result:
                self.user_data.update({f"订单_{k}": v for k, v in result.items()})
                self.log_message("✓ 订单提交成功", "success")
                self.log_message(f"  产品: {result.get('product', '')}", "info")
                self.log_message(f"  数量: {result.get('quantity', '')} 件", "info")
            else:
                self.log_message("✗ 用户取消订单", "warning")
        except Exception as e:
            self.log_message(f"订单表单操作失败: {e}", "error")
    
    async def show_embedded_settings_form(self) -> None:
        """显示设置表单"""
        try:
            self.log_message("显示设置表单", "info")
            
            input_fields = [
                {
                    'name': 'theme',
                    'label': '主题设置',
                    'placeholder': '输入主题名称 (dark/light)',
                    'required': True,
                    'default_value': 'dark'
                },
                {
                    'name': 'language',
                    'label': '语言设置',
                    'placeholder': '选择语言 (zh/en)',
                    'required': True,
                    'default_value': 'zh'
                },
                {
                    'name': 'auto_save',
                    'label': '自动保存',
                    'placeholder': '是否启用自动保存 (yes/no)',
                    'required': False,
                    'default_value': 'yes'
                },
                {
                    'name': 'notifications',
                    'label': '通知设置',
                    'placeholder': '通知级别 (all/important/none)',
                    'required': False,
                    'default_value': 'important'
                }
            ]
            
            result = await show_embedded_input_dialog(
                self,
                message="请配置应用设置：",
                input_fields=input_fields,
                title="应用设置",
                show_preview=True,
                submit_text="保存设置",
                cancel_text="取消"
            )
            
            if result:
                self.user_data.update({f"设置_{k}": v for k, v in result.items()})
                self.log_message("✓ 设置保存成功", "success")
            else:
                self.log_message("✗ 用户取消设置", "warning")
        except Exception as e:
            self.log_message(f"设置表单操作失败: {e}", "error")
    
    async def show_embedded_feedback_form(self) -> None:
        """显示反馈表单"""
        try:
            self.log_message("显示反馈表单", "info")
            
            def validate_rating(value: str):
                try:
                    rating = int(value)
                    if rating < 1 or rating > 5:
                        raise ValueError("评分必须在1-5之间")
                    return True
                except ValueError:
                    raise ValueError("请输入1-5之间的数字")
            
            input_fields = [
                {
                    'name': 'rating',
                    'label': '总体评分',
                    'placeholder': '请给我们的服务评分（1-5分）',
                    'required': True,
                    'validator': Function(validate_rating)
                },
                {
                    'name': 'feedback_type',
                    'label': '反馈类型',
                    'placeholder': '建议/问题/表扬/投诉',
                    'required': True,
                    'default_value': '建议'
                },
                {
                    'name': 'feedback_content',
                    'label': '反馈内容',
                    'placeholder': '请详细描述您的反馈',
                    'required': True
                },
                {
                    'name': 'contact_email',
                    'label': '联系邮箱',
                    'placeholder': '如需回复请留下邮箱',
                    'required': False
                }
            ]
            
            result = await show_embedded_input_dialog(
                self,
                message="感谢您使用我们的服务，请留下您的宝贵意见：",
                input_fields=input_fields,
                title="用户反馈",
                show_preview=True,
                submit_text="提交反馈",
                cancel_text="稍后再说"
            )
            
            if result:
                self.user_data.update({f"反馈_{k}": v for k, v in result.items()})
                self.log_message("✓ 反馈提交成功，感谢您的反馈！", "success")
                self.log_message(f"  评分: {result.get('rating', '')} 分", "info")
                self.log_message(f"  类型: {result.get('feedback_type', '')}", "info")
            else:
                self.log_message("✗ 用户跳过反馈", "warning")
        except Exception as e:
            self.log_message(f"反馈表单操作失败: {e}", "error")
    
    # ==================== WindowDialogWithInput直接使用演示方法 ====================
    
    async def show_direct_basic_demo(self) -> None:
        """显示WindowDialogWithInput的基础API调用演示"""
        try:
            self.log_message("显示WindowDialogWithInput的基础API调用演示", "info")
            
            # 直接使用WindowDialogWithInput类
            dialog = WindowDialogWithInput(
                message="这是直接使用WindowDialogWithInput类的基础演示。\n\n"
                       "演示功能：\n"
                       "• 直接实例化WindowDialogWithInput\n"
                       "• 自定义输入字段配置\n"
                       "• 基本输入验证\n"
                       "• 预览功能（Ctrl+P）\n"
                       "• 重置功能（Ctrl+R）\n\n"
                       "请尝试填写下方的基础信息：",
                input_fields=[
                    {
                        'name': 'username',
                        'label': '用户名',
                        'placeholder': '请输入用户名（至少3个字符）',
                        'required': True,
                        'validator': Function(lambda v: len(v) >= 3 or ValueError("用户名至少3个字符"))
                    },
                    {
                        'name': 'description',
                        'label': '个人简介',
                        'placeholder': '请输入个人简介（可选）',
                        'required': False
                    }
                ],
                title="基础API调用演示",
                submit_text="确认",
                cancel_text="取消",
                dialog_id="direct-basic-demo",
                show_preview=True
            )
            
            result = await self.push_screen_wait(dialog)
            
            if result:
                self.user_data.update({f"基础_{k}": v for k, v in result.items()})
                self.log_message(f"✓ 基础API调用演示完成，用户输入: {result}", "success")
            else:
                self.log_message("✗ 基础API调用演示取消", "warning")
        except Exception as e:
            self.log_message(f"基础API调用演示失败: {e}", "error")
    
    async def show_direct_validation_demo(self) -> None:
        """显示WindowDialogWithInput的高级验证演示"""
        try:
            self.log_message("显示WindowDialogWithInput的高级验证演示", "info")
            
            def validate_email(value: str):
                if "@" not in value or "." not in value:
                    raise ValueError("请输入有效的邮箱地址")
                if len(value) < 5:
                    raise ValueError("邮箱地址太短")
                return True
            
            def validate_phone(value: str):
                import re
                if not re.match(r'^1[3-9]\d{9}$', value):
                    raise ValueError("请输入有效的手机号码")
                return True
            
            # 直接使用WindowDialogWithInput类进行高级验证演示
            dialog = WindowDialogWithInput(
                message="这是WindowDialogWithInput高级验证功能演示。\n\n"
                       "请填写以下信息，每个字段都有自定义验证规则：\n\n"
                       "[dim]验证规则:[/dim]\n"
                       "[dim]• 邮箱：必须包含@和.，长度至少5个字符[/dim]\n"
                       "[dim]• 手机：必须是中国大陆手机号格式[/dim]\n"
                       "[dim]• 年龄：必须是18-120之间的整数[/dim]",
                input_fields=[
                    {
                        'name': 'email',
                        'label': '邮箱地址',
                        'placeholder': '例如: user@example.com',
                        'required': True,
                        'validator': Function(validate_email),
                        'default_value': self.user_data.get("验证邮箱", "")
                    },
                    {
                        'name': 'phone',
                        'label': '手机号码',
                        'placeholder': '例如: 13812345678',
                        'required': True,
                        'validator': Function(validate_phone)
                    },
                    {
                        'name': 'age',
                        'label': '年龄',
                        'placeholder': '请输入年龄（18-120）',
                        'required': True,
                        'validator': Function(lambda v: 18 <= int(v) <= 120 or ValueError("年龄必须在18-120之间"))
                    }
                ],
                title="高级验证演示",
                submit_text="确认",
                cancel_text="取消",
                dialog_id="direct-validation-demo",
                show_preview=True
            )
            
            result = await self.push_screen_wait(dialog)
            
            if result:
                self.user_data.update({f"验证_{k}": v for k, v in result.items()})
                self.log_message(f"✓ 高级验证演示完成，用户输入: {result}", "success")
            else:
                self.log_message("✗ 高级验证演示取消", "warning")
        except Exception as e:
            self.log_message(f"高级验证演示失败: {e}", "error")
    
    async def show_direct_dynamic_demo(self) -> None:
        """显示WindowDialogWithInput的动态字段演示"""
        try:
            self.log_message("显示WindowDialogWithInput的动态字段演示", "info")
            
            # 第一步：选择表单类型
            type_dialog = WindowDialogWithInput(
                message="这是WindowDialogWithInput动态字段功能演示。\n\n"
                       "演示功能：\n"
                       "• 根据用户选择动态生成不同的输入字段\n"
                       "• 多步骤对话框交互\n"
                       "• 条件性字段显示\n\n"
                       "请首先选择您想要的表单类型：",
                input_fields=[
                    {
                        'name': 'form_type',
                        'label': '表单类型',
                        'placeholder': '输入: personal 或 business',
                        'required': True,
                        'validator': Function(lambda v: v.lower() in ['personal', 'business'] or ValueError("请输入personal或business"))
                    }
                ],
                title="动态字段演示 - 步骤1",
                submit_text="下一步",
                cancel_text="取消",
                dialog_id="dynamic-type-demo"
            )
            
            type_result = await self.push_screen_wait(type_dialog)
            if not type_result:
                self.log_message("✗ 动态字段演示取消", "warning")
                return
            
            form_type = type_result.get('form_type', '').lower()
            self.log_message(f"✓ 用户选择表单类型: {form_type}", "info")
            
            # 第二步：根据类型显示不同字段
            if form_type == 'personal':
                input_fields = [
                    {
                        'name': 'name',
                        'label': '姓名',
                        'placeholder': '请输入您的姓名',
                        'required': True
                    },
                    {
                        'name': 'hobby',
                        'label': '爱好',
                        'placeholder': '请输入您的爱好',
                        'required': False
                    },
                    {
                        'name': 'birth_year',
                        'label': '出生年份',
                        'placeholder': '请输入出生年份（1900-2024）',
                        'required': True,
                        'validator': Function(lambda v: 1900 <= int(v) <= 2024 or ValueError("出生年份必须在1900-2024之间"))
                    }
                ]
                title = "个人信息表单"
                message = "请填写您的个人信息："
            else:  # business
                input_fields = [
                    {
                        'name': 'company',
                        'label': '公司名称',
                        'placeholder': '请输入公司名称',
                        'required': True
                    },
                    {
                        'name': 'industry',
                        'label': '行业',
                        'placeholder': '请输入所属行业',
                        'required': True
                    },
                    {
                        'name': 'employees',
                        'label': '员工数量',
                        'placeholder': '请输入员工数量',
                        'required': True,
                        'validator': Function(lambda v: int(v) > 0 or ValueError("员工数量必须大于0"))
                    }
                ]
                title = "商业信息表单"
                message = "请填写您的商业信息："
            
            # 显示动态生成的表单
            dynamic_dialog = WindowDialogWithInput(
                message=message,
                input_fields=input_fields,
                title=title,
                submit_text="确认",
                cancel_text="返回",
                dialog_id="dynamic-form-demo",
                show_preview=True
            )
            
            result = await self.push_screen_wait(dynamic_dialog)
            
            if result:
                # 保存结果
                result['form_type'] = form_type
                self.user_data.update({f"动态_{k}": v for k, v in result.items()})
                self.log_message(f"✓ 动态字段演示完成，表单类型: {form_type}，用户输入: {result}", "success")
            else:
                self.log_message("✗ 动态字段演示取消", "warning")
        except Exception as e:
            self.log_message(f"动态字段演示失败: {e}", "error")
    
    async def show_direct_callback_demo(self) -> None:
        """显示WindowDialogWithInput的回调函数演示"""
        try:
            self.log_message("显示WindowDialogWithInput的回调函数演示", "info")
            
            def submit_callback(values: dict):
                self.log_message(f"🔄 提交回调函数已执行，接收到的值: {values}", "success")
                # 可以在这里进行额外的处理，比如保存到数据库等
                
            def cancel_callback():
                self.log_message("🔄 取消回调函数已执行", "warning")
                # 可以在这里进行清理工作
            
            # 直接使用WindowDialogWithInput类并设置回调函数
            dialog = WindowDialogWithInput(
                message="这是WindowDialogWithInput回调函数功能演示。\n\n"
                       "演示功能：\n"
                       "• 提交时的回调函数（submit_callback）\n"
                       "• 取消时的回调函数（cancel_callback）\n"
                       "• 回调函数参数传递\n"
                       "• 异常处理机制\n\n"
                       "无论您选择确认还是取消，都会看到对应的回调执行日志：",
                input_fields=[
                    {
                        'name': 'test_data',
                        'label': '测试数据',
                        'placeholder': '请输入测试数据',
                        'required': True
                    },
                    {
                        'name': 'callback_demo',
                        'label': '回调演示',
                        'placeholder': '任意输入内容（可选）',
                        'required': False
                    }
                ],
                title="回调函数演示",
                submit_text="确认（触发提交回调）",
                cancel_text="取消（触发取消回调）",
                dialog_id="direct-callback-demo",
                show_preview=True,
                submit_callback=submit_callback,
                cancel_callback=cancel_callback
            )
            
            result = await self.push_screen_wait(dialog)
            
            if result:
                self.user_data.update({f"回调_{k}": v for k, v in result.items()})
                self.log_message(f"✓ 回调函数演示完成，对话框返回: {result}", "success")
            else:
                self.log_message("✗ 回调函数演示，对话框返回: None", "warning")
        except Exception as e:
            self.log_message(f"回调函数演示失败: {e}", "error")
    
    async def show_direct_wizard_demo(self) -> None:
        """显示WindowDialogWithInput的配置向导演示"""
        try:
            self.log_message("显示WindowDialogWithInput的配置向导演示", "info")
            
            def validate_port(value: str):
                try:
                    port = int(value)
                    if not (1 <= port <= 65535):
                        raise ValueError("端口号必须在1-65535之间")
                    return True
                except ValueError:
                    raise ValueError("请输入有效的端口号")
            
            def validate_memory(value: str):
                try:
                    memory = int(value)
                    if memory < 128:
                        raise ValueError("内存大小至少128MB")
                    return True
                except ValueError:
                    raise ValueError("请输入有效的内存大小")
            
            # 配置向导：服务器设置
            dialog = WindowDialogWithInput(
                message="这是WindowDialogWithInput配置向导功能演示。\n\n"
                       "模拟一个服务器配置向导，包含：\n"
                       "• 服务器基本信息配置\n"
                       "• 高级验证规则\n"
                       "• 实时预览功能\n"
                       "• 复杂表单处理\n\n"
                       "请配置您的服务器参数：",
                input_fields=[
                    {
                        'name': 'server_name',
                        'label': '服务器名称',
                        'placeholder': '例如: web-server-01',
                        'required': True,
                        'validator': Function(lambda v: len(v) >= 3 or ValueError("服务器名称至少3个字符"))
                    },
                    {
                        'name': 'port',
                        'label': '端口号',
                        'placeholder': '例如: 8080',
                        'required': True,
                        'validator': Function(validate_port),
                        'default_value': '8080'
                    },
                    {
                        'name': 'memory',
                        'label': '内存大小(MB)',
                        'placeholder': '例如: 1024',
                        'required': True,
                        'validator': Function(validate_memory),
                        'default_value': '512'
                    },
                    {
                        'name': 'env',
                        'label': '运行环境',
                        'placeholder': '输入: dev, test, prod',
                        'required': True,
                        'validator': Function(lambda v: v.lower() in ['dev', 'test', 'prod'] or ValueError("环境必须是dev、test或prod")),
                        'default_value': 'dev'
                    },
                    {
                        'name': 'description',
                        'label': '服务器描述',
                        'placeholder': '服务器用途描述（可选）',
                        'required': False
                    }
                ],
                title="服务器配置向导",
                submit_text="应用配置",
                cancel_text="取消配置",
                reset_text="重置参数",
                preview_text="预览配置",
                dialog_id="direct-wizard-demo",
                show_preview=True
            )
            
            result = await self.push_screen_wait(dialog)
            
            if result:
                self.user_data.update({f"服务器_{k}": v for k, v in result.items()})
                self.log_message(f"✓ 配置向导演示完成，服务器配置: {result}", "success")
                
                # 显示配置摘要
                summary = []
                for key, value in result.items():
                    summary.append(f"  {key}: {value}")
                self.log_message("服务器配置摘要:\n" + "\n".join(summary), "info")
            else:
                self.log_message("✗ 配置向导演示取消", "warning")
        except Exception as e:
            self.log_message(f"配置向导演示失败: {e}", "error")
    
    async def show_direct_batch_demo(self) -> None:
        """显示WindowDialogWithInput的批量操作演示"""
        try:
            self.log_message("显示WindowDialogWithInput的批量操作演示", "info")
            
            # 模拟批量用户导入功能
            def validate_csv_format(value: str):
                # 简单的CSV格式验证
                lines = value.strip().split('\n')
                if len(lines) < 1:
                    raise ValueError("至少需要一行数据")
                
                for i, line in enumerate(lines):
                    parts = line.split(',')
                    if len(parts) != 3:
                        raise ValueError(f"第{i+1}行格式错误，应为：姓名,邮箱,年龄")
                    
                    name, email, age = [p.strip() for p in parts]
                    if not name:
                        raise ValueError(f"第{i+1}行姓名不能为空")
                    if '@' not in email:
                        raise ValueError(f"第{i+1}行邮箱格式错误")
                    try:
                        age_int = int(age)
                        if not (0 <= age_int <= 120):
                            raise ValueError(f"第{i+1}行年龄必须在0-120之间")
                    except ValueError:
                        raise ValueError(f"第{i+1}行年龄必须是数字")
                
                return True
            
            # 批量操作对话框
            dialog = WindowDialogWithInput(
                message="这是WindowDialogWithInput批量操作功能演示。\n\n"
                       "模拟批量用户导入功能，包含：\n"
                       "• 复杂的多行数据验证\n"
                       "• CSV格式校验\n"
                       "• 批量数据处理\n"
                       "• 详细错误提示\n\n"
                       "请按照格式输入用户数据：",
                input_fields=[
                    {
                        'name': 'csv_data',
                        'label': 'CSV用户数据',
                        'placeholder': '格式：姓名,邮箱,年龄\n例如：\n张三,zhang@example.com,25\n李四,li@example.com,30',
                        'required': True,
                        'validator': Function(validate_csv_format)
                    },
                    {
                        'name': 'import_mode',
                        'label': '导入模式',
                        'placeholder': '输入: replace 或 append',
                        'required': True,
                        'validator': Function(lambda v: v.lower() in ['replace', 'append'] or ValueError("导入模式必须是replace或append")),
                        'default_value': 'append'
                    },
                    {
                        'name': 'notify_users',
                        'label': '通知用户',
                        'placeholder': '是否发送通知邮件: yes/no',
                        'required': False,
                        'validator': Function(lambda v: not v or v.lower() in ['yes', 'no'] or ValueError("通知选项必须是yes或no")),
                        'default_value': 'yes'
                    }
                ],
                title="批量用户导入",
                submit_text="开始导入",
                cancel_text="取消导入",
                dialog_id="direct-batch-demo",
                show_preview=True
            )
            
            result = await self.push_screen_wait(dialog)
            
            if result:
                # 处理批量数据
                csv_data = result.get('csv_data', '')
                import_mode = result.get('import_mode', '')
                notify_users = result.get('notify_users', '')
                
                # 解析CSV数据
                lines = csv_data.strip().split('\n')
                users = []
                for line in lines:
                    name, email, age = [p.strip() for p in line.split(',')]
                    users.append({'name': name, 'email': email, 'age': int(age)})
                
                # 保存结果
                self.user_data.update({
                    '批量_导入用户数': len(users),
                    '批量_导入模式': import_mode,
                    '批量_通知用户': notify_users,
                    '批量_用户列表': users
                })
                
                self.log_message(f"✓ 批量操作演示完成，成功导入{len(users)}个用户", "success")
                self.log_message(f"  导入模式: {import_mode}", "info")
                self.log_message(f"  通知用户: {notify_users}", "info")
                
                # 显示导入的用户
                for i, user in enumerate(users[:3]):  # 只显示前3个
                    self.log_message(f"  用户{i+1}: {user['name']} ({user['email']}, {user['age']}岁)", "info")
                if len(users) > 3:
                    self.log_message(f"  ... 还有{len(users)-3}个用户", "info")
            else:
                self.log_message("✗ 批量操作演示取消", "warning")
        except Exception as e:
            self.log_message(f"批量操作演示失败: {e}", "error")
    
    def action_clear_log(self) -> None:
        """清空日志"""
        self.log_messages.clear()
        self.update_status_display()
    
    async def action_show_help(self) -> None:
        """显示帮助信息"""
        await show_confirm_dialog(
            self,
            message="[bold cyan]窗口化对话框帮助[/bold cyan]\n\n"
                   "[yellow]确认对话框:[/yellow]\n"
                   "• 删除文件: 演示删除确认对话框\n"
                   "• 保存更改: 演示保存确认对话框\n"
                   "• 退出应用: 演示退出确认对话框\n"
                   "• 自定义确认: 演示完全自定义的确认对话框\n"
                   "• 回调演示: 演示回调函数功能\n"
                   "• 异步流程: 演示多步骤异步操作\n\n"
                   "[yellow]输入对话框:[/yellow]\n"
                   "• 文本输入: 基本文本输入演示\n"
                   "• 数字输入: 带数字验证的输入演示\n"
                   "• 密码输入: 密码隐藏输入演示\n"
                   "• 文件名输入: 带文件名验证的输入演示\n"
                   "• 自定义验证: 邮箱验证输入演示\n"
                   "• 用户信息: 多步骤信息收集演示\n\n"
                   "[yellow]内嵌输入对话框:[/yellow]\n"
                   "• 用户表单: 完整的用户信息表单\n"
                   "• 登录表单: 用户名密码登录表单\n"
                   "• 自定义表单: 项目信息自定义表单\n"
                   "• 订单表单: 购物订单信息表单\n"
                   "• 设置表单: 应用配置设置表单\n"
                   "• 反馈表单: 用户反馈评价表单\n\n"
                   "[yellow]WindowDialogWithInput直接使用:[/yellow]\n"
                   "• 基础API调用: 演示WindowDialogWithInput的基本API调用\n"
                   "• 高级验证: 演示带自定义验证的输入\n"
                   "• 动态字段: 演示动态添加/移除输入字段\n"
                   "• 回调演示: 演示回调函数功能\n"
                   "• 配置向导: 演示配置向导功能\n"
                   "• 批量操作: 演示批量输入多个字段\n\n"
                   "[yellow]键盘快捷键：[/yellow]\n"
                   "• Q: 退出应用\n"
                   "• C: 清空日志\n"
                   "• H: 显示此帮助\n\n"
                   "[yellow]对话框内快捷键：[/yellow]\n"
                   "• Enter/Y: 确认\n"
                   "• Escape/N: 取消",
            title="帮助信息",
            confirm_text="知道了",
            cancel_text="关闭"
        )


def main():
    """运行演示应用"""
    app = WindowDialogDemo()
    app.title = "窗口化对话框演示"
    app.sub_title = "基于 ModalScreen 的现代化对话框体验 - 确认 & 输入 & 内嵌表单"
    app.run()


if __name__ == "__main__":
    main() 