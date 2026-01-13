"""
flexllm CLI - LLM 客户端命令行工具

提供简洁的 LLM 调用命令:
    flexllm ask "你的问题"
    flexllm chat
    flexllm models
    flexllm test
"""
from __future__ import annotations

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional


class FlexLLMCli:
    """flexllm 命令行接口"""

    def __init__(self):
        self.config = self._load_config()

    def _get_config_paths(self):
        """获取配置文件搜索路径"""
        paths = []
        # 1. 当前目录
        paths.append(Path.cwd() / "flexllm_config.yaml")
        # 2. 用户配置目录
        paths.append(Path.home() / ".flexllm" / "config.yaml")
        return paths

    def _load_config(self) -> dict:
        """加载配置文件"""
        default_config = {
            "default": None,
            "models": []
        }

        for config_path in self._get_config_paths():
            if config_path.exists():
                try:
                    import yaml
                    with open(config_path, 'r', encoding='utf-8') as f:
                        file_config = yaml.safe_load(f)
                    if file_config:
                        return {**default_config, **file_config}
                except ImportError:
                    # 没有 pyyaml，尝试简单解析
                    pass
                except Exception:
                    pass

        # 从环境变量构建默认配置
        env_config = self._config_from_env()
        if env_config:
            default_config["models"] = [env_config]
            default_config["default"] = env_config.get("id")

        return default_config

    def _config_from_env(self) -> Optional[dict]:
        """从环境变量构建配置"""
        base_url = os.environ.get("FLEXLLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
        api_key = os.environ.get("FLEXLLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
        model = os.environ.get("FLEXLLM_MODEL") or os.environ.get("OPENAI_MODEL")

        if base_url and api_key and model:
            return {
                "id": model,
                "name": model,
                "base_url": base_url,
                "api_key": api_key,
                "provider": "openai"
            }
        return None

    def get_model_config(self, name_or_id: str = None) -> Optional[dict]:
        """获取模型配置

        Args:
            name_or_id: 模型名称或ID，为 None 时使用默认模型

        Returns:
            dict: 包含 id, name, base_url, api_key, provider 的配置
        """
        models = self.config.get("models", [])

        if not models:
            # 尝试从环境变量获取
            env_config = self._config_from_env()
            if env_config:
                return env_config
            return None

        # 未指定时使用默认模型
        if name_or_id is None:
            name_or_id = self.config.get("default")
            if not name_or_id:
                return models[0] if models else None

        # 按 name 查找
        for m in models:
            if m.get("name") == name_or_id:
                return m

        # 按 id 查找
        for m in models:
            if m.get("id") == name_or_id:
                return m

        return None

    def ask(self, prompt: str = None, system: str = None, model: str = None):
        """LLM 快速问答（适合程序/Agent 调用）

        纯文本输出，无格式化，适合管道和程序调用。
        支持从 stdin 读取输入。

        Args:
            prompt: 用户问题
            system: 系统提示词 (-s)
            model: 模型名称，使用配置默认值

        Examples:
            flexllm ask "什么是Python"
            flexllm ask "解释代码" -s "你是代码专家"
            echo "长文本" | flexllm ask "总结一下"
        """
        # 从 stdin 读取输入（如果有）
        stdin_content = None
        if not sys.stdin.isatty():
            stdin_content = sys.stdin.read().strip()

        # 如果没有 prompt 且没有 stdin，报错
        if not prompt and not stdin_content:
            print("错误: 请提供问题", file=sys.stderr)
            return

        # 组合 prompt
        if stdin_content:
            if prompt:
                full_prompt = f"{stdin_content}\n\n{prompt}"
            else:
                full_prompt = stdin_content
        else:
            full_prompt = prompt

        # 获取模型配置
        model_config = self.get_model_config(model)
        if not model_config:
            print(f"错误: 未找到模型配置，使用 'flexllm list_models' 查看可用模型", file=sys.stderr)
            print("提示: 设置环境变量 FLEXLLM_BASE_URL, FLEXLLM_API_KEY, FLEXLLM_MODEL 或创建 ~/.flexllm/config.yaml", file=sys.stderr)
            return

        model_id = model_config.get("id")
        base_url = model_config.get("base_url")
        api_key = model_config.get("api_key", "EMPTY")

        async def _ask():
            from flexllm import LLMClient

            client = LLMClient(model=model_id, base_url=base_url, api_key=api_key)

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": full_prompt})

            return await client.chat_completions(messages)

        try:
            result = asyncio.run(_ask())
            if result is None:
                return
            if isinstance(result, str):
                print(result)
                return
            # 处理错误情况
            if hasattr(result, 'status') and result.status == 'error':
                error_msg = result.data.get('detail', result.data.get('error', '未知错误'))
                print(f"错误: {error_msg}", file=sys.stderr)
                return
            print(str(result))
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)

    def chat(
        self,
        message: str = None,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = True,
    ):
        """交互式对话

        Args:
            message: 单条消息（不提供则进入多轮对话模式）
            model: 模型名称
            base_url: API 地址
            api_key: API 密钥
            system_prompt: 系统提示词
            temperature: 采样温度
            max_tokens: 最大生成 token 数
            stream: 是否流式输出

        Examples:
            flexllm chat                          # 多轮对话
            flexllm chat "你好"                   # 单条对话
            flexllm chat --model=gpt-4 "你好"     # 指定模型
        """
        # 获取配置
        model_config = self.get_model_config(model)
        if model_config:
            model = model or model_config.get("id")
            base_url = base_url or model_config.get("base_url")
            api_key = api_key or model_config.get("api_key", "EMPTY")

        if not base_url:
            print("错误: 未配置 base_url", file=sys.stderr)
            return

        if message:
            # 单次对话
            self._single_chat(message, model, base_url, api_key, system_prompt, temperature, max_tokens, stream)
        else:
            # 多轮对话
            self._interactive_chat(model, base_url, api_key, system_prompt, temperature, max_tokens, stream)

    def _single_chat(self, message, model, base_url, api_key, system_prompt, temperature, max_tokens, stream):
        """单次对话"""
        async def _run():
            from flexllm import LLMClient

            client = LLMClient(model=model, base_url=base_url, api_key=api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})

            if stream:
                print("Assistant: ", end="", flush=True)
                async for chunk in client.chat_completions_stream(messages, temperature=temperature, max_tokens=max_tokens):
                    print(chunk, end="", flush=True)
                print()
            else:
                result = await client.chat_completions(messages, temperature=temperature, max_tokens=max_tokens)
                print(f"Assistant: {result}")

        try:
            asyncio.run(_run())
        except KeyboardInterrupt:
            print("\n[中断]")
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)

    def _interactive_chat(self, model, base_url, api_key, system_prompt, temperature, max_tokens, stream):
        """多轮交互对话"""
        async def _run():
            from flexllm import LLMClient

            client = LLMClient(model=model, base_url=base_url, api_key=api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            print(f"\n多轮对话模式")
            print(f"模型: {model}")
            print(f"服务器: {base_url}")
            print(f"输入 'quit' 或 Ctrl+C 退出")
            print("-" * 50)

            while True:
                try:
                    user_input = input("\nYou: ").strip()

                    if user_input.lower() in ["quit", "exit", "q"]:
                        print("再见！")
                        break

                    if not user_input:
                        continue

                    messages.append({"role": "user", "content": user_input})

                    if stream:
                        print("Assistant: ", end="", flush=True)
                        full_response = ""
                        async for chunk in client.chat_completions_stream(messages, temperature=temperature, max_tokens=max_tokens):
                            print(chunk, end="", flush=True)
                            full_response += chunk
                        print()
                        messages.append({"role": "assistant", "content": full_response})
                    else:
                        result = await client.chat_completions(messages, temperature=temperature, max_tokens=max_tokens)
                        print(f"Assistant: {result}")
                        messages.append({"role": "assistant", "content": result})

                except EOFError:
                    print("\n再见！")
                    break

        try:
            asyncio.run(_run())
        except KeyboardInterrupt:
            print("\n再见！")

    def models(self, base_url: str = None, api_key: str = None, name: str = None):
        """列出远程服务器上的可用模型

        Args:
            base_url: API 地址
            api_key: API 密钥
            name: 模型配置名称（用于指定查询哪个服务器）
        """
        import requests

        # 获取配置
        model_config = self.get_model_config(name)
        if model_config:
            base_url = base_url or model_config.get("base_url")
            api_key = api_key or model_config.get("api_key", "EMPTY")
            provider = model_config.get("provider", "openai")
        else:
            provider = "openai"

        if not base_url:
            print("错误: 未配置 base_url", file=sys.stderr)
            return

        # 检测 provider 类型
        is_gemini = provider == "gemini" or "generativelanguage.googleapis.com" in base_url

        try:
            if is_gemini:
                # Gemini API 格式
                url = f"{base_url.rstrip('/')}/models?key={api_key}"
                response = requests.get(url, timeout=10)
            else:
                # OpenAI 兼容格式
                headers = {"Authorization": f"Bearer {api_key}"}
                response = requests.get(
                    f"{base_url.rstrip('/')}/models",
                    headers=headers,
                    timeout=10
                )

            if response.status_code == 200:
                models_data = response.json()

                print(f"\n可用模型列表")
                print(f"服务器: {base_url}")
                print("-" * 50)

                if is_gemini:
                    # Gemini 返回格式: {"models": [...]}
                    models = models_data.get("models", [])
                    if models:
                        for i, m in enumerate(models, 1):
                            name = m.get("name", "").replace("models/", "")
                            print(f"  {i:2d}. {name}")
                        print(f"\n共 {len(models)} 个模型")
                    else:
                        print("未找到可用模型")
                else:
                    # OpenAI 返回格式
                    if isinstance(models_data, dict) and "data" in models_data:
                        models = models_data["data"]
                    elif isinstance(models_data, list):
                        models = models_data
                    else:
                        models = []

                    if models:
                        for i, m in enumerate(models, 1):
                            if isinstance(m, dict):
                                model_id = m.get("id", m.get("name", "unknown"))
                                print(f"  {i:2d}. {model_id}")
                            else:
                                print(f"  {i:2d}. {m}")
                        print(f"\n共 {len(models)} 个模型")
                    else:
                        print("未找到可用模型")
            else:
                print(f"错误: HTTP {response.status_code}", file=sys.stderr)

        except requests.exceptions.RequestException as e:
            print(f"连接失败: {e}", file=sys.stderr)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)

    def list_models(self):
        """列出本地配置的模型"""
        models = self.config.get("models", [])
        default = self.config.get("default", "")

        if not models:
            print("未配置模型")
            print("提示: 创建 ~/.flexllm/config.yaml 或设置环境变量")
            return

        print(f"已配置模型 (共 {len(models)} 个):\n")
        for m in models:
            name = m.get("name", m.get("id", "?"))
            model_id = m.get("id", "?")
            provider = m.get("provider", "openai")
            is_default = " (默认)" if name == default or model_id == default else ""

            print(f"  {name}{is_default}")
            if name != model_id:
                print(f"    id: {model_id}")
            print(f"    provider: {provider}")
            print()

    def test(
        self,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        message: str = "Hello, please respond with 'OK' if you can see this message.",
        timeout: int = 30,
    ):
        """测试 LLM 服务连接

        Args:
            model: 模型名称
            base_url: API 地址
            api_key: API 密钥
            message: 测试消息
            timeout: 超时时间（秒）
        """
        import requests
        import time

        # 获取配置
        model_config = self.get_model_config(model)
        if model_config:
            model = model or model_config.get("id")
            base_url = base_url or model_config.get("base_url")
            api_key = api_key or model_config.get("api_key", "EMPTY")

        if not base_url:
            print("错误: 未配置 base_url", file=sys.stderr)
            return

        print(f"\nLLM 服务连接测试")
        print("-" * 50)

        # 1. 测试 /models 接口
        print(f"\n1. 测试服务器连接...")
        print(f"   地址: {base_url}")
        try:
            start = time.time()
            response = requests.get(
                f"{base_url.rstrip('/')}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=timeout
            )
            elapsed = time.time() - start

            if response.status_code == 200:
                print(f"   ✓ 连接成功 ({elapsed:.2f}s)")
                models_data = response.json()
                if isinstance(models_data, dict) and "data" in models_data:
                    model_count = len(models_data["data"])
                elif isinstance(models_data, list):
                    model_count = len(models_data)
                else:
                    model_count = 0
                print(f"   可用模型数: {model_count}")
            else:
                print(f"   ✗ 连接失败: HTTP {response.status_code}")
                return
        except Exception as e:
            print(f"   ✗ 连接失败: {e}")
            return

        # 2. 测试 chat completions
        if model:
            print(f"\n2. 测试 Chat API...")
            print(f"   模型: {model}")
            try:
                start = time.time()
                response = requests.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": message}],
                        "max_tokens": 50
                    },
                    timeout=timeout
                )
                elapsed = time.time() - start

                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"   ✓ 调用成功 ({elapsed:.2f}s)")
                    print(f"   响应: {content[:100]}...")
                else:
                    print(f"   ✗ 调用失败: HTTP {response.status_code}")
                    print(f"   {response.text[:200]}")
            except Exception as e:
                print(f"   ✗ 调用失败: {e}")

        print("\n测试完成")

    def version(self):
        """显示版本信息"""
        try:
            from importlib.metadata import version
            v = version("flexllm")
        except Exception:
            v = "0.1.0"
        print(f"flexllm {v}")

    def init(self, path: str = None):
        """初始化配置文件

        Args:
            path: 配置文件路径，默认 ~/.flexllm/config.yaml
        """
        if path is None:
            config_path = Path.home() / ".flexllm" / "config.yaml"
        else:
            config_path = Path(path)

        if config_path.exists():
            print(f"配置文件已存在: {config_path}")
            return

        config_path.parent.mkdir(parents=True, exist_ok=True)

        default_config = """# flexllm 配置文件
# 配置搜索路径:
#   1. 当前目录: ./flexllm_config.yaml
#   2. 用户目录: ~/.flexllm/config.yaml

# 默认模型
default: "gpt-4"

# 模型列表
models:
  - id: gpt-4
    name: gpt-4
    provider: openai
    base_url: https://api.openai.com/v1
    api_key: your-api-key

  - id: local-ollama
    name: local-ollama
    provider: openai
    base_url: http://localhost:11434/v1
    api_key: EMPTY
"""

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(default_config)
            print(f"已创建配置文件: {config_path}")
            print("请编辑配置文件填入 API 密钥")
        except Exception as e:
            print(f"创建失败: {e}", file=sys.stderr)


