"""
Claude API proxy server - Anthropic Messages API 兼容接口
实现标准的 Anthropic Messages API，可用于 Claude Code 和 Anthropic SDK
复用 __main__.py 中的认证逻辑
"""

import os
import sys
import argparse
import json
import time
import uuid
import traceback
import requests
from typing import Optional, List, Dict, Any, Union, AsyncGenerator, Literal
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import StreamingResponse, JSONResponse
from loguru import logger
from pydantic import BaseModel, Field

# 从 __main__ 模块导入复用的函数
from hexin_server.__main__ import (
    get_userid_and_token,
    api_request,
)

# Global variables for authentication
USER_ID: Optional[str] = None
TOKEN: Optional[str] = None

# Fixed API key for client authentication (Anthropic format)
FIXED_API_KEY = "sk-fastapi-proxy-key-12345"


# Anthropic Messages API Models
class ContentBlock(BaseModel):
    type: Literal["text", "image"] = "text"
    text: Optional[str] = None
    source: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, List[Dict[str, Any]]]


class MessagesRequest(BaseModel):
    """Anthropic Messages API request format"""
    model: str
    messages: List[Message]
    max_tokens: int = Field(default=4096, ge=1)
    system: Optional[Union[str, List[Dict[str, Any]]]] = None  # Can be string or content blocks
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=None, ge=0)
    stream: Optional[bool] = False
    stop_sequences: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class Usage(BaseModel):
    """Token usage statistics"""
    input_tokens: int
    output_tokens: int
    # Bedrock 缓存相关字段（可选）
    cache_creation_input_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None


