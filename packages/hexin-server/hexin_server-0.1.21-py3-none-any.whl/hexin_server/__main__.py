"""
FastAPI server that proxies OpenAI API endpoints using the hexin_engine backend.
"""
import copy
import json
import os
from pathlib import Path
import re
import sys
import time
import traceback
import uuid
import httpx
import httpx_sse
import requests
import argparse
from typing_extensions import List, Optional, Dict, Any, Union, AsyncGenerator, Literal
from contextlib import asynccontextmanager
from urllib.parse import urlencode

import uvicorn
from requests import Response
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import StreamingResponse, JSONResponse
from loguru import logger
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk, Choice as ChunkChoice, ChoiceDelta, ChoiceDeltaToolCall, ChoiceDeltaFunctionCall, ChoiceDeltaToolCallFunction
from openai.types.completion_usage import CompletionUsage
from openai.types.model import Model
from openai.types.create_embedding_response import CreateEmbeddingResponse, Embedding, Usage
from pydantic import BaseModel, Field

from xlin import xmap_async

TIMEOUT = 600


def get_userid_and_token(
    app_url,
    app_id,
    app_secret,
):
    d = {"app_id": app_id, "app_secret": app_secret}
    h = {"Content-Type": "application/json"}
    r = requests.post(app_url, json=d, headers=h)
    data = r.json()
    if "data" not in data:
        raise ValueError(f"Authentication failed: {data}")
    data = data["data"]
    return data["user_id"], data["token"]


def retry_request(func):
    def wrapper(*args, **kwargs):
        max_retry = kwargs.get("max_retry", 3)
        debug = kwargs.get("debug", False)
        for i in range(max_retry):
            try:
                result = func(*args, **kwargs)
                if not result:
                    if debug:
                        logger.error(f"Function {func.__name__} returned None, retrying {i + 1}/{max_retry}...")
                    continue
                # logger.debug(f"Function {func.__name__} succeeded on attempt {i + 1}.")
                return result
            except Exception as e:
                if debug:
                    logger.error(f"Request failed: {e}, retrying {i + 1}/{max_retry}...")
        if debug:
            logger.error("Max retries reached, returning None.")
        return None

    return wrapper


def api_request(
    url: str,
    params: dict,
    headers: dict,
    timeout: int = 100,
):
    res = requests.post(
        url,
        json=params,
        headers=headers,
        timeout=timeout,
    )
    return res


def prepare_api_request_params(
    user_id: str,
    token: str,
    messages: List[Dict[str, Any]],
    model: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    n: int,
    stream: bool = False,
    multi_modal: bool = False,
    tools: Optional[List[Dict[str, Any]]] = None,
    functions: Optional[List[Dict[str, Any]]] = None,
    function_call: Optional[Union[str, Dict[str, Any]]] = None,
    reasoning_effort: Optional[str] = None,
    thinking: Optional[Dict[str, Any]] = None,
) -> tuple[str, dict, dict, int]:
    """Prepare parameters for api_request based on model type"""

    # Base parameters
    params = {
        "messages": messages,
        "temperature": temperature,
        "model": model,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "n": n,
        "stream": stream,
    }

    if tools:
        params["tools"] = tools
    if functions:
        params["functions"] = functions
    if function_call:
        params["function_call"] = function_call
    if reasoning_effort:
        params["reasoning_effort"] = reasoning_effort
    if thinking:
        params["thinking"] = thinking

    rollout_n = None
    version = "v3"

    # Model-specific handling (copied from hexin_engine.py)
    if model == "claude" or model.startswith("claude-"):
        symbol = "claude"
        # Map Claude model names to backend model IDs
        # Backend supports these models:
        # - us.anthropic.claude-3-5-sonnet-20241022-v2:0
        # - us.anthropic.claude-3-7-sonnet-20250219-v1:0
        # - us.anthropic.claude-sonnet-4-20250514-v1:0
        # - us.anthropic.claude-opus-4-20250514-v1:0
        # - us.anthropic.claude-sonnet-4-5-20250929-v1:0
        # - global.anthropic.claude-opus-4-5-20251101-v1:0
        if "4.5" in model or "4-5" in model:
            # Claude 4.5 series
            if "opus" in model.lower():
                params["model"] = "global.anthropic.claude-opus-4-5-20251101-v1:0"
            elif "sonnet" in model.lower():
                params["model"] = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
            elif "haiku" in model.lower():
                params["model"] = "us.anthropic.claude-sonnet-4-20250514-v1:0"
            else:
                params["model"] = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        elif "4" in model and ("opus" in model.lower() or "sonnet" in model.lower()):
            # Claude 4 series
            if "opus" in model.lower():
                params["model"] = "us.anthropic.claude-opus-4-20250514-v1:0"
            else:
                params["model"] = "us.anthropic.claude-sonnet-4-20250514-v1:0"
        elif "3.7" in model or "3-7" in model:
            # Claude 3.7 series
            params["model"] = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        elif "3.5" in model or "3-5" in model:
            # Claude 3.5 series
            params["model"] = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        else:
            # Default to latest sonnet
            params["model"] = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

        # Bedrock API 使用 bedrock-2023-05-31 而不是 vertex-2023-10-16
        params["anthropic_version"] = "bedrock-2023-05-31"

        # Bedrock 不允许同时指定 temperature 和 top_p
        # 优先使用 temperature，如果没有则使用 top_p
        if temperature is not None and top_p is not None and top_p != 1.0:
            # 如果两者都指定了，删除 top_p
            params.pop("top_p", None)

        version = "v3"
        rollout_n = params.pop("n", None)
    elif "doubao" in model or model in [
        "ep-20250204210426-gclbn",
        "ep-20250410151344-fzm9z",
        "ep-20250410145517-rpbrz",
        "deepseek-reasoner",
        "deepseek-chat",
    ] or model.startswith("ep-"):
        symbol = "doubao"
        version = "v3"
        if "r1" in model or "reasoner" in model:
            params["model"] = "ep-20250410145517-rpbrz"
            rollout_n = params.pop("n", None)
        elif "v3" in model or "chat" in model:
            params["model"] = "ep-20250410151344-fzm9z"
    elif model == "r1-qianfan":
        symbol = "qianfan"
        params["model"] = "deepseek-r1"
        rollout_n = params.pop("n", None)
    elif model == "gemini":
        symbol = "gemini"
        params["model"] = "gemini-2.5-pro-preview-03-25"
    elif "qwen" in model:
        symbol = "qianwen"
        version = "v1"
    elif model in ["gpt-4o-mini", "o3", "o4-mini"] or model.startswith("gpt-") or re.match(r"^o[34](\-mini)?$", model):
        del params["max_tokens"]
        params["max_completion_tokens"] = max_tokens
        symbol = "chatgpt"
        if model in ["o3", "o4-mini"] or re.match(r"^o[34](\-mini)?$", model):
            del params["temperature"]
    else:
        symbol = "chatgpt"

    # Build URL
    if multi_modal:
        chat_url = "https://arsenal-openai.10jqka.com.cn:8443/vtuber/ai_access/chatgpt/v1/picture/chat/completions"
    elif symbol == "claude":
        # Claude 使用 Bedrock API 格式
        backend_model = params["model"]
        chat_url = f"https://arsenal-openai.10jqka.com.cn:8443/vtuber/ai_access/claude/model/{backend_model}/invoke"
    else:
        chat_url = f"https://arsenal-openai.10jqka.com.cn:8443/vtuber/ai_access/{symbol}/{version}/chat/completions"

    # Build headers
    headers = {"Content-Type": "application/json", "userId": user_id, "token": token}

    return chat_url, params, headers, rollout_n