def main():
    """CLI 入口点"""
    try:
        import fire
        fire.Fire(FlexLLMCli)
    except ImportError:
        # 没有 fire，使用简单的参数解析
        cli = FlexLLMCli()
        args = sys.argv[1:]

        if not args or args[0] in ["-h", "--help", "help"]:
            print("flexllm CLI")
            print("\n命令:")
            print("  ask <prompt>     快速问答")
            print("  chat            交互对话")
            print("  models          列出远程模型")
            print("  list_models     列出配置模型")
            print("  test            测试连接")
            print("  init            初始化配置")
            print("  version         显示版本")
            print("\n安装 fire 获得更好的 CLI 体验: pip install fire")
            return

        cmd = args[0]
        rest = args[1:]

        if cmd == "ask":
            prompt = rest[0] if rest else None
            cli.ask(prompt)
        elif cmd == "chat":
            message = rest[0] if rest else None
            cli.chat(message)
        elif cmd == "models":
            cli.models()
        elif cmd == "list_models":
            cli.list_models()
        elif cmd == "test":
            cli.test()
        elif cmd == "init":
            cli.init()
        elif cmd == "version":
            cli.version()
        else:
            print(f"未知命令: {cmd}")
            print("使用 'flexllm --help' 查看帮助")


if __name__ == "__main__":
    main()
