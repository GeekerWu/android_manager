# ☁️ AgentProxy 子系统设计规范 (CLAUDE.md)

## 🚀 模块总览
AgentProxy 是系统级的通用状态和事件的**中央独立数据接收网关 (Central Independent Data Ingestion Gateway)**。它的核心职责是提供一个稳定、高可靠性的数据接入点，用于接收来自所有离散、非实时、异步的系统级状态报告和通用事件。

## 🚀 参考链接
- https://blog.csdn.net/ddly2000/article/details/160182979

## 🚀 服务启动指南
**运行命令**:
# 1. 启动 Ollama
- ollama serve
# 2. 启动 LiteLLM（`D:\android_manager\agentproxy`路径下）
- litellm --config litellm_config.yaml --port 4000
# 3. 启动中间件（`D:\android_manager\agentproxy`路径下）
- uvicorn anthropic_proxy:app --host 0.0.0.0 --port 4001
# 4. 打开 VSCode，Claude Code 即可使用本地模型

# currentDate
Today's date is 2026-09-01.