def process_api_response(res: Response, url: str, model: str, debug: bool, rollout_n: Optional[int] = None):
    resp = res.json()
    if not rollout_n:
        rollout_n = 1
    if "data" in resp:
        resp = resp["data"]
    if debug or "choices" not in resp:
        logger.debug(f"API request to {repr(url)} returned: {json.dumps(resp, ensure_ascii=False, indent=2)}")
    if rollout_n is not None:
        if model == "claude" and "content" in resp:
            if isinstance(resp["content"], list) and len(resp["content"]) == 1 and resp["content"][0].get("type") == "text":
                resp["content"] = resp["content"][0]["text"]

            # 处理 Bedrock 返回的 usage 信息
            usage_data = resp.get("usage", {})
            input_tokens = usage_data.get("input_tokens", 0)
            output_tokens = usage_data.get("output_tokens", 0)

            # Bedrock 可能包含缓存相关的 tokens
            cache_creation_tokens = usage_data.get("cache_creation_input_tokens", 0)
            cache_read_tokens = usage_data.get("cache_read_input_tokens", 0)

            # 总 input tokens = 常规 input + 缓存创建 + 缓存读取
            total_input = input_tokens + cache_creation_tokens + cache_read_tokens

            resp = ChatCompletion(
                id=resp["id"],
                choices=[
                    Choice(
                        index=0,
                        message=ChatCompletionMessage(
                            role=resp["role"],
                            content=resp["content"]
                        ),
                        finish_reason=resp.get("stop_reason") if resp.get("stop_reason") in ["stop", "length", "tool_calls", "content_filter", "function_call"] else "stop",
                        logprobs=resp.get("logprobs"),
                    )
                ],
                created=int(time.time()),
                model=resp["model"],
                object="chat.completion",
                usage= CompletionUsage(
                    prompt_tokens=total_input,
                    completion_tokens=output_tokens,
                    total_tokens=total_input + output_tokens,
                )
            ).model_dump()
    choices: list = resp.get("choices", [])
    if debug:
        logger.debug(f"API request to {repr(url)} returned choices: {json.dumps(choices, ensure_ascii=False, indent=2)}")

    for i in range(min(rollout_n, len(choices))):
        item = choices[i]
        if "message" in item:
            message = item["message"]
            content = message.get("content", "")
            reasoning_content = message.get("reasoning_content", "")

            # Handle reasoning content
            if reasoning_content:
                content = f"<think>\n{reasoning_content}\n</think>\n{content}"

            message["content"] = content
        elif "text" in item:
            content = item["text"]
            item["message"] = {
                "role": "assistant",
                "content": content,
            }

    # Fill remaining slots with None if needed
    if len(choices) < rollout_n:
        choices += [None] * (rollout_n - len(choices))

    resp["choices"] = choices
    logger.debug(f"Processed API response: {json.dumps(resp, ensure_ascii=False, indent=2)}")
    return resp


