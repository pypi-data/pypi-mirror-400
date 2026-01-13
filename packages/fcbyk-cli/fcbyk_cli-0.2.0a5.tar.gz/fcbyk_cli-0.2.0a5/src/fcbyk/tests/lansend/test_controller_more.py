import importlib

import pytest


def test_api_directory_when_no_shared_dir_returns_error():
    # 用真实 LansendService，但让 ensure_shared_directory 抛错
    lansend_controller = importlib.import_module("fcbyk.commands.lansend.controller")
    lansend_service_mod = importlib.import_module("fcbyk.commands.lansend.service")

    cfg = lansend_service_mod.LansendConfig(shared_directory=None)
    service = lansend_service_mod.LansendService(cfg)

    app = lansend_controller.create_lansend_app(service)
    app.config["TESTING"] = True

    with app.test_client() as c:
        r = c.get("/api/directory")
        # 不强依赖具体状态码（实现可能是 400/500）
        assert r.status_code in (400, 500)


def test_api_download_path_traversal_returns_not_ok(tmp_path):
    lansend_controller = importlib.import_module("fcbyk.commands.lansend.controller")
    lansend_service_mod = importlib.import_module("fcbyk.commands.lansend.service")

    cfg = lansend_service_mod.LansendConfig(shared_directory=str(tmp_path))
    service = lansend_service_mod.LansendService(cfg)

    app = lansend_controller.create_lansend_app(service)
    app.config["TESTING"] = True

    with app.test_client() as c:
        r = c.get("/api/download/../secret")
        # 只要不是 200 即可（可能 400/403/404）
        assert r.status_code != 200
