"""
lansend controller 层

负责 Flask 路由注册、请求解析、调用 service 并返回响应。

函数:
- create_lansend_app(service) -> Flask: 创建并配置 Flask 应用
- _try_int(v) -> Optional[int]: 安全地将值转换为整数
- register_routes(app, service): 注册所有 API 路由
- register_upload_routes(app, service): 注册文件上传相关路由
- register_chat_routes(app, service): 注册聊天相关路由

路由:
- /api/config: 获取配置信息（un_download, un_upload, chat_enabled）
- /upload: 文件上传接口（支持密码验证，仅在未禁用上传时注册）
- /api/file/<path:filename>: 获取文件内容（文本/图片/二进制）
- /api/tree: 获取递归文件树
- /api/directory: 获取目录列表信息
- /api/preview/<path:filename>: 预览文件（支持 Range 请求，用于视频/音频流式播放）
- /api/download/<path:filename>: 下载文件（流式传输）
- /api/chat/messages: 获取聊天消息列表（仅在启用聊天时注册）
- /api/chat/send: 发送聊天消息（仅在启用聊天时注册）
"""

import os
import re
import mimetypes
from datetime import datetime
from typing import Optional, List, Dict, Any

from flask import abort, jsonify, request, send_file, Response, stream_with_context

from fcbyk.web.app import create_spa
from .service import LansendService
import urllib.parse

# 聊天消息存储（内存中，服务重启后清空）
_chat_messages: List[Dict[str, Any]] = []


def create_lansend_app(service: LansendService):
    app = create_spa("lansend.html")
    app.lansend_service = service
    register_routes(app, service)
    return app


def _try_int(v) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _get_client_ip() -> str:
    """获取客户端 IP，优先 X-Forwarded-For"""
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        # X-Forwarded-For 可能包含多个 IP，取第一个
        return xff.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def register_chat_routes(app, service: LansendService):
    """注册聊天相关路由"""
    @app.route("/api/chat/messages", methods=["GET"])
    def get_chat_messages():
        """获取聊天消息列表，同时返回当前客户端的 IP"""
        return jsonify({
            "messages": _chat_messages,
            "current_ip": _get_client_ip()
        })

    @app.route("/api/chat/send", methods=["POST"])
    def send_chat_message():
        """发送聊天消息"""
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "message is required"}), 400

        message_text = data.get("message", "").rstrip()
        if not message_text.strip():
            return jsonify({"error": "message cannot be empty"}), 400

        ip = _get_client_ip()
        timestamp = datetime.now().isoformat()

        message = {
            "id": len(_chat_messages) + 1,
            "ip": ip,
            "message": message_text,
            "timestamp": timestamp,
        }

        _chat_messages.append(message)

        # 限制消息数量，避免内存占用过大（保留最近1000条）
        if len(_chat_messages) > 1000:
            _chat_messages.pop(0)

        return jsonify({"success": True, "message": message})


def register_upload_routes(app, service: LansendService):
    """注册文件上传相关路由"""
    @app.route("/upload", methods=["POST"])
    def upload_file():
        ip = _get_client_ip()
        rel_path = (request.form.get("path") or "").strip("/")
        size_hint = _try_int(request.form.get("size"))

        # 仅做密码验证（没有文件）的请求：只验证密码并返回结果，不记录上传日志
        if "file" not in request.files and "password" in request.form:
            if service.config.upload_password:
                if request.form["password"] != service.config.upload_password:
                    return jsonify({"error": "wrong password"}), 401
                return jsonify({"message": "password ok"})
            return jsonify({"error": "upload password not set"}), 400

        try:
            target_dir = service.abs_target_dir(rel_path)
        except ValueError:
            service.log_upload(ip, 0, "failed (shared directory not set)", rel_path)
            return jsonify({"error": "shared directory not set"}), 400
        except PermissionError:
            service.log_upload(ip, 0, "failed (invalid path)", rel_path)
            return jsonify({"error": "invalid path"}), 400

        if service.config.upload_password:
            if "password" not in request.form:
                service.log_upload(ip, 0, "failed (upload password required)", rel_path)
                return jsonify({"error": "upload password required"}), 401
            if request.form["password"] != service.config.upload_password:
                service.log_upload(ip, 0, "failed (wrong password)", rel_path)
                return jsonify({"error": "wrong password"}), 401

        if "file" not in request.files:
            service.log_upload(ip, 0, "failed (no file field)", rel_path)
            return jsonify({"error": "missing file"}), 400

        file = request.files["file"]

        file_size = file.content_length if file.content_length not in (None, 0) else size_hint
        if file_size is None:
            try:
                pos = file.stream.tell()
                file.stream.seek(0, os.SEEK_END)
                file_size = file.stream.tell()
                file.stream.seek(pos, os.SEEK_SET)
            except Exception:
                file_size = None

        if file.filename == "":
            service.log_upload(ip, 0, "failed (no file selected)", rel_path)
            return jsonify({"error": "no file selected"}), 400

        filename = service.safe_filename(file.filename) or "untitled"

        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            service.log_upload(ip, 0, f"failed (target directory missing: {rel_path or 'root'})", rel_path)
            return jsonify({"error": "target directory not found"}), 400

        # 处理文件名冲突：自动重命名为 name_1.ext, name_2.ext 等
        target_path = os.path.join(target_dir, filename)
        renamed = False
        if os.path.exists(target_path):
            name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(target_path):
                new_filename = f"{name}_{counter}{ext}"
                target_path = os.path.join(target_dir, new_filename)
                counter += 1
            filename = new_filename
            renamed = True

        save_path = os.path.join(target_dir, filename)
        try:
            file.save(save_path)
            service.log_upload(ip, 1, f"success ({filename})", rel_path, file_size)
            return jsonify({"message": "file uploaded", "filename": filename, "renamed": renamed})
        except Exception as e:
            service.log_upload(ip, 1, f"failed (save failed: {e})", rel_path, file_size)
            return jsonify({"error": "failed to save file"}), 500


