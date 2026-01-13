"""
slide 控制器层
处理 Flask 路由、WebSocket 事件和 HTTP 请求/响应
"""
import os
from functools import wraps
from flask import jsonify, request, session
from flask_socketio import SocketIO, disconnect

from fcbyk.web.app import create_spa
from .service import SlideService


def create_slide_app(service: SlideService):
    """
    创建 slide Flask 应用
    
    Args:
        service: SlideService 实例
        
    Returns:
        (Flask应用, SocketIO实例)
    """
    # 使用工厂函数创建应用
    app = create_spa("slide.html")
    
    # 设置 secret_key 用于 session
    app.secret_key = os.urandom(24)
    
    # 创建 SocketIO 实例
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # 将 service 附加到 app
    app.slide_service = service
    
    # 注册路由和事件
    register_routes(app, service)
    register_socketio_events(socketio, service)
    
    return app, socketio


def require_auth(f):
    """装饰器：HTTP 路由要求认证"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_socketio_auth(f):
    """装饰器：WebSocket 事件要求认证"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return
        return f(*args, **kwargs)
    return decorated_function


def register_routes(app, service: SlideService):
    """注册 HTTP 路由"""
    
    @app.route('/api/login', methods=['POST'])
    def login():
        """登录验证"""
        data = request.get_json()
        password = data.get('password', '')
        
        if service.verify_password(password):
            session['authenticated'] = True
            return jsonify({'status': 'success', 'message': 'Login successful'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid password'}), 401
    
    @app.route('/api/check_auth', methods=['GET'])
    def check_auth():
        """检查认证状态"""
        if session.get('authenticated'):
            return jsonify({'status': 'success', 'authenticated': True})
        else:
            return jsonify({'status': 'success', 'authenticated': False})
    
    # ============ PPT 控制 API ============
    
    @app.route('/api/next', methods=['POST'])
    @require_auth
    def next_slide():
        """下一页"""
        success, error = service.next_slide()
        if success:
            return jsonify({'status': 'success', 'action': 'next'})
        else:
            return jsonify({'status': 'error', 'message': error}), 500
    
    @app.route('/api/prev', methods=['POST'])
    @require_auth
    def prev_slide():
        """上一页"""
        success, error = service.prev_slide()
        if success:
            return jsonify({'status': 'success', 'action': 'prev'})
        else:
            return jsonify({'status': 'error', 'message': error}), 500
    
    @app.route('/api/home', methods=['POST'])
    @require_auth
    def home_slide():
        """回到首页"""
        success, error = service.home_slide()
        if success:
            return jsonify({'status': 'success', 'action': 'home'})
        else:
            return jsonify({'status': 'error', 'message': error}), 500
    
    @app.route('/api/end', methods=['POST'])
    @require_auth
    def end_slide():
        """跳到最后"""
        success, error = service.end_slide()
        if success:
            return jsonify({'status': 'success', 'action': 'end'})
        else:
            return jsonify({'status': 'error', 'message': error}), 500
    
    # ============ 鼠标控制 API (HTTP 接口，保留兼容性) ============
    
    @app.route('/api/mouse/move', methods=['POST'])
    @require_auth
    def mouse_move():
        """移动鼠标"""
        data = request.get_json()
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        
        success, error = service.move_mouse(dx, dy)
        if success:
            return jsonify({'status': 'success', 'action': 'move'})
        else:
            return jsonify({'status': 'error', 'message': error}), 500
    
    @app.route('/api/mouse/click', methods=['POST'])
    @require_auth
    def mouse_click():
        """鼠标左键点击"""
        success, error = service.click_mouse()
        if success:
            return jsonify({'status': 'success', 'action': 'click'})
        else:
            return jsonify({'status': 'error', 'message': error}), 500
    
    @app.route('/api/mouse/rightclick', methods=['POST'])
    @require_auth
    def mouse_rightclick():
        """鼠标右键点击"""
        success, error = service.right_click_mouse()
        if success:
            return jsonify({'status': 'success', 'action': 'rightclick'})
        else:
            return jsonify({'status': 'error', 'message': error}), 500
    
    @app.route('/api/mouse/scroll', methods=['POST'])
    @require_auth
    def mouse_scroll():
        """鼠标滚动"""
        data = request.get_json()
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        
        success, error = service.scroll_mouse(dx, dy)
        if success:
            return jsonify({'status': 'success', 'action': 'scroll'})
        else:
            return jsonify({'status': 'error', 'message': error}), 500


def register_socketio_events(socketio: SocketIO, service: SlideService):
    """注册 WebSocket 事件"""
    
    @socketio.on('connect')
    def handle_connect():
        """WebSocket 连接时验证认证"""
        if not session.get('authenticated'):
            disconnect()
            return False
    
    @socketio.on('mouse_move')
    @require_socketio_auth
    def handle_mouse_move(data):
        """WebSocket 处理鼠标移动"""
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        service.move_mouse(dx, dy)
    
    @socketio.on('mouse_click')
    @require_socketio_auth
    def handle_mouse_click():
        """WebSocket 处理鼠标左键点击"""
        service.click_mouse()
    
    @socketio.on('mouse_rightclick')
    @require_socketio_auth
    def handle_mouse_rightclick():
        """WebSocket 处理鼠标右键点击"""
        service.right_click_mouse()
    
    @socketio.on('mouse_scroll')
    @require_socketio_auth
    def handle_mouse_scroll(data):
        """WebSocket 处理鼠标滚动"""
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        service.scroll_mouse(dx, dy)