def prepare_embedding_request_params(
    user_id: str,
    token: str,
    input_text: Union[str, List[str]],
    model: str,
) -> tuple[str, dict, dict, dict]:
    """Prepare parameters for embedding API request"""
    # Prepare request parameters - try different parameter formats for hexin API
    # Let's try various formats that the API might expect
    params = {
        "input": input_text,  # Original format
        "model": model,
    }

    embedding_url = "https://arsenal-openai.10jqka.com.cn:8443/vtuber/ai_access/chatgpt/v1/embeddings"

    # Build headers
    headers = {
        # "Content-Type": "application/json",
        'Content-Type': 'application/x-www-form-urlencoded',
        "userId": user_id,
        "token": token
    }

    return embedding_url, params, headers

def print_embedding_info(response: CreateEmbeddingResponse) -> None:
    """打印embedding响应信息"""
    print(f"- Object: {response.object}")
    print(f"- Model: {response.model}")
    print(f"- Data count: {len(response.data)}")

    if response.data:
        for first in response.data:
            print(f"- embedding: {first.object}, index={first.index}, vector_length={len(first.embedding)}")
            print(f"- few values: {first.embedding[:5]}")

    if response.usage:
        print(f"- Usage: prompt_tokens={response.usage.prompt_tokens}, total_tokens={response.usage.total_tokens}")

def process_embedding_response(res: Response, debug: bool = False) -> Optional[Dict[str, Any]]:
    """Process embedding API response"""
    try:
        resp = res.json()

        # if debug:

            # logger.debug(f"Embedding API response: {json.dumps(resp, ensure_ascii=False, indent=2)}")

        # Extract data from hexin response format
        # Try different possible response structures
        if "data" in resp:
            data = resp["data"]
            # Case 1: {"data": {"data": [...], "usage": {...}}}
            if "data" in data:
                return data
            # Case 2: {"data": [...]} where data is directly the embeddings array
            elif isinstance(data, list):
                return {"data": data}
            # Case 3: {"data": {...}} where data contains the complete response
            else:
                return data

        # Case 4: Direct response format without "data" wrapper
        elif "embeddings" in resp or ("object" in resp and resp.get("object") == "list"):
            return resp

        if debug:
            logger.warning(f"Unexpected embedding response format: {resp}")
        return None

    except Exception as e:
        if debug:
            logger.error(f"Error processing embedding response: {e}")
        return None


def create_embedding_response(
    embedding_data: Dict[str, Any],
    model: str,
    input_text: Union[str, List[str]],
) -> CreateEmbeddingResponse:
    """Create OpenAI-compatible embedding response"""

    # Convert input to list for consistent processing
    if isinstance(input_text, str):
        input_list = [input_text]
    else:
        input_list = input_text

    # Extract embeddings from response data
    embeddings_list = []
    if "data" in embedding_data:
        for item in embedding_data["data"]:
            embedding = Embedding(
                object="embedding",
                index=item.get("index", 0),
                embedding=item.get("embedding", [])
            )
            embeddings_list.append(embedding)

    # Create usage information
    usage_data = embedding_data.get("usage", {})
    usage = Usage(
        prompt_tokens=usage_data.get("prompt_tokens", len(" ".join(input_list))),
        total_tokens=usage_data.get("total_tokens", len(" ".join(input_list)))
    )

    return CreateEmbeddingResponse(
        object="list",
        data=embeddings_list,
        model=model,
        usage=usage
    )