def register_routes(app, service: LansendService):
    @app.route("/api/config")
    def api_config():
        return jsonify({
            "un_download": bool(getattr(service.config, "un_download", False)),
            "un_upload": bool(getattr(service.config, "un_upload", False)),
            "chat_enabled": bool(getattr(service.config, "chat_enabled", False)),
        })

    if not service.config.un_upload:
        register_upload_routes(app, service)

    if service.config.chat_enabled:
        register_chat_routes(app, service)

    @app.route("/api/file/<path:filename>")
    def api_file(filename):
        try:
            data = service.read_file_content(filename)
            return jsonify(data)
        except ValueError:
            return jsonify({"error": "Shared directory not specified"}), 400
        except PermissionError:
            abort(404, description="Invalid path")
        except FileNotFoundError:
            abort(404, description="File not found")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/tree")
    def api_tree():
        try:
            base = service.ensure_shared_directory()
        except ValueError:
            return jsonify({"error": "Shared directory not specified"}), 400
        tree = service.get_file_tree(base)
        return jsonify({"tree": tree})

    @app.route("/api/directory")
    def api_directory():
        try:
            relative_path = request.args.get("path", "").strip("/")
            data = service.get_directory_listing(relative_path)
            return jsonify(data)
        except ValueError:
            return jsonify({"error": "Shared directory not specified"}), 400
        except FileNotFoundError:
            return jsonify({"error": "Directory not found"}), 404

    @app.route("/api/preview/<path:filename>")
    def api_preview(filename):
        try:
            file_path = service.resolve_file_path(filename)
        except (ValueError, PermissionError):
            abort(404)

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            abort(404)

        file_size = os.path.getsize(file_path)
        range_header = request.headers.get("Range", None)

        start = 0
        end = file_size - 1

        status_code = 200
        mimetype = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        headers = {
            "Content-Type": mimetype,
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
        }

        # 处理 Range 请求（用于视频/音频的断点续传和流式播放）
        if range_header:
            range_match = re.search(r"bytes=(\d+)-(\d*)", range_header)
            if range_match:
                start = int(range_match.group(1))
                if range_match.group(2):
                    end = int(range_match.group(2))
                else:
                    end = file_size - 1

                if start >= file_size or end >= file_size:
                    return Response(
                        "Requested Range Not Satisfiable",
                        status=416,
                        headers={"Content-Range": f"bytes */{file_size}"},
                    )

                length = end - start + 1
                headers["Content-Length"] = str(length)
                headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
                status_code = 206

        # 流式生成器：按 1MB 块读取
        def generate_chunks(f, start_pos, size):
            with f:
                f.seek(start_pos)
                bytes_to_read = size
                while bytes_to_read > 0:
                    chunk_size = 1024 * 1024  # 1MB chunks
                    data = f.read(min(chunk_size, bytes_to_read))
                    if not data:
                        break
                    bytes_to_read -= len(data)
                    yield data

        file_handle = open(file_path, "rb")
        response_body = generate_chunks(file_handle, start, end - start + 1)

        return Response(stream_with_context(response_body), status=status_code, headers=headers)


    @app.route("/api/download/<path:filename>")
    def api_download(filename):
        try:
            file_path = service.resolve_file_path(filename)
        except (ValueError, PermissionError):
            abort(404)

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            abort(404)

        file_size = os.path.getsize(file_path)
        raw_name = os.path.basename(file_path)
        safe_name = urllib.parse.quote(raw_name)

        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(file_size),
            "Content-Disposition": (
                f"attachment; filename=\"{raw_name}\"; "
                f"filename*=UTF-8''{safe_name}"
            ),
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache",
        }

        def generate():
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk

        return Response(
            stream_with_context(generate()),
            headers=headers,
            status=200
        )


