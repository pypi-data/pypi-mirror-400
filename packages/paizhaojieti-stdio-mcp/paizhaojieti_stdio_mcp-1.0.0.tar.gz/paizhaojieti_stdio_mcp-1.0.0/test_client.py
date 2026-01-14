#!/usr/bin/env python3
"""
测试脚本 - 验证STDIO MCP服务功能
"""

import json
import time
import subprocess
import sys


def test_initialize(process, request_id=1):
    """测试initialize方法"""
    print("="*60)
    print("1. 测试initialize方法")
    print("="*60)
    
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "initialize",
        "params": {}
    }
    
    try:
        # 发送请求
        process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        if not response_line:
            print(f"✗ 没有收到响应")
            return False
        
        response = json.loads(response_line.strip())
        print(f"✓ initialize方法调用成功")
        print(f"  响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        return True
    except Exception as e:
        print(f"✗ initialize方法调用失败: {str(e)}")
        return False


def test_list_tools(process, request_id=2):
    """测试tools/list方法"""
    print("\n" + "="*60)
    print("2. 测试tools/list方法")
    print("="*60)
    
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        # 发送请求
        process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        if not response_line:
            print(f"✗ 没有收到响应")
            return False
        
        response = json.loads(response_line.strip())
        print(f"✓ tools/list方法调用成功")
        
        result = response.get("result", {})
        tools = result.get("tools", [])
        
        print(f"  可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"\n  工具名称: {tool.get('name')}")
            print(f"  描述: {tool.get('description')}")
            print(f"  参数schema: {json.dumps(tool.get('inputSchema'), indent=4, ensure_ascii=False)}")
        
        return True
    except Exception as e:
        print(f"✗ tools/list方法调用失败: {str(e)}")
        return False


def test_call_tool(process, request_id=3):
    """测试tools/call方法"""
    print("\n" + "="*60)
    print("3. 测试tools/call方法")
    print("="*60)
    
    # 修改为你自己的测试参数
    test_image_url = "https://markdown-doc-image-picgo.oss-cn-wuhan-lr.aliyuncs.com/anweichao_mac_m4/timu.png"
    test_api_key = "8de9b917859142399a0dd2fd87b2155c.2kY7wKDI5f4mt6E3"
    
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {
            "name": "solve_image_problem",
            "arguments": {
                "image_url": test_image_url,
                "api_key": test_api_key
            }
        }
    }
    
    try:
        print(f"  请求URL: {test_image_url}")
        print(f"  正在调用工具...")
        
        # 发送请求
        process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        if not response_line:
            print(f"✗ 没有收到响应")
            return False
        
        response = json.loads(response_line.strip())
        print(f"✓ tools/call方法调用成功")
        
        print("\n" + "-"*60)
        print("解题结果：")
        print("-"*60)
        
        if "result" in response:
            result_data = response["result"]
            if "content" in result_data:
                for content in result_data["content"]:
                    if content.get("type") == "text":
                        print(content.get("text"))
        elif "error" in response:
            print(f"  错误信息: {response['error']}")
        
        print("-"*60)
        return True
        
    except subprocess.TimeoutExpired:
        print(f"✗ 工具调用超时")
        return False
    except Exception as e:
        print(f"✗ 工具调用失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("\n")
    print("*"*60)
    print("*" + " "*20 + "Paizhaojieti STDIO MCP Server 测试" + " "*20 + "*")
    print("*"*60)
    print("")
    print(f"""测试时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}""")

    print("")
    
    # 启动MCP服务进程
    print("启动MCP服务进程...")
    try:
        process = subprocess.Popen(
            [sys.executable, "/home/yutian/code/paizhaojieti_stdio_mcp/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 行缓冲
            encoding='utf-8'
        )
        
        # 等待服务启动
        time.sleep(1)
        
        # 检查服务是否正常启动
        if process.poll() is not None:
            # 服务已退出，打印错误信息
            stderr_output = process.stderr.read()
            print(f"✗ 服务启动失败: {stderr_output}")
            return 1
        
        print("✓ MCP服务进程启动成功")
        
    except Exception as e:
        print(f"✗ 无法启动MCP服务进程: {str(e)}")
        return 1
    
    results = []
    
    try:
        # 测试initialize方法
        results.append(("initialize方法", test_initialize(process)))
        
        # 测试tools/list方法
        results.append(("tools/list方法", test_list_tools(process)))
        
        # 测试tools/call方法
        results.append(("tools/call方法", test_call_tool(process)))
        
    finally:
        # 关闭服务进程
        print("\n关闭MCP服务进程...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("✓ MCP服务进程已关闭")
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ 所有测试通过！STDIO MCP服务运行正常。")
    else:
        print("✗ 部分测试失败，请检查服务配置。")
    print("="*60)
    print("")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())