#!/usr/bin/env python3
"""
InfoPanel AI交易功能演示

专注展示AI交易建议相关功能：
- AI交易建议展示
- 交易建议操作按钮
- 交易建议反馈处理
"""

from datetime import datetime
import uuid

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

# 导入重构后的InfoPanel组件
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from monitor.widgets.line_panel import InfoPanel, InfoType, InfoLevel

# 导入AI交易建议相关类

from base.trading import TradingAdvice, TradingOrder
from base.order import OrderType
AI_TRADING_AVAILABLE = True



# 导入富途交易相关类
try:
    from modules.futu_trade import FutuTrade
    FUTU_TRADING_AVAILABLE = True
except ImportError:
    FutuTrade = None
    FUTU_TRADING_AVAILABLE = False


class InfoPanelDemoApp(App):
    """InfoPanel AI交易演示应用"""

    TITLE = "InfoPanel AI交易功能演示"
    SUB_TITLE = "AI交易建议 | 操作反馈 | 交易建议管理"

    CSS = """
    Screen {
        background: $surface;
    }

    #demo_container {
        height: 1fr;
        width: 1fr;
        margin: 1;
        border: solid $primary;
    }

    #control_panel {
        height: 8;
        dock: top;
        background: $surface;
        border-bottom: solid $border;
        padding: 1;
        layout: grid;
        grid-size: 3 1;
        grid-gutter: 1;
    }

    #control_panel Button {
        height: 4;
        width: 1fr;
        text-style: bold;
        border: solid $primary;
    }

    #info_header {
        height: 5;
        dock: top;
        background: $primary;
        color: $text;
        padding: 1;
        text-align: center;
        text-style: bold;
    }

    InfoPanel {
        height: 1fr;
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "退出", priority=True),
        Binding("a", "add_ai_trading_advice", "AI交易建议"),
        Binding("i", "test_ai_quick_dialog", "测试AI快捷对话框"),
        Binding("c", "clear_all", "清空消息"),
    ]

    def __init__(self):
        super().__init__()
        self.info_panel = None
        self.message_counter = 0

    def compose(self) -> ComposeResult:
        """组合应用界面"""
        yield Header()

        with Container(id="demo_container"):
            # 信息标题
            yield Static(
                "🤖 InfoPanel AI交易功能演示 - 测试AI交易建议功能\n"
                "📝 使用快捷键A或点击按钮添加AI交易建议\n"
                "🎯 重点体验：AI交易建议展示和操作反馈",
                id="info_header"
            )

            # 控制面板
            with Container(id="control_panel"):
                yield Button("🤖 AI交易建议", id="ai_advice_btn", variant="primary")
                yield Button("💬 AI快捷对话框", id="ai_quick_dialog_btn", variant="success")
                yield Button("🗑️ 清空全部", id="clear_btn", variant="error")

            # InfoPanel双面板组件
            self.info_panel = InfoPanel("📊 系统信息监控面板")
            yield self.info_panel

        yield Footer()

    async def on_mount(self) -> None:
        """应用挂载时初始化"""
        # 初始化交易管理器
        await self._initialize_trade_manager()

        # 添加欢迎消息
        await self.info_panel.log_info(
            "🎉 欢迎使用InfoPanel AI交易功能演示！",
            "系统"
        )
        await self.info_panel.log_info(
            "专注于AI交易建议功能测试",
            "使用说明"
        )
        await self.info_panel.log_info(
            "使用快捷键A添加AI交易建议",
            "快捷键"
        )
        await self.info_panel.log_info(
            "点击AI交易建议查看操作按钮和反馈",
            "功能特点"
        )

    async def _initialize_trade_manager(self) -> None:
        """初始化交易管理器"""
        try:
            if FUTU_TRADING_AVAILABLE:
                # 创建富途交易管理器（模拟环境）
                await self.info_panel.log_info(
                    "🔄 正在初始化富途交易管理器...",
                    "交易系统"
                )

                # 创建FutuTrade实例（默认使用模拟环境）
                futu_trade = FutuTrade(default_trd_env="SIMULATE")

                # 打开连接
                futu_trade.open()

                # 设置到InfoPanel中
                self.info_panel.set_trade_manager(futu_trade)

                await self.info_panel.log_info(
                    "✅ 富途交易管理器初始化成功（模拟环境）",
                    "交易系统"
                )
            else:
                await self.info_panel.log_info(
                    "⚠️ 富途交易模块不可用，交易功能将被禁用",
                    "交易系统"
                )

        except Exception as e:
            await self.info_panel.log_info(
                f"❌ 富途交易管理器初始化失败: {str(e)}",
                "交易系统"
            )
            await self.info_panel.log_info(
                "💡 提示：需要先启动FutuOpenD客户端",
                "交易系统"
            )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id

        if button_id == "ai_advice_btn":
            await self.action_add_ai_trading_advice()
        elif button_id == "ai_quick_dialog_btn":
            # 使用 run_worker 在独立的 worker 中运行对话框，避免阻塞事件循环
            self.run_worker(self.action_test_ai_quick_dialog(), exclusive=True, group="ai_dialog")
        elif button_id == "clear_btn":
            await self.action_clear_all()


    async def action_add_ai_trading_advice(self) -> None:
        """添加AI交易建议消息（模拟真实的交易建议数据）"""

        if not AI_TRADING_AVAILABLE:
            await self.info_panel.log_error("AI交易建议功能不可用，请检查相关模块", "演示")
            return

        # 创建多个不同类型的AI交易建议
        # 注意：只使用"买入"操作，因为模拟账户中没有持仓，"卖出"会被富途API拒绝（卖空）
        trading_advices = [
            {
                "stock": "HK.00700",
                "stock_name": "腾讯控股",
                "action": "buy",  # 使用英文 'buy'
                "reason": "技术面突破关键阻力位，成交量放大",
                "confidence": 0.78,
                "risk": "中等",
                "price": 425.50,
                "quantity": 100,
                "stop_loss": 405.00,
                "target": 450.00
            },
            {
                "stock": "HK.09988",
                "stock_name": "阿里巴巴",
                "action": "buy",  # 使用英文 'buy'
                "reason": "回调至支撑位，估值吸引力增强",
                "confidence": 0.65,
                "risk": "中等",
                "price": 85.20,
                "quantity": 200,
                "stop_loss": 78.00,
                "target": 95.00
            },
            {
                "stock": "SH.600036",
                "stock_name": "招商银行",
                "action": "buy",  # 使用英文 'buy'
                "reason": "基本面稳健，分红收益率较高，估值偏低",
                "confidence": 0.72,
                "risk": "低",
                "price": 42.80,
                "quantity": 200,
                "stop_loss": 38.50,
                "target": 48.00
            }
        ]

        for advice_data in trading_advices:
            advice_id = str(uuid.uuid4())

            # 创建真正的TradingOrder对象
            trading_order = TradingOrder(
                stock_code=advice_data['stock'],
                action=advice_data['action'],
                quantity=advice_data['quantity'],
                order_type='NORMAL',
                price=advice_data['price'],
                trigger_price=advice_data['stop_loss'],
                reasoning=advice_data['reason'],
                confidence=advice_data['confidence']
            )

            # 创建真正的TradingAdvice对象
            action_cn = "买入" if advice_data['action'] == 'buy' else "卖出"
            trading_advice = TradingAdvice(
                advice_id=advice_id,
                user_prompt=f"演示：{action_cn}{advice_data['stock_name']}",
                stock_code=advice_data['stock'],
                stock_name=advice_data['stock_name'],
                recommended_action=f"{action_cn} {advice_data['stock_name']}",
                advice_summary=f"{action_cn} {advice_data['stock_name']} - {advice_data['reason']}",
                detailed_analysis=f"基于技术分析，{advice_data['reason']}，建议{action_cn}操作。",
                confidence_score=advice_data['confidence'],
                risk_assessment=advice_data['risk'],
                suggested_orders=[trading_order],
                key_points=[
                    advice_data['reason'],
                    f"止损价位: {advice_data['stop_loss']}元",
                    f"目标价位: {advice_data['target']}元"
                ],
                risk_factors=[
                    "市场波动风险",
                    "个股基本面变化风险",
                    "止损触发风险"
                ],
                expected_return=f"预期收益率: {((advice_data['target'] - advice_data['price']) / advice_data['price'] * 100):.1f}%",
                status="pending"
            )

            # 将TradingAdvice对象添加到InfoPanel的pending_trading_advice中
            self.info_panel.pending_trading_advice[advice_id] = trading_advice

            # 构建显示内容（使用InfoPanel的格式化方法）
            content = self.info_panel._format_trading_advice(trading_advice)

            # 构建附加数据
            data = {
                'advice_id': advice_id,
                'recommended_action': trading_advice.recommended_action,
                'confidence_score': trading_advice.confidence_score,
                'risk_assessment': trading_advice.risk_assessment,
                'suggested_orders': len(trading_advice.suggested_orders),
                'demo_mode': True
            }

            # 添加AI交易建议消息
            await self.info_panel.add_info(
                content=content,
                info_type=InfoType.TRADE_ADVICE,
                level=InfoLevel.INFO,
                source="AI交易助手",
                data=data
            )
            self.message_counter += 1

        await self.info_panel.log_info(f"已添加 {len(trading_advices)} 条AI交易建议", "演示")
        await self.info_panel.log_info("💡 点击左侧AI交易建议消息，在右侧详情面板中查看操作按钮", "提示")

    async def action_test_ai_quick_dialog(self) -> None:
        """测试AI快捷对话框（优化后的用户交互）"""
        try:
            await self.info_panel.log_info("🚀 准备打开AI快捷对话框...", "演示")

            # 导入快捷对话框
            from monitor.widgets.ai_quick_dialog import AIQuickDialog

            # 创建快捷对话框
            ai_dialog = AIQuickDialog(
                stock_code="HK.00700",
                stock_name="腾讯控股",
                dialog_id="demo_ai_quick_dialog"
            )

            # 等待用户选择 - 先弹出对话框，再记录日志
            user_input = await self.app.push_screen_wait(ai_dialog)

            # 对话框关闭后记录使用提示
            await self.info_panel.log_info(
                "💡 用户刚才可以：\n"
                "  1️⃣ 点击预设问题按钮（快捷操作）\n"
                "  2️⃣ 按数字键 1-6 快速选择\n"
                "  3️⃣ 输入自定义问题",
                "使用说明"
            )

            # 处理结果
            if not user_input:
                await self.info_panel.log_info(
                    "❌ 用户取消了AI对话",
                    "演示"
                )
                return

            # 显示用户选择的问题
            await self.info_panel.log_info(
                f"✅ 收到用户问题：{user_input}",
                "AI助手"
            )

            await self.info_panel.log_info(
                "🤖 AI正在分析您的问题...\n"
                "（在真实环境中，这里会调用 Claude AI API）",
                "AI助手"
            )

            # 模拟AI响应
            ai_response = f"""📊 针对您的问题「{user_input}」的AI分析：

