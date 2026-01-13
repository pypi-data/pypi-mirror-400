#!/usr/bin/env python3
"""
gyy-mcp: 基于FastMCP开发的自定义MCP工具
这是一个简单的示例工具，展示了如何创建和使用FastMCP
"""

import os
import base64
import requests
from pathlib import Path
from fastmcp import FastMCP

# 创建 FastMCP 实例
mcp = FastMCP(name="gyy-mcp", version="1.1.1")

# 配置参数 - 从环境变量读取
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-vl:8b")


# 注册工具：info - 显示工具信息
@mcp.tool()
def info() -> str:
    """Show tool information"""
    return "📋 gyy-mcp Tool Information:\n  Name: gyy-mcp\n  Version: 1.0.0\n  Description: A simple FastMCP-based tool"


# 注册工具：recognize_image - 使用Ollama识别图片内容
@mcp.tool()
def recognize_image(image_path: str, prompt: str = "") -> str:
    """使用Ollama的qwen3-vl:8b模型识别图片内容，返回转换后的文字供编辑器AI使用
    
    Args:
        image_path: 图片文件路径或URL
        prompt: 自定义提示词，默认为通用识别提示词
    
    Returns:
        识别结果文字
    """
    try:
        # 验证文件路径
        if image_path.startswith(("http://", "https://")):
            # 如果是URL，直接使用
            image_data = image_path
        else:
            # 本地文件路径
            path = Path(image_path)
            if not path.exists():
                return f"❌ 错误：图片文件不存在 - {image_path}"
            
            if not path.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
                return f"❌ 错误：不支持的图片格式 - {path.suffix}"
            
            # 读取本地图片并转换为base64
            with open(path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 设置默认提示词
        if not prompt:
            prompt = "请详细描述这张图片中的内容\n1. 图片的主要主题和对象\n2. 文本内容（如果有）\n3. 颜色和视觉元素\n4. 任何重要的细节或信息\n请以清晰、结构化的方式组织您的描述。"
        
        # 调用Ollama API
        api_url = f"{OLLAMA_API_URL}/api/generate"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "images": [image_data] if isinstance(image_data, str) and not image_data.startswith(("http://", "https://")) else [],
            "stream": False
        }
        
        # 如果是URL，使用不同的请求方式
        if image_path.startswith(("http://", "https://")):
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "images": [image_path],
                "stream": False
            }
        
        response = requests.post(api_url, json=payload, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        if "response" in result:
            return f"✅ 图片识别结果：\n\n{result['response']}"
        else:
            return f"❌ 错误：无效的API响应 - {result}"
    
    except requests.exceptions.ConnectionError:
        return f"❌ 错误：无法连接到Ollama服务器 ({OLLAMA_API_URL})。请确保Ollama已启动。"
    except requests.exceptions.Timeout:
        return "❌ 错误：请求超时。图片识别耗时过长，请稍后重试。"
    except requests.exceptions.RequestException as e:
        return f"❌ 错误：API请求失败 - {str(e)}"
    except Exception as e:
        return f"❌ 错误：处理失败 - {str(e)}"


# 注册工具：set_ai_config - 配置AI服务
@mcp.tool()
def set_ai_config(api_url: str = "", model: str = "") -> str:
    """配置Ollama AI服务的地址和模型
    
    Args:
        api_url: Ollama API地址，例如 http://localhost:11434
        model: 使用的模型名称，例如 qwen3-vl:8b
    
    Returns:
        配置结果信息
    """
    global OLLAMA_API_URL, OLLAMA_MODEL
    
    try:
        result_msg = ""
        
        if api_url:
            OLLAMA_API_URL = api_url
            os.environ["OLLAMA_API_URL"] = api_url
            result_msg += f"✅ API地址已设置为: {api_url}\n"
        
        if model:
            OLLAMA_MODEL = model
            os.environ["OLLAMA_MODEL"] = model
            result_msg += f"✅ 模型已设置为: {model}\n"
        
        result_msg += f"\n📋 当前配置:\n  API地址: {OLLAMA_API_URL}\n  模型: {OLLAMA_MODEL}"
        
        return result_msg
    
    except Exception as e:
        return f"❌ 错误：配置失败 - {str(e)}"


# 注册工具：get_ai_config - 获取AI服务配置
@mcp.tool()
def get_ai_config() -> str:
    """获取当前Ollama AI服务的配置信息
    
    Returns:
        当前配置信息
    """
    return f"""📋 当前AI服务配置:
  API地址: {OLLAMA_API_URL}
  模型: {OLLAMA_MODEL}
  
💡 提示：
  - 可通过环境变量设置：OLLAMA_API_URL 和 OLLAMA_MODEL
  - 或使用 set_ai_config 工具动态配置
  - 默认值：http://localhost:11434 和 qwen3-vl:8b"""


if __name__ == "__main__":
    # 启动 MCP 服务器
    mcp.run()


def main():
    """MCP entry point for uvx"""
    mcp.run()
