import importlib

import pytest


@pytest.fixture
def app_client(tmp_path):
    lansend_controller = importlib.import_module("fcbyk.commands.lansend.controller")
    lansend_service_mod = importlib.import_module("fcbyk.commands.lansend.service")

    # 准备共享目录及文件
    f = tmp_path / "video.bin"
    f.write_bytes(b"0123456789" * 10)  # 100 bytes

    cfg = lansend_service_mod.LansendConfig(shared_directory=str(tmp_path), chat_enabled=True)
    # 开启上传密码，且允许上传路由注册
    cfg.upload_password = "pw"

    service = lansend_service_mod.LansendService(cfg)

    app = lansend_controller.create_lansend_app(service)
    app.config["TESTING"] = True

    with app.test_client() as c:
        yield app, c, service, f


def test_api_config_flags(app_client):
    _app, c, service, _f = app_client
    r = c.get("/api/config")
    assert r.status_code == 200
    assert r.json["chat_enabled"] is True
    # upload_password 字段不在 /api/config，un_download/un_upload 默认 False
    assert r.json["un_upload"] is False


def test_upload_password_check_only(app_client):
    _app, c, service, _f = app_client

    # 缺密码 => 401
    r = c.post("/upload", data={"path": ""})
    assert r.status_code in (400, 401)

    # 仅验证密码：不带 file，但带 password
    r = c.post("/upload", data={"path": "", "password": "pw"})
    assert r.status_code == 200
    assert r.json["message"] in ("password ok",)

    r = c.post("/upload", data={"path": "", "password": "bad"})
    assert r.status_code == 401


def test_api_file_invalid_path_returns_404(app_client):
    _app, c, _service, _f = app_client
    r = c.get("/api/file/../secret")
    assert r.status_code == 404


def test_api_tree_returns_tree(app_client, monkeypatch):
    _app, c, service, _f = app_client

    monkeypatch.setattr(service, "ensure_shared_directory", lambda: "/base")
    monkeypatch.setattr(service, "get_file_tree", lambda base: {"base": base})

    r = c.get("/api/tree")
    assert r.status_code == 200
    assert r.json == {"tree": {"base": "/base"}}


def test_api_preview_range_ok(app_client):
    _app, c, _service, f = app_client

    # Range: bytes=0-9
    r = c.get(f"/api/preview/{f.name}", headers={"Range": "bytes=0-9"})
    assert r.status_code == 206
    assert r.headers.get("Accept-Ranges") == "bytes"
    assert r.headers.get("Content-Range", "").startswith("bytes 0-9/")
    assert len(r.data) == 10


def test_api_preview_range_416(app_client):
    _app, c, _service, f = app_client

    # 超出范围
    r = c.get(f"/api/preview/{f.name}", headers={"Range": "bytes=999-1000"})
    assert r.status_code == 416


def test_api_download_headers_and_content(app_client):
    _app, c, _service, f = app_client

    r = c.get(f"/api/download/{f.name}")
    assert r.status_code == 200
    assert r.headers.get("Accept-Ranges") == "bytes"
    assert "attachment" in r.headers.get("Content-Disposition", "")
    assert r.data.startswith(b"0123456789")


def test_chat_send_and_messages(app_client):
    _app, c, _service, _f = app_client

    # 发送空消息
    r = c.post("/api/chat/send", json={"message": "   "})
    assert r.status_code == 400

    # 正常发送（带 XFF）
    r = c.post(
        "/api/chat/send",
        json={"message": "hello\n"},
        headers={"X-Forwarded-For": "9.9.9.9"},
    )
    assert r.status_code == 200
    assert r.json["success"] is True
    assert r.json["message"]["ip"] == "9.9.9.9"
    assert r.json["message"]["message"] == "hello"  # rstrip

    # 拉取消息
    r = c.get("/api/chat/messages", headers={"X-Forwarded-For": "9.9.9.9"})
    assert r.status_code == 200
    assert r.json["current_ip"] == "9.9.9.9"
    assert len(r.json["messages"]) >= 1

