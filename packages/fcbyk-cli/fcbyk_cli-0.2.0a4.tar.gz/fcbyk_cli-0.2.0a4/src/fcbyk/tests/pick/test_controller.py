import os

import pytest
import importlib

pick_controller = importlib.import_module("fcbyk.commands.pick.controller")


@pytest.fixture
def client(monkeypatch):
    # 隔离全局状态（controller 模块是全局单例 app/service）
    pick_controller.files_mode_root = None
    pick_controller.ADMIN_PASSWORD = None
    pick_controller.service.reset_state()

    pick_controller.app.config["TESTING"] = True
    with pick_controller.app.test_client() as c:
        yield c


def test_api_info_default(client):
    r = client.get("/api/info")
    assert r.status_code == 200
    assert r.json == {"files_mode": False}


def test_api_items_reads_config(monkeypatch, client):
    monkeypatch.setattr(pick_controller, "load_json_config", lambda *a, **k: {"items": ["a", "b"]})
    r = client.get("/api/items")
    assert r.status_code == 200
    assert r.json == {"items": ["a", "b"]}


def test_get_client_ip_prefers_xff(client):
    # 直接调用函数（需要请求上下文）
    with pick_controller.app.test_request_context(
        "/api/items",
        headers={"X-Forwarded-For": "9.9.9.9, 8.8.8.8"},
        environ_base={"REMOTE_ADDR": "1.1.1.1"},
    ):
        assert pick_controller._get_client_ip() == "9.9.9.9"


def test_get_client_ip_fallback_remote_addr(client):
    with pick_controller.app.test_request_context(
        "/api/items",
        headers={},
        environ_base={"REMOTE_ADDR": "2.2.2.2"},
    ):
        assert pick_controller._get_client_ip() == "2.2.2.2"


def test_api_pick_item_no_items(monkeypatch, client):
    monkeypatch.setattr(pick_controller, "load_json_config", lambda *a, **k: {"items": []})
    r = client.post("/api/pick")
    assert r.status_code == 400
    assert r.json["error"] == "no items available"


def test_api_pick_item_success(monkeypatch, client):
    monkeypatch.setattr(pick_controller, "load_json_config", lambda *a, **k: {"items": ["a", "b"]})
    monkeypatch.setattr(pick_controller.service, "pick_random_item", lambda items: "b")

    r = client.post("/api/pick")
    assert r.status_code == 200
    assert r.json == {"item": "b", "items": ["a", "b"]}


def test_api_files_requires_files_mode(client):
    pick_controller.files_mode_root = None
    r = client.get("/api/files")
    assert r.status_code == 400


def test_api_files_pick_requires_files_mode(client):
    pick_controller.files_mode_root = None
    r = client.post("/api/files/pick", json={"code": "AAAA"})
    assert r.status_code == 400


def test_api_files_code_mode_invalid_cases(tmp_path, client, monkeypatch):
    # files_mode_root + redeem_codes
    pick_controller.files_mode_root = str(tmp_path)
    pick_controller.service.reset_state()
    pick_controller.service.redeem_codes = {"ABCD": False}

    monkeypatch.setattr(pick_controller.service, "list_files", lambda root: [{"name": "a.txt", "path": "x", "size": 1}])
    monkeypatch.setattr(pick_controller, "_get_client_ip", lambda: "1.2.3.4")

    # 缺少 code
    r = client.post("/api/files/pick", json={})
    assert r.status_code == 400

    # code 无效
    r = client.post("/api/files/pick", json={"code": "ZZZZ"})
    assert r.status_code == 400

    # code 已使用
    pick_controller.service.redeem_codes["ABCD"] = True
    r = client.post("/api/files/pick", json={"code": "ABCD"})
    assert r.status_code == 429


def test_api_files_pick_code_mode_happy_path(tmp_path, client, monkeypatch):
    # 准备 files_mode_root 目录与文件
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("a", encoding="utf-8")
    f2.write_text("bb", encoding="utf-8")

    pick_controller.files_mode_root = str(tmp_path)

    # 设置兑换码模式
    pick_controller.service.reset_state()
    pick_controller.service.redeem_codes = {"ABCD": False}

    monkeypatch.setattr(
        pick_controller.service,
        "list_files",
        lambda root: [
            {"name": "a.txt", "path": str(f1), "size": 1},
            {"name": "b.txt", "path": str(f2), "size": 2},
        ],
    )
    monkeypatch.setattr(pick_controller.service, "pick_file", lambda cands: cands[0])
    monkeypatch.setattr(pick_controller, "_get_client_ip", lambda: "1.2.3.4")

    r = client.post("/api/files/pick", json={"code": "abcd"})
    assert r.status_code == 200
    assert r.json["mode"] == "code"
    assert r.json["code"] == "ABCD"
    assert r.json["file"]["name"] == "a.txt"

    # result 可以查询
    r2 = client.get("/api/files/result/ABCD")
    assert r2.status_code == 200
    assert r2.json["code"] == "ABCD"


