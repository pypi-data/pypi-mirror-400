"""
富途监控接口使用示例
演示如何使用新的监控模块接口获取数据和订阅实时数据
"""

import asyncio
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入监控模块
from monitor import FutuDataManager, IndicatorsManager, DataFlowManager


async def basic_data_example():
    """基础数据获取示例"""
    logger.info("=== 基础数据获取示例 ===")
    
    # 创建数据管理器
    data_manager = FutuDataManager()
    
    try:
        # 1. 验证股票代码
        stock_codes = ['HK.00700', 'HK.09988', 'US.AAPL']
        logger.info(f"验证股票代码: {stock_codes}")
        
        for code in stock_codes:
            is_valid = await data_manager.validate_stock_code(code)
            logger.info(f"  {code}: {'有效' if is_valid else '无效'}")
        
        # 2. 获取市场状态
        logger.info("获取市场状态...")
        market_status = await data_manager.get_market_status(stock_codes)
        for code, status in market_status.items():
            logger.info(f"  {code}: {status.value}")
        
        # 3. 获取实时行情
        logger.info("获取实时行情...")
        quotes = await data_manager.get_real_time_quotes(stock_codes)
        for code, quote in quotes.items():
            logger.info(f"  {code}: 价格={quote.current_price}, 涨跌幅={quote.change_rate:.2%}")
        
        # 4. 获取历史K线数据
        logger.info("获取历史K线数据...")
        for code in stock_codes[:1]:  # 只测试第一只股票
            klines = await data_manager.get_historical_klines(code, 30)
            if not klines.empty:
                logger.info(f"  {code}: 获取到 {len(klines)} 条K线数据")
                logger.info(f"    最新收盘价: {klines.iloc[-1]['close']}")
            else:
                logger.warning(f"  {code}: 未获取到K线数据")
                
    except Exception as e:
        logger.error(f"基础数据获取示例失败: {e}")
    finally:
        await data_manager.cleanup()


async def subscription_example():
    """实时数据订阅示例"""
    logger.info("=== 实时数据订阅示例 ===")
    
    data_manager = FutuDataManager()
    
    try:
        # 定义数据回调函数
        def data_callback(stock_code, data):
            logger.info(f"收到实时数据: {stock_code} - {data}")
        
        stock_codes = ['HK.00700']
        
        # 订阅实时数据
        logger.info(f"订阅实时数据: {stock_codes}")
        success = await data_manager.subscribe_real_time_data(stock_codes, data_callback)
        
        if success:
            logger.info("订阅成功，等待数据推送...")
            
            # 获取订阅状态
            status = await data_manager.get_subscription_status()
            logger.info(f"订阅状态: {status}")
            
            # 模拟等待一段时间接收数据
            await asyncio.sleep(10)
            
            # 取消订阅
            logger.info("取消订阅...")
            unsubscribe_success = await data_manager.unsubscribe_real_time_data(stock_codes)
            logger.info(f"取消订阅{'成功' if unsubscribe_success else '失败'}")
        else:
            logger.error("订阅失败")
            
    except Exception as e:
        logger.error(f"订阅示例失败: {e}")
    finally:
        await data_manager.cleanup()


async def indicators_example():
    """技术指标计算示例"""
    logger.info("=== 技术指标计算示例 ===")
    
    indicators_manager = IndicatorsManager()
    
    try:
        stock_codes = ['HK.00700']
        
        # 更新技术指标
        logger.info(f"计算技术指标: {stock_codes}")
        indicators = await indicators_manager.update_all_indicators(stock_codes)
        
        for code, indicator in indicators.items():
            logger.info(f"  {code} 技术指标:")
            if indicator.ma5:
                logger.info(f"    MA5: {indicator.ma5:.2f}")
            if indicator.ma10:
                logger.info(f"    MA10: {indicator.ma10:.2f}")
            if indicator.ma20:
                logger.info(f"    MA20: {indicator.ma20:.2f}")
            if indicator.rsi14:
                logger.info(f"    RSI14: {indicator.rsi14:.2f} [{indicator.rsi_signal.value}]")
            if indicator.macd_line:
                logger.info(f"    MACD: {indicator.macd_line:.2f} [{indicator.macd_signal.value}]")
                
    except Exception as e:
        logger.error(f"技术指标示例失败: {e}")
    finally:
        await data_manager.cleanup()


async def data_flow_example():
    """数据流管理示例"""
    logger.info("=== 数据流管理示例 ===")
    
    flow_manager = DataFlowManager()
    
    try:
        stock_codes = ['HK.00700', 'HK.09988']
        
        # 执行完整的数据更新周期
        logger.info(f"执行数据更新周期: {stock_codes}")
        result = await flow_manager.data_update_cycle(stock_codes)
        
        if result.success:
            logger.info("数据更新成功")
            logger.info(f"  获取到 {len(result.stock_data)} 只股票的实时数据")
            logger.info(f"  计算了 {len(result.indicators_data)} 只股票的技术指标")
            
            # 显示部分数据
            for code in stock_codes[:1]:  # 只显示第一只股票
                if code in result.stock_data:
                    stock = result.stock_data[code]
                    logger.info(f"  {code}: {stock.name} - {stock.current_price}")
                
                if code in result.indicators_data:
                    indicators = result.indicators_data[code]
                    logger.info(f"  {code} 指标: MA5={indicators.ma5}, RSI={indicators.rsi14}")
        else:
            logger.error(f"数据更新失败: {result.error_message}")
            
    except Exception as e:
        logger.error(f"数据流示例失败: {e}")
    finally:
        # 清理资源
        await flow_manager.data_manager.cleanup()


async def main():
    """主函数"""
    logger.info("开始运行富途监控接口示例")
    
    try:
        # 运行各个示例
        await basic_data_example()
        await asyncio.sleep(2)
        
        await indicators_example()
        await asyncio.sleep(2)
        
        await data_flow_example()
        await asyncio.sleep(2)
        
        # 注意：订阅示例需要实际的富途连接，可能会失败
        # await subscription_example()
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
    finally:
        logger.info("示例程序结束")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())