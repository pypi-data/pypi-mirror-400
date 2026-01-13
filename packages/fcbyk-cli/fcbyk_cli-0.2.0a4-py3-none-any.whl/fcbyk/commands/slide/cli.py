"""
slide 命令行接口模块
提供 PPT 远程控制的 CLI 命令
"""
import click
import pyperclip

from fcbyk.utils.port import ensure_port_available

from .service import SlideService
from .controller import create_slide_app
from fcbyk.cli_support.output import echo_network_urls
from fcbyk.utils.network import get_private_networks


@click.command(name='slide', help='Start PPT remote control server, control slides via mobile web page')
@click.option(
    "-p", "--port",
    default=80,
    help="Web server port (default: 80)"
)
def slide(port):
    """启动 PPT 远程控制服务器"""

    # 端口占用检测
    try:
        ensure_port_available(port, host="0.0.0.0")
    except OSError as e:
        click.echo(
            f" Error: Port {port} is already in use (or you don't have permission). "
            f" Please choose another port (e.g. --port {int(port) + 1})."
        )
        click.echo(f" * Details: {e}")
        return
    
    # 提示用户设置密码
    while True:
        password = click.prompt(
            "Please set access password",
            hide_input=True,
            confirmation_prompt=True
        )
        if password:
            break
        click.echo(" Error: Password cannot be empty")
    
    click.echo()

    # 创建服务
    service = SlideService(password)

    # 创建 Flask 应用和 SocketIO
    app, socketio = create_slide_app(service)
    
    # 获取网络信息
    private_networks = get_private_networks()
    if private_networks:
        local_ip = private_networks[0]["ips"][0]
    else:
        local_ip = "127.0.0.1"
        click.echo(" Warning: No private network interface found, using localhost")
        
    # 显示启动信息
    click.echo(f" PPT Remote Control Server")
    echo_network_urls(private_networks, port, include_virtual=True)
    click.echo(f" Open the URL above on your mobile device to control")

    # 复制 URL 到剪贴板
    try:
        pyperclip.copy(f"http://{local_ip}:{port}")
        click.echo(" URL has been copied to clipboard")
    except:
        click.echo(" Warning: Could not copy URL to clipboard")
    
    click.echo()

    # 运行服务器（使用 socketio.run 以支持 WebSocket）
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)