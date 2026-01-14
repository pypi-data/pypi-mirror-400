#!/usr/bin/env python3
"""
Yutian Image Problem Solver MCP Server (STDIO Mode)
基于智谱AI拍照解题智能体的MCP服务
"""

import json
import sys
from typing import Any, Optional
import requests


def glm_images_jieti(image_url, api_keys):
    '''
    调用智谱拍照解题智能体，上传图片，返回解题的答案
    参数:
        image_url: 图片URL地址
        api_keys: 智谱AI的API密钥
    返回:
        answer: 解题答案文本
    '''
    url = "https://open.bigmodel.cn/api/v1/agents"
    headers = {
        "Authorization": f"Bearer {api_keys}",
        "Content-Type": "application/json"
    }
    data = {
        "agent_id": "intelligent_education_solve_agent",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": image_url
                    }
                ]
            }
        ],
        "stream": True
    }

    response = requests.post(url, headers=headers, json=data, stream=True, timeout=30)
    response.raise_for_status()
    answer = ''
        
    for line in response.iter_lines():
        line = line.decode('utf-8')
        if line and 'DONE' not in line and 'done' not in line:
            json_line = json.loads(line[6:])
            if 'finish_reason' not in json_line['choices'][0]:
                answer += json_line['choices'][0]['messages'][0]['content']['text']
            else:
                print('解题完毕。', file=sys.stderr)
    return answer


def handle_request(request):
    """
    处理单个MCP请求
    """
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", 1)
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "paizhaojieti-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            tools = [
                {
                    "name": "solve_image_problem",
                    "description": "通过上传图片URL来解题。支持数学题、物理题、化学题等各种学科的题目识别和解答。需要提供图片URL和智谱AI的API密钥。",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "题目图片的URL地址，必须是公网可访问的图片链接"
                            },
                            "api_key": {
                                "type": "string",
                                "description": "智谱AI的API密钥，用于调用拍照解题智能体"
                            }
                        },
                        "required": ["image_url", "api_key"]
                    }
                }
            ]
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name != "solve_image_problem":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"未知的工具名称：{tool_name}"
                    }
                }
            
            image_url = arguments.get("image_url")
            api_key = arguments.get("api_key")
            
            if not image_url or not api_key:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "缺少必需的参数 image_url 或 api_key"
                    }
                }
            
            try:
                answer = glm_images_jieti(image_url, api_key)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": answer
                            }
                        ]
                    }
                }
            except requests.exceptions.RequestException as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"调用智谱AI API失败：{str(e)}"
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"解题失败：{str(e)}"
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"未知的方法：{method}"
                }
            }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "error": {
                "code": -32603,
                "message": f"服务器错误：{str(e)}"
            }
        }


def main():
    """
    STDIO MCP服务主函数
    从标准输入读取JSON-RPC请求，处理后写入标准输出
    """
    print("Yutian Image Problem Solver MCP Server (STDIO Mode)", file=sys.stderr)
    print("服务器已启动，等待请求...", file=sys.stderr)
    
    # 持续从标准输入读取请求
    while True:
        try:
            # 读取一行JSON请求
            line = sys.stdin.readline()
            if not line:
                # 标准输入关闭，退出程序
                break
            
            # 移除换行符和空格
            line = line.strip()
            if not line:
                continue
            
            # 解析JSON请求
            request = json.loads(line)
            print(f"收到请求: {json.dumps(request, ensure_ascii=False)}", file=sys.stderr)
            
            # 处理请求
            response = handle_request(request)
            
            # 发送JSON响应到标准输出
            response_str = json.dumps(response, ensure_ascii=False)
            print(response_str)
            # 刷新输出缓冲区，确保响应被立即发送
            sys.stdout.flush()
            print(f"发送响应: {response_str}", file=sys.stderr)
            
        except json.JSONDecodeError as e:
            # 处理无效的JSON格式
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"无效的JSON格式: {str(e)}"
                }
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()
            print(f"JSON解析错误: {str(e)}", file=sys.stderr)
        except Exception as e:
            # 处理其他异常
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"服务器错误: {str(e)}"
                }
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()
            print(f"服务器异常: {str(e)}", file=sys.stderr)


if __name__ == "__main__":
    main()