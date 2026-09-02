import json
import re
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

def _try_parse_tool_call(text: str):
    """从文本/代码块中提取工具调用 JSON"""
    # 直接解析
    try:
        parsed = json.loads(text.strip())
        if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    # 从 Markdown 代码块中提取
    for match in re.finditer(r'```(?:json)?\s*(.+?)\s*```', text, re.DOTALL):
        try:
            parsed = json.loads(match.group(1).strip())
            if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
                return parsed
        except json.JSONDecodeError:
            pass

    # 栈匹配：找 {"name": ... } 结构
    json_start = text.find('{"name"')
    if json_start != -1:
        depth, start = 0, text.rfind('{', 0, json_start)
        if start != -1:
            for i in range(start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            parsed = json.loads(text[start:i+1])
                            if isinstance(parsed, dict) and "name" in parsed:
                                return parsed
                        except json.JSONDecodeError:
                            pass
                        break
    return None


def _convert_openai_to_anthropic(litellm_data: dict, original_body: dict):
    """OpenAI 格式 → Anthropic /v1/messages 格式"""
    choices = litellm_data.get("choices", [])
    model = litellm_data.get("model", original_body.get("model", ""))

    if not choices:
        return {"type": "message", "role": "assistant", "model": model,
                "content": [{"type": "text", "text": "No response"}],
                "stop_reason": "end_turn", "stop_sequence": None}

    message = choices[0].get("message", {})
    tool_calls = message.get("tool_calls", [])
    text_content = message.get("content", "")
    anthropic_content = []
    found_tools = []

    # 工具名规范化映射（Qwen 模型经常乱起名）
    tool_name_map = {
        "shell": "bash", "local-exec": "bash", "exec": "bash", "run": "bash",
        "glob": "glob", "grep": "grep", "search": "grep",
        "read": "read", "cat": "read", "write": "write",
        "edit": "edit", "patch": "edit",
        "todos": "todo_write", "todowrite": "todo_write",
        "fetch": "webfetch", "notebook": "notebook",
    }

    # 处理 tool_calls 字段（标准路径）
    for tc in tool_calls:
        func = tc.get("function", {})
        name = func.get("name", "")
        raw_args = func.get("arguments", "{}")
        args_dict = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        found_tools.append(name)
        anthropic_content.append({"type": "tool_use", "name": name, "input": args_dict})

    # 处理 content 字段（Qwen 把工具调用写在文本里的情况）
    if text_content and text_content.strip():
        parsed = _try_parse_tool_call(text_content)
        if parsed:
            raw_name = parsed["name"].lower().strip()
            final_name = tool_name_map.get(raw_name, parsed["name"])
            found_tools.append(final_name)
            anthropic_content.append({
                "type": "tool_use",
                "name": final_name,
                "input": parsed.get("arguments", {})
            })
            print(f"[Proxy] 🔧 从 text 提取工具调用: {parsed['name']} → {final_name}")
        else:
            anthropic_content.append({"type": "text", "text": text_content})

    stop_reason = "tool_use" if found_tools else "end_turn"

    return {
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": anthropic_content,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": litellm_data.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": litellm_data.get("usage", {}).get("completion_tokens", 0),
        }
    }


@app.post("/v1/messages")
async def anthropic_messages(request: Request):
    body = await request.json()
    # print(f"body={body.get('model')}, messages={len(body.get('messages', []))}")
    # Anthropic → OpenAI 格式转换
    messages = []
    for msg in body.get("messages", []):
        content = msg.get("content", "")
        if isinstance(content, list):
            parts = []
            for block in content:
                if block["type"] == "text":
                    parts.append(block["text"])
                elif block["type"] == "tool_result":
                    parts.append(f"[Tool Result] {block.get('content', '')}")
            content = "\n".join(parts)
        messages.append({"role": msg["role"], "content": content})

    openai_body = {
        "model": body.get("model", "gemma4:e4b"),
        "messages": messages,
        "stream": False,
    }
    if body.get("tools"):
        openai_body["tools"] = body["tools"]
    # qwen3.5 禁用 thinking 模式
    if "qwen3" in body.get("model", "").lower():
        openai_body["options"] = {"think": False}

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "http://localhost:4000/v1/chat/completions",
            json=openai_body
        )
        litellm_data = resp.json()

    anthropic_response = _convert_openai_to_anthropic(litellm_data, body)
    # print(f"anthropic_response={anthropic_response}")
    # print(f"[Proxy] stop_reason={anthropic_response['stop_reason']}, "
    f"content_types={[c['type'] for c in anthropic_response['content']]}")
    return JSONResponse(content=anthropic_response)