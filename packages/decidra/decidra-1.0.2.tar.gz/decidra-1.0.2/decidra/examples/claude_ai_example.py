"""
Claude AI Client 使用示例

展示如何使用重构后的claude_ai_client进行股票分析和AI对话
基于claude-code-sdk，在Claude Code环境中自动使用应用内认证
"""

import asyncio
import os

try:
    import anyio
    ANYIO_AVAILABLE = True
except ImportError:
    ANYIO_AVAILABLE = False

# 添加项目根目录到sys.path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.ai.claude_ai_client import (
    AIAnalysisRequest, 
    create_claude_client,
    quick_stock_analysis
)


async def example_stock_analysis():
    """股票分析示例"""
    print("=== Claude AI 股票分析示例 ===\n")
    
    # 创建客户端 - 在Claude Code环境中自动使用应用内认证
    client = await create_claude_client()
    
    if not client.is_available():
        print("❌ Claude AI客户端不可用")
        print("请确保已安装claude-code-sdk: pip install claude-code-sdk")
        print("并在Claude Code应用中运行此代码")
        return
    
    print("✅ Claude AI客户端已就绪 (使用Claude Code应用内认证)\n")
    
    # 准备股票数据
    stock_code = "HK.00700"
    data_context = {
        'basic_info': {
            'code': 'HK.00700',
            'name': '腾讯控股',
            'stock_type': 'STOCK',
            'listing_date': '2004-06-16'
        },
        'realtime_quote': {
            'cur_price': 368.80,
            'change_rate': 2.15,
            'volume': 15680000,
            'turnover_rate': 1.65,
            'amplitude': 3.2
        },
        'technical_indicators': {
            'rsi': 65.3,
            'macd': {'dif': 2.34, 'dea': 1.89},
            'ma5': 365.20,
            'ma20': 350.80,
            'price_trend': '温和上涨',
            'volume_trend': '放量'
        }
    }
    
    # 创建分析请求
    request = AIAnalysisRequest(
        stock_code=stock_code,
        analysis_type='technical',
        data_context=data_context,
        user_question="这只股票目前适合买入吗？"
    )
    
    print(f"📊 开始分析股票: {stock_code}")
    print("分析类型: 技术分析")
    print("用户问题: 这只股票目前适合买入吗？\n")
    
    # 生成分析
    response = await client.generate_stock_analysis(request)
    
    print("🤖 AI分析结果:")
    print("=" * 50)
    print(response.content)
    print("=" * 50)
    
    print(f"\n📋 分析摘要:")
    print(f"股票代码: {response.stock_code}")
    print(f"分析类型: {response.analysis_type}")
    print(f"置信度: {response.confidence_score:.0%}")
    print(f"风险等级: {response.risk_level}")
    print(f"建议: {response.recommendation}")
    
    if response.key_points:
        print(f"\n🔍 关键要点:")
        for i, point in enumerate(response.key_points, 1):
            print(f"{i}. {point}")


async def example_ai_chat():
    """AI对话示例"""
    print("\n\n=== Claude AI 对话示例 ===\n")
    
    # 创建客户端
    client = await create_claude_client()
    
    if not client.is_available():
        print("❌ Claude AI客户端不可用")
        return
    
    # 股票上下文
    stock_context = {
        'stock_code': 'HK.00700',
        'stock_name': '腾讯控股',
        'current_price': 368.80
    }
    
    # 模拟对话
    questions = [
        "腾讯控股是做什么的？",
        "腾讯的主要竞争对手有哪些？",
        "现在买入腾讯风险大吗？",
        "如果我只有1万元，应该怎么投资腾讯？"
    ]
    
    print("💬 开始AI对话 (股票: 腾讯控股)\n")
    
    for i, question in enumerate(questions, 1):
        print(f"👤 用户问题 {i}: {question}")
        
        response = await client.chat_with_ai(question, stock_context)
        
        print(f"🤖 AI回答: {response}\n")
        print("-" * 60)


async def example_quick_analysis():
    """快速分析示例"""
    print("\n\n=== 快速分析示例 ===\n")
    
    # 简单的数据上下文
    simple_context = {
        'realtime_quote': {
            'cur_price': 45.60,
            'change_rate': -1.25,
            'volume': 8900000
        }
    }
    
    # 使用便捷函数进行快速分析
    result = await quick_stock_analysis(
        stock_code="US.AAPL",
        analysis_type="comprehensive",
        data_context=simple_context
    )
    
    print("📱 苹果公司 (US.AAPL) 快速综合分析:")
    print("=" * 50)
    print(result)
    print("=" * 50)


async def example_client_status():
    """客户端状态示例"""
    print("\n\n=== 客户端状态检查 ===\n")
    
    client = await create_claude_client()
    status = client.get_client_status()
    
    print("🔍 Claude AI客户端状态:")
    print(f"• 可用状态: {'✅ 可用' if status['available'] else '❌ 不可用'}")
    print(f"• SDK状态: {'✅ 已安装' if status['sdk_available'] else '❌ 未安装'}")
    print(f"• 认证方式: {status['authentication']}")
    
    # 测试连接
    if client.is_available():
        print("\n🔗 检查AI状态...")
        connection_ok = client.test_connection()
        print(f"AI状态: {'✅ 就绪' if connection_ok else '❌ 不可用'}")


async def example_different_analysis_types():
    """不同分析类型示例"""
    print("\n\n=== 不同分析类型示例 ===\n")
    
    client = await create_claude_client()
    
    if not client.is_available():
        print("❌ Claude AI客户端不可用")
        return
    
    # 准备股票数据
    stock_code = "SH.600036"
    data_context = {
        'basic_info': {
            'code': 'SH.600036',
            'name': '招商银行',
            'stock_type': 'STOCK'
        },
        'realtime_quote': {
            'cur_price': 35.80,
            'change_rate': 1.25,
            'volume': 12500000
        }
    }
    
    # 测试不同分析类型
    analysis_types = [
        ('technical', '技术分析'),
        ('fundamental', '基本面分析'),
        ('comprehensive', '综合分析')
    ]
    
    for analysis_type, type_name in analysis_types:
        print(f"📊 {type_name} - {stock_code}")
        
        request = AIAnalysisRequest(
            stock_code=stock_code,
            analysis_type=analysis_type,
            data_context=data_context
        )
        
        response = await client.generate_stock_analysis(request)
        
        print(f"🤖 {type_name}结果摘要:")
        print(f"• 置信度: {response.confidence_score:.0%}")
        print(f"• 风险等级: {response.risk_level}")
        print(f"• 投资建议: {response.recommendation}")
        print("-" * 50)


async def main():
    """主函数，运行所有示例"""
    print("🚀 Claude AI Client 使用示例 (重构版)")
    print("基于claude-code-sdk，使用Claude Code应用内认证")
    print("=" * 60)
    
    try:
        # 运行各种示例
        await example_client_status()
        await example_stock_analysis()
        await example_ai_chat()
        await example_quick_analysis()
        await example_different_analysis_types()
        
        print("\n\n✅ 所有示例运行完成!")
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        print("\n💡 解决方案:")
        print("1. 确保已安装依赖: pip install claude-code-sdk")
        print("2. 在Claude Code应用中运行此代码")
        print("3. 检查网络连接是否正常")


if __name__ == "__main__":
    # 运行示例，优先使用anyio（Claude Code SDK推荐）
    if ANYIO_AVAILABLE:
        anyio.run(main)
    else:
        asyncio.run(main())