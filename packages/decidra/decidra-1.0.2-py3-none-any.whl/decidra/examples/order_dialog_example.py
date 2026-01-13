"""
订单对话框使用示例

演示如何使用PlaceOrderDialog和ModifyOrderDialog进行下单和改单操作。
包括基本用法、回调处理和与富途API的集成示例。
"""
import asyncio
import sys
import os

# 添加src路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static, DataTable

from base.order import OrderData, ModifyOrderData
from monitor.widgets.order_dialog import (
    show_place_order_dialog,
    show_modify_order_dialog,
    PlaceOrderDialog,
    ModifyOrderDialog
)
from utils.global_vars import get_logger

class OrderDialogExample(App):
    """订单对话框示例应用"""

    CSS = """
    Screen {
        layout: vertical;
        padding: 2;
    }

    .title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 2;
    }

    .button-row {
        layout: horizontal;
        height: auto;
        align: center middle;
        margin-bottom: 2;
    }

    .button-row Button {
        margin: 0 2;
        min-width: 20;
    }

    .result-area {
        background: $surface;
        border: solid $primary;
        padding: 1;
        margin-top: 2;
        height: auto;
        min-height: 10;
    }

    .result-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .result-content {
        color: $text;
    }

    DataTable {
        margin-top: 1;
        height: auto;
    }
    """

    def __init__(self):
        super().__init__()
        self.orders_data = []  # 存储订单数据
        self.order_counter = 1  # 订单计数器
        self.logger = get_logger("OrderDialogExample")

    def compose(self) -> ComposeResult:
        """构建应用界面"""
        yield Static("富途订单对话框演示", classes="title")

        with Horizontal(classes="button-row"):
            yield Button("下单对话框", id="place-order-btn", variant="success")
            yield Button("改单对话框", id="modify-order-btn", variant="warning")
            yield Button("预填写下单", id="prefilled-order-btn", variant="primary")
            yield Button("清空结果", id="clear-btn", variant="error")

        with Vertical(classes="result-area"):
            yield Static("操作结果", classes="result-title")
            yield Static("点击上方按钮开始操作...", classes="result-content", id="result-text")

            # 订单表格
            table = DataTable(id="orders-table")
            table.add_columns("订单ID", "股票代码", "方向", "数量", "价格", "类型", "状态")
            yield table

    @on(Button.Pressed, "#place-order-btn")
    async def on_place_order_clicked(self, event: Button.Pressed) -> None:
        """处理下单按钮点击"""
        event.stop()

        def submit_callback(order_data: OrderData):
            """下单成功回调"""
            self.query_one("#result-text", Static).update(
                f"✅ 下单成功！\n"
                f"股票代码: {order_data.code}\n"
                f"价格: {order_data.price}\n"
                f"数量: {order_data.qty}\n"
                f"方向: {'买入' if order_data.trd_side == 'BUY' else '卖出'}\n"
                f"订单类型: {order_data.order_type}\n"
                f"交易环境: {order_data.trd_env}"
            )

        def cancel_callback():
            """取消回调"""
            self.query_one("#result-text", Static).update("❌ 用户取消了下单操作")

        try:
            # 显示下单对话框
            order_data = await show_place_order_dialog(
                self,
                title="下单 - 富途证券",
                submit_callback=submit_callback,
                cancel_callback=cancel_callback,
                dialog_id="place_order_1"
            )

            self.logger.info(f"DEBUG: 对话框返回的数据: {order_data}")

            if order_data:
                # 生成临时本地ID
                temp_order_id = f"ORD{self.order_counter:06d}"
                self.order_counter += 1

                # 先添加到订单表格（使用临时ID）
                table = self.query_one("#orders-table", DataTable)
                table.add_row(
                    temp_order_id,
                    order_data.code,
                    "买入" if order_data.trd_side == "BUY" else "卖出",
                    str(order_data.qty),
                    f"{order_data.price:.3f}",
                    order_data.order_type,
                    "提交中..."
                )

                # 模拟与富途API集成的示例，获取真实订单ID
                real_order_id = await self._simulate_futu_api_call(order_data, temp_order_id)

                # 使用真实的API返回ID存储到orders_data
                self.orders_data.append({
                    "temp_id": temp_order_id,
                    "id": real_order_id,
                    "data": order_data
                })

                # 更新表格中的订单ID和状态
                self._update_order_in_table(temp_order_id, real_order_id, "已确认")

                # 添加调试信息
                self.logger.info(f"DEBUG: 订单已添加 - 临时ID: {temp_order_id}, 真实ID: {real_order_id}, 总订单数: {len(self.orders_data)}")
            else:
                self.logger.info("DEBUG: 对话框返回了 None，可能是用户取消了或者验证失败")
                self.query_one("#result-text", Static).update("❌ 下单失败：用户取消了操作或输入验证失败")

        except Exception as e:
            self.query_one("#result-text", Static).update(f"❌ 错误: {str(e)}")

    @on(Button.Pressed, "#modify-order-btn")
    async def on_modify_order_clicked(self, event: Button.Pressed) -> None:
        """处理改单按钮点击"""
        event.stop()

        # 添加调试信息
        debug_info = f"当前订单数量: {len(self.orders_data)}"
        if self.orders_data:
            debug_info += f"\n最新订单真实ID: {self.orders_data[-1]['id']}"

        if not self.orders_data:
            self.query_one("#result-text", Static).update(f"❌ 没有可修改的订单，请先下单\n{debug_info}")
            return

        # 获取最后一个订单，使用真实的API返回ID
        last_order = self.orders_data[-1]
        real_order_id = last_order["id"]  # 使用真实的API订单ID
        order_data = last_order["data"]

        def submit_callback(modify_data: ModifyOrderData):
            """改单成功回调"""
            self.query_one("#result-text", Static).update(
                f"✅ 改单成功！\n"
                f"订单ID: {modify_data.order_id}\n"
                f"新价格: {modify_data.price if modify_data.price else '未修改'}\n"
                f"新数量: {modify_data.qty if modify_data.qty else '未修改'}\n"
                f"辅助价格: {modify_data.aux_price if modify_data.aux_price else '未设置'}"
            )

        def cancel_callback():
            """取消回调"""
            self.query_one("#result-text", Static).update("❌ 用户取消了改单操作")

        try:
            # 显示改单对话框，使用真实的API订单ID
            modify_data = await show_modify_order_dialog(
                self,
                title="修改订单 - 富途证券",
                order_id=real_order_id,  # 使用真实的API订单ID
                current_price=order_data.price,
                current_qty=order_data.qty,
                submit_callback=submit_callback,
                cancel_callback=cancel_callback,
                dialog_id="modify_order_1"
            )

            if modify_data:
                # 模拟与富途API集成的改单示例
                await self._simulate_futu_modify_call(modify_data)

        except Exception as e:
            self.query_one("#result-text", Static).update(f"❌ 错误: {str(e)}")

    @on(Button.Pressed, "#prefilled-order-btn")
    async def on_prefilled_order_clicked(self, event: Button.Pressed) -> None:
        """处理预填写下单按钮点击"""
        event.stop()

        # 预设的默认值
        default_values = {
            "code": "HK.00700",
            "price": 100.50,
            "qty": 500,
            "order_type": "NORMAL",
            "trd_side": "BUY",
            "trd_env": "SIMULATE",
            "market": "HK",
            "time_in_force": "DAY",
            "remark": "预设订单示例"
        }

        def submit_callback(order_data: OrderData):
            """预填写下单成功回调"""
            self.query_one("#result-text", Static).update(
                f"✅ 预填写下单成功！\n"
                f"使用了预设的腾讯控股(00700)数据\n"
                f"股票代码: {order_data.code}\n"
                f"价格: {order_data.price}\n"
                f"数量: {order_data.qty}\n"
                f"备注: {order_data.remark}"
            )

        try:
            order_data = await show_place_order_dialog(
                self,
                title="预填写下单 - 腾讯控股",
                default_values=default_values,
                submit_callback=submit_callback,
                dialog_id="prefilled_order"
            )

            if order_data:
                # 生成临时本地ID
                temp_order_id = f"ORD{self.order_counter:06d}"
                self.order_counter += 1

                # 先添加到订单表格（使用临时ID）
                table = self.query_one("#orders-table", DataTable)
                table.add_row(
                    temp_order_id,
                    order_data.code,
                    "买入" if order_data.trd_side == "BUY" else "卖出",
                    str(order_data.qty),
                    f"{order_data.price:.3f}",
                    order_data.order_type,
                    "提交中..."
                )

                # 模拟与富途API集成的示例，获取真实订单ID
                real_order_id = await self._simulate_futu_api_call(order_data, temp_order_id)

                # 使用真实的API返回ID存储到orders_data
                self.orders_data.append({
                    "temp_id": temp_order_id,
                    "id": real_order_id,
                    "data": order_data
                })

                # 更新表格中的订单ID和状态
                self._update_order_in_table(temp_order_id, real_order_id, "已确认")

        except Exception as e:
            self.query_one("#result-text", Static).update(f"❌ 错误: {str(e)}")

    @on(Button.Pressed, "#clear-btn")
    def on_clear_clicked(self, event: Button.Pressed) -> None:
        """清空结果"""
        event.stop()
        self.query_one("#result-text", Static).update("结果已清空")

        # 清空表格
        table = self.query_one("#orders-table", DataTable)
        table.clear()
        table.add_columns("订单ID", "股票代码", "方向", "数量", "价格", "类型", "状态")

        # 清空订单数据
        self.orders_data.clear()
        self.order_counter = 1

    async def _simulate_futu_api_call(self, order_data: OrderData, temp_order_id: str) -> str:
        """模拟富途API调用，返回真实的订单ID"""
        try:
            # 这里演示如何与富途API集成
            # 实际使用时需要导入并使用真实的富途客户端

            # from api.futu_trade import TradeManager
            # trade_manager = TradeManager(futu_client)
            #
            # result = trade_manager.place_order(
            #     code=order_data.code,
            #     price=order_data.price,
            #     qty=order_data.qty,
            #     order_type=order_data.order_type,
            #     trd_side=order_data.trd_side,
            #     aux_price=order_data.aux_price,
            #     trd_env=order_data.trd_env,
            #     market=order_data.market
            # )

            # 模拟API调用延迟
            await asyncio.sleep(0.5)

            # 模拟富途API返回的真实订单ID
            import random
            real_order_id = f"FT{random.randint(100000000, 999999999)}"

            result_text = self.query_one("#result-text", Static)
            current_text = result_text.renderable
            result_text.update(f"{current_text}\n\n📡 模拟API调用完成\n🔗 临时ID: {temp_order_id} → 真实ID: {real_order_id}")

            return real_order_id

        except Exception as e:
            result_text = self.query_one("#result-text", Static)
            current_text = result_text.renderable
            result_text.update(f"{current_text}\n\n❌ API调用失败: {str(e)}")
            # 如果API调用失败，返回临时ID作为fallback
            return temp_order_id

    def _update_order_in_table(self, temp_order_id: str, real_order_id: str, status: str):
        """更新表格中的订单ID和状态"""
        try:
            table = self.query_one("#orders-table", DataTable)
            # 遍历表格行，找到匹配的临时ID并更新
            for row_key in table.rows:
                row_data = table.get_row(row_key)
                if row_data[0] == temp_order_id:  # 第0列是订单ID
                    # 更新这一行的数据
                    table.update_cell(row_key, "订单ID", real_order_id)
                    table.update_cell(row_key, "状态", status)
                    self.logger.info(f"表格更新成功: {temp_order_id} → {real_order_id}, 状态: {status}")
                    break
            else:
                self.logger.warning(f"未找到临时ID为 {temp_order_id} 的订单行")
        except Exception as e:
            self.logger.error(f"更新表格失败: {e}")

    async def _simulate_futu_modify_call(self, modify_data: ModifyOrderData):
        """模拟富途改单API调用"""
        try:
            # 这里演示如何与富途改单API集成
            # 实际使用时需要导入并使用真实的富途客户端

            # from api.futu_trade import TradeManager
            # trade_manager = TradeManager(futu_client)
            #
            # result = trade_manager.modify_order(
            #     order_id=modify_data.order_id,
            #     price=modify_data.price,
            #     qty=modify_data.qty,
            #     trd_env="SIMULATE",
            #     market="HK"
            # )

            # 模拟API调用延迟
            await asyncio.sleep(0.5)

            result_text = self.query_one("#result-text", Static)
            current_text = result_text.renderable
            result_text.update(f"{current_text}\n\n📡 模拟改单API调用完成")

        except Exception as e:
            result_text = self.query_one("#result-text", Static)
            current_text = result_text.renderable
            result_text.update(f"{current_text}\n\n❌ 改单API调用失败: {str(e)}")


