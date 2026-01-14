# ModelScope MCP 部署配置

## MCP服务信息

**服务名称**: Paizhaojieti STDIO MCP Server  
**服务描述**: 基于智谱AI拍照解题智能体的STDIO类型MCP服务，提供图片题目识别和解答功能  
**服务类型**: STDIO  
**GitHub仓库**: https://github.com/yourusername/paizhaojieti_stdio_mcp  

## 服务配置

### mcp_config.json

```json
{
  "name": "paizhaojieti-mcp",
  "version": "1.0.0",
  "description": "基于智谱AI拍照解题智能体的STDIO类型MCP服务",
  "type": "stdio",
  "main": "server.py",
  "command": "python server.py",
  "dependencies": {
    "requirements": "requirements.txt"
  },
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
```

## 项目结构

```
paizhaojieti_stdio_mcp/
├── server.py          # STDIO类型MCP服务主程序
├── test_client.py     # 测试脚本
├── requirements.txt   # 依赖文件
└── mcp_config.json    # ModelScope部署配置文件
```

## 在ModelScope MCP广场发布步骤

### 步骤1: 准备GitHub仓库

1. 访问 https://github.com/new
2. 创建新仓库，命名为 `paizhaojieti_stdio_mcp`
3. 选择 Public（推荐）
4. 上传代码到仓库

```bash
cd /home/yutian/code/paizhaojieti_stdio_mcp
git init
git add .
git commit -m "Initial commit: Paizhaojieti STDIO MCP Server"
git remote add origin https://github.com/yourusername/paizhaojieti_stdio_mcp.git
git branch -M main
git push -u origin main
```

### 步骤2: 在ModelScope MCP广场提交

1. 访问 https://modelscope.cn/mcp
2. 点击"创建MCP服务"或"发布MCP服务"
3. 填写基本信息：
   - **MCP名称**: Paizhaojieti STDIO MCP Server
   - **MCP描述**: 基于智谱AI拍照解题智能体的STDIO类型MCP服务，提供图片题目识别和解答功能
   - **MCP类型**: STDIO
   - **GitHub仓库**: https://github.com/yourusername/paizhaojieti_stdio_mcp
   - **部署方式**: 选择"个人阿里云函数计算资源"
   - **配置文件路径**: mcp_config.json
4. 提供使用说明和示例

### 步骤3: 验证发布

1. 在ModelScope MCP广场搜索 "Paizhaojieti STDIO MCP"
2. 确认服务信息正确
3. 测试服务是否可以正常调用

## 工具说明

### solve_image_problem工具

**功能**: 通过上传图片URL来解题，支持数学题、物理题、化学题等各种学科的题目识别和解答。

**参数**: 
- `image_url`: 题目图片的URL地址，必须是公网可访问的图片链接
- `api_key`: 智谱AI的API密钥，用于调用拍照解题智能体

**响应**: 
- 返回解题答案文本，包含题目分析、解析过程和最终答案

## 使用示例

### 在ModelScope中使用

1. 访问 https://modelscope.cn/mcp
2. 搜索并找到 "Paizhaojieti STDIO MCP Server"
3. 点击"调用"按钮
4. 填写调用参数：
   - `image_url`: 题目图片URL
   - `api_key`: 智谱AI API密钥
5. 点击"执行"查看结果

### 本地测试

```bash
# 直接运行服务
python server.py

# 或者使用测试脚本
python test_client.py
```

### 在代码中调用

```python
import subprocess
import json

# 启动MCP服务进程
process = subprocess.Popen(
    ["python", "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    encoding='utf-8'
)

# 发送请求
def call_mcp(method, params=None):
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    # 发送请求
    process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
    process.stdin.flush()
    
    # 读取响应
    response_line = process.stdout.readline()
    return json.loads(response_line.strip())

# 初始化服务
call_mcp("initialize")

# 获取工具列表
tools_response = call_mcp("tools/list")
print(f"可用工具: {json.dumps(tools_response, indent=2, ensure_ascii=False)}")

# 调用解题工具
result = call_mcp("tools/call", {
    "name": "solve_image_problem",
    "arguments": {
        "image_url": "https://example.com/problem.png",
        "api_key": "your_zhipu_api_key"
    }
})

print(f"解题结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

# 关闭服务
process.terminate()
```

## 注意事项

1. **服务类型**: 此服务为STDIO类型，适合在ModelScope上使用个人授权的阿里云函数计算资源部署
2. **API密钥**: 用户需要提供自己的智谱AI API密钥
3. **图片URL**: 必须是公网可访问的图片链接
4. **依赖**: 仅需要requests库，已在requirements.txt中指定
5. **部署环境**: ModelScope会自动处理依赖安装和服务启动

## 本地开发和测试

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行测试

```bash
python test_client.py
```

测试脚本会自动启动服务，测试所有功能，并输出详细结果。

## 故障排除

### 问题1: 服务部署失败

**可能原因**:
- mcp_config.json配置错误
- 依赖包安装失败
- 代码语法错误

**解决方案**:
1. 检查mcp_config.json格式和内容
2. 确保requirements.txt中包含所有必要依赖
3. 在本地运行测试脚本验证代码正确性

### 问题2: 工具调用失败

**可能原因**:
- API密钥无效
- 图片URL不可访问
- 智谱AI API服务异常

**解决方案**:
1. 验证API密钥
2. 确认图片URL可访问
3. 查看服务日志获取详细错误信息

## 技术支持

如有问题或建议，请通过以下方式联系：

- GitHub Issues: https://github.com/yourusername/paizhaojieti_stdio_mcp/issues
- Email: your.email@example.com

---

**配置版本**: 1.0.0  
**最后更新**: 2026-01-09  
**状态**: ✅ 可用于ModelScope MCP广场发布，支持个人阿里云函数计算资源部署