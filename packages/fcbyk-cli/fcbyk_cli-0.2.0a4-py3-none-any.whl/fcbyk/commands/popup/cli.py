""" popup 命令行接口模块 """

import click

from .service import PopupOptions, PopupService


@click.command(name='popup', help='Display multiple popup windows with random tips at random screen positions')
@click.option('--title', '-t', default='温馨提示', help='Title text for the popup windows')
@click.option('--numbers', '-n', default=20, type=int, help='Number of popup windows to display (default: 20, max recommended: 50)')
@click.argument('tips', nargs=-1)
def popup(title, numbers, tips):
    # 验证参数
    if numbers < 1:
        click.echo("Number of popups must be greater than 0")
        return

    if numbers > 50:
        click.echo(f"Warning: Will create {numbers} windows, this may affect performance!")
        if not click.confirm('Do you want to continue?'):
            return

    service = PopupService()
    opts = PopupOptions(title=title, numbers=numbers, tips=tips)
    service.spawn_many(opts)

