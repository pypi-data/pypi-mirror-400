"""
pick 业务逻辑层

负责抽奖核心逻辑：文件列表、随机选择、兑换码生成、抽奖动画等。

类:
- PickService: 抽奖服务核心类
  - reset_state(): 重置所有抽奖状态
  - list_files(files_mode_root) -> List[Dict]: 列出文件模式下可供抽取的文件
  - pick_file(candidates) -> Dict: 从候选文件列表中随机选择一个
  - pick_random_item(items) -> str: 从列表中随机选择一个元素
  - generate_redeem_codes(count, length) -> Iterable[str]: 生成若干个随机兑换码
  - pick_item(items): 执行抽奖动画（命令行模式）

状态管理:
- ip_draw_records: IP 抽奖记录（旧逻辑，按 IP 限制）
- redeem_codes: 兑换码使用状态（新逻辑，按兑换码限制）
- ip_file_history: IP 文件历史（避免同一 IP 重复抽到同一文件）
- code_results: 兑换码抽奖结果（用于页面刷新后恢复）
"""

import click
import random
import string
import time
import os
from typing import Iterable, Dict, Set, List
from fcbyk.utils.config import load_json_config


class PickService:
    """抽奖服务业务逻辑"""
    
    def __init__(self, config_file: str, default_config: dict):
        self.config_file = config_file
        self.default_config = default_config
        
        # 抽奖限制模式：
        # - 旧逻辑：按 IP 限制（ip_draw_records），每个 IP 只能抽一次
        # - 新逻辑：按兑换码限制（redeem_codes），当 redeem_codes 不为空时优先生效，每个兑换码只能使用一次
        # - ip_file_history：记录每个 IP 已经抽中过哪些文件，避免同一 IP 重复抽到同一个文件
        self.ip_draw_records: Dict[str, str] = {}                    # {ip: filename}
        self.redeem_codes: Dict[str, bool] = {}                      # {code: used_flag}
        self.ip_file_history: Dict[str, Set[str]] = {}               # {ip: {filename, ...}}
        self.code_results: Dict[str, Dict] = {}                      # {code: {file: {...}, download_url: str, timestamp: str}} 保存兑换码的抽奖结果

    def reset_state(self):
        """重置抽奖状态"""
        self.ip_draw_records = {}
        self.redeem_codes = {}
        self.ip_file_history = {}
        self.code_results = {}

    def list_files(self, files_mode_root: str) -> List[Dict]:
        """列出文件模式下可供抽取的文件（支持单文件或目录）"""
        if not files_mode_root:
            return []
        root = files_mode_root
        if os.path.isfile(root):
            return [{
                'name': os.path.basename(root),
                'path': root,
                'size': os.path.getsize(root) if os.path.exists(root) else 0
            }]
        files = []
        try:
            for name in sorted(os.listdir(root)):
                full = os.path.join(root, name)
                if os.path.isfile(full):
                    files.append({
                        'name': name,
                        'path': full,
                        'size': os.path.getsize(full)
                    })
        except FileNotFoundError:
            return []
        return files

    def pick_file(self, candidates: List[Dict]) -> Dict:
        """从候选文件列表中随机选择一个"""
        return random.choice(candidates)

    def pick_random_item(self, items: List[str]) -> str:
        """从列表中随机选择一个元素"""
        return random.choice(items)

    def generate_redeem_codes(self, count: int, length: int = 4) -> Iterable[str]:
        """生成若干个随机兑换码（字母数字混合，大写）"""
        charset = string.ascii_uppercase + string.digits
        codes = set()
        while len(codes) < count:
            code = ''.join(random.choice(charset) for _ in range(length))
            codes.add(code)
        return sorted(codes)

    def pick_item(self, items: List[str]):
        """执行抽奖动画"""
        if not items:
            click.echo("Error: No items available. Please use --add to add items first")
            return
        
        click.echo("=== Random Pick ===")
        click.echo("Spinning...")
        
        max_length = max(len(f"Current pointer: {item}") for item in items) if items else 0

        def show_animation_frame(iterations: int, delay: float) -> None:
            """显示抽奖动画的一帧
            Args:
                iterations: 动画帧数
                delay: 每帧之间的延迟（秒）
            """
            for _ in range(iterations):
                current = random.choice(items)
                # 使用空格填充确保清除整行
                display_text = f"Current pointer: {current}"
                padding = " " * max(0, max_length - len(display_text))
                click.echo(f"\r{display_text}{padding}", nl=False)
                time.sleep(delay)
        
        # 三个阶段：快速 -> 中速 -> 慢速
        show_animation_frame(random.randint(100, 200), 0.05)
        show_animation_frame(random.randint(20, 40), 0.3)
        show_animation_frame(random.randint(3, 10), 0.7)
        
        click.echo("\nPick finished!")