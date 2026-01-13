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

from flask import abort, jsonify, request, Response, stream_with_context

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

    # -------------------- 分片上传（备用接口） --------------------
    # 协议：
    # 1) POST /api/upload/init  (form)
    #    fields: filename, size, path, chunk_size, total_chunks, password?
    #    -> {upload_id, chunk_size, total_chunks, filename, renamed}
    # 2) POST /api/upload/chunk (binary)
    #    query: upload_id, index
    #    header: X-Upload-Password 可选
    #    body: chunk bytes (application/octet-stream)
    #    -> {ok:true}
    # 3) POST /api/upload/complete (json)
    #    body: {upload_id}
    #    -> {message:'file uploaded', filename, renamed}
    # 4) POST /api/upload/abort (json)
    #    body: {upload_id}
    #    -> {ok:true}

    def _verify_password_from_request() -> Optional[Response]:
        if not service.config.upload_password:
            return None
        pw = request.headers.get("X-Upload-Password") or request.form.get("password")
        if not pw:
            return jsonify({"error": "upload password required"}), 401
        if pw != service.config.upload_password:
            return jsonify({"error": "wrong password"}), 401
        return None

    def _get_upload_tmp_dir() -> str:
        # 临时目录放在共享目录下，避免跨盘/权限问题
        base = service.ensure_shared_directory()
        tmp_dir = os.path.join(base, ".lansend_upload_tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        return tmp_dir

    def _safe_upload_id(upload_id: str) -> str:
        # 只允许简单字符，防止路径穿越
        return re.sub(r"[^a-zA-Z0-9_-]", "", upload_id or "")

    @app.route("/api/upload/init", methods=["POST"])
    def upload_init():
        ip = _get_client_ip()
        err = _verify_password_from_request()
        if err:
            return err

        filename_raw = (request.form.get("filename") or "").strip()
        size = _try_int(request.form.get("size"))
        rel_path = (request.form.get("path") or "").strip("/")
        chunk_size = _try_int(request.form.get("chunk_size")) or (8 * 1024 * 1024)
        total_chunks = _try_int(request.form.get("total_chunks"))

        if not filename_raw:
            return jsonify({"error": "filename is required"}), 400
        if size is None or size < 0:
            return jsonify({"error": "size is required"}), 400
        if total_chunks is None or total_chunks <= 0:
            return jsonify({"error": "total_chunks is required"}), 400
        if chunk_size <= 0:
            return jsonify({"error": "invalid chunk_size"}), 400

        try:
            target_dir = service.abs_target_dir(rel_path)
        except ValueError:
            service.log_upload(ip, 0, "failed (shared directory not set)", rel_path)
            return jsonify({"error": "shared directory not set"}), 400
        except PermissionError:
            service.log_upload(ip, 0, "failed (invalid path)", rel_path)
            return jsonify({"error": "invalid path"}), 400

        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            service.log_upload(ip, 0, f"failed (target directory missing: {rel_path or 'root'})", rel_path, size)
            return jsonify({"error": "target directory not found"}), 400

        filename = service.safe_filename(filename_raw) or "untitled"

        # 冲突处理：先预生成最终文件名
        final_path = os.path.join(target_dir, filename)
        renamed = False
        if os.path.exists(final_path):
            name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(final_path):
                filename = f"{name}_{counter}{ext}"
                final_path = os.path.join(target_dir, filename)
                counter += 1
            renamed = True

        # upload_id：时间戳+pid+随机
        upload_id = f"{int(datetime.now().timestamp()*1000)}_{os.getpid()}_{os.urandom(6).hex()}"

        tmp_root = _get_upload_tmp_dir()
        upload_dir = os.path.join(tmp_root, upload_id)
        os.makedirs(upload_dir, exist_ok=True)

        meta = {
            "upload_id": upload_id,
            "filename": filename,
            "size": size,
            "rel_path": rel_path,
            "target_dir": target_dir,
            "final_path": final_path,
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "renamed": renamed,
            "created_at": datetime.now().isoformat(),
        }
        with open(os.path.join(upload_dir, "meta.json"), "w", encoding="utf-8") as f:
            import json
            json.dump(meta, f, ensure_ascii=False)

        return jsonify({
            "upload_id": upload_id,
            "chunk_size": chunk_size,
            "total_chunks": total_chunks,
            "filename": filename,
            "renamed": renamed,
        })

    @app.route("/api/upload/chunk", methods=["POST"])
    def upload_chunk():
        ip = _get_client_ip()
        err = _verify_password_from_request()
        if err:
            return err

        upload_id = _safe_upload_id(request.args.get("upload_id") or "")
        index = _try_int(request.args.get("index"))
        if not upload_id:
            return jsonify({"error": "upload_id is required"}), 400
        if index is None or index < 0:
            return jsonify({"error": "index is required"}), 400

        tmp_root = _get_upload_tmp_dir()
        upload_dir = os.path.join(tmp_root, upload_id)
        meta_path = os.path.join(upload_dir, "meta.json")
        if not os.path.exists(meta_path):
            return jsonify({"error": "upload not found"}), 404

        # 直接读取 raw body（每块 8~16MB），避免 multipart 解析
        chunk_path = os.path.join(upload_dir, f"chunk_{index:08d}.part")
        try:
            with open(chunk_path, "wb") as f:
                # request.stream 是类文件对象
                while True:
                    buf = request.stream.read(1024 * 1024)
                    if not buf:
                        break
                    f.write(buf)
        except Exception as e:
            service.log_upload(ip, 1, f"failed (chunk save failed: {e})")
            return jsonify({"error": "failed to save chunk"}), 500

        return jsonify({"ok": True})

    @app.route("/api/upload/complete", methods=["POST"])
    def upload_complete():
        import json
        ip = _get_client_ip()
        err = _verify_password_from_request()
        if err:
            return err

        data = request.get_json(silent=True) or {}
        upload_id = _safe_upload_id(data.get("upload_id") or "")
        if not upload_id:
            return jsonify({"error": "upload_id is required"}), 400

        tmp_root = _get_upload_tmp_dir()
        upload_dir = os.path.join(tmp_root, upload_id)
        meta_path = os.path.join(upload_dir, "meta.json")
        if not os.path.exists(meta_path):
            return jsonify({"error": "upload not found"}), 404

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        total_chunks = int(meta["total_chunks"])
        final_path = meta["final_path"]
        filename = meta["filename"]
        rel_path = meta.get("rel_path", "")
        size = int(meta.get("size") or 0)
        renamed = bool(meta.get("renamed"))

        # 校验分片是否齐全
        missing = []
        for i in range(total_chunks):
            p = os.path.join(upload_dir, f"chunk_{i:08d}.part")
            if not os.path.exists(p):
                missing.append(i)
                if len(missing) > 20:
                    break
        if missing:
            return jsonify({"error": f"missing chunks: {missing[:20]}"}), 400

        # 合并写入最终文件（流式，不占内存）
        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, "wb") as out:
                for i in range(total_chunks):
                    p = os.path.join(upload_dir, f"chunk_{i:08d}.part")
                    with open(p, "rb") as inp:
                        while True:
                            buf = inp.read(1024 * 1024)
                            if not buf:
                                break
                            out.write(buf)
        except Exception as e:
            service.log_upload(ip, 1, f"failed (merge failed: {e})", rel_path, size)
            return jsonify({"error": "failed to merge file"}), 500

        # 清理临时目录
        try:
            for name in os.listdir(upload_dir):
                try:
                    os.remove(os.path.join(upload_dir, name))
                except Exception:
                    pass
            try:
                os.rmdir(upload_dir)
            except Exception:
                pass
        except Exception:
            pass

        service.log_upload(ip, 1, f"success ({filename})", rel_path, size)
        return jsonify({"message": "file uploaded", "filename": filename, "renamed": renamed})

    @app.route("/api/upload/abort", methods=["POST"])
    def upload_abort():
        err = _verify_password_from_request()
        if err:
            return err
        data = request.get_json(silent=True) or {}
        upload_id = _safe_upload_id(data.get("upload_id") or "")
        if not upload_id:
            return jsonify({"error": "upload_id is required"}), 400
        tmp_root = _get_upload_tmp_dir()
        upload_dir = os.path.join(tmp_root, upload_id)
        if os.path.exists(upload_dir):
            # 尽力删除
            for root, dirs, files in os.walk(upload_dir, topdown=False):
                for fn in files:
                    try:
                        os.remove(os.path.join(root, fn))
                    except Exception:
                        pass
                for dn in dirs:
                    try:
                        os.rmdir(os.path.join(root, dn))
                    except Exception:
                        pass
            try:
                os.rmdir(upload_dir)
            except Exception:
                pass
        return jsonify({"ok": True})


    # -------------------- 普通上传接口 --------------------
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

        # 对视频/音频：即使客户端未带 Range，也强制走 206（更利于浏览器尽快开始后续分段请求）
        is_media = (mimetype or '').startswith('video/') or (mimetype or '').startswith('audio/')

        # 处理 Range 请求（用于视频/音频的断点续传和流式播放）
        if range_header or is_media:
            # 没有 Range 但属于媒体文件：默认从 0 开始
            effective_range = range_header or 'bytes=0-'
            range_match = re.search(r"bytes=(\d+)-(\d*)", effective_range)
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

                # 媒体文件优化：限制单次 Range 响应的最大大小，避免浏览器发 bytes=0- 时返回超大区间
                if is_media:
                    max_media_chunk = 512 * 1024  # 512KB
                    end = min(end, start + max_media_chunk - 1)

                length = end - start + 1
                headers["Content-Length"] = str(length)
                headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
                status_code = 206

        headers.setdefault('Cache-Control', 'no-cache')

        # 流式生成器：按 1MB 块读取（在生成器内部打开文件，避免文件句柄生命周期问题）
        def generate_chunks(path, start_pos, size):
            with open(path, "rb") as f:
                f.seek(start_pos)
                bytes_to_read = size
                while bytes_to_read > 0:
                    chunk_size = 256 * 1024  # 256KB chunks
                    data = f.read(min(chunk_size, bytes_to_read))
                    if not data:
                        break
                    bytes_to_read -= len(data)
                    yield data

        response_body = generate_chunks(file_path, start, end - start + 1)

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

        # 关键修复：构建一个完全符合 RFC 规范且为纯 ASCII 的 Content-Disposition 头
        # 1. 将原始文件名进行 URL 编码，用于 filename* 参数，这部分是纯 ASCII
        safe_name_utf8 = urllib.parse.quote(raw_name)

        # 2. 创建一个只包含 ASCII 字符的回退文件名，给不支持 RFC 6266 的老客户端用
        fallback_name = raw_name.encode('ascii', 'ignore').decode('ascii').strip()

        # 如果过滤后只剩扩展名（例如中文名导致变成 ".png"），则生成更友好的回退名：download.png
        ext = os.path.splitext(raw_name)[1]
        if not fallback_name or fallback_name == ext:
            fallback_name = f"download{ext}" if ext else 'download'

        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(file_size),
            "Content-Disposition": f"attachment; filename=\"{fallback_name}\"; filename*=UTF-8''{safe_name_utf8}",
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

