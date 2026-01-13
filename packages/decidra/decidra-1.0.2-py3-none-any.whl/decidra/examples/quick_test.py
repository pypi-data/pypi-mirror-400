"""
快速测试股票分析功能
"""

import asyncio
import sys
import os

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.ai.claude_ai_client import AIAnalysisRequest, create_claude_client


async def test_simple_analysis():
    """测试简单的股票分析"""
    print("🔍 测试简单股票分析...")
    
    client = await create_claude_client()
    
    if not client.is_available():
        print("❌ 客户端不可用")
        return
    
    # 简单的分析请求
    request = AIAnalysisRequest(
        stock_code="HK.00700",
        analysis_type="technical",
        data_context={
            'realtime_quote': {
                'cur_price': 368.80,
                'change_rate': 2.15,
                'volume': 15680000
            }
        },
        user_question="这只股票怎么样？"
    )
    
    print("📊 开始分析...")
    response = await client.generate_stock_analysis(request)
    
    print("\n🤖 分析结果:")
    print("=" * 50)
    print(response.content)
    print("=" * 50)
    
    print(f"\n📋 摘要:")
    print(f"股票: {response.stock_code}")
    print(f"类型: {response.analysis_type}")
    print(f"建议: {response.recommendation[:100]}...")


async def main():
    await test_simple_analysis()


if __name__ == "__main__":
    asyncio.run(main())