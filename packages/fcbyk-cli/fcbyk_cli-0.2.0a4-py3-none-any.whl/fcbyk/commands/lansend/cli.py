"""
lansend 命令行接口模块

对外提供 lansend / ls 命令，用于在局域网内共享文件。

函数:
- _lansend_impl(port, directory, password, no_browser, un_download, un_upload, chat): 启动文件共享服务的核心实现
- lansend(): Click 命令入口，提供完整参数选项
- ls(): Click 命令入口，lansend 的别名
"""

import os
import webbrowser
from fcbyk.utils.port import ensure_port_available

import click
import pyperclip

from fcbyk.cli_support.output import echo_network_urls
from fcbyk.utils.network import get_private_networks

from .controller import create_lansend_app
from .service import LansendConfig, LansendService


def _lansend_impl(port: int, directory: str, password: bool = False, no_browser: bool = False, un_download: bool = False, un_upload: bool = False, chat: bool = False):
    if not os.path.exists(directory):
        click.echo(f"Error: Directory {directory} does not exist")
        return

    if not os.path.isdir(directory):
        click.echo(f"Error: {directory} is not a directory")
        return

    shared_directory = os.path.abspath(directory)

    config = LansendConfig(
        shared_directory=shared_directory,
        upload_password=None,
        un_download=un_download,
        un_upload=un_upload,
        chat_enabled=chat,
    )
    service = LansendService(config)
    config.upload_password = service.pick_upload_password(password, un_upload, click)
    
    click.echo()
    private_networks = get_private_networks()
    if private_networks:
        local_ip = private_networks[0]["ips"][0]
    else:
        local_ip = "127.0.0.1"
        click.echo(" * Warning: No private network interface found, using localhost")

    try:
        ensure_port_available(port, host="0.0.0.0")
    except OSError as e:
        click.echo(
            f" Error: Port {port} is already in use (or you don't have permission). "
            f" Please choose another port (e.g. --port {int(port) + 1})."
        )
        click.echo(f" Details: {e}")
        return

    click.echo(f" Directory: {shared_directory}")
    if config.upload_password:
        click.echo(" Upload Password: Enabled")
    echo_network_urls(private_networks, port, include_virtual=True)

    try:
        pyperclip.copy(f"http://{local_ip}:{port}")
        click.echo(" URL has been copied to clipboard")
    except Exception:
        click.echo(" Warning: Could not copy URL to clipboard")

    if not no_browser:
        webbrowser.open(f"http://{local_ip}:{port}")
    click.echo()
    app = create_lansend_app(service)
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)


@click.command(help="Start a local web server for sharing files over LAN")
@click.option("-p", "--port", default=80, help="Web server port (default: 80)")
@click.option("-d", "--directory", default=".", help="Directory to share (default: current directory)")
@click.option(
    "-pw",
    "--password",
    is_flag=True,
    default=False,
    help="Prompt to set upload password (default: no password, or 123456 if skipped)",
)
@click.option("-nb", "--no-browser", is_flag=True, help="Disable automatic browser opening")
@click.option("-un-d","--un-download", is_flag=True, default=False, help="Hide download buttons in directory tab")
@click.option("-un-up","--un-upload", is_flag=True, default=False, help="Disable upload functionality")
@click.option("--chat", is_flag=True, default=False, help="Enable chat functionality")
def lansend(port, directory, password, no_browser, un_download: bool = False, un_upload: bool = False, chat: bool = False):
    _lansend_impl(port, directory, password, no_browser, un_download, un_upload, chat)


@click.command(name="ls", help="alias for lansend")
@click.option("-p", "--port", default=80, help="Web server port (default: 80)")
@click.option("-d", "--directory", default=".", help="Directory to share (default: current directory)")
@click.option(
    "-pw",
    "--password",
    is_flag=True,
    default=False,
    help="Prompt to set upload password (default: no password, or 123456 if skipped)",
)
@click.option("-nb", "--no-browser", is_flag=True, help="Disable automatic browser opening")
@click.option("-un-d","--un-download", is_flag=True, default=False, help="Hide download buttons in directory tab")
@click.option("-un-up","--un-upload", is_flag=True, default=False, help="Disable upload functionality")
@click.option("--chat", is_flag=True, default=False, help="Enable chat functionality")
def ls(port, directory, password, no_browser, un_download: bool = False, un_upload: bool = False, chat: bool = False):
    _lansend_impl(port, directory, password, no_browser, un_download, un_upload, chat)