def prepare_response_request_params(
    user_id: str,
    token: str,
    model: str,
    input_data: Union[str, List[Dict[str, Any]]],
    reasoning: Optional[Dict[str, Any]] = None,
    text: Optional[Dict[str, Any]] = None,
    instructions: Optional[str] = None,
    max_output_tokens: Optional[int] = None,
    temperature: Optional[float] = 1.0,
    top_p: Optional[float] = 1.0,
    stream: bool = False,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[str] = "auto",
    parallel_tool_calls: Optional[bool] = True,
    store: Optional[bool] = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> tuple[str, dict, dict]:
    """Prepare parameters for responses API request"""

    # Base parameters according to OpenAI responses API spec
    params = {
        "model": model,
        "input": input_data,
    }

    # Add optional parameters
    if reasoning:
        params["reasoning"] = reasoning
    if text:
        params["text"] = text
    if instructions:
        params["instructions"] = instructions
    if max_output_tokens:
        params["max_output_tokens"] = max_output_tokens
    if temperature != 1.0:
        params["temperature"] = temperature
    if top_p != 1.0:
        params["top_p"] = top_p
    if stream:
        params["stream"] = stream
    if tools:
        params["tools"] = tools
    if tool_choice != "auto":
        params["tool_choice"] = tool_choice
    if parallel_tool_calls is not None:
        params["parallel_tool_calls"] = parallel_tool_calls
    if store is not None:
        params["store"] = store
    if metadata:
        params["metadata"] = metadata

    # Build URL - according to the documentation
    response_url = "https://arsenal-openai.10jqka.com.cn:8443/vtuber/ai_access/chatgpt/v1/responses"

    # Build headers
    headers = {
        "Content-Type": "application/json",
        "userId": user_id,
        "token": token
    }

    return response_url, params, headers


def process_response_api_response(res: Response, debug: bool = False) -> Optional[Dict[str, Any]]:
    """Process responses API response"""
    try:
        resp = res.json()

        if debug:
            logger.debug(f"Responses API response: {json.dumps(resp, ensure_ascii=False, indent=2)}")

        # 检查是否返回了错误状态
        if "success" in resp and resp["success"] is False:
            error_msg = resp.get("status_msg", "Unknown error")
            error_code = resp.get("status_code", -1)
            logger.error(f"Backend API returned error (code: {error_code}): {error_msg}")
            raise ValueError(f"后端API错误 (代码: {error_code}): {error_msg}")

        # Extract data from hexin response format
        if "data" in resp:
            return resp["data"]
        else:
            return resp

    except Exception as e:
        if debug:
            logger.error(f"Error processing responses API response: {e}")
        return None


async def create_response_stream(
    response_data: Dict[str, Any],
    request_id: str,
) -> AsyncGenerator[str, None]:
    """Create streaming response for responses API"""

    # For streaming responses, we need to follow the SSE format from the documentation
    # The actual streaming would come from the backend API
    # This is a simplified version that yields the complete response as chunks

    # Send response.created event
    created_event = {
        "type": "response.created",
        "response": {
            "id": response_data.get("id", request_id),
            "object": "response",
            "created_at": response_data.get("created_at", int(time.time())),
            "status": "in_progress",
            "model": response_data.get("model"),
            "output": []
        }
    }
    yield f"event: response.created\ndata: {json.dumps(created_event)}\nretry: 300\n\n"

    # Send response.in_progress event
    progress_event = {
        "type": "response.in_progress",
        "response": created_event["response"]
    }
    yield f"event: response.in_progress\ndata: {json.dumps(progress_event)}\nretry: 300\n\n"

    # Process output items
    output_items = response_data.get("output", [])
    for i, item in enumerate(output_items):
        # Send output_item.added event
        added_event = {
            "type": "response.output_item.added",
            "output_index": i,
            "item": {
                "id": item.get("id"),
                "type": item.get("type"),
                "summary": item.get("summary", []) if item.get("type") == "reasoning" else None
            }
        }
        if added_event["item"]["summary"] is None:
            del added_event["item"]["summary"]
        yield f"event: response.output_item.added\ndata: {json.dumps(added_event)}\nretry: 300\n\n"

        # For reasoning items, send summary parts
        if item.get("type") == "reasoning" and "summary" in item:
            for j, summary_part in enumerate(item["summary"]):
                summary_event = {
                    "type": "response.reasoning_summary_part.added",
                    "item_id": item.get("id"),
                    "output_index": i,
                    "summary_index": j,
                    "part": summary_part
                }
                yield f"event: response.reasoning_summary_part.added\ndata: {json.dumps(summary_event)}\nretry: 300\n\n"

        # Send output_item.done event
        done_event = {
            "type": "response.output_item.done",
            "output_index": i,
            "item": item
        }
        yield f"event: response.output_item.done\ndata: {json.dumps(done_event)}\nretry: 300\n\n"

    # Send final completed event
    completed_event = {
        "type": "response.completed",
        "response": response_data
    }
    yield f"event: response.completed\ndata: {json.dumps(completed_event)}\nretry: 300\n\n"


# Global variables for authentication
USER_ID: Optional[str] = None
TOKEN: Optional[str] = None

# Fixed API key for client authentication
FIXED_API_KEY = "sk-fastapi-proxy-key-12345"


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
        logger.info(f"Authentication successful. User ID: {USER_ID}")
    except Exception as e:
        logger.error(f"Failed to authenticate: {e}")
        raise

    yield

    # Cleanup (if needed)
    logger.info("Shutting down FastAPI server")


app = FastAPI(
    title="OpenAI API Proxy",
    description="A FastAPI server that proxies OpenAI API endpoints using hexin_engine backend",
    version="1.0.0",
    lifespan=lifespan
)


def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verify API key from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <api_key>'")

    api_key = authorization[7:]  # Remove "Bearer " prefix
    if api_key != FIXED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key


# Pydantic models for request/response
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 0.6
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Union[str, Dict[str, Any]]] = None
    reasoning_effort: Optional[str] = None  # 支持 "low", "medium", "high"
    debug: Optional[bool] = True


class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: Optional[str] = "text-embedding-ada-002"
    user: Optional[str] = None
    debug: Optional[bool] = True


class ReasoningConfig(BaseModel):
    effort: Optional[str] = "medium"  # "low", "medium", "high"
    summary: Optional[str] = "detailed"  # "brief", "detailed"


