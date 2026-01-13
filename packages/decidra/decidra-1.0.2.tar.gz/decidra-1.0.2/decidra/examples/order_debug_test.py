#!/usr/bin/env python3
"""
订单对话框调试测试脚本
用于复现和验证"没有对应订单"问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from base.order import OrderData
from utils.global_vars import get_logger
def simulate_order_operations():
    """模拟订单操作流程"""

    # 模拟应用状态
    orders_data = []
    order_counter = 1
    test_logger = get_logger("OrderDebugTest")

    def simulate_prefilled_order_success():
        """模拟预填写下单成功"""
        nonlocal order_counter
        test_logger.info("=== 模拟预填写下单成功流程 ===")

        # 模拟对话框返回订单数据
        order_data = OrderData(
            code="HK.00700",
            price=100.50,
            qty=500,
            order_type="NORMAL",
            trd_side="BUY",
            trd_env="SIMULATE",
            market="HK",
            time_in_force="DAY",
            remark="预设订单示例"
        )

        if order_data:
            # 添加到订单表格
            order_id = f"ORD{order_counter:06d}"
            order_counter += 1

            orders_data.append({
                "id": order_id,
                "data": order_data
            })

            test_logger.info(f"✅ 订单已添加 - ID: {order_id}, 总订单数: {len(orders_data)}")
            return True
        else:
            test_logger.info("❌ 预填写下单失败：用户取消了操作或输入验证失败")
            return False

    def simulate_prefilled_order_cancel():
        """模拟预填写下单被取消"""
        test_logger.info("=== 模拟预填写下单取消流程 ===")

        # 模拟对话框返回None（用户取消）
        order_data = None

        if order_data:
            # 这个分支不会执行
            pass
        else:
            test_logger.info("❌ 预填写下单失败：用户取消了操作或输入验证失败")
            return False

    def simulate_modify_order():
        """模拟改单操作"""
        test_logger.info("=== 模拟改单操作流程 ===")

        debug_info = f"当前订单数量: {len(orders_data)}"
        if orders_data:
            debug_info += f"\n最新订单ID: {orders_data[-1]['id']}"

        test_logger.info(debug_info)

        if not orders_data:
            test_logger.error(f"❌ 没有可修改的订单，请先下单\n{debug_info}")
            return False

        # 获取最后一个订单
        last_order = orders_data[-1]
        order_id = last_order["id"]
        order_data = last_order["data"]

        test_logger.info(f"✅ 找到可修改的订单 - ID: {order_id}")
        return True

    # 测试场景1：预填写下单成功 -> 改单
    test_logger.info("📊 测试场景1：预填写下单成功 -> 改单")
    success = simulate_prefilled_order_success()
    if success:
        simulate_modify_order()

    # 清空数据，测试场景2
    orders_data.clear()
    order_counter = 1

    # 测试场景2：预填写下单取消 -> 改单
    test_logger.info("\n📊 测试场景2：预填写下单取消 -> 改单")
    success = simulate_prefilled_order_cancel()
    if not success:
        simulate_modify_order()  # 这会触发"没有对应订单"错误

    return orders_data

def analyze_code_logic():
    """分析代码逻辑中的问题"""
    test_logger = get_logger("CodeAnalysis")

    test_logger.info("=== 代码逻辑分析 ===")

    # 分析预填写下单的代码逻辑
    test_logger.info("📝 预填写下单逻辑分析：")
    test_logger.info("1. 用户点击'预填写下单'按钮")
    test_logger.info("2. 调用 show_place_order_dialog() 显示对话框")
    test_logger.info("3. 等待用户操作（填写信息或取消）")
    test_logger.info("4. 如果用户取消，order_data = None")
    test_logger.info("5. 检查 if order_data: -> False，不会添加到 orders_data")
    test_logger.info("6. 显示错误信息并结束")

    test_logger.info("\n📝 改单逻辑分析：")
    test_logger.info("1. 用户点击'改单对话框'按钮")
    test_logger.info("2. 检查 if not self.orders_data:")
    test_logger.info("3. 如果没有订单，显示'❌ 没有可修改的订单，请先下单'")
    test_logger.info("4. 这就是用户看到的错误信息")

    test_logger.info("\n🔍 问题根源：")
    test_logger.info("- 用户在预填写下单对话框中点击了'取消'按钮")
    test_logger.info("- 或者输入验证失败导致对话框返回 None")
    test_logger.info("- 没有订单被添加到 orders_data 列表")
    test_logger.info("- 然后用户点击改单按钮，发现没有订单可以修改")

    test_logger.info("\n💡 解决方案：")
    test_logger.info("1. 在错误信息中提供更详细的说明")
    test_logger.info("2. 添加更好的用户指导信息")
    test_logger.info("3. 在界面上显示当前订单状态")
    test_logger.info("4. 改善对话框的用户体验，减少取消操作")

if __name__ == "__main__":
    print("🔍 开始订单对话框问题调试...")

    # 模拟订单操作
    final_orders = simulate_order_operations()

    # 分析代码逻辑
    analyze_code_logic()

    print(f"\n📊 最终订单数量: {len(final_orders)}")
    print("🔍 调试测试完成！")