import click

import fcbyk.cli_support.output as output


def test_colored_key_value_returns_string_with_colon(monkeypatch):
    # 避免依赖 click.style 的具体 ANSI 实现，只要被调用即可
    calls = []

    def _style(s, fg=None):
        calls.append((s, fg))
        return f"<{fg}>{s}</{fg}>"

    monkeypatch.setattr(click, "style", _style)

    text = output.colored_key_value("k", "v", key_color="red", value_color="blue")
    assert text == "<red>k</red>: <blue>v</blue>"
    assert calls == [("k", "red"), ("v", "blue")]


def test_show_config_when_value_false_does_nothing(monkeypatch):
    # value=False 时应直接 return，不读配置不退出
    called = {"load": 0, "exit": 0, "echo": 0}

    monkeypatch.setattr(output, "load_json_config", lambda *a, **k: called.__setitem__("load", called["load"] + 1))
    monkeypatch.setattr(click, "echo", lambda *a, **k: called.__setitem__("echo", called["echo"] + 1))

    class _Ctx:
        def exit(self, code=0):
            called["exit"] += 1

    output.show_config(_Ctx(), None, False, "x.json", {"a": 1})
    assert called == {"load": 0, "exit": 0, "echo": 0}


def test_show_config_prints_and_exits(monkeypatch):
    # value=True 时：应输出 config file + 所有字段，并 ctx.exit()
    cfg = {"a": 1, "b": False}

    monkeypatch.setattr(output, "load_json_config", lambda path, default: cfg)
    monkeypatch.setattr(output, "colored_key_value", lambda k, v, **kw: f"{k}={v}")

    lines = []
    monkeypatch.setattr(click, "echo", lambda s: lines.append(s))

    class _Ctx:
        def __init__(self):
            self.exited = False

        def exit(self, code=0):
            self.exited = True

    ctx = _Ctx()
    output.show_config(ctx, None, True, "cfg.json", {"a": 0})

    assert ctx.exited is True
    assert lines[0] == "config file=cfg.json"
    assert set(lines[1:]) == {"a=1", "b=False"}


def test_echo_network_urls_filters_virtual(monkeypatch):
    monkeypatch.setattr(output, "colored_key_value", lambda k, v, **kw: f"{k}{v}")

    lines = []
    monkeypatch.setattr(click, "echo", lambda s: lines.append(s))

    networks = [
        {"iface": "Ethernet", "ips": ["192.168.0.2"], "virtual": False},
        {"iface": "Docker", "ips": ["10.0.0.2"], "virtual": True},
    ]

    output.echo_network_urls(networks, port=5173, include_virtual=False)

    # local 两条 + 只包含非虚拟网卡一条
    assert len(lines) == 3
    assert any("localhost:5173" in s for s in lines)
    assert any("127.0.0.1:5173" in s for s in lines)
    assert any("192.168.0.2:5173" in s for s in lines)
    assert all("10.0.0.2:5173" not in s for s in lines)


def test_echo_network_urls_include_virtual(monkeypatch):
    monkeypatch.setattr(output, "colored_key_value", lambda k, v, **kw: f"{k}{v}")

    lines = []
    monkeypatch.setattr(click, "echo", lambda s: lines.append(s))

    networks = [
        {"iface": "Docker", "ips": ["10.0.0.2"], "virtual": True},
    ]

    output.echo_network_urls(networks, port=80, include_virtual=True)
    assert any("10.0.0.2:80" in s for s in lines)

