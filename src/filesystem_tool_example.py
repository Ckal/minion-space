#!/usr/bin/env python3

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from mcp_integration import MCPBrainClient, create_final_answer_tool, add_filesystem_tool


async def demo_filesystem_tool():
    """演示文件系统工具的基本功能"""
    print("🔍 文件系统工具演示")
    print("=" * 50)
    
    try:
        async with MCPBrainClient() as client:
            print("✓ 初始化 MCP 客户端")
            
            # 添加文件系统工具
            try:
                await add_filesystem_tool(client, workspace_paths=[
                    "/Users/femtozheng/workspace",
                    "/Users/femtozheng/python-project/minion-agent"
                ])
                print("✓ 文件系统工具添加成功")
                
                # 获取所有工具
                tools = client.get_tools_for_brain()
                print(f"✓ 总共可用工具: {len(tools)}")
                
                # 筛选文件系统相关工具
                fs_tools = [t for t in tools if any(keyword in t.name.lower() 
                           for keyword in ['file', 'read', 'write', 'list', 'directory'])]
                
                if fs_tools:
                    print(f"\n📁 发现 {len(fs_tools)} 个文件系统工具:")
                    for i, tool in enumerate(fs_tools, 1):
                        print(f"  {i}. {tool.name}")
                        print(f"     描述: {tool.description}")
                        if hasattr(tool, 'parameters') and tool.parameters:
                            props = tool.parameters.get('properties', {})
                            if props:
                                print(f"     参数: {', '.join(props.keys())}")
                        print()
                    
                    # 演示如何在 brain.step 中使用
                    print("💡 在 brain.step 中使用示例:")
                    print("```python")
                    print("# 添加最终答案工具")
                    print("final_tool = create_final_answer_tool()")
                    print("all_tools = fs_tools + [final_tool]")
                    print()
                    print("# 在 brain.step 中使用")
                    print("obs, score, *_ = await brain.step(")
                    print("    query='请读取 README.md 文件的内容',")
                    print("    route='raw',")
                    print("    check=False,")
                    print("    tools=all_tools")
                    print(")")
                    print("```")
                    
                    # 模拟 brain.step 调用
                    print("\n🧠 模拟 brain.step 集成:")
                    final_tool = create_final_answer_tool()
                    all_tools = fs_tools + [final_tool]
                    
                    tool_specs = [tool.to_function_spec() for tool in all_tools]
                    print(f"✓ 生成了 {len(tool_specs)} 个工具规格")
                    print("✓ 工具已准备好供 brain.step 使用")
                    
                    # 展示工具规格格式
                    if fs_tools:
                        sample_tool = fs_tools[0]
                        print(f"\n📋 示例工具规格 ({sample_tool.name}):")
                        spec = sample_tool.to_function_spec()
                        print(f"  类型: {spec.get('type', 'N/A')}")
                        print(f"  函数名: {spec.get('function', {}).get('name', 'N/A')}")
                        print(f"  描述: {spec.get('function', {}).get('description', 'N/A')}")
                        
                else:
                    print("⚠ 没有发现文件系统相关工具")
                    print("可能的原因:")
                    print("- @modelcontextprotocol/server-filesystem 未正确安装")
                    print("- Node.js/npx 环境问题")
                    print("- 工具名称不包含预期的关键词")
                    
            except Exception as e:
                print(f"❌ 添加文件系统工具失败: {e}")
                print("\n故障排除:")
                print("1. 确保安装了 Node.js 和 npx")
                print("2. 运行: npx @modelcontextprotocol/server-filesystem --help")
                print("3. 检查网络连接")
                print("4. 确保指定的路径存在且可访问")
                
    except Exception as e:
        print(f"❌ 演示失败: {e}")