def test_api_files_result_not_found(tmp_path, client):
    pick_controller.files_mode_root = str(tmp_path)
    pick_controller.service.reset_state()

    r = client.get("/api/files/result/NOPE")
    assert r.status_code == 404


def test_api_files_pick_ip_mode_and_already_picked(tmp_path, client, monkeypatch):
    # ip 模式：redeem_codes 为空
    pick_controller.files_mode_root = str(tmp_path)
    pick_controller.service.reset_state()

    files = [
        {"name": "a.txt", "path": str(tmp_path / "a.txt"), "size": 1},
    ]
    monkeypatch.setattr(pick_controller.service, "list_files", lambda root: files)
    monkeypatch.setattr(pick_controller.service, "pick_file", lambda cands: cands[0])
    monkeypatch.setattr(pick_controller, "_get_client_ip", lambda: "1.1.1.1")

    # 第一次
    r1 = client.post("/api/files/pick")
    assert r1.status_code == 200
    assert r1.json["mode"] == "ip"

    # 第二次（已抽过）
    r2 = client.post("/api/files/pick")
    assert r2.status_code == 429
    assert r2.json["error"] == "already picked"


def test_download_file_dir_mode_invalid_path_and_not_found(tmp_path, client):
    pick_controller.files_mode_root = str(tmp_path)

    # 路径穿越
    r = client.get("/api/files/download/../x")
    assert r.status_code == 400

    # 文件不存在
    r = client.get("/api/files/download/nope.txt")
    assert r.status_code == 404


def test_download_file_single_file_mode_wrong_name(tmp_path, client):
    f = tmp_path / "a.txt"
    f.write_text("hi", encoding="utf-8")

    pick_controller.files_mode_root = str(f)

    r = client.get("/api/files/download/other.txt")
    assert r.status_code == 404


def test_download_file_single_file_mode_success(tmp_path, client):
    f = tmp_path / "a.txt"
    f.write_text("hi", encoding="utf-8")

    pick_controller.files_mode_root = str(f)

    r = client.get("/api/files/download/a.txt")
    assert r.status_code == 200
    assert r.data == b"hi"


def test_start_web_server_sets_state_and_opens_browser(monkeypatch, tmp_path):
    # 避免真正启动 Flask 服务器
    ran = {}

    # Mock waitress.serve（延迟导入，使用 sys.modules）
    import sys
    import types
    mock_waitress = types.ModuleType('waitress')
    def mock_serve(app, **kw):
        ran.update(kw)
    mock_waitress.serve = mock_serve
    sys.modules['waitress'] = mock_waitress
    
    monkeypatch.setattr(pick_controller.socket, "gethostname", lambda: "h")
    monkeypatch.setattr(pick_controller.socket, "gethostbyname", lambda h: "10.0.0.9")

    opened = {"ok": 0}
    monkeypatch.setattr(pick_controller.webbrowser, "open", lambda *_: opened.__setitem__("ok", opened["ok"] + 1))

    # 带 files_root + codes
    froot = tmp_path
    pick_controller.start_web_server(
        port=1234,
        no_browser=False,
        files_root=str(froot),
        codes=["ab", ""],
        admin_password="pw",
    )

    assert pick_controller.ADMIN_PASSWORD == "pw"
    assert pick_controller.files_mode_root == os.path.abspath(str(froot))
    assert "AB" in pick_controller.service.redeem_codes
    assert opened["ok"] == 1
    assert ran["host"] == "0.0.0.0"
    assert ran["port"] == 1234


def test_admin_login_and_codes_add(client):
    pick_controller.ADMIN_PASSWORD = "pw"

    # 登录失败
    r = client.post("/api/admin/login", json={"password": "x"})
    assert r.status_code == 401

    # 登录成功
    r = client.post("/api/admin/login", json={"password": "pw"})
    assert r.status_code == 200
    assert r.json == {"success": True}

    # codes 需要 header
    r = client.get("/api/admin/codes")
    assert r.status_code == 401

    # 新增 code：非法字符
    r = client.post("/api/admin/codes/add", headers={"X-Admin-Password": "pw"}, json={"code": "A-1"})
    assert r.status_code == 400

    # 新增 code：空
    r = client.post("/api/admin/codes/add", headers={"X-Admin-Password": "pw"}, json={"code": ""})
    assert r.status_code == 400

    # 新增 code：成功
    r = client.post("/api/admin/codes/add", headers={"X-Admin-Password": "pw"}, json={"code": "A1b2"})
    assert r.status_code == 200
    assert r.json["success"] is True
    assert r.json["code"] == "A1B2"

    # 新增 code：重复
    r = client.post("/api/admin/codes/add", headers={"X-Admin-Password": "pw"}, json={"code": "A1B2"})
    assert r.status_code == 400

    # 获取 codes
    r = client.get("/api/admin/codes", headers={"X-Admin-Password": "pw"})
    assert r.status_code == 200
    assert r.json["total_codes"] == 1
    assert r.json["used_codes"] == 0
    assert r.json["left_codes"] == 1
