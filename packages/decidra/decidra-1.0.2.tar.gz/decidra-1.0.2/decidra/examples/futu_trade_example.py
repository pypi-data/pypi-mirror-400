#!/usr/bin/env python3
"""
富途交易模块使用示例

演示如何使用FutuTrade类进行股票交易操作
"""

import sys
import os
from typing import Dict, Any

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.futu_trade import FutuTrade


def demo_basic_trading():
    """演示基本交易功能"""
    print("=== 富途交易模块基本功能演示 ===\n")
    
    try:
        # 初始化交易客户端（模拟环境）
        trader = FutuTrade(
            default_trd_env="SIMULATE",
            default_market="HK", 
            default_currency="HKD"
        )
        
        print("1. 获取交易状态")
        status = trader.get_trading_status()
        print(f"   交易状态: {status}")
        print()
        
        print("2. 解锁交易功能")
        # 注意：这里需要有效的交易密码
        unlock_result = trader.unlock_trading("your_password_here")
        print(f"   解锁结果: {unlock_result}")
        print()
        
        print("3. 获取账户信息")
        account_info = trader.get_account_info()
        print(f"   账户信息: {account_info}")
        print()
        
        print("4. 获取资金信息")
        funds_info = trader.get_funds_info()
        print(f"   资金信息: {funds_info}")
        print()
        
        print("5. 获取持仓列表")
        positions = trader.get_position_list()
        print(f"   持仓数量: {len(positions)}")
        if positions:
            for pos in positions[:3]:  # 显示前3个持仓
                print(f"   - {pos.get('code', 'N/A')}: {pos.get('qty', 0)}股")
        print()
        
        print("6. 风险控制配置")
        risk_config = trader.get_risk_config()
        print(f"   当前风险配置: {risk_config}")
        
        # 修改风险配置
        new_risk_config = {
            "max_single_order_amount": 50000,
            "max_position_ratio": 0.2,
            "enable_risk_control": True
        }
        trader.set_risk_config(new_risk_config)
        print(f"   更新后风险配置: {trader.get_risk_config()}")
        print()
        
    except Exception as e:
        print(f"基本功能演示出错: {e}")


def demo_order_operations():
    """演示订单操作"""
    print("=== 订单操作演示 ===\n")
    
    try:
        trader = FutuTrade()
        
        print("1. 获取最大买入数量")
        max_buy = trader.get_max_buy_qty("HK.00700", 500.0)
        print(f"   HK.00700 在价格500的最大买入数量: {max_buy}")
        print()
        
        print("2. 获取订单费用预估")
        fee_info = trader.get_order_fee("HK.00700", 500.0, 100)
        print(f"   订单费用预估: {fee_info}")
        print()
        
        print("3. 下单操作（演示）")
        # 注意：这是演示代码，实际使用时需要有效的交易环境
        order_result = trader.place_order(
            code="HK.00700",
            price=500.0,
            qty=100,
            order_type="NORMAL",
            trd_side="BUY",
            enable_risk_check=True
        )
        print(f"   下单结果: {order_result}")
        print()
        
        print("4. 获取订单列表")
        orders = trader.get_order_list()
        print(f"   当前订单数量: {len(orders)}")
        print()
        
        print("5. 获取成交列表")
        deals = trader.get_deal_list()
        print(f"   成交记录数量: {len(deals)}")
        print()
        
    except Exception as e:
        print(f"订单操作演示出错: {e}")


def demo_advanced_features():
    """演示高级功能"""
    print("=== 高级功能演示 ===\n")
    
    try:
        trader = FutuTrade()
        
        print("1. 市价买入（按金额）")
        market_buy_result = trader.market_buy("HK.00700", 10000)  # 买入1万港币的腾讯
        print(f"   市价买入结果: {market_buy_result}")
        print()
        
        print("2. 市价卖出（全部持仓）")
        market_sell_result = trader.market_sell("HK.00700")  # 卖出所有腾讯持仓
        print(f"   市价卖出结果: {market_sell_result}")
        print()
        
        print("3. 批量下单")
        batch_orders = [
            {
                "code": "HK.00700",
                "price": 500.0,
                "qty": 100,
                "trd_side": "BUY",
                "enable_risk_check": False
            },
            {
                "code": "HK.00388",
                "price": 100.0,
                "qty": 200,
                "trd_side": "BUY",
                "enable_risk_check": False
            }
        ]
        batch_results = trader.batch_place_orders(batch_orders)
        print(f"   批量下单结果: {len(batch_results)}个订单")
        print()
        
        print("4. 获取当日盈亏")
        daily_pnl = trader.get_daily_pnl()
        print(f"   当日盈亏: {daily_pnl}")
        print()
        
        print("5. 获取绩效总结（最近7天）")
        performance = trader.get_performance_summary(7)
        print(f"   绩效总结: {performance}")
        print()
        
        print("6. 系统健康检查")
        health = trader.health_check()
        print(f"   系统健康状态: {health}")
        print()
        
    except Exception as e:
        print(f"高级功能演示出错: {e}")


def demo_event_handling():
    """演示事件处理"""
    print("=== 事件处理演示 ===\n")
    
    def order_callback(data):
        """订单状态变化回调"""
        print(f"订单状态变化: {data}")
    
    def deal_callback(data):
        """成交回调"""
        print(f"成交通知: {data}")
    
    try:
        trader = FutuTrade()
        
        print("1. 设置订单状态回调")
        trader.set_order_callback(order_callback)
        print("   订单回调已设置")
        print()
        
        print("2. 设置成交回调")
        trader.set_deal_callback(deal_callback)
        print("   成交回调已设置")
        print()
        
        print("3. 启用订单推送")
        trader.enable_order_push()
        print("   订单推送已启用")
        print()
        
        print("4. 启用成交推送")
        trader.enable_deal_push()
        print("   成交推送已启用")
        print()
        
    except Exception as e:
        print(f"事件处理演示出错: {e}")


def main():
    """主函数"""
    print("富途交易模块使用示例\n")
    print("注意：此示例仅用于演示API使用方法")
    print("实际交易时请确保：")
    print("1. FutuOpenD网关程序正在运行")
    print("2. 已正确配置交易密码")
    print("3. 账户有足够的资金和权限")
    print("4. 了解交易风险\n")
    
    try:
        # 运行各个演示
        demo_basic_trading()
        demo_order_operations() 
        demo_advanced_features()
        demo_event_handling()
        
        print("=== 演示完成 ===")
        print("更多功能请参考FutuTrade类的文档和测试用例")
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")


if __name__ == "__main__":
    main()