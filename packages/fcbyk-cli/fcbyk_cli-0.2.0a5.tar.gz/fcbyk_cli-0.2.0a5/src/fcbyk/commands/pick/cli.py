"""
pick 命令行接口模块

提供随机抽奖功能，支持列表抽奖和文件抽奖两种模式。

常量:
- config_file: 配置文件路径
- default_config: 默认配置（items 列表）

函数:
- delayed_newline_simple(): 延迟打印空行（用于改善控制台输出体验）
- pick(): Click 命令入口，处理所有参数和模式切换
"""

import click
from fcbyk.utils.config import get_config_path, load_json_config, save_config
from fcbyk.cli_support.output import show_config
from .service import PickService
from .controller import start_web_server
from fcbyk.utils.port import ensure_port_available

config_file = get_config_path('fcbyk', 'pick.json')

default_config = {
    'items': []
}


@click.command(name='pick', help='Randomly pick one item from the list')
@click.option(
    "--config", "-c",
    is_flag=True,
    callback=lambda ctx, param, value: show_config(
        ctx, param, value, config_file, default_config
    ),
    expose_value=False,
    is_eager=True,
    help="show configuration and exit"
)
@click.option('--add', '-a', multiple=True, help='Add item to list (can be used multiple times)')
@click.option('--remove', '-r', multiple=True, help='Remove item from list (can be used multiple times)')
@click.option('--clear', is_flag=True, help='Clear the list')
@click.option('--list', '-l', 'show_list', is_flag=True, help='Show current list')
@click.option('--web', '-w', is_flag=True, help='Start web picker server')
@click.option('--port', '-p', default=80, show_default=True, type=int, help='Port for web mode')
@click.option('--no-browser', is_flag=True, help='Do not auto-open browser in web mode')
@click.option('--files','-f', type=click.Path(exists=True, dir_okay=True, file_okay=True, readable=True, resolve_path=True), help='Start web file picker with given file')
@click.option('--gen-codes','-gc', type=int, default=5, show_default=True, help='Generate redeem codes for web file picker (only with --files)')
@click.option('--show-codes','-sc', is_flag=True, help='Show the redeem codes in console (only with --files)')
@click.option('--password', '-pw', is_flag=True, default=False, help='Prompt to set admin password (default: 123456 if not set)')
@click.argument('items', nargs=-1)
@click.pass_context
def pick(ctx, add, remove, clear, show_list, web, port, no_browser, files, gen_codes, show_codes, password, items):
    config = load_json_config(config_file, default_config)
    service = PickService(config_file, default_config)
    
    # 端口占用检测
    if files or web:
        try:
            ensure_port_available(port, host="0.0.0.0")
        except OSError as e:
            click.echo(f" Error: Port {port} is already in use (or you don't have permission). Please choose another port (e.g. --port {int(port) + 1}).")
            click.echo(f" Details: {e}")
            return
    
    if show_list:
        items_list = config.get('items', [])
        if items_list:
            click.echo("Current items list:")
            for i, item in enumerate(items_list, 1):
                click.echo(f"  {i}. {item}")
        else:
            click.echo("List is empty. Please use --add to add items")
        return
    
    if clear:
        config['items'] = []
        save_config(config, config_file)
        click.echo("List cleared")
        return
    
    if add:
        items_list = config.get('items', [])
        for item in add:
            if item not in items_list:
                items_list.append(item)
                click.echo(f"Added: {item}")
            else:
                click.echo(f"Item already exists: {item}")
        config['items'] = items_list
        save_config(config, config_file)
        return
    
    if remove:
        items_list = config.get('items', [])
        for item in remove:
            if item in items_list:
                items_list.remove(item)
                click.echo(f"Removed: {item}")
            else:
                click.echo(f"Item does not exist: {item}")
        config['items'] = items_list
        save_config(config, config_file)
        return
    
    if files:
        codes = None
        if gen_codes and gen_codes > 0:
            codes = list(service.generate_redeem_codes(gen_codes))
            if show_codes:
                click.echo()
                click.echo("Generated redeem codes (each can be used once):")
                for c in codes:
                    click.echo(f"  {c}")

        if password:
            admin_password = click.prompt(
                'Admin password (press Enter to use default: 123456)',
                hide_input=True,
                default='123456',
                show_default=False,
            )
            if not admin_password:
                admin_password = '123456'
        else:
            admin_password = '123456'

        start_web_server(
            port,
            no_browser,
            files_root=files,
            codes=codes,
            admin_password=admin_password,
        )
        return

    if web:
        start_web_server(port, no_browser)
        return
    
    # 优先使用命令行参数，否则使用配置文件中的列表
    if items:
        service.pick_item(list(items))
    else:
        items_list = config.get('items', [])
        if not items_list:
            click.echo("Error: No items available")
            click.echo("Usage:")
            click.echo("  1. Use --add to add items: fcbyk pick --add item1 --add item2")
            click.echo("  2. Or provide items directly: fcbyk pick item1 item2 item3")
            return
        service.pick_item(items_list)