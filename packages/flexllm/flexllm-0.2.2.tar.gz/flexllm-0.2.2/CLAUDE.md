# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

flexllm 是一个高性能 LLM 客户端库，支持批量处理、响应缓存和断点续传。支持 OpenAI 兼容 API（vLLM、Ollama、DeepSeek 等）和 Google Gemini API。

## 常用命令

```bash
# 安装依赖
pip install -e ".[all]"      # 安装所有功能
pip install -e ".[dev]"      # 开发环境

# 运行测试
pytest                        # 运行所有测试
pytest tests/test_xxx.py     # 运行单个测试文件
pytest -k "test_name"        # 按名称匹配运行测试
pytest -m "not slow"         # 跳过慢测试

# 代码格式化
black flexllm tests
isort flexllm tests

# CLI 使用
flexllm ask "问题"           # 快速问答
flexllm chat                 # 交互式聊天
flexllm test                 # 测试连接
```

## 核心架构

```
LLMClient (统一入口，自动选择底层客户端)
    ├── OpenAIClient (OpenAI 兼容 API)
    └── GeminiClient (Google Gemini API)
            │
            └── 继承自 LLMClientBase (抽象基类)
                    │
                    ├── ConcurrentRequester (async_api/ 异步并发引擎)
                    ├── ResponseCache (响应缓存，使用 flaxkv2)
                    └── ImageProcessor (processors/ 图片处理)

LLMClientPool (多 Endpoint 负载均衡)
    └── ProviderRouter (路由策略：round_robin/weighted/random/fallback)
```

### 关键设计模式

1. **客户端抽象**：`LLMClientBase` 定义 4 个核心抽象方法，子类只需实现差异化逻辑：
   - `_get_url()` - 构造请求 URL
   - `_get_headers()` - 构造请求头
   - `_build_request_body()` - 构造请求体
   - `_extract_content()` - 提取响应内容

2. **断点续传**：`chat_completions_batch()` 通过 `output_file` 参数支持 JSONL 增量写入，中断后自动恢复

3. **响应缓存**：通过 `ResponseCacheConfig` 配置，支持 TTL 和 IPC 多进程共享

## 测试配置

测试需要环境变量：
- `GEMINI_API_KEY` - Gemini 测试
- `SILICONFLOW_API_KEY` - SiliconFlow 测试

pytest 配置已启用 `asyncio_mode = auto`，异步测试函数会自动运行。

## CLI 配置

配置文件位置：`~/.flexllm/config.yaml`

环境变量：
- `FLEXLLM_BASE_URL`
- `FLEXLLM_API_KEY`
- `FLEXLLM_MODEL`
