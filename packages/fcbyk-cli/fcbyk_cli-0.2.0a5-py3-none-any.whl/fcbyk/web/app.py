import os
from flask import Flask, redirect, send_from_directory, make_response

def create_spa(
    entry_html: str,
    root: str = "dist",
    page=None,
    cli_data=None,
) -> Flask:
    """
    entry_html: SPA 入口文件，如 'slide.html'
    dist/
      ├─ slide.html
      └─ assets/
         ├─ xxx.js
         └─ xxx.css
    """
    app = Flask(
        __name__,
        static_folder=f"{root}/assets",
        static_url_path="/assets"
    )

    dist_root = os.path.join(app.root_path, root)

    # SPA 入口
    @app.route("/")
    def index():
        response = make_response(send_from_directory(dist_root, entry_html))
        # 禁用缓存，防止切换应用时显示旧的 HTML
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    # 前端路由列表 - 统一返回入口主页
    if page:
        for url in page:
            def view(entry_html=entry_html, dist_root=dist_root):
                response = make_response(send_from_directory(dist_root, entry_html))
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                return response

            # 保证每个路由的 endpoint 唯一
            endpoint = f"page_{url.strip('/').replace('/', '_') or 'root'}"
            app.add_url_rule(url, endpoint, view)

    if cli_data:
        app.cli_data = cli_data

    return app


def create_app(
    default_page,
    page_map = None,
    cli_data = None
) -> Flask:
    """
    创建并配置 Flask 应用，用于提供静态 HTML 页面服务。

    - 根路径 "/" 重定向到默认页面
    - 按语义 URL 映射静态 HTML 页面

    Args:
        default_page(str): 默认入口页面路径，如 "pick/index.html"
        page_map(dict | None): 语义 URL 与 HTML 文件路径映射
        cli_data(any | None): 附加到 app 的命令行数据，供蓝图使用

    Returns:
        Flask: 已配置的 Flask 应用实例
    """
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/"
    )

    static_root = os.path.join(app.root_path, "static")

    # 根路径 "/" → 重定向到默认页面
    @app.route("/")
    def index():
        return redirect(f"/{default_page}")

    # 注册语义 URL → 静态 HTML 页面
    if page_map:
        for url, file in page_map.items():
            def view(file=file):
                """从静态目录中返回指定的 HTML 文件。"""
                dir_, name = os.path.split(file)
                return send_from_directory(
                    os.path.join(static_root, dir_),
                    name
                )

            # 保证每个路由的 endpoint 唯一
            endpoint = f"page_{url.strip('/').replace('/', '_') or 'root'}"
            app.add_url_rule(url, endpoint, view)
        
    if cli_data:
        app.cli_data = cli_data

    return app