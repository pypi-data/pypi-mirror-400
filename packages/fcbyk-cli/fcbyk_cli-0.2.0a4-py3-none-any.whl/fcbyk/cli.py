#!/usr/bin/env python3
import click
import logging
import sys

# 禁用 Flask 的日志
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from .commands import lansend, ls, ai, pick, jiahao, popup, slide

# 动态导入 GUI 模块（可选依赖）
try:
    from .gui.app import HAS_GUI, show_gui
except ImportError:
    HAS_GUI = False
    show_gui = None

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    
    version = "unknown"
    try:
        # 优先使用现代方法 (Python 3.8+)
        from importlib import metadata
        version = metadata.version("fcbyk-cli")
    except ImportError:
        # 回退到旧方法 (Python 3.6/3.7)
        try:
            import pkg_resources
            version = pkg_resources.get_distribution("fcbyk-cli").version
        except Exception:
            pass
     
    click.echo("v{}".format(version))
    ctx.exit()

def print_gui(ctx, param, value):
    """启动 GUI 窗口"""
    if not value or ctx.resilient_parsing:
        return
    
    if not HAS_GUI:
        click.echo("错误: GUI 功能未安装。", err=True)
        click.echo("请使用以下命令安装 GUI 依赖：", err=True)
        click.echo("  pip install fcbyk-cli[gui]", err=True)
        click.echo("或", err=True)
        click.echo("  pip install PySide6", err=True)
        ctx.exit(1)
    
    try:
        result = show_gui()
        if result == "activated":
            click.echo("GUI 已在运行，已唤醒并置前（如果被遮挡请看任务栏）。")
        else:
            click.echo("GUI 正在启动...（已在独立进程运行）")
    except Exception as e:
        click.echo(f"启动 GUI 时出错: {e}", err=True)
        ctx.exit(1)

    ctx.exit()

def print_kill_gui(ctx, param, value):
    """退出 GUI 进程（如果正在运行）"""
    if not value or ctx.resilient_parsing:
        return

    if not HAS_GUI:
        click.echo("GUI 功能未安装，无法退出 GUI。", err=True)
        ctx.exit(1)

    try:
        from .gui.app import kill_gui
        result = kill_gui(force=True)
        if result == "terminated":
            click.echo("GUI 无响应，已强制结束进程。")
        elif result == "requested":
            click.echo("已发送退出指令给 GUI。")
        elif result == "not_running":
            click.echo("未发现正在运行的 GUI。")
        else:
            click.echo("退出 GUI 失败（未能连接单例通道，也未找到 PID 文件）。", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"退出 GUI 时出错: {e}", err=True)
        ctx.exit(1)

    ctx.exit()

# 创建 CLI（在定义阶段动态附加可选参数）
# 注意：不能在 click 回调函数内部重新绑定 cli（会导致 cli=None / 装饰器失效）

def _add_gui_options(func):
    if HAS_GUI:
        func = click.option('--kill-gui', is_flag=True, callback=print_kill_gui, expose_value=False, is_eager=True, help='Kill/quit GUI process.')(func)
        func = click.option('--gui', is_flag=True, callback=print_gui, expose_value=False, is_eager=True, help='Launch GUI window.')(func)
    return func

@click.group(
    context_settings=dict(help_option_names=['-h', '--help']),
    invoke_without_command=True
)
@click.option('--version', '-v', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Show version and exit.')
@_add_gui_options
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(r'''
  ______ _____ ______     ___  __      _____ _      _____ 
 |  ____/ ____|  _ \ \   / / |/ /     / ____| |    |_   _|
 | |__ | |    | |_) \ \_/ /| ' /_____| |    | |      | |  
 |  __|| |    |  _ < \   / |  <______| |    | |      | |  
 | |   | |____| |_) | | |  | . \     | |____| |____ _| |_ 
 |_|    \_____|____/  |_|  |_|\_\     \_____|______|_____|                                                                                                                                            
    ''')
        click.echo(ctx.get_help())

# 添加子命令
cli.add_command(lansend)
cli.add_command(ls)
cli.add_command(ai)
cli.add_command(pick)
cli.add_command(jiahao)
cli.add_command(popup)
cli.add_command(slide)

if __name__ == "__main__":
    cli()
