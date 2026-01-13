# flexllm 文档

高性能 LLM 客户端库，支持批量处理、响应缓存和断点续传。

## 文档目录

```
docs/
├── index.md              # 本文档（主入口）
├── api.md                # API 详细参考
└── advanced.md           # 高级用法
```

## 快速开始

### 安装

```bash
pip install flexllm[all]
```

### 基本使用

```python
from flexllm import LLMClient

client = LLMClient(
    model="gpt-4",
    base_url="https://api.openai.com/v1",
    api_key="your-api-key"
)

# 同步调用
result = client.chat_completions_sync([
    {"role": "user", "content": "Hello!"}
])
print(result)
```

## 核心概念

### 1. 客户端层次

```
LLMClient (推荐，统一入口)
    ├── OpenAIClient (OpenAI 兼容 API)
    └── GeminiClient (Google Gemini)

LLMClientPool (多 Endpoint 负载均衡)
    └── 内部管理多个 LLMClient
```

### 2. 请求模式

| 模式 | 方法 | 说明 |
|------|------|------|
| 单条同步 | `chat_completions_sync()` | 简单场景 |
| 单条异步 | `chat_completions()` | 高性能场景 |
| 批量异步 | `chat_completions_batch()` | 大规模处理 |
| 流式输出 | `chat_completions_stream()` | 实时显示 |

### 3. 缓存机制

```python
from flexllm import ResponseCacheConfig

# 启用缓存（1小时 TTL）
cache = ResponseCacheConfig(enabled=True, ttl=3600)

# 永久缓存
cache = ResponseCacheConfig(enabled=True, ttl=0)
```

缓存基于消息内容的 hash，相同请求自动命中缓存。

### 4. 断点续传

批量处理支持自动断点续传：

```python
results = await client.chat_completions_batch(
    messages_list,
    output_file="results.jsonl",  # 关键：指定输出文件
)
```

- 结果增量写入文件
- 程序中断后，重新运行自动跳过已完成的请求
- 配合缓存使用效果更好

## 支持的 Provider

| Provider | 客户端 | 说明 |
|----------|--------|------|
| OpenAI | LLMClient/OpenAIClient | GPT 系列 |
| DeepSeek | LLMClient/OpenAIClient | 支持 thinking 模式 |
| Qwen | LLMClient/OpenAIClient | 通义千问 |
| vLLM | LLMClient/OpenAIClient | 本地部署 |
| Ollama | LLMClient/OpenAIClient | 本地部署 |
| Gemini | LLMClient/GeminiClient | Google AI |
| Vertex AI | GeminiClient | GCP 托管 |

## CLI 工具

```bash
# 快速问答
flexllm ask "什么是 Python?"

# 交互对话
flexllm chat

# 测试连接
flexllm test

# 初始化配置
flexllm init
```

## 下一步

- [API 详细参考](api.md) - 完整的 API 文档
- [高级用法](advanced.md) - 负载均衡、多模态、链式推理等