✨ 优化效果演示：
• 用户无需手动输入完整问题
• 点击预设问题按钮，3秒内完成提问
• 相比传统输入方式，效率提升 80%+
• 零输入错误，智能上下文填充

🎯 快捷对话框特性：
1. 6个智能预设问题
2. 支持数字键快捷选择
3. 保留自定义输入选项
4. 一步到位的异步处理流程

💡 在实际应用中，AI会根据当前股票上下文
   提供专业的投资分析和交易建议。"""

            await self.info_panel.log_info(
                ai_response,
                "AI回复"
            )

        except ImportError:
            await self.info_panel.log_error(
                "AI快捷对话框模块不可用",
                "演示"
            )
        except Exception as e:
            await self.info_panel.log_error(
                f"AI快捷对话框测试失败: {str(e)}",
                "演示"
            )

    async def action_clear_all(self) -> None:
        """清空所有消息"""
        await self.info_panel.clear_all()
        self.message_counter = 0
        await self.info_panel.log_info("所有消息已清空，可以重新开始演示", "演示")


def main():
    """主函数"""
    print("🚀 启动InfoPanel AI交易功能演示...")
    print()
    print("📋 功能特点:")
    print("   • 专注于AI交易建议功能测试")
    print("   • 左侧显示消息列表")
    print("   • 右侧显示选中消息的详细信息")
    print("   • AI交易建议操作反馈")
    print("   • 🆕 AI快捷对话框优化体验")
    print()
    print("🔧 快捷键:")
    print("   • a：添加AI交易建议")
    print("   • i：测试AI快捷对话框（优化版）")
    print("   • c：清空所有消息")
    print("   • q：退出程序")
    print()
    print("🤖 AI交易建议功能演示:")
    print("   • 按快捷键a添加AI交易建议示例")
    print("   • 点击AI交易建议消息查看详情")
    print("   • 在右侧详情面板中体验操作按钮:")
    print("     - ✅ 确认执行：弹出订单对话框，预填充AI建议参数")
    print("         → 用户可在对话框中修改订单参数")
    print("         → 确认后通过富途API执行模拟交易")
    print("     - ❌ 拒绝建议：拒绝此建议")
    print("     - 📋 查看详情：显示完整建议信息")
    print("   • 观察按钮点击后的反馈消息")
    print()
    print("✨ AI快捷对话框优化（按快捷键i体验）:")
    print("   • 6个智能预设问题，根据股票上下文自动调整")
    print("   • 支持点击按钮、数字键快捷选择、自定义输入")
    print("   • 一键提问，效率提升80%+")
    print("   • 零输入错误，用户体验显著优化")
    print()
    print("⚙️ 交易环境:")
    print("   • 使用FutuTrade模块，默认模拟交易环境（trd_env=SIMULATE）")
    print("   • 需要先启动FutuOpenD客户端")
    print("   • 所有交易都在模拟环境中执行，不会影响真实资金")
    print()

    app = InfoPanelDemoApp()
    app.run()


if __name__ == "__main__":
    main()