class ResponseRequest(BaseModel):
    model: str
    input: Union[str, List[Dict[str, Any]]]  # Can be string or messages array
    reasoning: Optional[ReasoningConfig] = None
    text: Optional[Dict[str, Any]] = None
    instructions: Optional[str] = None
    max_output_tokens: Optional[int] = None
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    stream: Optional[bool] = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = "auto"
    parallel_tool_calls: Optional[bool] = True
    store: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None
    debug: Optional[bool] = True


def simplify_params_for_logging(params: Dict[str, Any]) -> Dict[str, Any]:
    """简化 params 用于日志打印，将 tools 参数简化为只显示个数和名称"""
    if not params:
        return params

    simplified = copy.deepcopy(params)

    # 简化 tools 参数
    if "tools" in simplified and simplified["tools"]:
        tools = simplified["tools"]
        tool_names = []
        for tool in tools:
            if isinstance(tool, dict):
                # OpenAI format: {"type": "function", "function": {"name": "..."}}
                if "function" in tool and "name" in tool["function"]:
                    tool_names.append(tool["function"]["name"])
                # Anthropic format: {"name": "..."}
                elif "name" in tool:
                    tool_names.append(tool["name"])
        simplified["tools"] = f"<{len(tools)} tools: {', '.join(tool_names)}>"

    return simplified


class ListModelsResponse(BaseModel):
    object: Literal["list"] = "list"
    data: List[Model]


