"""AI 子命令：CLI 层测试

目标：覆盖 fcbyk.commands.ai.cli 中 CLI 入口与聊天循环的主要分支。

覆盖点：
- _print_streaming_chunks: 流式 chunk 打印与拼接
- ai 命令：
  - 未配置 api_key 时退出（exit_code=1）
  - 传入参数时保存配置并退出
- _chat_loop:
  - 非流式回复路径
  - 流式回复路径（只验证分支被走到，不依赖实际 click 输出内容）
  - AIServiceError 分支
  - KeyboardInterrupt/EOF 退出分支

说明：
- 测试通过 monkeypatch input/AIService/click 输出，避免真实交互。
- 不对 Click 的 ANSI/终端行为做严格断言，只关注本项目逻辑。
"""

import importlib


def test_print_streaming_chunks_appends_and_outputs(monkeypatch):
    """_print_streaming_chunks 会把 delta.content 输出并拼接成完整字符串。"""

    from fcbyk.commands.ai.cli import _print_streaming_chunks

    outputs = []

    monkeypatch.setattr("click.secho", lambda *a, **k: outputs.append(("secho", a, k)))
    monkeypatch.setattr("click.echo", lambda *a, **k: outputs.append(("echo", a, k)))

    chunks = [
        {"choices": [{"delta": {"content": "he"}}]},
        {"choices": [{"delta": {"content": ""}}]},
        {"choices": [{"delta": {"content": "llo"}}]},
    ]

    reply = _print_streaming_chunks(chunks)
    assert reply == "hello"


def test_ai_cli_no_api_key_exits_1(monkeypatch):
    """无参数进入聊天模式时，如果 api_key 为空应退出 1。"""

    from click.testing import CliRunner
    from fcbyk.commands.ai.cli import ai

    ai_cli = importlib.import_module("fcbyk.commands.ai.cli")

    # 强制 effective_config 没有 api_key
    monkeypatch.setattr(
        ai_cli,
        "get_effective_config",
        lambda *a, **k: {
            "model": "m",
            "api_url": "u",
            "api_key": None,
            "stream": False,
        },
    )

    result = CliRunner().invoke(ai, [])
    assert result.exit_code == 1
    assert "未配置 api_key" in result.output


def test_ai_cli_with_options_saves_config_and_exits(monkeypatch):
    """传入任意配置项参数时应保存配置并退出。"""

    from click.testing import CliRunner
    from fcbyk.commands.ai.cli import ai

    ai_cli = importlib.import_module("fcbyk.commands.ai.cli")

    saved = {}

    monkeypatch.setattr(
        ai_cli,
        "get_effective_config",
        lambda cli_options, *a, **k: {
            "model": cli_options.get("model") or "m",
            "api_url": cli_options.get("api_url") or "u",
            "api_key": cli_options.get("api_key") or "k",
            "stream": cli_options.get("stream") or False,
        },
    )

    monkeypatch.setattr(
        ai_cli,
        "save_config",
        lambda cfg, path: saved.update({"cfg": cfg, "path": path}),
    )

    result = CliRunner().invoke(ai, ["--model", "x"])
    assert result.exit_code == 0
    assert "配置已保存" in result.output
    assert saved["cfg"]["model"] == "x"


def test_ai_cli_chat_loop_non_stream_happy_path(monkeypatch):
    """_chat_loop 非流式分支：输入 hi -> exit，输出应包含回复内容。"""

    ai_cli = importlib.import_module("fcbyk.commands.ai.cli")

    # mock input 序列：hi, exit
    inputs = iter(["hi", "exit"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))

    # mock AIService
    class _Svc:
        def chat(self, req):
            return {"choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(ai_cli, "AIService", lambda: _Svc())

    # mock 输出
    lines = []
    monkeypatch.setattr("click.echo", lambda s="", **k: lines.append(str(s)))
    monkeypatch.setattr("click.secho", lambda s="", **k: lines.append(str(s)))

    ai_cli._chat_loop({"model": "m", "api_url": "u", "api_key": "k", "stream": False})

    joined = "\n".join(lines)
    assert "聊天已开始" in joined
    assert "ok" in joined


def test_ai_cli_chat_loop_stream_happy_path(monkeypatch):
    """_chat_loop 流式分支：确保走到 _print_streaming_chunks 分支即可。"""

    ai_cli = importlib.import_module("fcbyk.commands.ai.cli")

    inputs = iter(["hi", "exit"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))

    chunks = [
        {"choices": [{"delta": {"content": "he"}}]},
        {"choices": [{"delta": {"content": "llo"}}]},
    ]

    class _Svc:
        def chat(self, req):
            return chunks

    monkeypatch.setattr(ai_cli, "AIService", lambda: _Svc())

    called = {"n": 0}

    def _print_chunks(ch):
        called["n"] += 1
        return "hello"

    monkeypatch.setattr(ai_cli, "_print_streaming_chunks", _print_chunks)

    # 不断言输出内容，只断言分支被调用
    ai_cli._chat_loop({"model": "m", "api_url": "u", "api_key": "k", "stream": True})
    assert called["n"] == 1


def test_ai_cli_chat_loop_ai_service_error(monkeypatch):
    """AIServiceError 分支：发生错误时应输出错误提示并继续循环。"""

    ai_cli = importlib.import_module("fcbyk.commands.ai.cli")

    inputs = iter(["hi", "exit"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))

    class _Svc:
        def chat(self, req):
            raise ai_cli.AIServiceError("boom")

    monkeypatch.setattr(ai_cli, "AIService", lambda: _Svc())

    lines = []
    monkeypatch.setattr("click.secho", lambda s="", **k: lines.append(str(s)))
    monkeypatch.setattr("click.echo", lambda s="", **k: lines.append(str(s)))

    ai_cli._chat_loop({"model": "m", "api_url": "u", "api_key": "k", "stream": False})
    assert any("错误：" in x for x in lines)


def test_ai_cli_chat_loop_keyboard_interrupt_exits(monkeypatch):
    """KeyboardInterrupt/EOFError 应中断聊天循环并提示退出。"""

    ai_cli = importlib.import_module("fcbyk.commands.ai.cli")

    def _raise(*_a, **_k):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", _raise)

    lines = []
    monkeypatch.setattr("click.secho", lambda s="", **k: lines.append(str(s)))

    ai_cli._chat_loop({"model": "m", "api_url": "u", "api_key": "k", "stream": False})
    assert any("已退出对话" in x for x in lines)
