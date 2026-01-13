"""
lansend 业务逻辑层

负责纯业务逻辑：路径/文件处理、目录树、内容读取等。

数据类:
- LansendConfig: 配置封装（shared_directory, upload_password, un_download, un_upload, chat_enabled）

类:
- LansendService: 文件共享服务核心类
  - safe_filename(filename) -> str: 清理文件名中的非法字符
  - is_image_file(filename) -> bool: 判断是否为图片文件
  - format_size(num_bytes) -> str: 格式化文件大小
  - get_path_parts(current_path) -> List[Dict]: 将路径拆分为面包屑导航
  - log_upload(ip, file_count, status, rel_path, file_size): 记录上传日志
  - ensure_shared_directory() -> str: 确保共享目录已设置
  - abs_target_dir(rel_path) -> str: 获取目标目录的绝对路径（带安全检查）
  - get_file_tree(base_path, relative_path) -> List[Dict]: 获取递归文件树
  - get_directory_listing(relative_path) -> Dict: 获取目录列表信息
  - resolve_file_path(filename) -> str: 解析并验证文件路径（带安全检查）
  - read_file_content(relative_path) -> Dict: 读取文件内容（文本/图片/二进制）
  - pick_upload_password(flag_password, un_upload, click_module) -> Optional[str]: 根据参数决定是否提示输入上传密码
"""

import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class LansendConfig:
    shared_directory: Optional[str] = None
    upload_password: Optional[str] = None
    un_download: bool = False
    un_upload: bool = False
    chat_enabled: bool = False


class LansendService:
    def __init__(self, config: LansendConfig):
        self.config = config

    # -------------------- 基础工具 --------------------
    @staticmethod
    def safe_filename(filename: str) -> str:
        return re.sub(r"[^\w\s\u4e00-\u9fff\-\.]", "", filename)

    @staticmethod
    def is_image_file(filename: str) -> bool:
        image_extensions = {
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff", ".tif"
        }
        ext = os.path.splitext(filename)[1].lower()
        return ext in image_extensions

    @staticmethod
    def format_size(num_bytes: Optional[int]) -> str:
        if num_bytes is None:
            return "unknown size"
        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(num_bytes)
        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{size:.2f} {unit}" if unit != "B" else f"{int(size)} {unit}"
            size /= 1024

    @staticmethod
    def get_path_parts(current_path: str) -> List[Dict[str, str]]:
        """把相对路径拆成面包屑。

        注意：这里必须统一使用 URL 风格的 "/" 分隔符。
        在 Windows 上如果用 os.path.join，会生成 "\\"，从而导致前端面包屑拼接/跳转异常。
        """
        parts: List[Dict[str, str]] = []
        if current_path:
            path_parts = current_path.split("/")
            current = ""
            for part in path_parts:
                if part:
                    # 强制使用 "/" 作为分隔符，避免 Windows 反斜杠污染 API 返回
                    current = f"{current}/{part}" if current else part
                    parts.append({"name": part, "path": current})
        return parts

    def log_upload(
        self,
        ip: str,
        file_count: int,
        status: str,
        rel_path: str = "",
        file_size: Optional[int] = None,
    ) -> None:

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path_str = f"/{rel_path}" if rel_path else "/"
        size_str = self.format_size(file_size) if file_size is not None else "unknown size"
        log_msg = f" [{ts}] {ip} upload {file_count} file(s), status: {status}, path: {path_str}, size: {size_str}\n"
        sys.stderr.write(log_msg)
        sys.stderr.flush()

    # -------------------- 业务逻辑 --------------------
    def ensure_shared_directory(self) -> str:
        if not self.config.shared_directory:
            raise ValueError("shared directory not set")
        return self.config.shared_directory

    def abs_target_dir(self, rel_path: str) -> str:
        base = self.ensure_shared_directory()
        rel_path = (rel_path or "").strip("/")
        target_dir = os.path.abspath(os.path.join(base, rel_path))
        base_abs = os.path.abspath(base)
        # 安全检查：确保目标目录在共享目录内，防止路径遍历攻击
        if not target_dir.startswith(base_abs):
            raise PermissionError("invalid path")
        return target_dir

    def get_file_tree(self, base_path: str, relative_path: str = "") -> List[Dict[str, Any]]:
        current_path = os.path.join(base_path, relative_path) if relative_path else base_path
        items: List[Dict[str, Any]] = []

        if not os.path.exists(current_path) or not os.path.isdir(current_path):
            return items

        for name in os.listdir(current_path):
            full_path = os.path.join(current_path, name)
            item_path = os.path.join(relative_path, name) if relative_path else name

            item: Dict[str, Any] = {
                "name": name,
                "path": item_path.replace("\\", "/"),  # 统一使用 "/" 分隔符
                "is_dir": os.path.isdir(full_path),
            }

            if item["is_dir"]:
                item["children"] = self.get_file_tree(base_path, item_path)

            items.append(item)

        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return items

    def get_directory_listing(self, relative_path: str = "") -> Dict[str, Any]:
        base = self.ensure_shared_directory()
        relative_path = (relative_path or "").strip("/")
        current_path = os.path.join(base, relative_path) if relative_path else base

        if not os.path.exists(current_path) or not os.path.isdir(current_path):
            raise FileNotFoundError("Directory not found")

        items: List[Dict[str, Any]] = []
        for name in os.listdir(current_path):
            full_path = os.path.join(current_path, name)
            item_path = os.path.join(relative_path, name) if relative_path else name
            items.append(
                {
                    "name": name,
                    "path": item_path.replace("\\", "/"),  # 统一使用 "/" 分隔符
                    "is_dir": os.path.isdir(full_path),
                }
            )
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

        share_name = os.path.basename(base)
        return {
            "share_name": share_name,
            "relative_path": relative_path,
            "path_parts": self.get_path_parts(relative_path),
            "items": items,
            "require_password": bool(self.config.upload_password),
        }

    def resolve_file_path(self, filename: str) -> str:
        base = self.ensure_shared_directory()
        normalized_path = (filename or "").replace("/", os.sep)
        file_path = os.path.abspath(os.path.join(base, normalized_path))
        # 安全检查：确保文件路径在共享目录内，防止路径遍历攻击
        if not file_path.startswith(os.path.abspath(base)):
            raise PermissionError("Invalid path")
        return file_path

    def read_file_content(self, relative_path: str) -> Dict[str, Any]:
        file_path = self.resolve_file_path(relative_path)

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            raise FileNotFoundError("File not found")

        if self.is_image_file(file_path):
            return {
                "is_image": True,
                "path": relative_path,
                "name": os.path.basename(relative_path),
            }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "content": content,
                "path": relative_path,
                "name": os.path.basename(relative_path),
                "is_image": False,
            }
        except UnicodeDecodeError:
            return {
                "is_binary": True,
                "path": relative_path,
                "name": os.path.basename(relative_path),
                "error": "Binary file cannot be displayed",
            }

    def pick_upload_password(self, flag_password: bool, un_upload: bool, click_module) -> Optional[str]:
        """根据参数决定是否提示输入上传密码（保持旧行为）。"""
        if flag_password and not un_upload:
            pw = click_module.prompt(
                "Upload password (press Enter to use default: 123456)",
                hide_input=True,
                default="123456",
                show_default=False,
            )
            pw = pw if pw else "123456"
            return pw
        return None

