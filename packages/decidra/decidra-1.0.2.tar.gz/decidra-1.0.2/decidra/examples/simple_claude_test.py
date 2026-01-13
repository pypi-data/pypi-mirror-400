"""
简单的Claude Code SDK测试
用于验证基本功能，避免复杂的异步任务管理问题
"""

import asyncio
import sys
import os

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from claude_code_sdk import query
    from claude_code_sdk.types import SystemMessage
    print("✅ Claude Code SDK导入成功")
    SDK_AVAILABLE = True
except ImportError as e:
    print(f"❌ Claude Code SDK导入失败: {e}")
    SDK_AVAILABLE = False
    SystemMessage = None


async def simple_test():
    """简单测试Claude Code SDK"""
    if not SDK_AVAILABLE:
        print("❌ SDK不可用，跳过测试")
        return
    
    print("🔍 开始简单测试...")
    
    try:
        # 最简单的测试
        prompt = "请简单回复'测试成功'"
        print(f"📝 发送提示: {prompt}")
        
        response_parts = []
        message_count = 0
        async for message in query(prompt=prompt):
            message_count += 1
            print(f"📨 消息 {message_count} 类型: {type(message)}")
            print(f"📨 消息内容预览: {str(message)[:100]}...")
            
            # 跳过SystemMessage
            if SystemMessage and isinstance(message, SystemMessage):
                print("⏭️ 跳过SystemMessage")
                continue
            
            # 处理实际响应
            if isinstance(message, str):
                response_parts.append(message)
                print(f"✅ 添加字符串响应: {message}")
            elif hasattr(message, 'content'):
                content = str(message.content)
                response_parts.append(content)
                print(f"✅ 添加内容响应: {content}")
            elif hasattr(message, 'text'):
                text = str(message.text)
                response_parts.append(text)
                print(f"✅ 添加文本响应: {text}")
            else:
                text = str(message)
                response_parts.append(text)
                print(f"✅ 添加其他响应: {text}")
            
            # 收集几个消息看看完整流程
            if message_count >= 5:
                break
        
        full_response = ''.join(response_parts)
        print(f"✅ 完整响应: {full_response}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("🚀 Claude Code SDK简单测试")
    print("=" * 40)
    
    await simple_test()
    
    print("=" * 40)
    print("✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(main())