import os
import json
from typing import Dict, Any, List, Optional


def get_config_path(app_name: str, filename: str) -> str:
    """
    获取指定应用的配置文件路径。

    生成路径格式为：
        ~/.{app_name}/{filename}

    Args:
        app_name (str): 应用名，用作隐藏目录名称。
        filename (str): 配置文件名。

    Returns:
        str: 配置文件绝对路径。
    """
    return os.path.join(
        os.path.expanduser("~"),
        f".{app_name}",
        filename
    )


def load_json_config(path: str, default: Dict[str, Any]) -> Dict[str, Any]:
    """
    加载 JSON 配置文件，并确保缺失字段被补齐。

    功能：
    - 如果配置文件不存在，则创建新文件并写入默认值。
    - 如果配置文件损坏（无法解析 JSON），则重建文件。
    - 如果文件中缺少默认配置字段，则自动补齐。

    Args:
        path (str): 配置文件路径。
        default (Dict[str, Any]): 默认配置字典，用于补齐或新建文件。

    Returns:
        Dict[str, Any]: 配置字典，包含所有默认字段。
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(path), exist_ok=True)

    config: Dict[str, Any] = {}

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            # 文件损坏或无法解析，重建
            config = {}
    else:
        # 文件不存在
        config = {}

    # 补齐缺失字段
    updated = False
    for k, v in default.items():
        if k not in config:
            config[k] = v
            updated = True

    # 如果文件不存在或有字段更新，则写回文件
    if not os.path.exists(path) or updated:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    return config


def save_config(config: Dict[str, Any], config_file: str) -> None:
    """
    将配置字典保存到指定 JSON 文件。

    如果文件不存在，会创建新文件；如果存在，则覆盖。

    Args:
        config (Dict[str, Any]): 配置字典
        config_file (str): 配置文件路径

    Returns:
        None

    Example:
        >>> config = {"model": "deepseek-chat", "stream": True}
        >>> save_config(config, "config.json")
    """
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_effective_config(
    cli_options: Dict[str, Any],
    config_file: str,
    default_config: Dict[str, Any],
    fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    根据 CLI 参数和配置文件返回最终生效的配置。

    优先级：
        CLI 参数 > 配置文件 > 默认配置

    Args:
        cli_options (Dict[str, Any]): CLI 参数字典，例如 {"model": "gpt", "stream": "1"}
        config_file (str): 配置文件路径
        default_config (Dict[str, Any]): 默认配置字典
        fields (List[str], optional): 需要处理的配置字段列表，默认处理所有默认配置字段

    Returns:
        Dict[str, Any]: 最终生效的配置字典

    Notes:
        - 对布尔字段会自动处理 "1"/"0" 或 "true"/"false"。
        - 如果 fields 指定了子集，只处理该子集。

    Example:
        >>> cli_options = {"model": "gpt", "stream": "1"}
        >>> effective_config = get_effective_config(cli_options, "config.json", default_config)
        >>> effective_config["stream"]
        True
    """
    config = load_json_config(config_file, default_config)

    if fields is None:
        fields = list(default_config.keys())

    for key in fields:
        if key in cli_options and cli_options[key] is not None:
            if isinstance(config.get(key), bool):
                # 处理布尔型字段，如 stream
                config[key] = str(cli_options[key]).lower() in ['1', 'true']
            else:
                config[key] = cli_options[key]

    return config