class SimpleOrderDialogExample(App):
    """简单订单对话框示例"""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("SimpleOrderDialogExample")

    def compose(self) -> ComposeResult:
        yield Static("简单订单对话框示例", classes="title")
        yield Button("显示下单对话框", id="simple-place-btn")

    @on(Button.Pressed, "#simple-place-btn")
    async def show_simple_dialog(self, event: Button.Pressed) -> None:
        """显示简单的下单对话框"""
        event.stop()

        # 最简单的用法
        order_data = await show_place_order_dialog(self)

        if order_data:
            self.logger.info(f"下单成功: {order_data.code} {order_data.trd_side} {order_data.qty}@{order_data.price}")
        else:
            self.logger.info("用户取消了下单")


async def demo_programmatic_usage():
    """演示编程方式使用对话框"""
    demo_logger = get_logger("demo_programmatic_usage")
    demo_logger.info("=== 编程方式使用订单对话框演示 ===")

    # 创建一个简单的测试应用
    app = SimpleOrderDialogExample()

    # 这里演示如何在代码中直接创建和使用对话框
    # 注意：实际应用中需要在Textual应用上下文中运行

    try:
        # 创建订单数据
        sample_order = OrderData(
            code="HK.00700",
            price=100.50,
            qty=500,
            order_type="NORMAL",
            trd_side="BUY"
        )
        demo_logger.info(f"示例订单数据: {sample_order}")

        # 创建改单数据
        sample_modify = ModifyOrderData(
            order_id="ORD123456",
            price=105.00,
            qty=600
        )
        demo_logger.info(f"示例改单数据: {sample_modify}")

    except Exception as e:
        demo_logger.info(f"演示过程中出现错误: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="订单对话框示例")
    parser.add_argument(
        "--mode",
        choices=["full", "simple", "demo"],
        default="full",
        help="运行模式: full=完整演示, simple=简单示例, demo=编程演示"
    )

    args = parser.parse_args()

    if args.mode == "full":
        print("启动完整订单对话框演示...")
        app = OrderDialogExample()
        app.run()
    elif args.mode == "simple":
        print("启动简单订单对话框示例...")
        app = SimpleOrderDialogExample()
        app.run()
    elif args.mode == "demo":
        print("运行编程演示...")
        asyncio.run(demo_programmatic_usage())


if __name__ == "__main__":
    main()