import os

import pytest

import importlib

pick_service_mod = importlib.import_module("fcbyk.commands.pick.service")
PickService = pick_service_mod.PickService


def test_list_files_returns_empty_on_none():
    s = PickService("cfg.json", {"items": []})
    assert s.list_files(None) == []


def test_list_files_single_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hi", encoding="utf-8")

    s = PickService("cfg.json", {"items": []})
    out = s.list_files(str(f))
    assert out == [{"name": "a.txt", "path": str(f), "size": 2}]


def test_list_files_directory_sorted(tmp_path):
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "a.txt").write_text("aa", encoding="utf-8")

    s = PickService("cfg.json", {"items": []})
    out = s.list_files(str(tmp_path))

    assert [x["name"] for x in out] == ["a.txt", "b.txt"]


def test_list_files_dir_not_found(tmp_path):
    s = PickService("cfg.json", {"items": []})
    out = s.list_files(str(tmp_path / "missing"))
    assert out == []


def test_generate_redeem_codes_properties():
    s = PickService("cfg.json", {"items": []})
    codes = list(s.generate_redeem_codes(10, length=4))
    assert len(codes) == 10
    assert len(set(codes)) == 10
    assert all(len(c) == 4 for c in codes)
    assert all(c.isalnum() and c.upper() == c for c in codes)


def test_pick_item_empty_items_prints_error(monkeypatch):
    s = PickService("cfg.json", {"items": []})

    lines = []
    monkeypatch.setattr("click.echo", lambda msg="", **k: lines.append(msg))

    s.pick_item([])
    assert any("No items available" in str(x) for x in lines)


def test_pick_item_runs_animation_without_sleep(monkeypatch):
    s = PickService("cfg.json", {"items": []})

    # 减少随机次数 + 禁用 sleep
    monkeypatch.setattr(pick_service_mod.random, "randint", lambda a, b: a)
    monkeypatch.setattr(pick_service_mod.time, "sleep", lambda *_: None)
    monkeypatch.setattr(pick_service_mod.random, "choice", lambda items: items[0])

    lines = []
    monkeypatch.setattr("click.echo", lambda msg="", **k: lines.append(msg))

    s.pick_item(["x", "yy"])
    assert any("Random Pick" in str(x) for x in lines)
    assert any("Pick finished" in str(x) for x in lines)

