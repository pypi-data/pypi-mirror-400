"""
ai 命令行接口模块

常量:
- CONFIG_FILE_URL: 配置文件路径
- DEFAULT_CONFIG: 默认配置（model, api_url, api_key, stream）
- SYSTEM_PROMPT: AI 系统提示词（控制输出格式）

函数:
- _print_streaming_chunks(chunks) -> str: 边打印边拼接流式响应
- _chat_loop(config: dict): 聊天主循环
- ai(): Click 命令入口，处理参数和配置
"""

import click

from fcbyk.cli_support.output import show_config
from fcbyk.utils.config import get_config_path, save_config, get_effective_config

from .service import (
    AIService,
    AIServiceError,
    ChatRequest,
    extract_assistant_reply,
)


CONFIG_FILE_URL = get_config_path('fcbyk', 'openai.json')

DEFAULT_CONFIG = {
    'model': 'deepseek-chat',
    'api_url': 'https://api.deepseek.com/v1/chat/completions',
    'api_key': None,
    'stream': False,
}

SYSTEM_PROMPT = (
    "You are a helpful assistant. Respond in plain text suitable for a console environment. "
    "Avoid using Markdown, code blocks, or any rich formatting. "
    "Use simple line breaks and spaces for alignment."
)


def _print_streaming_chunks(chunks) -> str:
    reply = ''
    click.secho('AI：', fg='blue', nl=False)
    for chunk in chunks:
        delta = chunk['choices'][0]['delta'].get('content', '')
        if delta:
            click.echo(delta, nl=False)
            reply += delta
    click.echo('')
    return reply


def _chat_loop(config: dict):
    service = AIService()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    click.secho('聊天已开始，输入 exit 退出', fg='cyan')

    while True:
        try:
            user_input = input('You: ').strip()
        except (EOFError, KeyboardInterrupt):
            click.secho('\n已退出对话', fg='cyan')
            break

        if user_input.lower() == 'exit':
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        req = ChatRequest(
            messages=messages,
            model=config['model'],
            api_key=config['api_key'],
            api_url=config['api_url'],
            stream=bool(config['stream']),
        )

        try:
            resp_or_chunks = service.chat(req)

            if req.stream:
                reply = _print_streaming_chunks(resp_or_chunks)
            else:
                reply = extract_assistant_reply(resp_or_chunks)
                click.secho('AI：', fg='blue', nl=False)
                click.echo(f' {reply}')

            messages.append({"role": "assistant", "content": reply})

        except AIServiceError as e:
            click.secho(f'错误：{e}', fg='red')
            messages.pop()  # 移除失败的用户消息
        except Exception as e:
            click.secho(f'未知错误：{e}', fg='red')
            messages.pop()


@click.command(name='ai', help='use openai api to chat in terminal')
@click.option(
    "--config", "-c",
    is_flag=True,
    callback=lambda ctx, param, value: show_config(
        ctx, param, value, CONFIG_FILE_URL, DEFAULT_CONFIG
    ),
    expose_value=False,
    is_eager=True,
    help="show config and exit"
)
@click.option('--model', '-m', help='set model')
@click.option('--api-key', '-k', help='set api key')
@click.option('--api-url', '-u', help='set api url (full url)')
@click.option('--stream', '-s', help='set stream, 0 for false, 1 for true')
@click.pass_context
def ai(ctx, model, api_key, api_url, stream):
    cli_options = ctx.params.copy()
    cli_options.pop('config', None)

    effective_config = get_effective_config(cli_options, CONFIG_FILE_URL, DEFAULT_CONFIG)

    # 无参数则进入聊天模式，有参数则保存配置
    if not any([model, api_key, api_url, stream]):
        if not effective_config['api_key']:
            click.secho('错误：未配置 api_key，请先通过 --api-key 或配置文件设置', fg='red', err=True)
            ctx.exit(1)

        _chat_loop(effective_config)
    else:
        save_config(effective_config, CONFIG_FILE_URL)
        click.secho('配置已保存', fg='green')
        ctx.exit()