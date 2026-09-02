# 🤖 AgentProxy: Central Independent Data Ingestion Gateway

## 🚀 概述

`AgentProxy` 是一个系统级的通用状态和事件的**中央独立数据接收网关 (Central Independent Data Ingestion Gateway)**。它的核心职责是提供一个稳定、高可靠性的数据接入点，用于接收来自所有离散、非实时、异步的系统级状态报告和通用事件。

本项目作为模型适配层，实现了核心目标：用本地 Ollama 运行的开源大模型，替换掉 Claude Code 背后的 Anthropic API，实现完全本地、零费用的 AI 编程助手。

## 🎯 核心架构流程图

```
Claude Code (VSCode 插件)
        ↓  Anthropic /v1/messages 协议
anthropic_proxy.py (FastAPI, 端口 4001) 
        ↓  OpenAI /v1/chat/completions 协议
LiteLLM (端口 4000)
        ↓
Ollama (本地模型服务)
        ↓
gemma4:e4b / qwen3.5:9b 等本地模型
```

## 📖 架构深度解析与核心难点 (坑点总结)

### 1. 核心组件角色
*   **Claude Code (Client)**: 调用方，使用 Anthropic 协议。
*   **`anthropic_proxy.py` (网关)**: **本项目的核心。** 负责在 Anthropic 协议和 OpenAI 协议之间进行格式转换（`Anthropic -> OpenAI`），并在接收到结果后，再转换回 Anthropic 的工具调用标准格式。
*   **LiteLLM (网关)**: 接收到 OpenAI 格式请求，将其转发给 Ollama。
*   **Ollama (后端)**: 负责实际的大模型推理。

### 2. 关键技术难点及解决方案 (Why 编写中间件)

| 坑点 | 根因 | 解决方案 |
| :--- | :--- | :--- |
| **工具调用格式错误** | LiteLLM 在 1.82.x 版本中，当 Ollama 模型通过 `tool_calls` 字段返回工具调用时，会错误地将工具调用信息塞进 `text` 字符串，而不是生成正确的 `tool_use` block。 | **【关键】自写 FastAPI 中间件**：接管 `/v1/messages` 端点，手动解析 LLM 的输出（包括文本和工具调用），并重新封装为标准的 `tool_use` 块，确保 `stop_reason` 准确为 `tool_use`。 |
| **模型输出不规范** | 某些模型（如 Qwen 系列）有时不走标准的 `tool_calls` 字段，而是将工具调用 JSON 直接写在 `content` 文本里，甚至包在 Markdown 代码块中。 | **【防御性编程】**：在 `_try_parse_tool_call` 函数中增加多重兜底解析逻辑：直接解析、正则提取 Markdown 代码块、使用栈匹配算法定位嵌套 JSON 对象。 |
| **工具名不匹配** | 模型对工具名的发挥空间很大，同一功能可能输出 `Shell`、`local-exec`、`run` 等变体。 | **【规范化映射】**：在中间件中加入 `tool_name_map` 规范化映射，将所有变体统一映射到 Claude Code 原生的工具名（如 `bash`）。 |
| **网络兼容性** | Windows PowerShell 的 `curl` 命令是 `Invoke-WebRequest` 的别名，不支持 `-d` 参数。 | **【环境适配】**：使用 `Invoke-RestMethod` 或安装并使用真正的 `curl.exe`。 |
| **参数残留** | Claude Code 发送给本地模型可能会携带 Ollama 不认识的参数（如 `context_management`）。 | **【配置优化】**：在 `litellm_settings` 下添加 `drop_params: true`，自动过滤掉不支持的参数。 |
| **Thinking 模式** | 某些模型默认开启 "思维链" 推理 (`<think>...</think>`)，会显著拖慢响应速度并干扰解析。 | **【请求优化】**：在请求 options 中显式禁用：`"options": {"think": False}`。 |

---

## 🛠️ 运行部署指南 (Local Setup)

**前提条件:**

1. Python 3.10+ 环境。
2. 已安装 `ollama` 和 `litellm`。

**部署步骤 (请按顺序执行):**

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **启动 Ollama**:
   ```bash
   ollama serve
   ```

3. **启动 LiteLLM (API 网关)**:
   ```bash
   litellm --config litellm_config.yaml --port 4000
   ```

4. **启动 AgentProxy 中间件 (核心)**:
   ```bash
   uvicorn anthropic_proxy:app --host 0.0.0.0 --port 4001
   ```

## 📚 配置与模型建议

### 1. `litellm_config.yaml` 配置
**关键点：**
*   对外暴露模型名：`claude-3-opus-local`
*   实际调用本地模型：`ollama_chat/gemma4:e4b`

### 2. VSCode 插件配置
修改 `~/.claude/settings.json`：
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:4001",
    "ANTHROPIC_AUTH_TOKEN": "fake-key",
    "ANTHROPIC_MODEL": "claude-3-opus-local",
    "ANTHROPIC_SMALL_FAST_MODEL": "claude-3-opus-local"
  }
}
```
**注意：** `ANTHROPIC_BASE_URL` 必须指向我们的中间件端口 `4001`。

### 3. 模型选择建议 (根据本地部署环境)

| 模型 | 显存占用 (估算) | 稳定性 | 推荐指数 |
| :--- | :--- | :--- | :--- |
| gemma4:e4b | 适中 | ✅ 适配性好 | ⭐⭐⭐⭐ |
| qwen3.5:9b | 中高 | ✅ 兼容性强 | ⭐⭐⭐ |

***
**参考资料来源:** 
*   原始博文：[https://blog.csdn.net/ddly2000/article/details/160182979](https://blog.csdn.net/ddly2000/article/details/160182979) (内容已进行结构化和优化，用于内部文档)。
**版权声明:** 本文内容已根据原始资料进行提炼、重构和优化，用于本项目内部文档目的。
