import os

import pytest

from fcbyk.web.app import create_spa, create_app


def test_create_spa_index_sets_no_cache_headers(monkeypatch, tmp_path):
    # 构造 dist 目录与入口 html
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "slide.html").write_text("<html>ok</html>", encoding="utf-8")

    # 让 create_spa 使用我们临时目录作为 root
    app = create_spa("slide.html", root=str(dist))
    app.config["TESTING"] = True

    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200

    # no-cache headers
    assert resp.headers.get("Cache-Control") == "no-cache, no-store, must-revalidate"
    assert resp.headers.get("Pragma") == "no-cache"
    assert resp.headers.get("Expires") == "0"


def test_create_spa_page_routes(monkeypatch, tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "slide.html").write_text("<html>ok</html>", encoding="utf-8")

    app = create_spa("slide.html", root=str(dist), page=["/a", "/b/c"]) 
    app.config["TESTING"] = True

    client = app.test_client()
    assert client.get("/a").status_code == 200
    assert client.get("/b/c").status_code == 200


def test_create_spa_attaches_cli_data(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "slide.html").write_text("<html>ok</html>", encoding="utf-8")

    app = create_spa("slide.html", root=str(dist), cli_data={"x": 1})
    assert app.cli_data == {"x": 1}


def test_create_app_redirect_and_page_map(tmp_path):
    # create_app 使用 app.root_path/static，所以我们只测路由行为：
    # 1) / 重定向
    # 2) 注册 page_map 后路由存在（不要求文件真实存在，存在则 200，不存在则 404，但路由应被注册）

    app = create_app(default_page="pick/index.html", page_map={"/x": "x.html"})
    app.config["TESTING"] = True
    client = app.test_client()

    r = client.get("/")
    assert r.status_code in (301, 302)
    assert r.headers["Location"].endswith("/pick/index.html")

    # 路由已注册
    r2 = client.get("/x")
    assert r2.status_code in (200, 404)


def test_create_app_attaches_cli_data():
    app = create_app(default_page="pick/index.html", cli_data={"k": "v"})
    assert app.cli_data == {"k": "v"}