class MessagesResponse(BaseModel):
    """Anthropic Messages API response format"""
    id: str
    type: Literal["message"] = "message"
    role: Literal["assistant"] = "assistant"
    content: List[Dict[str, Any]]
    model: str
    stop_reason: Optional[str] = None
    stop_sequence: Optional[str] = None
    usage: Usage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize authentication on startup"""
    global USER_ID, TOKEN

    app_url = os.getenv("HITHINK_APP_URL")
    app_id = os.getenv("HITHINK_APP_ID")
    app_secret = os.getenv("HITHINK_APP_SECRET")

    if not app_id or not app_secret:
        raise ValueError("HITHINK_APP_ID and HITHINK_APP_SECRET must be set in environment variables.")

    try:
        USER_ID, TOKEN = get_userid_and_token(app_url=app_url, app_id=app_id, app_secret=app_secret)
        logger.info(f"Claude Messages API proxy authentication successful. User ID: {USER_ID}")
    except Exception as e:
        logger.error(f"Failed to authenticate: {e}")
        raise

    yield

    # Cleanup
    logger.info("Shutting down Claude Messages API proxy server")


app = FastAPI(
    title="Claude Messages API Proxy",
    description="Anthropic Messages API compatible proxy server using hexin_engine backend",
    version="1.0.0",
    lifespan=lifespan
)


def verify_api_key(x_api_key: Optional[str] = None, authorization: Optional[str] = None):
    """Verify API key from x-api-key or Authorization header"""
    logger.info(f"Received x-api-key: {x_api_key}")
    logger.info(f"Received authorization: {authorization}")
    logger.info(f"Expected API key: {FIXED_API_KEY}")

    # Try x-api-key first
    api_key = x_api_key

    # If no x-api-key, try Authorization Bearer
    if not api_key and authorization:
        if authorization.startswith("Bearer "):
            api_key = authorization[7:]  # Remove "Bearer " prefix
            logger.info(f"Extracted API key from Authorization header: {api_key}")

    if not api_key:
        logger.error("No API key found in x-api-key or Authorization header")
        raise HTTPException(
            status_code=401,
            detail={"type": "error", "error": {"type": "authentication_error", "message": "API key required (use x-api-key header or Authorization: Bearer)"}}
        )

    if api_key != FIXED_API_KEY:
        logger.error(f"Invalid API key. Received: {api_key}, Expected: {FIXED_API_KEY}")
        raise HTTPException(
            status_code=401,
            detail={"type": "error", "error": {"type": "authentication_error", "message": "invalid API key"}}
        )

    logger.info("API key verification successful")
    return api_key


def convert_anthropic_to_hexin_format(
    messages: List[Message],
    system: Optional[Union[str, List[Dict[str, Any]]]] = None,
) -> tuple[List[Dict[str, Any]], Optional[str]]:
    """将 Anthropic Messages 格式转换为 hexin 后端格式

    Returns:
        (hexin_messages, system_message): 消息列表和系统消息
    """
    hexin_messages = []

    # 处理 system - 可能是字符串或内容块数组
    system_text = None
    if system:
        if isinstance(system, str):
            system_text = system
        elif isinstance(system, list):
            # 从内容块中提取文本
            text_parts = []
            for block in system:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            system_text = "\n".join(text_parts) if text_parts else None

    # 转换消息
    for msg in messages:
        content = msg.content

        # 如果 content 是列表，提取 text 内容
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = "\n".join(text_parts)

        # 跳过空消息（Bedrock 不允许空的 assistant 消息）
        if not content or (isinstance(content, str) and content.strip() == ""):
            continue

        hexin_messages.append({
            "role": msg.role,
            "content": content
        })

    return hexin_messages, system_text


def convert_hexin_to_anthropic_format(
    hexin_response: Dict[str, Any],
    request_model: str,
) -> MessagesResponse:
    """将 hexin 后端响应转换为 Anthropic Messages 格式"""

    # 从 data 中提取响应
    if "data" in hexin_response:
        hexin_response = hexin_response["data"]

    # 提取内容
    content = hexin_response.get("content", [])
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    elif isinstance(content, list) and len(content) > 0:
        # 确保格式正确
        formatted_content = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                formatted_content.append(item)
            elif isinstance(item, str):
                formatted_content.append({"type": "text", "text": item})
        content = formatted_content if formatted_content else content

    # 提取 usage 信息
    usage_data = hexin_response.get("usage", {})
    if not usage_data and "input_tokens" in hexin_response:
        usage_data = {
            "input_tokens": hexin_response.get("input_tokens", 0),
            "output_tokens": hexin_response.get("output_tokens", 0)
        }

    # Bedrock 返回的 usage 结构可能包含缓存相关字段
    usage_params = {
        "input_tokens": usage_data.get("input_tokens", 0),
        "output_tokens": usage_data.get("output_tokens", 0)
    }

    # 添加缓存相关字段（如果存在）
    if "cache_creation_input_tokens" in usage_data:
        usage_params["cache_creation_input_tokens"] = usage_data["cache_creation_input_tokens"]
    if "cache_read_input_tokens" in usage_data:
        usage_params["cache_read_input_tokens"] = usage_data["cache_read_input_tokens"]

    usage = Usage(**usage_params)

    # 构造 Anthropic 响应
    response = MessagesResponse(
        id=hexin_response.get("id", f"msg_{uuid.uuid4().hex}"),
        type="message",
        role="assistant",
        content=content,
        model=hexin_response.get("model", request_model),
        stop_reason=hexin_response.get("stop_reason", "end_turn"),
        stop_sequence=hexin_response.get("stop_sequence"),
        usage=usage
    )

    return response


async def create_message_stream(
    hexin_response: Dict[str, Any],
    request_model: str,
) -> AsyncGenerator[str, None]:
    """创建 Anthropic Messages API 流式响应"""

    # Convert to Anthropic format
    message = convert_hexin_to_anthropic_format(hexin_response, request_model)

    # Send message_start event
    yield f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': message.model_dump()})}\n\n"

    # Send content_block_start for each content block
    for i, content_block in enumerate(message.content):
        yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': i, 'content_block': content_block})}\n\n"

        # Send content_block_delta with text
        if content_block.get("type") == "text" and content_block.get("text"):
            text = content_block["text"]
            yield f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': i, 'delta': {'type': 'text_delta', 'text': text}})}\n\n"

        # Send content_block_stop
        yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': i})}\n\n"

    # Send message_delta with usage
    yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': message.stop_reason, 'stop_sequence': message.stop_sequence}, 'usage': {'output_tokens': message.usage.output_tokens}})}\n\n"

    # Send message_stop
    yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"


@app.post("/v1/messages")
async def create_message(
    request: MessagesRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    request_obj: Request = None
):
    """Create a message using Anthropic Messages API format"""
    # Log all headers for debugging
    if request_obj:
        logger.info(f"All headers: {dict(request_obj.headers)}")

    # Verify API key (supports both x-api-key and Authorization: Bearer)
    verify_api_key(x_api_key, authorization)

    global USER_ID, TOKEN

    if not USER_ID or not TOKEN:
        raise HTTPException(
            status_code=500,
            detail={"type": "error", "error": {"type": "api_error", "message": "Server authentication not initialized"}}
        )

    # Extract parameters
    model = request.model
    max_tokens = request.max_tokens
    temperature = request.temperature
    top_p = request.top_p
    stream = request.stream

    request_id = f"msg_{uuid.uuid4().hex}"

    try:
        # 转换消息格式
        hexin_messages, system_prompt = convert_anthropic_to_hexin_format(
            messages=request.messages,
            system=request.system
        )

        # Map Claude model names to backend model IDs
        # Backend supports these models:
        # - us.anthropic.claude-3-5-sonnet-20241022-v2:0
        # - us.anthropic.claude-3-7-sonnet-20250219-v1:0
        # - us.anthropic.claude-sonnet-4-20250514-v1:0
        # - us.anthropic.claude-opus-4-20250514-v1:0
        # - us.anthropic.claude-sonnet-4-5-20250929-v1:0
        # - global.anthropic.claude-opus-4-5-20251101-v1:0

        # If model already has the full prefix, use it directly
        if model.startswith("us.anthropic.") or model.startswith("global.anthropic."):
            backend_model = model
            # Ensure it has the version suffix
            if not backend_model.endswith(":0"):
                backend_model += ":0"
        else:
            # Map common model names to backend models
            backend_model = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"  # Default

            if "4.5" in model or "4-5" in model:
                # Claude 4.5 series
                if "opus" in model.lower():
                    backend_model = "global.anthropic.claude-opus-4-5-20251101-v1:0"
                elif "sonnet" in model.lower():
                    backend_model = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
                elif "haiku" in model.lower():
                    backend_model = "us.anthropic.claude-sonnet-4-20250514-v1:0"
                else:
                    backend_model = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
            elif "4" in model and ("opus" in model.lower() or "sonnet" in model.lower()):
                # Claude 4 series
                if "opus" in model.lower():
                    backend_model = "us.anthropic.claude-opus-4-20250514-v1:0"
                else:
                    backend_model = "us.anthropic.claude-sonnet-4-20250514-v1:0"
            elif "3.7" in model or "3-7" in model:
                # Claude 3.7 series
                backend_model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
            elif "3.5" in model or "3-5" in model or model.startswith("claude-3-5"):
                # Claude 3.5 series
                backend_model = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

        # Set appropriate max_tokens limit based on model
        if "3-5-sonnet" in backend_model or "3.5" in model:
            # Claude 3.5 Sonnet has max 8192 tokens
            if max_tokens > 8192:
                max_tokens = 8192
        elif max_tokens > 32000:
            # Other models have higher limits
            max_tokens = 32000

        # 准备请求参数 (Amazon Bedrock 格式)
        params = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": hexin_messages,
        }

        # 添加可选参数
        # 注意：Bedrock Claude 不允许同时指定 temperature 和 top_p
        # 优先使用 temperature，如果没有则使用 top_p
        if temperature is not None:
            params["temperature"] = temperature
        elif top_p is not None:
            params["top_p"] = top_p

        # 注意：后端 Bedrock API 不支持 system 参数
        # 如果有 system prompt，我们将其合并到第一条用户消息中
        if system_prompt and hexin_messages:
            # 找到第一条用户消息
            for msg in hexin_messages:
                if msg["role"] == "user":
                    msg["content"] = f"[System Instruction: {system_prompt}]\n\n{msg['content']}"
                    break

        if request.stop_sequences:
            params["stop_sequences"] = request.stop_sequences

        # API URL (Bedrock 格式：model ID 在 URL 中)
        chat_url = f"https://arsenal-openai.10jqka.com.cn:8443/vtuber/ai_access/claude/model/{backend_model}/invoke"

        # Headers (Bedrock 使用 token 或 Authorization)
        headers = {
            "Content-Type": "application/json",
            "token": TOKEN
        }

        logger.info(f"Claude Messages API request ID: {request_id}\nModel: {model}\nMessages: {len(hexin_messages)}")
        logger.debug(f"Request params: {json.dumps(params, ensure_ascii=False, indent=2)}")

        # 发送请求
        res = api_request(
            url=chat_url,
            params=params,
            headers=headers,
            timeout=600,
        )

        # 处理响应
        hexin_response = res.json()
        logger.debug(f"Hexin response: {json.dumps(hexin_response, ensure_ascii=False, indent=2)}")

        if stream:
            # 返回流式响应
            return StreamingResponse(
                create_message_stream(hexin_response, model),
                media_type="text/event-stream"
            )
        else:
            # 返回标准响应
            anthropic_response = convert_hexin_to_anthropic_format(hexin_response, model)
            return JSONResponse(content=anthropic_response.model_dump())
    except Exception as e:
        logger.error(f"Error in create message: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"type": "error", "error": {"type": "api_error", "message": str(e)}}
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "authenticated": USER_ID is not None and TOKEN is not None,
        "service": "claude-messages-api-proxy"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Claude Messages API Proxy Server",
        "version": "1.0.0",
        "api_version": "anthropic-2023-06-01",
        "endpoints": [
            "/v1/messages",
            "/health"
        ]
    }


def main():
    """Main entry point for the claude proxy server"""
    parser = argparse.ArgumentParser(
        description="Run the Claude Messages API proxy server",
        prog="python -m hexin_server.claude"
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8778, help="Port to bind to (default: 8778)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", type=str, default="info", choices=["debug", "info", "warning", "error"], help="Log level (default: info)")
    parser.add_argument("--env-file", type=str, default=".env", help="Path to environment file (default: .env)")

    args = parser.parse_args()

    print(f"Loading environment variables from {args.env_file}")
    load_dotenv(args.env_file)
    print(f"Starting Claude Messages API Proxy Server on {args.host}:{args.port}")
    print(f"Log level: {args.log_level}")
    if args.reload:
        print("Auto-reload enabled")

    print(f"\nClaude Messages API Configuration:")
    print(f"BASE_URL = \"http://{args.host}:{args.port}\"")
    print(f"API_KEY = \"{FIXED_API_KEY}\"")
    print(f"API Version: anthropic-2023-06-01")

    try:
        uvicorn.run(
            "hexin_server.claude:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
        )
    except KeyboardInterrupt:
        print("\nClaude Messages API proxy server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Claude Messages API proxy server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
