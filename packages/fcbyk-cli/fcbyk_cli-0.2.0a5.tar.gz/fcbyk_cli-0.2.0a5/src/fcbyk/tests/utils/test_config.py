import json
import os

from fcbyk.utils.config import load_json_config, save_config, get_effective_config


def test_load_json_config_creates_file_and_fills_defaults(tmp_path):
    cfg = tmp_path / "cfg" / "a.json"
    default = {"a": 1, "b": False}

    loaded = load_json_config(str(cfg), default)
    assert loaded == default
    assert cfg.exists()

    # 文件内容也应是补齐后的
    data = json.loads(cfg.read_text(encoding="utf-8"))
    assert data == default


def test_load_json_config_repairs_broken_json(tmp_path):
    cfg = tmp_path / "cfg" / "a.json"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text("{bad json", encoding="utf-8")

    default = {"a": 1}
    loaded = load_json_config(str(cfg), default)
    assert loaded == default


def test_load_json_config_fills_missing_fields(tmp_path):
    cfg = tmp_path / "cfg" / "a.json"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(json.dumps({"a": 1}), encoding="utf-8")

    default = {"a": 1, "b": 2}
    loaded = load_json_config(str(cfg), default)
    assert loaded == {"a": 1, "b": 2}


def test_save_config_writes_json(tmp_path):
    cfg = tmp_path / "a.json"
    save_config({"x": 1}, str(cfg))
    assert json.loads(cfg.read_text(encoding="utf-8")) == {"x": 1}


def test_get_effective_config_precedence_and_bool_parse(tmp_path):
    cfg = tmp_path / "a.json"

    default = {"model": "m0", "stream": False, "n": 1}
    # 配置文件先写入一个值
    save_config({"model": "m1", "stream": False, "n": 2}, str(cfg))

    cli_options = {"model": "m2", "stream": "1", "n": None}

    eff = get_effective_config(cli_options, str(cfg), default)

    # CLI > file > default
    assert eff["model"] == "m2"
    assert eff["stream"] is True
    # n 传 None => 不覆盖 file 中的 2
    assert eff["n"] == 2


def test_get_effective_config_fields_subset(tmp_path):
    cfg = tmp_path / "a.json"
    default = {"a": 1, "b": 2, "stream": False}
    save_config({"a": 10, "b": 20, "stream": False}, str(cfg))

    eff = get_effective_config({"b": 99, "stream": "1"}, str(cfg), default, fields=["b"])

    # 只处理 b 字段
    assert eff["a"] == 10
    assert eff["b"] == 99
    assert eff["stream"] is False