# Available models mapping
AVAILABLE_MODELS = [
    {
        "id": "gpt-3.5-turbo",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
    {
        "id": "gpt-4o",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
    {
        "id": "gpt-4o-mini",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
    {
        "id": "o3",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
    {
        "id": "o4-mini",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
    {
        "id": "gpt4",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
    {
        "id": "claude",
        "object": "model",
        "created": 1677610602,
        "owned_by": "anthropic",
    },
    {
        "id": "gemini",
        "object": "model",
        "created": 1677610602,
        "owned_by": "google",
    },
    {
        "id": "doubao-deepseek-r1",
        "object": "model",
        "created": 1677610602,
        "owned_by": "bytedance",
    },
    {
        "id": "ep-20250204210426-gclbn",
        "object": "model",
        "created": 1677610602,
        "owned_by": "bytedance",
    },
    {
        "id": "deepseek-reasoner",
        "object": "model",
        "created": 1677610602,
        "owned_by": "deepseek",
    },
    {
        "id": "doubao-deepseek-v3",
        "object": "model",
        "created": 1677610602,
        "owned_by": "bytedance",
    },
    {
        "id": "ep-20250410145517-rpbrz",
        "object": "model",
        "created": 1677610602,
        "owned_by": "bytedance",
    },
    {
        "id": "deepseek-chat",
        "object": "model",
        "created": 1677610602,
        "owned_by": "deepseek",
    },
    {
        "id": "r1-qianfan",
        "object": "model",
        "created": 1677610602,
        "owned_by": "baidu",
    },
    # Embedding models
    {
        "id": "text-embedding-ada-002",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
    {
        "id": "text-embedding-3-small",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
    {
        "id": "text-embedding-3-large",
        "object": "model",
        "created": 1677610602,
        "owned_by": "openai",
    },
]




def create_chat_completion_response(
    resp: dict,
) -> ChatCompletion:
    result = ChatCompletion.model_validate(resp)
    return result


async def create_chat_completion_stream(
    resp: dict,
) -> AsyncGenerator[str, None]:
    """Create streaming response for chat completion"""
    result = ChatCompletion.model_validate(resp)
    choices = []
    for c in result.choices:
        tool_calls = c.message.tool_calls if hasattr(c.message, 'tool_calls') else None
        function_call = c.message.function_call if hasattr(c.message, 'function_call') else None
        refusal = c.message.refusal if hasattr(c.message, 'refusal') else None
        delta_tool_calls = None
        if tool_calls:
            delta_tool_calls = []
            for i, tool_call in enumerate(tool_calls):
                delta_tool_calls.append(ChoiceDeltaToolCall(
                    index=i,
                    id=tool_call.id,
                    type=tool_call.type,
                    function=ChoiceDeltaToolCallFunction(
                        name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                    )
                ))
        if function_call:
            function_call = ChoiceDeltaFunctionCall(
                name=function_call.name,
                arguments=function_call.arguments,
            )
        chunk_delta = ChoiceDelta(
            role=c.message.role,
            content=c.message.content,
            tool_calls=delta_tool_calls,
            function_call=function_call,
            refusal=refusal,
        )
        chunk_choice = ChunkChoice(
            index=c.index,
            delta=chunk_delta,
            finish_reason=c.finish_reason,
            logprobs=c.logprobs,
        )
        choices.append(chunk_choice)
    chunk = ChatCompletionChunk(
        id=result.id,
        choices=choices,
        created=result.created,
        model=result.model,
        object="chat.completion.chunk",
        service_tier=result.service_tier,
        system_fingerprint=result.system_fingerprint,
        usage=result.usage,
    )
    yield f"data: {chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


@app.get("/v1/models", response_model=ListModelsResponse)
async def list_models(api_key: str = Header(None, alias="authorization")):
    """List available models"""
    verify_api_key(api_key)
    models = [Model(**model_data) for model_data in AVAILABLE_MODELS]
    return ListModelsResponse(data=models)


@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest, authorization: Optional[str] = Header(None), request_original: Request = None):
    """Create a chat completion"""
    # Verify API key
    verify_api_key(authorization)

    global USER_ID, TOKEN

    if not USER_ID or not TOKEN:
        raise HTTPException(status_code=500, detail="Server authentication not initialized")

    # Extract parameters
    model = request.model
    messages = request.messages
    max_tokens = request.max_tokens or 1000
    temperature = request.temperature or 0.6
    top_p = request.top_p or 1.0
    n = request.n or 1
    stream = request.stream or False
    tools = request.tools
    functions = request.functions
    function_call = request.function_call
    reasoning_effort = request.reasoning_effort
    request_original_json = await request_original.json()
    thinking = request_original_json.get('thinking', None)
    debug = request.debug or False
    # Validate model
    # available_model_ids = [m["id"] for m in AVAILABLE_MODELS]
    # if model not in available_model_ids:
    #     raise HTTPException(status_code=400, detail=f"Model {model} not available")

    request_id = f"chatcmpl-{uuid.uuid4().hex}"

    try:
        # Prepare API request parameters
        chat_url, params, headers, rollout_n = prepare_api_request_params(
            user_id=USER_ID,
            token=TOKEN,
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n,
            tools=tools,
            functions=functions,
            function_call=function_call,
            reasoning_effort=reasoning_effort,
            thinking=thinking,
        )

        logger.info(f"Chat completion request ID: {request_id}\nrollout_n = {rollout_n}\n{json.dumps(params, ensure_ascii=False, indent=2)}")

        if rollout_n and rollout_n > 1:
            logger.warning(f"Model {model} does not support n-sampling, manually requesting {rollout_n} completions.")
            async def async_request(i):
                # Call the backend API directly
                res = api_request(
                    url=chat_url,
                    params=params,
                    headers=headers,
                    timeout=TIMEOUT,
                )
                res.raise_for_status()

                resp = process_api_response(
                    res,
                    url=chat_url,
                    model=model,
                    debug=debug,
                    rollout_n=1,
                )
                return resp
            resp_list = await xmap_async(list(range(rollout_n)), async_request, is_async_work_func=True)
            resp = resp_list[0]
            resp["choices"] = sum([resp_item["choices"] for resp_item in resp_list], [])
        else:
            # Call the backend API directly
            res = api_request(
                url=chat_url,
                params=params,
                headers=headers,
                timeout=TIMEOUT,
            )
            res.raise_for_status()

            resp = process_api_response(
                res,
                url=chat_url,
                model=model,
                debug=debug,
                rollout_n=rollout_n,
            )

        if stream:
            return StreamingResponse(
                create_chat_completion_stream(resp),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        else:
            # Non-streaming response
            completion = create_chat_completion_response(resp)
            return completion

    except Exception as e:
        logger.error(f"Error in chat completion: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/embeddings")
async def create_embeddings(request: EmbeddingRequest, authorization: Optional[str] = Header(None)):
    """Create embeddings for the given input"""
    # Verify API key
    verify_api_key(authorization)

    global USER_ID, TOKEN

    if not USER_ID or not TOKEN:
        raise HTTPException(status_code=500, detail="Server authentication not initialized")

    # Extract parameters
    input_text = request.input
    model = request.model or "text-embedding-ada-002"
    debug = request.debug if request.debug is not None else True

    # Validate model - check if it's a supported embedding model
    # embedding_models = ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]
    # if model not in embedding_models:
    #     raise HTTPException(status_code=400, detail=f"Embedding model {model} not supported. Available models: {embedding_models}")

    try:
        # Prepare API request parameters
        embedding_url, params, headers = prepare_embedding_request_params(
            user_id=USER_ID,
            token=TOKEN,
            input_text=input_text,
            model=model,
        )

        if debug:
            logger.debug(f"Embedding request URL: {embedding_url}")
            logger.debug(f"Embedding request params: {json.dumps(simplify_params_for_logging(params), ensure_ascii=False, indent=2)}")

        # Try primary request first
        res = requests.post(
            embedding_url,
            data=urlencode(params),
            headers=headers,
            timeout=TIMEOUT,
        )
        res.raise_for_status()

        # Process the response
        embedding_data = process_embedding_response(res, debug=debug)

        if not embedding_data:
            raise HTTPException(status_code=500, detail="Failed to get valid embedding response from backend")

        # Create OpenAI-compatible response
        embedding_response = create_embedding_response(
            embedding_data=embedding_data,
            model=model,
            input_text=input_text,
        )

        return embedding_response

    except Exception as e:
        logger.error(f"Error in embedding creation: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/responses")
async def create_response(request: ResponseRequest, authorization: Optional[str] = Header(None), request_original: Request = None):
    """Create a response using OpenAI's responses API"""
    # Verify API key
    verify_api_key(authorization)

    global USER_ID, TOKEN

    if not USER_ID or not TOKEN:
        raise HTTPException(status_code=500, detail="Server authentication not initialized")

    # Extract parameters
    model = request.model
    input_data = request.input
    reasoning = request.reasoning.model_dump() if request.reasoning else None
    text = request.text
    instructions = request.instructions
    max_output_tokens = request.max_output_tokens
    temperature = request.temperature or 1.0
    top_p = request.top_p or 1.0
    stream = request.stream or False
    tools = request.tools
    tool_choice = request.tool_choice or "auto"
    parallel_tool_calls = request.parallel_tool_calls
    store = request.store
    metadata = request.metadata
    debug = request.debug if request.debug is not None else True

    session_id = request_original.headers.get('X-Session-ID', None)

    # Validate model - responses API supports specific models
    # supported_models = ["o3", "o4-mini"]
    # if model not in supported_models:
    #     raise HTTPException(status_code=400, detail=f"Model {model} not supported for responses API. Supported models: {supported_models}")

    try:
        # Prepare API request parameters
        response_url, params, headers = prepare_response_request_params(
            user_id=USER_ID,
            token=TOKEN,
            model=model,
            input_data=input_data,
            reasoning=reasoning,
            text=text,
            instructions=instructions,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
            tools=tools,
            tool_choice=tool_choice,
            parallel_tool_calls=parallel_tool_calls,
            store=store,
            metadata=metadata,
        )
        # 同一个session_id会打到同一个微软节点
        headers["arsenal-openai-hash"] = session_id
        headers["X-Trace-Id"] = session_id

        if debug:
            logger.debug(f"session_id: {session_id}")
            logger.debug(f"headers: {headers}")
            logger.debug(f"Responses request URL: {response_url}")
            logger.debug(f"Responses request params: {json.dumps(simplify_params_for_logging(params), ensure_ascii=False, indent=2)}")

        # Call the backend API
        if stream:
            # Create a streaming response that forwards SSE events
            def forward_sse_stream():
                client = httpx.Client()
                with client.stream("POST", response_url, json=params, headers=headers, timeout=TIMEOUT) as res:
                    for event in httpx_sse.EventSource(res).iter_sse():
                        text = f"event: {event.event}\ndata: {event.data}\n\n"
                        yield text
            return StreamingResponse(
                forward_sse_stream(),
                media_type="text/event-stream",
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        else:
            # Non-streaming request with retry logic
            max_retries = 3
            retry_delay = 2  # 秒
            last_error = None

            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        logger.warning(f"Retrying responses API call (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(retry_delay * attempt)  # 递增延迟

                    res = requests.post(
                        response_url,
                        json=params,
                        headers=headers,
                        timeout=TIMEOUT,
                    )
                    res.raise_for_status()

                    # Process the response
                    response_data = process_response_api_response(res, debug=debug)

                    if not response_data:
                        raise ValueError("后端返回的响应数据为空")

                    # Return the response directly (it should already be in OpenAI format)
                    return response_data

                except ValueError as e:
                    # ValueError 是由 process_response_api_response 抛出的业务错误
                    last_error = e
                    error_msg = str(e)
                    if "Connection reset" in error_msg or "SocketException" in error_msg:
                        logger.warning(f"连接被重置，尝试重试... ({attempt + 1}/{max_retries})")
                        continue
                    else:
                        # 其他业务错误不重试
                        raise HTTPException(status_code=500, detail=str(e))

                except requests.exceptions.Timeout as e:
                    last_error = e
                    logger.warning(f"请求超时，尝试重试... ({attempt + 1}/{max_retries})")
                    continue

                except requests.exceptions.ConnectionError as e:
                    last_error = e
                    logger.warning(f"连接错误，尝试重试... ({attempt + 1}/{max_retries})")
                    continue

                except Exception as e:
                    last_error = e
                    logger.error(f"请求失败: {e}\n{traceback.format_exc()}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        break

            # 如果所有重试都失败了
            error_detail = f"在 {max_retries} 次重试后仍然失败: {str(last_error)}"
            logger.error(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)

    except Exception as e:
        logger.error(f"Error in response creation: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error in response creation: {e}\n{traceback.format_exc()}")


def verify_claude_api_key(x_api_key: Optional[str] = None, authorization: Optional[str] = None):
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


@app.post("/v1/messages")
async def create_message(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    request_obj: Request = None
):
    """Create a message using Anthropic Messages API format"""
    # Log all headers for debugging
    if request_obj:
        logger.info(f"All headers: {dict(request_obj.headers)}")
        body = await request_obj.json()
        logger.info(f"params: {json.dumps(body, ensure_ascii=False, indent=2)}")

    # Verify API key (supports both x-api-key and Authorization: Bearer)
    verify_claude_api_key(x_api_key=x_api_key, authorization=authorization)

    global USER_ID, TOKEN

    if not USER_ID or not TOKEN:
        raise HTTPException(
            status_code=500,
            detail={"type": "error", "error": {"type": "api_error", "message": "Server authentication not initialized"}}
        )

    # Extract parameters from request body (support all Anthropic SDK parameters)
    model = body.get("model")
    max_tokens = body.get("max_tokens", 4096)
    temperature = body.get("temperature")
    top_p = body.get("top_p")
    top_k = body.get("top_k")
    stream = body.get("stream", False)
    messages = body.get("messages", [])
    system = body.get("system")
    stop_sequences = body.get("stop_sequences")
    tools = body.get("tools")
    tool_choice = body.get("tool_choice")
    metadata = body.get("metadata")
    thinking = body.get("thinking")

    request_id = f"msg_{uuid.uuid4().hex}"

    try:
        # 转换消息格式 (使用 SDK 类型，转换为字典)
        hexin_messages = messages


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
        if system:
            params["system"] = system

        # 添加可选参数
        # 注意：Bedrock Claude 不允许同时指定 temperature 和 top_p
        # 优先使用 temperature，如果没有则使用 top_p
        if temperature is not None:
            params["temperature"] = temperature
        elif top_p is not None:
            params["top_p"] = top_p

        if top_k is not None:
            params["top_k"] = top_k

        if stop_sequences:
            params["stop_sequences"] = stop_sequences

        # 添加工具调用支持
        if tools:
            params["tools"] = tools
        if tool_choice:
            params["tool_choice"] = tool_choice

        # 添加元数据和思考配置支持
        if metadata:
            params["metadata"] = metadata
        if thinking:
            params["thinking"] = thinking

        # API URL (Bedrock 格式：model ID 在 URL 中)
        # 流式调用使用 invoke-with-response-stream，非流式使用 invoke
        if stream:
            chat_url = f"https://arsenal-openai.10jqka.com.cn:8443/vtuber/ai_access/claude/model/{backend_model}/invoke-with-response-stream"
        else:
            chat_url = f"https://arsenal-openai.10jqka.com.cn:8443/vtuber/ai_access/claude/model/{backend_model}/invoke"

        # Headers (Bedrock 使用 token 或 Authorization)
        headers = {
            "Content-Type": "application/json",
            "token": TOKEN
        }

        logger.info(f"Claude Messages API request ID: {request_id}\nModel: {model}\nMessages: {len(hexin_messages)}\nStream: {stream}")
        logger.debug(f"Request params: {json.dumps(simplify_params_for_logging(params), ensure_ascii=False, indent=2)}")

        if stream:
            # 流式调用：转发 SSE 事件
            async def forward_claude_stream():
                """转发 Claude Bedrock 流式响应"""
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        chat_url,
                        json=params,
                        headers=headers,
                        timeout=600.0
                    ) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if line:
                                # 转发所有 SSE 行 (data:, retry:, event: 等)
                                yield f"{line}\n"
                            else:
                                # 保留空行（SSE 消息分隔符）
                                yield "\n"

            return StreamingResponse(
                forward_claude_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
                }
            )
        else:
            # 非流式调用：直接返回响应
            res = api_request(
                url=chat_url,
                params=params,
                headers=headers,
                timeout=600,
            )

            # 处理响应
            hexin_response = res.json()
            logger.debug(f"Hexin response: {json.dumps(hexin_response, ensure_ascii=False, indent=2)}")

            # 检查后端是否返回错误
            if isinstance(hexin_response, dict) and hexin_response.get("success") is False:
                error_msg = hexin_response.get("status_msg", "Unknown error")
                error_code = hexin_response.get("status_code", -1)
                logger.error(f"Backend API error (code: {error_code}): {error_msg}")
                raise HTTPException(
                    status_code=502,  # Bad Gateway - 后端服务错误
                    detail={
                        "type": "error",
                        "error": {
                            "type": "api_error",
                            "message": f"Backend error: {error_msg} (code: {error_code})"
                        }
                    }
                )

            # 返回标准响应
            return JSONResponse(content=hexin_response)
    except Exception as e:
        logger.error(f"Error in create message: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"type": "error", "error": {"type": "api_error", "message": str(e)}}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "authenticated": USER_ID is not None and TOKEN is not None}


def main():
    """Main entry point for the hexin_server module"""

    parser = argparse.ArgumentParser(
        description="Run the FastAPI server for OpenAI API proxy",
        prog="python -m hexin_server"
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8777, help="Port to bind to (default: 8777)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", type=str, default="info", choices=["debug", "info", "warning", "error"], help="Log level (default: info)")
    parser.add_argument("--env-file", type=str, default=".env", help="Path to environment file (default: .env)")

    args = parser.parse_args()

    print(f"Loading environment variables from {Path(args.env_file).resolve()}")
    load_dotenv(args.env_file)
    print(f"Starting Hexin Server on {args.host}:{args.port}")
    print(f"Log level: {args.log_level}")
    if args.reload:
        print("Auto-reload enabled")

    print(f"BASE_URL = \"http://{args.host}:{args.port}\"")
    print(f"API_KEY = \"{FIXED_API_KEY}\"")

    try:
        uvicorn.run(
            "hexin_server.__main__:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