async def test_filesystem_paths():
    """测试不同的文件系统路径配置"""
    print("\n🛠 测试自定义路径配置")
    print("=" * 50)
    
    # 测试不同的路径组合
    test_paths = [
        ["/Users/femtozheng/workspace"],
        ["/Users/femtozheng/python-project/minion-agent"],
        ["/Users/femtozheng/workspace", "/Users/femtozheng/python-project/minion-agent"],
        [".", str(Path.home() / "Documents")]  # 相对路径和绝对路径混合
    ]
    
    for i, paths in enumerate(test_paths, 1):
        print(f"\n📁 测试配置 {i}: {paths}")
        try:
            # 检查路径是否存在
            existing_paths = []
            for path in paths:
                if Path(path).exists():
                    existing_paths.append(path)
                    print(f"  ✓ 路径存在: {path}")
                else:
                    print(f"  ⚠ 路径不存在: {path}")
            
            if existing_paths:
                async with MCPBrainClient() as client:
                    await add_filesystem_tool(client, workspace_paths=existing_paths)
                    tools = client.get_tools_for_brain()
                    fs_tools = [t for t in tools if any(keyword in t.name.lower() 
                               for keyword in ['file', 'read', 'write', 'list'])]
                    print(f"  ✓ 配置成功，发现 {len(fs_tools)} 个文件系统工具")
            else:
                print("  ⚠ 跳过测试（没有有效路径）")
                
        except Exception as e:
            print(f"  ❌ 配置失败: {e}")


async def show_integration_example():
    """展示完整的集成示例"""
    print("\n🚀 完整集成示例")
    print("=" * 50)
    
    print("""
这里是如何在实际项目中使用文件系统工具的示例:

```python
from mcp_integration import MCPBrainClient, add_filesystem_tool, create_final_answer_tool
from minion.main.brain import Brain
from minion.main import LocalPythonEnv  
from minion.providers import create_llm_provider

async def use_filesystem_in_brain():
    # 1. 设置 MCP 客户端和文件系统工具
    async with MCPBrainClient() as mcp_client:
        await add_filesystem_tool(mcp_client, workspace_paths=[
            "/Users/femtozheng/workspace",
            "/Users/femtozheng/python-project/minion-agent"
        ])
        
        # 2. 获取所有工具
        mcp_tools = mcp_client.get_tools_for_brain()
        final_tool = create_final_answer_tool()
        all_tools = mcp_tools + [final_tool]
        
        # 3. 创建 brain 实例
        llm = create_llm_provider(your_config)
        python_env = LocalPythonEnv(verbose=False)
        brain = Brain(python_env=python_env, llm=llm)
        
        # 4. 使用 brain.step 处理文件操作
        obs, score, *_ = await brain.step(
            query="请读取项目根目录的 README.md 文件并总结其内容",
            route="raw",
            check=False,
            tools=all_tools
        )
        
        print(f"Brain 响应: {obs}")

# 其他用例:
# - "列出 workspace 目录下的所有 Python 文件"
# - "读取 config.json 文件并解析其配置"
# - "在指定目录创建一个新的文档文件"
# - "搜索包含特定关键词的文件"
```

🎯 主要优势:
- 🔒 安全: 只能访问预先配置的路径
- 🔄 异步: 所有文件操作都是异步的
- 🧠 智能: AI 可以理解文件内容并进行推理
- 🛠 灵活: 支持读取、写入、列表等多种操作
""")


async def main():
    """运行所有演示"""
    print("📁 MCP 文件系统工具集成演示")
    print("=" * 80)
    
    await demo_filesystem_tool()
    await test_filesystem_paths()
    await show_integration_example()
    
    print("\n✅ 演示完成!")
    print("\n📝 下一步:")
    print("1. 运行: python app_with_mcp.py")
    print("2. 在界面中启用 'MCP Tools'")
    print("3. 测试文件相关查询，如: '读取当前目录的文件列表'")
    print("4. 或者直接在代码中使用文件系统工具")


if __name__ == "__main__":
    asyncio.run(main()) 